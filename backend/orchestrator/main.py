"""
Orchestrator Agent using Semantic Kernel for multi-agent coordination
"""

import asyncio
import logging
import json
import time
import httpx
from typing import Dict, List, Any, Optional, AsyncGenerator, Callable
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import uuid

# Semantic Kernel imports
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.kernel import Kernel
from semantic_kernel.functions import kernel_function
from semantic_kernel.prompt_template import PromptTemplateConfig, InputVariable
from semantic_kernel.functions import KernelArguments

from common.schemas import (
    A2AMessage, A2AResponse, QueryRequest, QueryResponse, 
    StreamingUpdate, Citation, AgentType, IntentType, 
    A2AContext, MessageStatus
)
from common.config import get_settings, get_cors_origins
from common.auth import get_credential, get_openai_access_token
from a2a.broker import create_broker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QueryRouter:
    """Intelligent router that uses LLM to determine which agents to use based on query analysis."""
    
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        
        # Agent routing template
        self.routing_template = """You are an intelligent agent router for a financial advisory system. Analyze the user's query and determine which data sources/agents are needed to provide a complete answer.

Available Agents:
1. NL2SQL Agent: Accesses structured database data including:
   - Household financial data (assets, liabilities, net worth)
   - Account information (balances, types, allocations)
   - Transaction history
   - Portfolio performance metrics
   - Asset allocation data
   - Investment holdings

2. Vector Agent: Accesses unstructured CRM data including:
   - Client meeting notes and communications
   - Advisor observations and insights
   - Client preferences and goals
   - Relationship management notes
   - Executive summaries from past interactions
   - Action items and follow-ups
   - Client feedback and concerns

3. API Agent: Accesses external market data including:
   - Real-time portfolio performance
   - Market benchmarks and comparisons
   - Asset allocation analysis
   - Rebalancing recommendations

User Query: {{$query}}

Analyze this query and determine which agents are needed. Consider:
- Does it need structured financial data from the database? (NL2SQL)
- Does it need client notes, communications, or relationship insights? (Vector)
- Does it need external market data or performance analysis? (API)

Respond with a JSON object containing:
{
  "agents_needed": ["NL2SQL", "VECTOR", "API"],
  "reasoning": "Brief explanation of why each agent is needed",
  "primary_agent": "The most important agent for this query"
}

Only include agents that are actually needed. Be precise and avoid unnecessary agents."""
        
    async def get_required_agents(self, query: str) -> List[AgentType]:
        """Determine which agents are needed using LLM analysis."""
        try:
            logger.info(f"🤖 Analyzing query for agent routing: '{query}'")
            
            # Create routing function
            from semantic_kernel.prompt_template import PromptTemplateConfig, InputVariable
            
            input_variables = [
                InputVariable(name="query", description="User's query to analyze")
            ]
            
            prompt_config = PromptTemplateConfig(
                template=self.routing_template,
                input_variables=input_variables
            )
            
            logger.info(f"📝 Creating routing function...")
            routing_function = self.kernel.add_function(
                function_name="route_query",
                plugin_name="QueryRouter",
                prompt_template_config=prompt_config
            )
            logger.info(f"✅ Routing function created successfully")
            
            # Execute routing analysis
            from semantic_kernel.functions import KernelArguments
            kernel_args = KernelArguments(query=query)
            
            logger.info(f"🚀 Calling LLM for agent routing with query: '{query[:100]}...'")
            result = await self.kernel.invoke(routing_function, kernel_args)
            routing_response = str(result).strip()
            
            logger.info(f"🧠 LLM Routing Analysis (length: {len(routing_response)}): {routing_response}")
            
            if not routing_response:
                logger.error(f"❌ Empty response from LLM routing")
                return self._fallback_keyword_routing(query)
            
            # Parse the JSON response - handle markdown code blocks
            import json
            try:
                # Clean the response - remove markdown code blocks if present
                cleaned_response = routing_response.strip()
                
                # Remove ```json and ``` if present
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:]  # Remove ```json
                elif cleaned_response.startswith("```"):
                    cleaned_response = cleaned_response[3:]   # Remove ```
                
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3]  # Remove trailing ```
                
                cleaned_response = cleaned_response.strip()
                
                logger.info(f"🧹 Cleaned JSON: {cleaned_response[:200]}...")
                
                routing_data = json.loads(cleaned_response)
                agents_needed = routing_data.get("agents_needed", [])
                reasoning = routing_data.get("reasoning", "")
                primary_agent = routing_data.get("primary_agent", "")
                
                logger.info(f"📋 Agents needed: {agents_needed}")
                logger.info(f"💭 Reasoning: {reasoning}")
                logger.info(f"🎯 Primary agent: {primary_agent}")
                
                # Convert to AgentType enums
                agent_mapping = {
                    "NL2SQL": AgentType.NL2SQL,
                    "VECTOR": AgentType.VECTOR,
                    "API": AgentType.API
                }
                
                required_agents = []
                for agent_name in agents_needed:
                    if agent_name in agent_mapping:
                        required_agents.append(agent_mapping[agent_name])
                
                if not required_agents:
                    # Fallback to NL2SQL if no agents detected
                    logger.warning("⚠️ No agents detected, falling back to NL2SQL")
                    required_agents = [AgentType.NL2SQL]
                
                logger.info(f"✅ Final agent list: {[agent.value for agent in required_agents]}")
                return required_agents
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse routing JSON: {e}")
                logger.error(f"Raw response: {routing_response}")
                
                # Fallback: Use keyword-based routing
                return self._fallback_keyword_routing(query)
                
        except Exception as e:
            logger.error(f"❌ Agent routing failed: {e}")
            logger.error(f"❌ Exception type: {type(e)}")
            logger.error(f"❌ Query was: '{query}'")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            # Fallback: Use keyword-based routing
            return self._fallback_keyword_routing(query)
    
    def _fallback_keyword_routing(self, query: str) -> List[AgentType]:
        """Fallback keyword-based routing when LLM routing fails."""
        logger.info(f"🔄 Using fallback keyword routing")
        query_lower = query.lower()
        
        agents = []
        
        # Check for CRM/Vector keywords
        crm_keywords = [
            "notes", "crm", "conversation", "meeting", "discussion", "client notes",
            "communications", "activities", "insights", "action items", "opportunities",
            "executive summary", "client relationship", "interactions", "conversations",
            "communications history", "relationship management", "client feedback",
            "meeting notes", "call notes", "follow up", "follow-up"
        ]
        
        # Check for API keywords
        api_keywords = ["performance", "returns", "allocation", "drift", "rebalance"]
        
        # Add Vector agent for CRM queries
        if any(keyword in query_lower for keyword in crm_keywords):
            agents.append(AgentType.VECTOR)
        
        # Add API agent for performance queries
        if any(keyword in query_lower for keyword in api_keywords):
            agents.append(AgentType.API)
        
        # Add NL2SQL for financial data queries (or as default)
        if not agents or any(keyword in query_lower for keyword in ["household", "account", "balance", "asset", "portfolio", "total"]):
            agents.append(AgentType.NL2SQL)
        
        logger.info(f"🔄 Fallback routing result: {[agent.value for agent in agents]}")
        return agents

