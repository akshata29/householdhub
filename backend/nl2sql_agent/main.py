"""
NL2SQL Agent using MCP Server for MSSQL
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from common.schemas import (
    A2AMessage, NL2SQLRequest, NL2SQLResponse, 
    AgentType, MessageStatus
)
from common.config import get_settings, get_cors_origins
from common.mcp_client import MCPSQLServer
from common.auth import get_openai_access_token
from a2a.broker import create_broker
from openai import AzureOpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NL2SQLAgent:
    """NL2SQL Agent using MCP Server architecture with pure LLM-driven query understanding"""
    
    def __init__(self, connection_string: str):
        self.mcp_server = MCPSQLServer(connection_string)
        self.schema_cache = {}
        settings = get_settings()
        self.settings = settings
        
        # Initialize Azure OpenAI client for intelligent SQL generation
        self.openai_client = None
        if self.settings.azure_openai_endpoint:
            try:
                access_token = get_openai_access_token()
                self.openai_client = AzureOpenAI(
                    azure_endpoint=self.settings.azure_openai_endpoint,
                    azure_ad_token=access_token,
                    api_version=self.settings.azure_openai_api_version
                )
                logger.info("✅ Azure OpenAI client initialized for intelligent SQL generation")
            except Exception as e:
                logger.warning(f"⚠️ Could not initialize Azure OpenAI client: {e}")
        
        # No need for predefined patterns - let the LLM understand any query!
    
    async def verify_database_data(self) -> Dict[str, Any]:
        """Verify what data exists in the database for debugging"""
        try:
            verification_queries = {
                "households_count": "SELECT COUNT(*) as count FROM dbo.Households",
                "accounts_count": "SELECT COUNT(*) as count FROM dbo.Accounts", 
                "sample_households": "SELECT TOP 5 HouseholdID, Name FROM dbo.Households",
                "sample_accounts_with_balance": "SELECT TOP 5 AccountID, Name, Balance FROM dbo.Accounts WHERE Balance > 0"
            }
            
            results = {}
            for query_name, query in verification_queries.items():
                result = await self.mcp_server.call_tool("read_data", {"query": query})
                if result.get("success"):
                    results[query_name] = result.get("data", [])
                    logger.info(f"🔍 DB Verification - {query_name}: {results[query_name]}")
                else:
                    results[query_name] = f"Error: {result.get('error')}"
                    logger.error(f"❌ DB Verification - {query_name} failed: {result.get('error')}")
            
            return results
            
        except Exception as e:
            logger.error(f"Database verification failed: {e}")
            return {"error": str(e)}
        
    async def get_schema_info(self) -> Dict[str, Any]:
        """Get database schema information using MCP Server."""
        if self.schema_cache:
            return self.schema_cache
            
        try:
            schema_result = await self.mcp_server.get_schema_info()
            if schema_result.get("success"):
                self.schema_cache = schema_result.get("schema", {})
                return self.schema_cache
            else:
                logger.error(f"Failed to get schema: {schema_result.get('error')}")
                return {}
        except Exception as e:
            logger.error(f"Error getting schema info: {e}")
            return {}
       
    async def translate_nl_to_sql(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Translate natural language to SQL using MCP Server and intent detection."""
        try:
            logger.info(f"🔍 NL2SQL Translation Starting")
            logger.info(f"📝 Input Query: '{query}'")
            logger.info(f"📋 Context: {context}")
            
            # Get schema information
            schema_info = await self.get_schema_info()
            logger.info(f"📊 Schema Info Retrieved: {len(schema_info)} tables/objects")
            
            # Generate SQL using LLM 
            sql_query = await self._use_llm_to_generate_sql(query, schema_info, context)
            
            if not sql_query:
                logger.error(f"❌ Failed to generate SQL query")
                return {
                    "success": False,
                    "error": "Could not generate SQL query from natural language input"
                }
            
            logger.info(f"🔧 Generated SQL Query:")
            logger.info(f"📄 SQL: {sql_query}")
            
            # Execute query using MCP Server
            logger.info(f"⚡ Executing SQL via MCP Server...")
            result = await self.mcp_server.call_tool("read_data", {"query": sql_query})
            
            logger.info(f"📊 SQL Execution Result:")
            logger.info(f"   Success: {result.get('success')}")
            logger.info(f"   Row Count: {result.get('row_count', 'N/A')}")
            logger.info(f"   Execution Time: {result.get('execution_time_ms', 'N/A')}ms")
            
            if result.get("success"):
                data = result.get("data", [])
                logger.info(f"✅ Query Successful - Retrieved {len(data)} rows")
                if len(data) > 0:
                    logger.info(f"📝 Sample Data (first 3 rows): {data[:3]}")
                else:
                    logger.warning(f"⚠️  Query returned no results - this might be the issue!")
                    
                return {
                    "success": True,
                    "sql_query": sql_query,
                    "results": data,
                    "row_count": result.get("row_count", 0),
                    "execution_time_ms": result.get("execution_time_ms", 0),

                    "message": result.get("message", "Query executed successfully")
                }
            else:
                error_msg = result.get("error", "Query execution failed")
                logger.error(f"❌ SQL Execution Failed: {error_msg}")
                return {
                    "success": False,
                    "sql_query": sql_query,
                    "error": error_msg,

                }
                
        except Exception as e:
            logger.error(f"💥 Exception in NL to SQL translation: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
       
    async def _use_llm_to_generate_sql(self, query: str, schema_info: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Intelligently generate SQL using LLM with dynamic schema discovery and data analysis"""
        
        # If no LLM client available, use simple fallback
        if not self.openai_client:
            return await self._simple_fallback(schema_info)
        
        try:
            # Step 1: Build comprehensive schema context with actual column names
            schema_context = self._build_schema_context(schema_info)
            
            # Step 2: Create a context-aware prompt
            household_context = ""
            if context and context.get('household_id') and context['household_id'] != 'general':
                household_id = context['household_id']
                household_context = f"""

IMPORTANT CONTEXT - HOUSEHOLD FILTER REQUIRED:
This query is for a SPECIFIC household only (identifier: "{household_id}").

HOUSEHOLD FILTERING RULES:
- If the household identifier is numeric (like "1", "2"), filter by: WHERE h.[HouseholdID] = {household_id}
- If the household identifier contains text/dashes (like "wilson-retirement", "multigenerational-wealth"), 
  you need to find the matching household by name pattern.
  
IMPORTANT: The identifier "{household_id}" is likely a URL slug that may not match the actual household name.

SPECIAL MAPPING RULES for common slugs:
- "multigenerational-wealth" maps to household name containing "Anderson" or "Legacy" 
- "wilson-retirement" maps to household name containing "Wilson"
- "johnson-family" maps to household name containing "Johnson"

BEST APPROACH: Use HouseholdCode field for exact matching:
   WHERE h.[HouseholdCode] = '{household_id}'

If no results, try fallback patterns:
   WHERE LOWER(h.[HouseholdCode]) = LOWER('{household_id}')
   OR LOWER(h.[Name]) LIKE '%anderson%' (for multigenerational-wealth)
   OR LOWER(h.[Name]) LIKE '%wilson%' (for wilson-retirement)
   OR LOWER(h.[Name]) LIKE '%johnson%' (for johnson-family)

For "{household_id}": Start with WHERE h.[HouseholdCode] = '{household_id}'

EXAMPLES:
- For "wilson-retirement": WHERE LOWER(h.[Name]) LIKE '%wilson%' OR LOWER(h.[Name]) LIKE '%retirement%'
- For "multigenerational-wealth": WHERE LOWER(h.[Name]) LIKE '%multigenerational%' OR LOWER(h.[Name]) LIKE '%wealth%'
- For numeric "1": WHERE h.[HouseholdID] = 1

If no matches are found, the query should still filter properly but may return 0 results, which is correct.
DO NOT return data for all households - MUST include the household filter even if it returns no results.
"""
            else:
                household_context = """

CONTEXT: This is a GLOBAL query across ALL households. Include data from all households unless specifically asked to filter or rank by household."""

            # Build additional context information
            additional_context = ""
            if context:
                context_items = []
                if context.get('limit'):
                    context_items.append(f"- Limit results to {context['limit']} rows")
                if context.get('days'):
                    context_items.append(f"- Consider timeframe of {context['days']} days")
                if context.get('account_id'):
                    context_items.append(f"- Focus on account ID: {context['account_id']}")
                
                if context_items:
                    additional_context = f"""

ADDITIONAL CONTEXT FROM USER REQUEST:
{chr(10).join(context_items)}
"""

            prompt = f"""You are an expert SQL Server analyst. Generate a SIMPLE SQL query that returns meaningful data with proper JOINs.

USER QUESTION: {query}
{household_context}{additional_context}

{schema_context}

CRITICAL REQUIREMENTS:
1. ALWAYS JOIN to get names instead of returning just ID numbers
2. When you see HouseholdID, MUST JOIN to dbo.Households to get h.[Name] AS HouseholdName  
3. Use ONLY column names shown in schema (in square brackets)
4. Use proper SQL Server syntax: dbo.[TableName] and [ColumnName]
5. Use the foreign key relationships shown above to create proper JOINs
6. SIMPLE SELECT ONLY - NO CTEs, NO WITH clauses, NO subqueries
7. Use basic date filtering with DATEADD() and GETDATE() functions directly in WHERE clause
8. HOUSEHOLD FILTERING: {f'MUST include household filter as described above for "{context.get("household_id")}"' if context and context.get('household_id') and context['household_id'] != 'general' else 'Include all households unless specifically requested to filter'}
9. If limit is specified in context, use TOP clause appropriately
10. Return ONLY the SQL query without explanations or comments

Generate simple SQL query:"""

            # Call Azure OpenAI for completely dynamic SQL generation
            logger.info(f"🤖 Generating SQL using intelligent analysis of actual database schema and data")
            
            response = self.openai_client.chat.completions.create(
                model=self.settings.azure_openai_deployment,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert SQL analyst who generates queries by analyzing actual database schema and sample data. You make no assumptions about business domain - you learn everything from the provided data."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent, precise SQL
                max_tokens=800,  # Increased for complex queries
                top_p=0.95
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Clean up the response (remove any markdown formatting)
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
            
            logger.info(f"🔧 RAW LLM Response:")
            logger.info(f"📄 Original: {response.choices[0].message.content}")
            logger.info(f"🧹 Cleaned SQL: {sql_query}")
            
            # Log the actual schema that was sent to LLM for debugging
            logger.info(f"🗂️ Schema sent to LLM (first 1000 chars): {schema_context[:1000]}...")
            
            # Validate the generated SQL
            validated_sql = self._validate_sql_query(sql_query, context)
            
            return validated_sql
            
        except Exception as e:
            logger.error(f"❌ LLM SQL generation failed: {e}")
            logger.info(f"🔄 Falling back to simple query")
            return await self._simple_fallback(schema_info)
    
    def _build_schema_context(self, schema_info: Dict[str, Any]) -> str:
        """Build comprehensive schema context for LLM with actual column names"""
        tables = schema_info.get("tables", {})
        logger.info(f"🔧 Building schema context from {len(tables)} tables")
        
        schema_context = "=== DATABASE SCHEMA ===\n\n"
        
        for full_table_name, table_info in tables.items():
            schema_context += f"TABLE: {full_table_name}\n"
            schema_context += "COLUMNS (use these EXACT names with brackets):\n"
            
            # Show actual column names from MCP server schema
            columns = table_info.get("columns", [])
            actual_columns = []
            
            for col in columns:
                col_name = col.get('column_name')
                data_type = col.get('data_type') 
                is_nullable = col.get('is_nullable', False)
                actual_columns.append(col_name)
                schema_context += f"  - [{col_name}] ({data_type}) {'NULL' if is_nullable else 'NOT NULL'}\n"
            
            # Add primary keys info
            primary_keys = table_info.get("primary_keys", [])
            if primary_keys:
                schema_context += f"PRIMARY KEY: {primary_keys}\n"
            
            logger.info(f"  ✅ Table {full_table_name} columns: {actual_columns}")
            schema_context += "\n"
        
        # Add relationship information with JOIN examples
        relationships = schema_info.get("relationships", [])
        if relationships:
            schema_context += "FOREIGN KEY RELATIONSHIPS (ALWAYS JOIN TO GET MEANINGFUL DATA):\n"
            for rel in relationships:
                schema_context += f"- {rel['from_table']}.[{rel['from_column']}] -> {rel['to_table']}.[{rel['to_column']}]\n"
            schema_context += "\n"
            
            # Add explicit JOIN examples for common patterns
            schema_context += "REQUIRED JOIN PATTERNS FOR MEANINGFUL RESULTS:\n"
            for rel in relationships:
                if 'household' in rel['to_table'].lower():
                    from_table_short = rel['from_table'].split('.')[-1]
                    from_alias = from_table_short[0].lower()
                    schema_context += f"  -- To get household names: JOIN {rel['to_table']} h ON {from_alias}.[{rel['from_column']}] = h.[{rel['to_column']}]\n"
                    schema_context += f"  -- Then SELECT h.[Name] AS HouseholdName instead of just {from_alias}.[{rel['from_column']}]\n"
            schema_context += "\n"
        
        schema_context += """
CRITICAL INSTRUCTIONS:
- ALWAYS include meaningful names by JOINing to related tables when you see ID columns
- Use ONLY the column names shown above in square brackets []
- Do NOT return just IDs - JOIN to get names and descriptions  
- For HouseholdID columns: ALWAYS JOIN to dbo.Households to get h.[Name] AS HouseholdName
- Use proper table aliases (h for Households, a for Accounts, p for PerformanceData)
- Example: SELECT h.[Name] AS HouseholdName, SUM(p.[TotalReturn]) FROM dbo.PerformanceData p JOIN dbo.Households h ON p.[HouseholdID] = h.[HouseholdID]

"""
        
        logger.info(f"�️ Schema context built ({len(schema_context)} chars)")
        logger.info(f"� EXACT SCHEMA BEING SENT TO LLM:\n{schema_context}")
        
        return schema_context
       
    async def _simple_fallback(self, schema_info: Dict[str, Any]) -> str:
        """Simple fallback - just return data from first available table"""
        try:
            tables = schema_info.get("tables", {})
            if tables:
                first_table = list(tables.keys())[0]
                return f"SELECT TOP 10 * FROM {first_table}"
            return "SELECT 1"
        except Exception as e:
            logger.error(f"❌ Simple fallback failed: {e}")
            return "SELECT 1"
           
    def _validate_sql_query(self, sql: str, context: Dict[str, Any] = None) -> str:
        """Validate and secure SQL query."""
        sql_upper = sql.upper().strip()
        
        # Security checks
        forbidden_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'CREATE', 'ALTER', 'TRUNCATE', 'EXEC']
        for keyword in forbidden_keywords:
            if keyword in sql_upper:
                raise ValueError(f"Forbidden SQL keyword: {keyword}")
        
        # Add TOP clause if not present
        if not 'TOP ' in sql_upper and 'SELECT' in sql_upper:
            sql = sql.replace('SELECT', 'SELECT TOP 100', 1)
        
        # Add household/account filters if context provided
        if context:
            household_id = context.get('household_id')
            if household_id and 'household_id' in sql.lower():
                # Add WHERE clause for household filtering
                if 'WHERE' not in sql_upper:
                    sql += f" WHERE h.household_id = '{household_id}'"
                else:
                    sql += f" AND h.household_id = '{household_id}'"
        
        return sql
    
class NL2SQLAgentService:
    """Simplified NL2SQL Agent Service - handles any natural language query dynamically."""
    
    def __init__(self):
        logger.info("🔧 Initializing NL2SQL Agent Service...")
        self.settings = get_settings()
        logger.info(f"✅ Settings loaded: SQL connection string present = {bool(self.settings.azure_sql_connection_string)}")
        
        logger.info("🔧 Creating NL2SQL Agent...")
        self.nl2sql_agent = NL2SQLAgent(self.settings.azure_sql_connection_string)
        logger.info("✅ NL2SQL Agent created")
        
        logger.info("🔧 Creating message broker...")
        self.broker = create_broker("nl2sql-agent")
        logger.info(f"✅ Message broker created: {type(self.broker).__name__}")
        
        # Register single generic handler for any NL query
        logger.info("🔧 Registering generic query handler...")
        self.broker.register_handler("NLQuery", self.handle_natural_language_query)
    
    async def handle_natural_language_query(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle any natural language query - let the LLM understand and generate appropriate SQL."""
        try:
            # Get the original user query - no modifications needed!
            query = message.payload.get('query', '')
            if not query:
                return {
                    'success': False,
                    'error': 'No query provided'
                }
            
            # Extract context from message
            context = message.context.model_dump() if message.context else {}
            
            # Add any additional parameters from payload to context
            for key in ['limit', 'days', 'account_id', 'schema_hint']:
                if key in message.payload:
                    context[key] = message.payload[key]
            
            logger.info(f"🔍 Processing natural language query: '{query}'")
            logger.info(f"📋 Context: {context}")
            
            # Let the LLM do its magic!
            result = await self.nl2sql_agent.translate_nl_to_sql(query, context)
            
            # Dynamically determine tables used from the actual SQL generated
            tables_used = self._extract_tables_from_sql(result.get('sql_query', ''))
            
            return {
                'sql_query': result.get('sql_query', ''),
                'results': result.get('results', []),
                'tables_used': tables_used,
                'row_count': result.get('row_count', 0),
                'execution_time_ms': result.get('execution_time_ms', 0),
                'success': result.get('success', False),
                'error': result.get('error'),
                'message': result.get('message', ''),
                'query_type': 'dynamic'  # Indicate this was dynamically processed
            }
            
        except Exception as e:
            logger.error(f"Natural language query processing failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_tables_from_sql(self, sql_query: str) -> List[str]:
        """Extract table names from the generated SQL query."""
        if not sql_query:
            return []
        
        tables_used = []
        sql_upper = sql_query.upper()
        
        # Common table names in your system
        table_names = [
            'HOUSEHOLDS', 'ACCOUNTS', 'POSITIONS', 'ALLOCTARGETS', 
            'BENEFICIARIES', 'CONTRIBUTIONS', 'PERFORMANCE', 'PERSONS',
            'PERFORMANCEDATA', 'ALLOCATIONS'
        ]
        
        for table in table_names:
            if table in sql_upper or f'DBO.{table}' in sql_upper:
                tables_used.append(table.lower().capitalize())
        
        return list(set(tables_used))  # Remove duplicates
    
    async def process_direct_query(self, request: NL2SQLRequest) -> NL2SQLResponse:
        """Process direct NL2SQL request (HTTP API) - simplified version."""
        try:
            # Build context from request
            context = {}
            if request.household_id:
                context['household_id'] = request.household_id
            if request.account_id:
                context['account_id'] = request.account_id
            if request.schema_hint:
                context['schema_hint'] = request.schema_hint
            
            logger.info(f"🔍 Direct API query: '{request.query}'")
            logger.info(f"📋 Context: {context}")
            
            # Let the LLM handle any query
            result = await self.nl2sql_agent.translate_nl_to_sql(request.query, context)
            
            if not result.get('success'):
                raise HTTPException(
                    status_code=400,
                    detail=f"Query processing failed: {result.get('error', 'Unknown error')}"
                )
            
            # Use the same table extraction logic
            tables_used = self._extract_tables_from_sql(result.get('sql_query', ''))
            
            return NL2SQLResponse(
                sql_query=result.get('sql_query', ''),
                results=result.get('results', []),
                tables_used=tables_used,
                row_count=result.get('row_count', 0),
                execution_time_ms=result.get('execution_time_ms', 0)
            )
            
        except Exception as e:
            logger.error(f"Direct query failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


# Global agent instance
agent: Optional[NL2SQLAgentService] = None

async def _start_broker_with_error_handling(broker):
    """Start broker with proper error handling."""
    try:
        logger.info("🚀 ATTEMPTING TO START MESSAGE BROKER...")
        await broker.start_listening()
    except Exception as e:
        logger.error(f"❌ BROKER STARTUP FAILED: {e}")
        import traceback
        logger.error(f"❌ FULL TRACEBACK: {traceback.format_exc()}")
        raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    global agent
    
    # Startup
    logger.info("🎯 Starting NL2SQL Agent with MCP Server")
    try:
        agent = NL2SQLAgentService()
        logger.info("✅ NL2SQL Agent Service created successfully")
        
        # Start message broker in background with error handling
        logger.info("🎧 Starting message broker...")
        broker_task = asyncio.create_task(_start_broker_with_error_handling(agent.broker))
        logger.info("✅ Broker task created")
        
    except Exception as e:
        logger.error(f"❌ AGENT STARTUP FAILED: {e}")
        import traceback
        logger.error(f"❌ FULL TRACEBACK: {traceback.format_exc()}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down NL2SQL Agent...")
    if agent:
        try:
            await agent.broker.close()
            logger.info("✅ Broker closed successfully")
        except Exception as e:
            logger.error(f"❌ Error closing broker: {e}")
    logger.info("🏁 NL2SQL Agent stopped")

# FastAPI application
app = FastAPI(
    title="NL2SQL Agent",
    description="Natural Language to SQL Agent using MCP Server",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "agent": "nl2sql"}

@app.post("/query", response_model=NL2SQLResponse)
async def process_query(request: NL2SQLRequest):
    """Process any natural language query directly - no intent classification needed!"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return await agent.process_direct_query(request)

@app.post("/ask")
async def ask_anything(request: Dict[str, Any]):
    """
    Ask any question about the database in natural language.
    Simple endpoint that accepts: {"query": "your question", "household_id": "optional"}
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    query = request.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    # Build NL2SQLRequest from simple input
    nl_request = NL2SQLRequest(
        query=query,
        household_id=request.get("household_id"),
        account_id=request.get("account_id"),
        schema_hint=request.get("schema_hint")
    )
    
    return await agent.process_direct_query(nl_request)

@app.get("/schema")
async def get_schema():
    """Get database schema information."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        schema_info = await agent.nl2sql_agent.get_schema_info()
        return {"schema": schema_info}
    except Exception as e:
        logger.error(f"Schema retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools")
async def list_mcp_tools():
    """List available MCP tools."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        tools = await agent.nl2sql_agent.mcp_server.list_tools()
        return {"tools": tools}
    except Exception as e:
        logger.error(f"Tools listing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/{tool_name}")
async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]):
    """Call a specific MCP tool directly."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        result = await agent.nl2sql_agent.mcp_server.call_tool(tool_name, arguments)
        return result
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)