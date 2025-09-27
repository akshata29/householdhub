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
import pyodbc
from contextlib import asynccontextmanager

from common.schemas import (
    A2AMessage, NL2SQLRequest, NL2SQLResponse, 
    AgentType, MessageStatus
)
from common.config import get_settings, get_cors_origins
from common.auth import get_sql_access_token
from a2a.broker import create_broker

logger = logging.getLogger(__name__)


class MCPSQLClient:
    """Client for MSSQL MCP Server."""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.schema_cache = {}
        
    async def get_connection(self) -> pyodbc.Connection:
        """Get database connection with Managed Identity."""
        try:
            # For Managed Identity, we need to get an access token
            access_token = get_sql_access_token()
            if access_token:
                # Use token-based authentication
                conn_str = self.connection_string.replace(
                    "Authentication=Active Directory Managed Identity",
                    f"AccessToken={access_token}"
                )
            else:
                conn_str = self.connection_string
                
            return pyodbc.connect(
                conn_str,
                timeout=30,
                autocommit=True
            )
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def get_schema_info(self) -> Dict[str, Any]:
        """Get database schema information."""
        if self.schema_cache:
            return self.schema_cache
            
        try:
            conn = await self.get_connection()
            cursor = conn.cursor()
            
            # Get table information
            tables_query = """
            SELECT 
                t.TABLE_SCHEMA,
                t.TABLE_NAME,
                c.COLUMN_NAME,
                c.DATA_TYPE,
                c.IS_NULLABLE,
                c.COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.TABLES t
            JOIN INFORMATION_SCHEMA.COLUMNS c ON t.TABLE_NAME = c.TABLE_NAME 
                AND t.TABLE_SCHEMA = c.TABLE_SCHEMA
            WHERE t.TABLE_TYPE = 'BASE TABLE'
                AND t.TABLE_SCHEMA NOT IN ('sys', 'INFORMATION_SCHEMA')
            ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME, c.ORDINAL_POSITION
            """
            
            cursor.execute(tables_query)
            rows = cursor.fetchall()
            
            schema_info = {}
            for row in rows:
                schema_name = row[0]
                table_name = row[1]
                column_name = row[2]
                data_type = row[3]
                is_nullable = row[4]
                
                if schema_name not in schema_info:
                    schema_info[schema_name] = {}
                
                if table_name not in schema_info[schema_name]:
                    schema_info[schema_name][table_name] = []
                
                schema_info[schema_name][table_name].append({
                    'column': column_name,
                    'type': data_type,
                    'nullable': is_nullable == 'YES'
                })
            
            # Get foreign key relationships
            fk_query = """
            SELECT 
                fk.TABLE_SCHEMA,
                fk.TABLE_NAME,
                fk.COLUMN_NAME,
                pk.TABLE_SCHEMA AS REF_SCHEMA,
                pk.TABLE_NAME AS REF_TABLE,
                pk.COLUMN_NAME AS REF_COLUMN
            FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
            JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE fk ON rc.CONSTRAINT_NAME = fk.CONSTRAINT_NAME
            JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE pk ON rc.UNIQUE_CONSTRAINT_NAME = pk.CONSTRAINT_NAME
            """
            
            cursor.execute(fk_query)
            fk_rows = cursor.fetchall()
            
            relationships = []
            for row in fk_rows:
                relationships.append({
                    'from_table': f"{row[0]}.{row[1]}",
                    'from_column': row[2],
                    'to_table': f"{row[3]}.{row[4]}",
                    'to_column': row[5]
                })
            
            self.schema_cache = {
                'tables': schema_info,
                'relationships': relationships
            }
            
            conn.close()
            return self.schema_cache
            
        except Exception as e:
            logger.error(f"Failed to get schema info: {e}")
            raise
    
    async def translate_nl_to_sql(self, query: str, context: Dict[str, Any] = None) -> str:
        """Translate natural language to SQL using schema context."""
        schema_info = await self.get_schema_info()
        
        # Simple NL to SQL translation logic
        # In a real implementation, this would use the MCP server with an LLM
        sql_query = await self._generate_sql_from_nl(query, schema_info, context)
        
        # Validate and secure the query
        validated_sql = self._validate_sql_query(sql_query, context)
        
        return validated_sql
    
    async def _generate_sql_from_nl(self, query: str, schema_info: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Generate SQL from natural language query."""
        query_lower = query.lower()
        
        # Pattern matching for common queries
        if "top cash" in query_lower or "highest cash" in query_lower:
            return """
            SELECT TOP 10 
                h.name as household_name,
                h.household_id,
                SUM(a.cash) as total_cash
            FROM dbo.Households h
            JOIN dbo.Accounts a ON h.household_id = a.household_id
            GROUP BY h.household_id, h.name
            ORDER BY total_cash DESC
            """
        
        elif "allocation" in query_lower and "mismatch" in query_lower:
            return """
            SELECT 
                h.name as household_name,
                at.asset_class,
                at.target_pct,
                ISNULL(current_pct, 0) as current_pct,
                ISNULL(current_pct, 0) - at.target_pct as drift
            FROM dbo.Households h
            JOIN dbo.AllocTargets at ON h.household_id = at.household_id
            LEFT JOIN (
                SELECT 
                    p.account_id,
                    a.household_id,
                    p.asset_class,
                    SUM(p.mv) * 100.0 / SUM(SUM(p.mv)) OVER (PARTITION BY a.household_id) as current_pct
                FROM dbo.Positions p
                JOIN dbo.Accounts a ON p.account_id = a.account_id
                GROUP BY p.account_id, a.household_id, p.asset_class
            ) current ON at.household_id = current.household_id AND at.asset_class = current.asset_class
            WHERE ABS(ISNULL(current_pct, 0) - at.target_pct) > 5
            ORDER BY ABS(ISNULL(current_pct, 0) - at.target_pct) DESC
            """
        
        elif "beneficiary" in query_lower and "missing" in query_lower:
            return """
            SELECT 
                h.name as household_name,
                a.account_id,
                a.name as account_name,
                a.type as account_type
            FROM dbo.Households h
            JOIN dbo.Accounts a ON h.household_id = a.household_id
            LEFT JOIN dbo.Beneficiaries b ON a.account_id = b.account_id
            WHERE b.account_id IS NULL
                AND a.type IN ('401k', 'IRA', 'Roth IRA')
            ORDER BY h.name, a.name
            """
        
        elif "rmd" in query_lower or "required minimum distribution" in query_lower:
            return """
            SELECT 
                h.name as household_name,
                p.name as person_name,
                a.account_id,
                a.name as account_name,
                a.mv as current_value,
                DATEDIFF(day, GETDATE(), DATEADD(year, 1, DATEADD(year, 73 - YEAR(GETDATE() - p.dob), p.dob))) as days_to_rmd
            FROM dbo.Households h
            JOIN dbo.Persons p ON h.household_id = p.household_id
            JOIN dbo.Accounts a ON h.household_id = a.household_id
            WHERE a.type IN ('401k', 'Traditional IRA')
                AND DATEDIFF(year, p.dob, GETDATE()) >= 72
                AND DATEDIFF(day, GETDATE(), DATEADD(year, 1, DATEADD(year, 73 - YEAR(GETDATE() - p.dob), p.dob))) <= 90
            ORDER BY days_to_rmd
            """
        
        elif "ira contribution" in query_lower and "ytd" in query_lower:
            return """
            SELECT 
                h.name as household_name,
                a.account_id,
                a.name as account_name,
                c.ytd_contribution,
                c.limit as annual_limit,
                c.limit - c.ytd_contribution as remaining_capacity
            FROM dbo.Households h
            JOIN dbo.Accounts a ON h.household_id = a.household_id
            JOIN dbo.Contributions c ON a.account_id = c.account_id
            WHERE a.type LIKE '%IRA%'
                AND c.year = YEAR(GETDATE())
                AND c.ytd_contribution = 0
            ORDER BY h.name, a.name
            """
        
        else:
            # Default fallback for general queries
            return f"""
            -- Generated SQL for: {query}
            SELECT 'No specific pattern matched for this query' as message
            """
    
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
    
    async def execute_sql(self, sql: str) -> List[Dict[str, Any]]:
        """Execute SQL query safely."""
        try:
            conn = await self.get_connection()
            cursor = conn.cursor()
            
            start_time = time.time()
            cursor.execute(sql)
            results = cursor.fetchall()
            execution_time = int((time.time() - start_time) * 1000)
            
            # Convert results to list of dictionaries
            columns = [desc[0] for desc in cursor.description]
            rows = []
            for row in results:
                row_dict = {}
                for i, value in enumerate(row):
                    # Handle different data types
                    if hasattr(value, 'isoformat'):  # datetime objects
                        row_dict[columns[i]] = value.isoformat()
                    else:
                        row_dict[columns[i]] = value
                rows.append(row_dict)
            
            conn.close()
            
            return {
                'results': rows,
                'row_count': len(rows),
                'execution_time_ms': execution_time,
                'columns': columns
            }
            
        except Exception as e:
            logger.error(f"SQL execution failed: {e}")
            raise


class NL2SQLAgent:
    """NL2SQL Agent service."""
    
    def __init__(self):
        self.settings = get_settings()
        self.mcp_client = MCPSQLClient(self.settings.azure_sql_connection_string)
        self.broker = create_broker("nl2sql-agent")
        
        # Register message handlers
        self.broker.register_handler("TopCash", self.handle_top_cash)
        self.broker.register_handler("Recon", self.handle_recon)
        self.broker.register_handler("MissingBen", self.handle_missing_beneficiaries)
        self.broker.register_handler("RMD", self.handle_rmd)
        self.broker.register_handler("IRAReminder", self.handle_ira_reminder)
    
    async def handle_top_cash(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle top cash balance queries."""
        try:
            limit = message.payload.get('limit', 10)
            sql = await self.mcp_client.translate_nl_to_sql(
                f"top {limit} cash balances by household",
                message.context.model_dump()
            )
            
            result = await self.mcp_client.execute_sql(sql)
            
            return {
                'sql_query': sql,
                'results': result['results'],
                'tables_used': ['Households', 'Accounts'],
                'row_count': result['row_count'],
                'execution_time_ms': result['execution_time_ms']
            }
            
        except Exception as e:
            logger.error(f"Top cash query failed: {e}")
            raise
    
    async def handle_recon(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle allocation reconciliation queries."""
        try:
            sql = await self.mcp_client.translate_nl_to_sql(
                "allocation mismatch analysis",
                message.context.model_dump()
            )
            
            result = await self.mcp_client.execute_sql(sql)
            
            return {
                'sql_query': sql,
                'results': result['results'],
                'tables_used': ['Households', 'AllocTargets', 'Positions', 'Accounts'],
                'row_count': result['row_count'],
                'execution_time_ms': result['execution_time_ms']
            }
            
        except Exception as e:
            logger.error(f"Recon query failed: {e}")
            raise
    
    async def handle_missing_beneficiaries(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle missing beneficiary queries."""
        try:
            sql = await self.mcp_client.translate_nl_to_sql(
                "missing beneficiary information",
                message.context.model_dump()
            )
            
            result = await self.mcp_client.execute_sql(sql)
            
            return {
                'sql_query': sql,
                'results': result['results'],
                'tables_used': ['Households', 'Accounts', 'Beneficiaries'],
                'row_count': result['row_count'],
                'execution_time_ms': result['execution_time_ms']
            }
            
        except Exception as e:
            logger.error(f"Missing beneficiaries query failed: {e}")
            raise
    
    async def handle_rmd(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle RMD deadline queries."""
        try:
            days = message.payload.get('days', 90)
            sql = await self.mcp_client.translate_nl_to_sql(
                f"upcoming RMD deadlines within {days} days",
                message.context.model_dump()
            )
            
            result = await self.mcp_client.execute_sql(sql)
            
            return {
                'sql_query': sql,
                'results': result['results'],
                'tables_used': ['Households', 'Persons', 'Accounts'],
                'row_count': result['row_count'],
                'execution_time_ms': result['execution_time_ms']
            }
            
        except Exception as e:
            logger.error(f"RMD query failed: {e}")
            raise
    
    async def handle_ira_reminder(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle IRA contribution reminder queries."""
        try:
            sql = await self.mcp_client.translate_nl_to_sql(
                "IRA contributions YTD zero",
                message.context.model_dump()
            )
            
            result = await self.mcp_client.execute_sql(sql)
            
            return {
                'sql_query': sql,
                'results': result['results'],
                'tables_used': ['Households', 'Accounts', 'Contributions'],
                'row_count': result['row_count'],
                'execution_time_ms': result['execution_time_ms']
            }
            
        except Exception as e:
            logger.error(f"IRA reminder query failed: {e}")
            raise
    
    async def process_direct_query(self, request: NL2SQLRequest) -> NL2SQLResponse:
        """Process direct NL2SQL request (HTTP API)."""
        try:
            context = {
                'household_id': request.household_id,
                'account_id': request.account_id
            }
            
            sql = await self.mcp_client.translate_nl_to_sql(
                request.query, 
                context
            )
            
            result = await self.mcp_client.execute_sql(sql)
            
            # Extract table names from SQL
            tables_used = []
            sql_upper = sql.upper()
            table_names = ['HOUSEHOLDS', 'ACCOUNTS', 'POSITIONS', 'ALLOCTARGETS', 'BENEFICIARIES', 'CONTRIBUTIONS', 'PERFORMANCE', 'PERSONS']
            for table in table_names:
                if table in sql_upper:
                    tables_used.append(table.lower().capitalize())
            
            return NL2SQLResponse(
                sql_query=sql,
                results=result['results'],
                tables_used=tables_used,
                row_count=result['row_count'],
                execution_time_ms=result['execution_time_ms']
            )
            
        except Exception as e:
            logger.error(f"Direct query failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


# Global agent instance
agent: Optional[NL2SQLAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    global agent
    
    # Startup
    logger.info("Starting NL2SQL Agent")
    agent = NL2SQLAgent()
    
    # Start message broker in background
    asyncio.create_task(agent.broker.start_listening())
    
    yield
    
    # Shutdown
    if agent:
        await agent.broker.close()
    logger.info("NL2SQL Agent stopped")


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
    """Process NL2SQL query directly."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return await agent.process_direct_query(request)


@app.get("/schema")
async def get_schema():
    """Get database schema information."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return await agent.mcp_client.get_schema_info()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)