class ResponseComposer:
    """Composes final responses from agent results using Semantic Kernel."""
    
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        
        # Enhanced template that can handle financial queries with CRM context
        self.template = """You are a financial advisor AI assistant. Answer the user's question based on the provided data.

User Question: {{$query}}

SQL Query Results: {{$sql_results}}

SQL Query Used: {{$sql_query}}

CRM Notes and Communications: {{$search_results}}

CRM Points of Interest: {{$crm_results}}

Performance Data: {{$api_results}}

CRITICAL INSTRUCTIONS:
1. You MUST use ONLY the exact data provided above in the results sections. 
2. Do NOT create, invent, or hallucinate any fake data, names, or numbers.
3. Use the exact household names, account names, amounts, and CRM notes from the provided data.
4. Answer the user's specific question directly using the real data provided.
5. If SQL results show household names like "Singh Global Family Office" with amounts like "37000000.00", use those exact names and amounts.
6. If CRM notes are provided in the "CRM Notes and Communications" section, incorporate relevant insights, conversations, and client communications into your response.
7. For executive summary requests, structure your response with clear sections: Overview, Key Insights, Action Items, and Opportunities.
8. Do NOT use generic names like "Household A" or fake amounts.
9. Format your response professionally and include proper citations.
10. When CRM context is available, prioritize client communication insights and relationship management aspects.
11. If a data section is empty or contains "[]" or null, simply ignore that section and focus on the available data.

Answer the question now using the exact data provided above."""
        
    async def compose_response(
        self,
        query: str,
        agent_results: Dict[AgentType, Dict[str, Any]]
    ) -> QueryResponse:
        """Compose final response using Semantic Kernel."""
        
        try:
            start_time = time.time()
            
            logger.info(f"🤖 Response Composition Starting")
            logger.info(f"📝 Original Query: '{query}'")
            logger.info(f"🔧 Agent Results Summary:")
            for agent_type, results in agent_results.items():
                logger.info(f"   - {agent_type}: success={results.get('success')}, data_rows={len(results.get('data', []))}")
            
            # Use single intelligent template for all queries
            template_text = self.template
            logger.info(f"📋 Using universal intelligent template")
            
            # Prepare context variables
            context = self._prepare_context(query, agent_results)
            logger.info(f"📊 LLM Context Variables:")
            for key, value in context.items():
                logger.info(f"   - {key}: {str(value)[:200]}{'...' if len(str(value)) > 200 else ''}")
            
            # Create semantic function with explicit variable definitions
            input_variables = [
                InputVariable(name="query", description="User's question"),
                InputVariable(name="sql_results", description="SQL query results data"),
                InputVariable(name="sql_query", description="SQL query used"),
                InputVariable(name="search_results", description="CRM search results", is_required=False),
                InputVariable(name="crm_results", description="CRM points of interest", is_required=False),
                InputVariable(name="api_results", description="External API results", is_required=False)
            ]
            
            prompt_config = PromptTemplateConfig(
                template=template_text,
                input_variables=input_variables
            )
            
            compose_function = self.kernel.add_function(
                function_name="compose_response",
                plugin_name="ResponseComposer",
                prompt_template_config=prompt_config
            )
            
            # Execute function with context using proper KernelArguments
            logger.info(f"🚀 Sending to LLM for response generation...")
            logger.info(f"📋 Context keys being passed to kernel: {list(context.keys())}")
            logger.info(f"🔍 Template content: {template_text[:200]}...")
            
            # Debug: Print each context variable
            for key, value in context.items():
                logger.info(f"   🔑 {key}: {str(value)[:100]}...")
            
            # Use KernelArguments as per Semantic Kernel documentation
            kernel_args = KernelArguments(**context)
            logger.info(f"✅ Created KernelArguments with keys: {list(kernel_args.keys()) if hasattr(kernel_args, 'keys') else 'N/A'}")
            
            try:
                result = await self.kernel.invoke(compose_function, kernel_args)
            except Exception as kernel_error:
                logger.error(f"❌ Kernel invocation failed: {kernel_error}")
                # Fallback to individual parameter passing
                logger.info(f"🔄 Trying fallback method...")
                kernel_args = KernelArguments(
                    query=context.get('query', ''),
                    sql_results=context.get('sql_results', ''),
                    sql_query=context.get('sql_query', ''),
                    search_results=context.get('search_results', ''),
                    crm_results=context.get('crm_results', ''),
                    api_results=context.get('api_results', '')
                )
                result = await self.kernel.invoke(compose_function, kernel_args)
            
            answer = str(result)
            logger.info(f"✅ LLM Response Generated (length: {len(answer)} chars)")
            
            # Extract citations
            citations = self._extract_citations(agent_results)
            
            # Get agent calls list
            agent_calls = list(agent_results.keys())
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return QueryResponse(
                answer=answer,
                citations=citations,
                sql_generated=self._extract_sql(agent_results),
                execution_time_ms=execution_time,
                agent_calls=[agent.value for agent in agent_calls]
            )
            
        except Exception as e:
            logger.error(f"Response composition failed: {e}")
            # Fallback to simple response
            return QueryResponse(
                answer=f"I apologize, but I encountered an error while processing your request: {str(e)}",
                citations=[],
                execution_time_ms=0,
                agent_calls=[]
            )
    
    def _prepare_context(self, query: str, agent_results: Dict[AgentType, Dict[str, Any]]) -> Dict[str, str]:
        """Prepare context variables for prompt template."""
        # Initialize all template variables with default values
        context = {
            'query': query, 
            'original_query': query,
            'sql_results': '[]',
            'sql_query': '',
            'search_results': '[]',
            'crm_results': '[]',
            'points_of_interest': '[]',
            'api_results': '[]',
            'performance_data': '[]',
            'intent': ''
        }
        
        logger.info(f"🔧 Preparing LLM Context from Agent Results:")
        
        for agent, results in agent_results.items():
            logger.info(f"   Processing {agent} results...")
            
            if agent == AgentType.NL2SQL:
                sql_results = results.get('results', [])
                sql_query = results.get('sql_query', '')
                intent = results.get('intent', '')
                
                logger.info(f"     📊 SQL Results: {len(sql_results)} rows")
                logger.info(f"     🔍 SQL Query: {sql_query}")
                logger.info(f"     🎯 Intent: {intent}")
                
                if len(sql_results) == 0:
                    logger.warning(f"     ⚠️  ISSUE FOUND: SQL query returned 0 rows!")
                    logger.warning(f"     🔍 This is likely why the response says 'no results'")
                
                context['sql_results'] = json.dumps(sql_results, indent=2)
                context['sql_query'] = sql_query
                context['intent'] = intent
                
                # Additional debugging for SQL results
                logger.info(f"     🔍 DETAILED SQL RESULTS DEBUG:")
                logger.info(f"     📄 SQL Results JSON: {context['sql_results'][:500]}...")
                if sql_results:
                    logger.info(f"     📊 First result sample: {sql_results[0]}")
                    logger.info(f"     📊 All results count: {len(sql_results)}")
                else:
                    logger.error(f"     ❌ SQL RESULTS ARE EMPTY OR NONE!")
                
            elif agent == AgentType.VECTOR:
                search_results = results.get('results', [])
                poi = results.get('points_of_interest', [])
                
                logger.info(f"     🔍 Search Results: {len(search_results)} items")
                logger.info(f"     📍 Points of Interest: {len(poi)} items")
                
                context['search_results'] = json.dumps(search_results, indent=2)
                context['crm_results'] = json.dumps(poi, indent=2)
                context['points_of_interest'] = json.dumps(poi, indent=2)
                
            elif agent == AgentType.API:
                logger.info(f"     🌐 API Results: {len(str(results))} chars")
                context['api_results'] = json.dumps(results, indent=2)
                context['performance_data'] = json.dumps(results, indent=2)
        
        # Combine all results for general template
        context['results'] = json.dumps(agent_results, indent=2)
        
        logger.info(f"✅ Context preparation complete - {len(context)} variables prepared")
        return context
    
    def _extract_citations(self, agent_results: Dict[AgentType, Dict[str, Any]]) -> List[Citation]:
        """Extract citations from agent results."""
        citations = []
        
        for agent, results in agent_results.items():
            if agent == AgentType.NL2SQL:
                tables = results.get('tables_used', [])
                for table in tables:
                    citations.append(Citation(
                        source=f"sql:{table.lower()}",
                        description=f"SQL query on {table} table",
                        confidence=0.9
                    ))
            
            elif agent == AgentType.VECTOR:
                search_results = results.get('results', [])
                for result in search_results[:3]:  # Top 3 results
                    citations.append(Citation(
                        source=f"search:crm-notes:{result.get('id', 'unknown')}",
                        description=f"CRM note by {result.get('metadata', {}).get('author', 'Unknown')}",
                        confidence=result.get('score', 0.5)
                    ))
            
            elif agent == AgentType.API:
                citations.append(Citation(
                    source="api:external-services",
                    description="External API data (Plan Performance, Pershing)",
                    confidence=0.8
                ))
        
        return citations
    
    def _extract_sql(self, agent_results: Dict[AgentType, Dict[str, Any]]) -> Optional[str]:
        """Extract SQL query from NL2SQL agent results."""
        nl2sql_results = agent_results.get(AgentType.NL2SQL, {})
        return nl2sql_results.get('sql_query')

class OrchestratorAgent:
    """Main orchestrator agent using Semantic Kernel."""
    
    def __init__(self):
        self.settings = get_settings()
        self.broker = create_broker("orchestrator")
        
        # Initialize Semantic Kernel
        self.kernel = self._create_kernel()
        self.router = QueryRouter(self.kernel)
        self.composer = ResponseComposer(self.kernel)
        
        # Track active queries
        self._active_queries: Dict[str, Dict[str, Any]] = {}
        
    def _create_kernel(self) -> Kernel:
        """Create and configure Semantic Kernel."""
        kernel = Kernel()
        
        # Add Azure OpenAI service
        kernel.add_service(
            AzureChatCompletion(
                deployment_name=self.settings.azure_openai_deployment,
                endpoint=self.settings.azure_openai_endpoint,
                api_version=self.settings.azure_openai_api_version,
                ad_token_provider=get_openai_access_token
            )
        )
        
        return kernel
    
    async def process_query_streaming(
        self,
        request: QueryRequest
    ) -> AsyncGenerator[str, None]:
        """Process query with streaming updates."""
        
        correlation_id = str(uuid.uuid4())
        
        try:
            # Initialize query tracking
            self._active_queries[correlation_id] = {
                'status': 'processing',
                'agent_results': {},
                'start_time': time.time()
            }
            
            # Yield initial status
            yield self._format_streaming_update(
                "status", "Processing query...", AgentType.ORCHESTRATOR
            )
            
            # Determine required agents
            target_agents = await self.router.get_required_agents(request.query)
            
            yield self._format_streaming_update(
                "status", f"Routing to agents: {[a.value for a in target_agents]}", AgentType.ORCHESTRATOR
            )
            
            # Send requests to agents
            agent_tasks = []
            for agent in target_agents:
                task = asyncio.create_task(
                    self._query_agent(agent, request, correlation_id)
                )
                agent_tasks.append((agent, task))
            
            # Collect results as they complete
            agent_results = {}
            for agent, task in agent_tasks:
                try:
                    yield self._format_streaming_update(
                        "status", f"Waiting for {agent.value}...", agent
                    )
                    
                    result = await asyncio.wait_for(task, timeout=30)
                    agent_results[agent] = result
                    
                    yield self._format_streaming_update(
                        "partial", f"Received response from {agent.value}", agent
                    )
                    
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout waiting for {agent.value}")
                    yield self._format_streaming_update(
                        "status", f"Timeout from {agent.value}, continuing...", agent
                    )
                except Exception as e:
                    logger.error(f"Error from {agent.value}: {e}")
                    yield self._format_streaming_update(
                        "status", f"Error from {agent.value}: {str(e)}", agent
                    )
            
            # Compose final response
            yield self._format_streaming_update(
                "status", "Composing final response...", AgentType.ORCHESTRATOR
            )
            
            response = await self.composer.compose_response(
                request.query, agent_results
            )
            
            # Store results
            self._active_queries[correlation_id]['response'] = response
            self._active_queries[correlation_id]['status'] = 'complete'
            
            # Yield final response
            yield self._format_streaming_update(
                "complete", json.dumps(response.model_dump()), AgentType.ORCHESTRATOR
            )
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            self._active_queries[correlation_id]['status'] = 'error'
            
            yield self._format_streaming_update(
                "error", f"Query processing failed: {str(e)}", AgentType.ORCHESTRATOR
            )
    
    async def _query_agent(
        self,
        agent: AgentType,
        request: QueryRequest,
        correlation_id: str
    ) -> Dict[str, Any]:
        """Send query to specific agent and wait for response."""
        
        if agent == AgentType.NL2SQL:
            return await self._query_nl2sql_agent(request, correlation_id)
        elif agent == AgentType.VECTOR:
            return await self._query_vector_agent(request, correlation_id)
        elif agent == AgentType.API:
            return await self._query_api_agent(request, correlation_id)
        else:
            logger.warning(f"Unknown agent type: {agent}")
            return {
                'status': 'error',
                'message': f'Unknown agent type: {agent}',
                'processing_time_ms': 0
            }
    
    async def _query_nl2sql_agent(self, request: QueryRequest, correlation_id: str) -> Dict[str, Any]:
        """Query NL2SQL agent with direct HTTP call."""
        try:
            logger.info(f"🚀 ORCHESTRATOR: Making direct call to NL2SQL agent")
            logger.info(f"   Query: {request.query}")
            logger.info(f"   Household ID: {request.household_id}")
            logger.info(f"   Account ID: {request.account_id}")
            try:
                async with httpx.AsyncClient() as client:
                    logger.info(f"🔗 Making direct HTTP call to NL2SQL agent...")
                    # Prepare the request in the format expected by NL2SQLRequest
                    nl2sql_request = {
                        "query": request.query,
                        "household_id": request.household_id,
                        "account_id": request.account_id,
                        "schema_hint": None  # Not used currently
                    }
                    
                    response = await client.post(
                        f"http://localhost:9001/query",
                        json=nl2sql_request,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        nl2sql_result = response.json()
                        logger.info(f"✅ NL2SQL HTTP SUCCESS!")
                        logger.info(f"   Response keys: {list(nl2sql_result.keys())}")
                        logger.info(f"   Results count: {len(nl2sql_result.get('results', []))}")
                        logger.info(f"   SQL Query: {nl2sql_result.get('sql_query', 'N/A')[:100]}...")
                        logger.info(f"   Full response: {nl2sql_result}")
                        return nl2sql_result
                    else:
                        logger.error(f"❌ NL2SQL HTTP call failed: {response.status_code} - {response.text}")
                        
            except Exception as http_error:
                logger.error(f"❌ HTTP call to NL2SQL failed: {http_error}")
            
            # Fallback: return placeholder if HTTP call fails
            return {
                'status': 'success',
                'message': f'Query sent to NL2SQL agent with correlation ID: {correlation_id}',
                'processing_time_ms': 100,
                'results': [],  # Empty results instead of payload
                'sql_query': '',
                'row_count': 0
            }
            
        except Exception as e:
            logger.error(f"NL2SQL agent query failed: {e}")
            return {
                'status': 'error',
                'message': f'NL2SQL agent error: {str(e)}',
                'processing_time_ms': 0
            }
    
    async def _query_vector_agent(self, request: QueryRequest, correlation_id: str) -> Dict[str, Any]:
        """Query Vector agent for CRM/search data."""
        try:
            start_time = time.time()
            logger.info(f"🔍 ORCHESTRATOR: Making direct call to Vector agent")
            
            # Vector agent URL - default to localhost:9002
            vector_agent_url = "http://localhost:9002"
            
            # Determine household ID from request context
            household_id = getattr(request, 'household_id', 'international-family')
            if not household_id:
                household_id = 'international-family'  # Default household for testing
            
            logger.info(f"🏠 Using household_id: {household_id}")
            logger.info(f"❓ Query: {request.query}")
            
            # Call vector agent's CRM endpoint
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info(f"🔗 Making HTTP call to Vector agent at {vector_agent_url}")
                
                # Build query parameters
                params = {
                    'query': request.query,
                    'limit': 20
                }
                
                url = f"{vector_agent_url}/household/{household_id}/crm"
                logger.info(f"🌐 Full URL: {url}")
                logger.info(f"📊 Params: {params}")
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"✅ Vector agent responded successfully")
                logger.info(f"📊 Got {len(result.get('results', []))} CRM notes")
                
                # Also get executive summary for context
                try:
                    summary_url = f"{vector_agent_url}/household/{household_id}/summary"
                    summary_response = await client.get(summary_url, params={'days_back': 90})
                    
                    if summary_response.status_code == 200:
                        summary_data = summary_response.json()
                        logger.info(f"📋 Also retrieved executive summary")
                        
                        # Add summary to results
                        result['executive_summary'] = summary_data.get('summary', {})
                except Exception as summary_error:
                    logger.warning(f"⚠️ Could not retrieve summary: {summary_error}")
                    result['executive_summary'] = {}
                
                processing_time = int((time.time() - start_time) * 1000)
                
                return {
                    'status': 'success',
                    'message': f'Retrieved {len(result.get("results", []))} CRM notes',
                    'results': result.get('results', []),
                    'points_of_interest': result.get('executive_summary', {}),
                    'total_found': result.get('total_found', 0),
                    'household_id': household_id,
                    'processing_time_ms': processing_time
                }
                
        except Exception as e:
            logger.error(f"❌ Vector agent call failed: {e}")
            processing_time = int((time.time() - start_time) * 1000)
            return {
                'status': 'error',
                'message': f'Vector agent error: {str(e)}',
                'results': [],
                'processing_time_ms': processing_time
            }
    
    async def _query_api_agent(self, request: QueryRequest, correlation_id: str) -> Dict[str, Any]:
        """Query API agent for external data."""
        # Placeholder for API agent query  
        return {
            'status': 'success',
            'message': 'API agent response (placeholder)',
            'data': {},
            'processing_time_ms': 2000
        }
    
    def _format_streaming_update(
        self,
        update_type: str,
        content: str,
        agent: AgentType
    ) -> str:
        """Format streaming update as JSON."""
        update = StreamingUpdate(
            type=update_type,
            content=content,
            agent=agent
        )
        return f"data: {update.model_dump_json()}\n\n"
    
    async def process_query_sync(self, request: QueryRequest) -> QueryResponse:
        """Process query synchronously (for testing/API)."""
        
        # Collect all streaming updates
        updates = []
        async for update in self.process_query_streaming(request):
            updates.append(update)
        
        # Extract final response from last update
        if updates and updates[-1].startswith("data: "):
            try:
                last_data = updates[-1][6:]  # Remove "data: " prefix
                last_update = json.loads(last_data)
                if last_update.get('type') == 'complete':
                    return QueryResponse(**json.loads(last_update['content']))
            except Exception:
                pass
        
        # Fallback response
        return QueryResponse(
            answer="Sorry, I couldn't process your request at this time.",
            citations=[],
            execution_time_ms=0,
            agent_calls=[]
        )

# Global agent instance
agent: Optional[OrchestratorAgent] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    global agent
    
    # Startup
    logger.info("Starting Orchestrator Agent")
    agent = OrchestratorAgent()
    
    yield
    
    # Shutdown
    if agent:
        await agent.broker.close()
    logger.info("Orchestrator Agent stopped")

# FastAPI application
app = FastAPI(
    title="Orchestrator Agent",
    description="Multi-Agent Orchestrator using Semantic Kernel",
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
    return {"status": "healthy", "agent": "orchestrator"}

@app.post("/debug/context")
async def debug_context(request: QueryRequest):
    """Debug endpoint to see what context is prepared for LLM."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Get required agents for this query
        required_agents = await agent.router.get_required_agents(request.query)
        from uuid import uuid4
        correlation_id = str(uuid4())
        
        # Query agents
        agent_results = {}
        for target_agent in required_agents:
            result = await agent._query_agent(target_agent, request, correlation_id)
            agent_results[target_agent] = result
        
        # Prepare context (without LLM call)
        context = agent.composer._prepare_context(request.query, agent_results)
        
        return {
            "query": request.query,
            "required_agents": [str(a) for a in required_agents],
            "agent_results": agent_results,
            "llm_context": context
        }
    except Exception as e:
        logger.error(f"Debug context failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/copilot/query")
async def process_query_sync(request: QueryRequest):
    """Process query synchronously."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return await agent.process_query_sync(request)

@app.post("/copilot/query/stream")
async def process_query_stream(request: QueryRequest):
    """Process query with streaming updates."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    async def generate_stream():
        async for update in agent.process_query_streaming(request):
            yield update
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)