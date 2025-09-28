"""
Vector Agent for CRM notes using Azure AI Search
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from azure.search.documents.aio import SearchClient
from azure.search.documents.indexes.aio import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SearchField, SearchFieldDataType, 
    VectorSearch, HnswAlgorithmConfiguration, VectorSearchProfile,
    SemanticConfiguration, SemanticSearch, SemanticField, SemanticPrioritizedFields
)
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from openai import AsyncAzureOpenAI

from common.schemas import (
    A2AMessage, A2AContext, VectorSearchRequest, VectorSearchResponse, 
    VectorSearchResult, PointOfInterest, AgentType, IntentType
)
from common.config import get_settings, get_cors_origins
from a2a.broker import create_broker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def resolve_household_id(household_identifier: str) -> str:
    """
    Resolve household identifier to numeric ID used in CRM data.
    If already numeric, return as-is. If it's a household code, 
    map it to the appropriate numeric ID.
    """
    # If it's already numeric, return as-is
    if household_identifier.isdigit():
        return household_identifier
    
    # Map household codes to numeric IDs based on our synthetic data
    # This mapping corresponds to the households we generated CRM data for
    household_code_to_id = {
        'johnson-family-trust': '1',      # The Johnson Family Trust
        'martinez-family': '2',           # Martinez Family Wealth  
        'chen-enterprises': '3',          # Chen Enterprises
        'wilson-retirement': '4',         # Wilson Retirement Fund
        'garcia-foundation': '5',         # Garcia Foundation
        'thompson-individual': '6',       # Thompson Individual Account
        'retired-educators': '7',         # Retired Educators Fund
        'startup-founder': '8',           # Startup Founder Portfolio
        'multigenerational-wealth': '9',  # Multigenerational Wealth
        'divorced-single-parent': '10',   # Divorced Single Parent
        'real-estate-investors': '11',    # Real Estate Investors
        'young-inheritance': '12',        # Young Inheritance Recipients
        'energy-executive': '13',         # Energy Executive Account
        'healthcare-professionals': '14', # Healthcare Professionals
        'military-retirees': '15',        # Military Retirees Fund
        'entertainment-industry': '16',   # Entertainment Industry
        'small-business-owners': '17',    # Small Business Owners
        'legal-professionals': '18',      # Legal Professionals
        'international-family': '19',     # International Family Office
        'tech-entrepreneur': '20',        # Tech Entrepreneur Portfolio
        'nonprofit-endowment': '21',      # Nonprofit Endowment Fund
    }
    
    # Return mapped ID or default to '1' if not found
    return household_code_to_id.get(household_identifier, '1')


class AzureSearchClient:
    """Client for Azure AI Search with vector capabilities."""
    
    def __init__(self):
        # Clear the cache and reload settings to ensure fresh config
        get_settings.cache_clear()
        self.settings = get_settings()
        self.index_name = self.settings.ai_search_index_name
        self.degraded_mode = False
        
        # Initialize clients
        self._search_client: Optional[SearchClient] = None
        self._index_client: Optional[SearchIndexClient] = None
        self._openai_client: Optional[AsyncAzureOpenAI] = None
        
    async def _get_search_client(self) -> SearchClient:
        """Get or create search client."""
        if self._search_client is None:
            self._search_client = SearchClient(
                endpoint=self.settings.ai_search_endpoint,
                index_name=self.index_name,
                credential=AzureKeyCredential(self.settings.ai_search_key)
            )
        return self._search_client
    
    async def _get_index_client(self) -> SearchIndexClient:
        """Get or create index client."""
        if self._index_client is None:
            self._index_client = SearchIndexClient(
                endpoint=self.settings.ai_search_endpoint,
                credential=AzureKeyCredential(self.settings.ai_search_key)
            )
        return self._index_client
    
    async def _get_openai_client(self) -> AsyncAzureOpenAI:
        """Get or create OpenAI client."""
        if self._openai_client is None:
            # Use API key for authentication
            self._openai_client = AsyncAzureOpenAI(
                azure_endpoint=self.settings.azure_openai_endpoint,
                api_version=self.settings.azure_openai_api_version,
                api_key=self.settings.azure_openai_key
            )
        return self._openai_client
    
    async def ensure_index_exists(self):
        """Create search index if it doesn't exist."""
        try:
            index_client = await self._get_index_client()
            
            # Define index schema
            fields = [
                SearchField(name="id", type=SearchFieldDataType.String, key=True, searchable=False),
                SearchField(name="account_id", type=SearchFieldDataType.String, filterable=True, searchable=False),
                SearchField(name="household_id", type=SearchFieldDataType.String, filterable=True, searchable=False),
                SearchField(name="text", type=SearchFieldDataType.String, searchable=True, analyzer_name="en.microsoft"),
                SearchField(name="author", type=SearchFieldDataType.String, filterable=True, searchable=True),
                SearchField(name="created_at", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True),
                SearchField(name="tags", type=SearchFieldDataType.Collection(SearchFieldDataType.String), filterable=True, searchable=True),
                SearchField(
                    name="content_vector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=1536,  # text-embedding-3-small dimensions
                    vector_search_profile_name="default-vector-profile"
                )
            ]
            
            # Vector search configuration
            vector_search = VectorSearch(
                algorithms=[
                    HnswAlgorithmConfiguration(name="default-hnsw")
                ],
                profiles=[
                    VectorSearchProfile(
                        name="default-vector-profile",
                        algorithm_configuration_name="default-hnsw"
                    )
                ]
            )
            
            # Semantic search configuration
            semantic_config = SemanticConfiguration(
                name="default-semantic-config",
                prioritized_fields=SemanticPrioritizedFields(
                    title_field=SemanticField(field_name="author"),
                    content_fields=[SemanticField(field_name="text")],
                    keywords_fields=[SemanticField(field_name="tags")]
                )
            )
            
            semantic_search = SemanticSearch(
                configurations=[semantic_config]
            )
            
            # Create index
            index = SearchIndex(
                name=self.index_name,
                fields=fields,
                vector_search=vector_search,
                semantic_search=semantic_search
            )
            
            try:
                await index_client.create_index(index)
                logger.info(f"Created search index: {self.index_name}")
            except Exception as e:
                error_msg = str(e).lower()
                if "already exists" in error_msg:
                    logger.info(f"Index {self.index_name} already exists")
                elif "quota" in error_msg or "exceeded" in error_msg:
                    logger.warning(f"Index quota exceeded. Index {self.index_name} may already exist or you need to delete unused indexes.")
                    # Try to check if index exists instead of creating
                    try:
                        await index_client.get_index(self.index_name)
                        logger.info(f"Index {self.index_name} already exists - using existing index")
                    except:
                        logger.warning(f"Index {self.index_name} doesn't exist and cannot be created due to quota limits")
                        logger.warning("Vector Agent will operate in degraded mode without search index")
                        # Set a flag to indicate degraded mode
                        self.degraded_mode = True
                        return
                else:
                    raise
                    
        except Exception as e:
            logger.error(f"Failed to create search index: {e}")
            raise
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts using Azure OpenAI."""
        try:
            openai_client = await self._get_openai_client()
            
            response = await openai_client.embeddings.create(
                input=texts,
                model=self.settings.azure_openai_embedding_deployment
            )
            
            return [item.embedding for item in response.data]
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    async def ingest_document(self, document: Dict[str, Any]):
        """Ingest a single document into the search index."""
        try:
            # Generate embedding for the text
            embeddings = await self.generate_embeddings([document['text']])
            document['content_vector'] = embeddings[0]
            
            search_client = await self._get_search_client()
            await search_client.upload_documents([document])
            
            logger.debug(f"Ingested document: {document['id']}")
            
        except Exception as e:
            logger.error(f"Failed to ingest document {document.get('id', 'unknown')}: {e}")
            raise
    
    async def ingest_documents(self, documents: List[Dict[str, Any]]):
        """Ingest multiple documents into the search index."""
        try:
            # Generate embeddings for all texts
            texts = [doc['text'] for doc in documents]
            embeddings = await self.generate_embeddings(texts)
            
            # Add embeddings to documents
            for doc, embedding in zip(documents, embeddings):
                doc['content_vector'] = embedding
            
            search_client = await self._get_search_client()
            await search_client.upload_documents(documents)
            
            logger.info(f"Ingested {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Failed to ingest documents: {e}")
            raise
    
    async def hybrid_search(
        self, 
        query: str, 
        top_k: int = 5,
        filters: Optional[str] = None
    ) -> List[VectorSearchResult]:
        """Perform hybrid search (vector + BM25)."""
        if self.degraded_mode:
            logger.warning("Vector Agent in degraded mode - returning mock search results")
            return [
                VectorSearchResult(
                    id="mock-1",
                    text=f"Mock CRM note related to: {query}",
                    score=0.95,
                    metadata={
                        "author": "System",
                        "created_at": "2024-01-01T00:00:00Z",
                        "tags": ["mock"],
                        "account_id": "mock-account",
                        "household_id": "mock-household"
                    }
                )
            ]

        try:
            # Check if query is meaningful (not empty, not just "*", not just whitespace)
            meaningful_query = query and query.strip() and query.strip() != "*"
            
            # Generate query embedding only for meaningful queries
            query_embedding = None
            if meaningful_query:
                query_embedding = await self.generate_embeddings([query.strip()])
                
            search_client = await self._get_search_client()
            
            # Create vector query only if we have an embedding
            vector_queries = []
            if query_embedding:
                vector_query = VectorizedQuery(
                    vector=query_embedding[0],
                    k_nearest_neighbors=top_k * 2,  # Get more candidates for reranking
                    fields="content_vector"
                )
                vector_queries.append(vector_query)
            
            # Perform search - use text search for non-meaningful queries, hybrid for meaningful ones
            if meaningful_query and vector_queries:
                results = await search_client.search(
                    search_text=query.strip(),
                    vector_queries=vector_queries,
                    filter=filters,
                    top=top_k,
                    select=["id", "text", "author", "created_at", "tags", "account_id", "household_id"]
                )
            else:
                # For empty/wildcard queries, just do filtered search without vector/text
                results = await search_client.search(
                    search_text=None,
                    vector_queries=None,
                    filter=filters,
                    top=top_k,
                    select=["id", "text", "author", "created_at", "tags", "account_id", "household_id"]
                )
            
            search_results = []
            async for result in results:
                search_results.append(VectorSearchResult(
                    id=result["id"],
                    text=result["text"],
                    score=result["@search.score"],
                    metadata={
                        "author": result.get("author"),
                        "created_at": result.get("created_at"),
                        "tags": result.get("tags", []),
                        "account_id": result.get("account_id"),
                        "household_id": result.get("household_id")
                    }
                ))
            
            return search_results
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            raise


class VectorAgent:
    """Vector Agent service for CRM notes retrieval and analysis."""
    
    def __init__(self):
        self.settings = get_settings()
        self.search_client = AzureSearchClient()
        self.broker = create_broker("vector-agent")
        self.degraded_mode = False
        
        # Register message handlers
        self.broker.register_handler("CRMPOI", self.handle_crm_poi)
        self.broker.register_handler("ExecSummary", self.handle_exec_summary)
    
    async def initialize(self):
        """Initialize the vector agent."""
        try:
            await self.search_client.ensure_index_exists()
            # Check if search client is in degraded mode
            self.degraded_mode = getattr(self.search_client, 'degraded_mode', False)
        except Exception as e:
            logger.warning(f"Failed to initialize search index: {e}")
            self.degraded_mode = True
    
    async def handle_crm_poi(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle CRM points of interest queries."""
        try:
            query = message.payload.get('query', 'important points of interest')
            household_id = message.context.household_id
            account_id = message.context.account_id
            top_k = message.payload.get('top_k', 5)
            
            # Build filter
            filters = []
            if household_id:
                filters.append(f"household_id eq '{household_id}'")
            if account_id:
                filters.append(f"account_id eq '{account_id}'")
            
            filter_str = " and ".join(filters) if filters else None
            
            # Perform search
            results = await self.search_client.hybrid_search(
                query=query,
                top_k=top_k,
                filters=filter_str
            )
            
            # Extract points of interest
            pois = await self.extract_points_of_interest(results)
            
            return {
                'query': query,
                'results': [result.model_dump() for result in results],
                'points_of_interest': [poi.model_dump() for poi in pois],
                'total_found': len(results),
                'query_time_ms': 0  # TODO: Add timing
            }
            
        except Exception as e:
            logger.error(f"CRM POI query failed: {e}")
            raise
    
    async def handle_exec_summary(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle executive summary queries for CRM insights."""
        try:
            household_id = message.context.household_id
            account_id = message.context.account_id
            days_back = message.payload.get('days_back', 90)
            
            # Build comprehensive query for executive summary
            queries = [
                "performance review quarterly meeting client satisfaction",
                "risk assessment portfolio allocation changes recommendations",
                "tax planning strategies opportunities savings",
                "estate planning updates beneficiaries documents",
                "retirement planning projections income goals"
            ]
            
            all_results = []
            for query in queries:
                # Build filter
                filters = []
                if household_id:
                    filters.append(f"household_id eq '{household_id}'")
                if account_id:
                    filters.append(f"account_id eq '{account_id}'")
                
                # Add date filter for recent items
                from datetime import datetime, timedelta
                cutoff_date = (datetime.utcnow() - timedelta(days=days_back)).isoformat() + 'Z'
                filters.append(f"created_at ge {cutoff_date}")
                
                filter_str = " and ".join(filters) if filters else None
                
                # Perform search
                results = await self.search_client.hybrid_search(
                    query=query,
                    top_k=3,
                    filters=filter_str
                )
                all_results.extend(results)
            
            # Remove duplicates and sort by relevance
            unique_results = {}
            for result in all_results:
                if result.id not in unique_results or result.score > unique_results[result.id].score:
                    unique_results[result.id] = result
            
            sorted_results = sorted(unique_results.values(), key=lambda x: x.score, reverse=True)[:10]
            
            # Generate executive summary insights
            summary = await self.generate_executive_summary(sorted_results)
            
            return {
                'household_id': household_id,
                'account_id': account_id,
                'period_days': days_back,
                'summary': summary,
                'key_insights': summary.get('key_insights', []),
                'action_items': summary.get('action_items', []),
                'results': [result.model_dump() for result in sorted_results],
                'total_found': len(sorted_results)
            }
            
        except Exception as e:
            logger.error(f"Executive summary query failed: {e}")
            raise
    
    async def generate_executive_summary(self, results: List[VectorSearchResult]) -> Dict[str, Any]:
        """Generate executive summary from CRM search results using AI."""
        if self.degraded_mode or not results:
            return {
                'overview': 'Limited data available for executive summary.',
                'key_insights': ['Sample insight: Portfolio review completed'],
                'action_items': ['Sample action: Schedule follow-up meeting'],
                'trends': ['Sample trend: Increasing client engagement']
            }
        
        try:
            # Prepare context from search results
            context_notes = []
            for result in results:
                note_summary = {
                    'date': result.metadata.get('created_at', ''),
                    'author': result.metadata.get('author', ''),
                    'content': result.text[:300] + '...' if len(result.text) > 300 else result.text,
                    'tags': result.metadata.get('tags', [])
                }
                context_notes.append(note_summary)
            
            # Generate summary using OpenAI
            openai_client = await self.search_client._get_openai_client()
            
            summary_prompt = f"""
Analyze the following CRM notes and provide an executive summary in VALID JSON format only.

CRM Notes:
{json.dumps(context_notes, indent=2)}

You must respond with ONLY a valid JSON object in this exact format (no other text):
{{
    "overview": "Brief 2-3 sentence overview of the household's current financial status and recent activities",
    "key_insights": ["Insight 1", "Insight 2", "Insight 3"],
    "action_items": ["Action 1", "Action 2", "Action 3"],
    "opportunities": ["Opportunity 1", "Opportunity 2", "Opportunity 3"]
}}

Requirements:
- Respond with ONLY valid JSON (no markdown, no explanations)
- Include 3-5 items in each array
- Focus on actionable, specific insights
- Base all insights on the actual CRM notes provided
"""

            response = await openai_client.chat.completions.create(
                model=self.settings.azure_openai_deployment,
                messages=[
                    {"role": "system", "content": "You are an expert financial advisor. You MUST respond with ONLY valid JSON format. No explanations, no markdown, just pure JSON."},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.1,  # Lower temperature for more consistent JSON
                max_tokens=800
            )
            
            summary_text = response.choices[0].message.content
            
            # Parse JSON response
            try:
                # Clean the response text (remove potential markdown formatting)
                clean_text = summary_text.strip()
                if clean_text.startswith('```json'):
                    clean_text = clean_text.replace('```json', '').replace('```', '').strip()
                elif clean_text.startswith('```'):
                    clean_text = clean_text.replace('```', '').strip()
                
                summary_data = json.loads(clean_text)
                
                # Validate required fields and fix if necessary
                if not isinstance(summary_data.get('key_insights'), list):
                    summary_data['key_insights'] = []
                if not isinstance(summary_data.get('action_items'), list):
                    summary_data['action_items'] = []
                if not isinstance(summary_data.get('opportunities'), list):
                    summary_data['opportunities'] = []
                if not summary_data.get('overview'):
                    summary_data['overview'] = 'Executive summary generated from recent CRM activity'
                    
                return summary_data
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse AI summary as JSON: {e}")
                logger.warning(f"Raw AI response: {summary_text[:200]}...")
                
                # Create a structured response from the raw text
                lines = summary_text.split('\n')
                overview_lines = [line for line in lines if line.strip() and not line.strip().startswith('-')][:3]
                
                return {
                    'overview': ' '.join(overview_lines) if overview_lines else 'Recent CRM activity summary available.',
                    'key_insights': [
                        'Portfolio and investment activity reviewed',
                        'Client communication and meeting notes updated',
                        'Financial planning discussions documented'
                    ],
                    'action_items': [
                        'Review recent account activity',
                        'Schedule client follow-up meeting',
                        'Update investment recommendations'
                    ],
                    'opportunities': [
                        'Assess portfolio rebalancing needs',
                        'Review tax planning strategies',
                        'Evaluate additional investment opportunities'
                    ]
                }
                
        except Exception as e:
            logger.error(f"Failed to generate executive summary: {e}")
            return {
                'overview': f'Summary generation failed: {str(e)}',
                'key_insights': ['Error in AI analysis'],
                'action_items': ['Review system logs'],
                'trends': ['Unable to analyze'],
                'risk_factors': ['System error'],
                'opportunities': ['Check configuration']
            }
    
    async def search_crm_by_household(
        self, 
        household_id: str, 
        query: str = "*", 
        top_k: int = 10,
        category_filter: Optional[str] = None,
        date_range_days: Optional[int] = None
    ) -> List[VectorSearchResult]:
        """Search CRM notes for a specific household with optional filters."""
        try:
            # Build filters
            filters = [f"household_id eq '{household_id}'"]
            
            if category_filter:
                filters.append(f"category eq '{category_filter}'")
            
            if date_range_days:
                from datetime import datetime, timedelta
                cutoff_date = (datetime.utcnow() - timedelta(days=date_range_days)).isoformat() + 'Z'
                filters.append(f"created_at ge {cutoff_date}")
            
            filter_str = " and ".join(filters)
            
            # Perform search
            results = await self.search_client.hybrid_search(
                query=query,
                top_k=top_k,
                filters=filter_str
            )
            
            return results
            
        except Exception as e:
            logger.error(f"CRM search by household failed: {e}")
            raise
    
    async def get_crm_categories(self, household_id: str) -> List[Dict[str, Any]]:
        """Get available CRM categories for a household."""
        if self.degraded_mode:
            return [
                {"category": "investment_review", "count": 5},
                {"category": "financial_planning", "count": 3},
                {"category": "client_communication", "count": 8}
            ]
        
        try:
            # Search for all categories
            results = await self.search_client.hybrid_search(
                query="*",
                top_k=100,
                filters=f"household_id eq '{household_id}'"
            )
            
            # Count categories from tags
            category_counts = {}
            for result in results:
                tags = result.metadata.get('tags', [])
                # Extract categories from tags - look for known category patterns
                categories_found = []
                for tag in tags:
                    if tag in ['investment review', 'financial planning', 'client communication', 
                              'account management', 'compliance review', 'market events']:
                        categories_found.append(tag.replace(' ', '_'))
                
                # If no known categories found, use first tag or 'uncategorized'
                if not categories_found:
                    if tags:
                        categories_found = [tags[0].replace(' ', '_')]
                    else:
                        categories_found = ['uncategorized']
                
                # Count each category
                for category in categories_found:
                    category_counts[category] = category_counts.get(category, 0) + 1
            
            return [
                {"category": cat, "count": count} 
                for cat, count in sorted(category_counts.items())
            ]
            
        except Exception as e:
            logger.error(f"Failed to get CRM categories: {e}")
            return []
    
    async def extract_points_of_interest(self, results: List[VectorSearchResult]) -> List[PointOfInterest]:
        """Extract points of interest from search results."""
        pois = []
        
        # Simple extraction logic (could be enhanced with LLM)
        for result in results:
            text = result.text.lower()
            created_at = result.metadata.get('created_at')
            author = result.metadata.get('author', 'Unknown')
            
            # Pattern matching for different POI types
            if any(keyword in text for keyword in ['tax', 'planning', 'loss']):
                pois.append(PointOfInterest(
                    date=datetime.fromisoformat(created_at).date() if created_at else datetime.now().date(),
                    author=author,
                    poi="Tax planning opportunity identified",
                    why="Potential tax optimization based on conversation context"
                ))
            
            elif any(keyword in text for keyword in ['concentration', 'risk', 'diversification']):
                pois.append(PointOfInterest(
                    date=datetime.fromisoformat(created_at).date() if created_at else datetime.now().date(),
                    author=author,
                    poi="Concentration risk flagged",
                    why="Portfolio diversification discussion noted"
                ))
            
            elif any(keyword in text for keyword in ['529', 'education', 'college']):
                pois.append(PointOfInterest(
                    date=datetime.fromisoformat(created_at).date() if created_at else datetime.now().date(),
                    author=author,
                    poi="Education funding discussion",
                    why="529 plan or education savings mentioned"
                ))
            
            elif any(keyword in text for keyword in ['insurance', 'coverage', 'policy']):
                pois.append(PointOfInterest(
                    date=datetime.fromisoformat(created_at).date() if created_at else datetime.now().date(),
                    author=author,
                    poi="Insurance review needed",
                    why="Coverage gaps or policy changes discussed"
                ))
        
        return pois[:5]  # Return top 5 POIs
    
    async def generate_summary(self, results: List[VectorSearchResult], household_id: str) -> str:
        """Generate executive summary from search results."""
        if not results:
            return "No relevant CRM notes found for this household."
        
        # Simple summary generation (could be enhanced with LLM)
        themes = {
            'tax': 0,
            'risk': 0,
            'performance': 0,
            'planning': 0,
            'insurance': 0
        }
        
        total_notes = len(results)
        recent_activity = sum(1 for r in results if 'created_at' in r.metadata and 
                            datetime.fromisoformat(r.metadata['created_at']) > datetime.now().replace(day=1))
        
        for result in results:
            text = result.text.lower()
            if any(word in text for word in ['tax', 'planning']):
                themes['tax'] += 1
            if any(word in text for word in ['risk', 'concentration']):
                themes['risk'] += 1
            if any(word in text for word in ['performance', 'return']):
                themes['performance'] += 1
            if any(word in text for word in ['planning', 'goal']):
                themes['planning'] += 1
            if any(word in text for word in ['insurance', 'coverage']):
                themes['insurance'] += 1
        
        top_theme = max(themes.keys(), key=lambda k: themes[k])
        
        return f"""Executive Summary for Household {household_id}:
        
• Recent Activity: {recent_activity} notes this month out of {total_notes} total
• Primary Focus: {top_theme.title()} planning ({themes[top_theme]} related discussions)
• Key Themes: {', '.join([k for k, v in themes.items() if v > 0])}
• Recommendation: Follow up on {top_theme} discussions and review action items"""
    
    async def process_direct_search(self, request: VectorSearchRequest) -> VectorSearchResponse:
        """Process direct vector search request (HTTP API)."""
        try:
            start_time = time.time()
            
            # Build filter
            filters = []
            if request.household_id:
                filters.append(f"household_id eq '{request.household_id}'")
            if request.account_id:
                filters.append(f"account_id eq '{request.account_id}'")
            
            for key, value in request.filters.items():
                if isinstance(value, str):
                    filters.append(f"{key} eq '{value}'")
                elif isinstance(value, list):
                    filter_values = "','".join(str(v) for v in value)
                    filters.append(f"{key}/any(t: search.in(t, '{filter_values}'))")
            
            filter_str = " and ".join(filters) if filters else None
            
            # Perform search
            results = await self.search_client.hybrid_search(
                query=request.query,
                top_k=request.top_k,
                filters=filter_str
            )
            
            query_time = int((time.time() - start_time) * 1000)
            
            return VectorSearchResponse(
                results=results,
                total_found=len(results),
                query_time_ms=query_time
            )
            
        except Exception as e:
            logger.error(f"Direct search failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Global agent instance
agent: Optional[VectorAgent] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    global agent
    
    # Startup
    logger.info("Starting Vector Agent")
    agent = VectorAgent()
    await agent.initialize()
    
    # Start message broker in background
    asyncio.create_task(agent.broker.start_listening())
    
    yield
    
    # Shutdown
    if agent:
        await agent.broker.close()
    logger.info("Vector Agent stopped")

# FastAPI application
app = FastAPI(
    title="Vector Agent",
    description="Vector Agent for CRM notes retrieval using Azure AI Search",
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
    return {"status": "healthy", "agent": "vector"}

@app.post("/search", response_model=VectorSearchResponse)
async def search_crm_notes(request: VectorSearchRequest):
    """Search CRM notes using hybrid search."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return await agent.process_direct_search(request)

@app.post("/ingest")
async def ingest_documents(documents: List[Dict[str, Any]]):
    """Ingest documents into the search index."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    await agent.search_client.ingest_documents(documents)
    return {"message": f"Ingested {len(documents)} documents"}

@app.get("/household/{household_id}/crm")
async def get_household_crm_notes(
    household_id: str,
    query: str = "*",
    category: Optional[str] = None,
    days: Optional[int] = None,
    limit: int = 20
):
    """Get CRM notes for a specific household with optional filters."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Resolve household code to numeric ID
        resolved_household_id = resolve_household_id(household_id)
        
        results = await agent.search_crm_by_household(
            household_id=resolved_household_id,
            query=query,
            top_k=limit,
            category_filter=category,
            date_range_days=days
        )
        
        return {
            "household_id": household_id,
            "results": [result.model_dump() for result in results],
            "total_found": len(results),
            "filters_applied": {
                "category": category,
                "days_back": days,
                "query": query
            }
        }
    except Exception as e:
        logger.error(f"Error fetching household CRM notes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/household/{household_id}/categories")
async def get_household_categories(household_id: str):
    """Get available CRM categories for a household."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Resolve household code to numeric ID
        resolved_household_id = resolve_household_id(household_id)
        
        categories = await agent.get_crm_categories(resolved_household_id)
        return {"household_id": household_id, "categories": categories}
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/household/{household_id}/summary")
async def get_household_executive_summary(
    household_id: str,
    days_back: int = 90
):
    """Get executive summary for a household based on recent CRM activity."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Resolve household code to numeric ID
        resolved_household_id = resolve_household_id(household_id)
        
        # Create A2A message for exec summary
        message = A2AMessage(
            from_agent=AgentType.VECTOR,
            to_agents=[AgentType.VECTOR],
            intent=IntentType.EXEC_SUMMARY,
            payload={"days_back": days_back},
            context=A2AContext(household_id=resolved_household_id)
        )
        
        result = await agent.handle_exec_summary(message)
        return result
        
    except Exception as e:
        logger.error(f"Error generating executive summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/household/{household_id}/crm/simple")
async def get_household_crm_simple(household_id: str, limit: int = 5):
    """Get CRM notes using simple text search (no embeddings)."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Resolve household code to numeric ID
        resolved_household_id = resolve_household_id(household_id)
        
        search_client = await agent.search_client._get_search_client()
        
        # Simple text search without vector embeddings
        results = await search_client.search(
            search_text="*",
            filter=f"household_id eq '{resolved_household_id}'",
            top=limit,
            select=["id", "text", "author", "created_at", "tags", "household_id"]
        )
        
        search_results = []
        async for result in results:
            search_results.append({
                "id": result["id"],
                "text": result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"],
                "author": result.get("author"),
                "created_at": result.get("created_at"),
                "tags": result.get("tags", []),
                "household_id": result.get("household_id")
            })
        
        return {
            "household_id": household_id,
            "results": search_results,
            "total_found": len(search_results)
        }
        
    except Exception as e:
        logger.error(f"Simple search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/settings")
async def debug_settings():
    """Debug agent settings."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return {
        "ai_search_endpoint": agent.settings.ai_search_endpoint,
        "ai_search_index_name": agent.settings.ai_search_index_name,
        "azure_openai_endpoint": agent.settings.azure_openai_endpoint,
        "azure_openai_deployment": agent.settings.azure_openai_deployment,
        "azure_openai_embedding_deployment": agent.settings.azure_openai_embedding_deployment,
        "azure_openai_api_version": agent.settings.azure_openai_api_version,
        "has_openai_key": bool(agent.settings.azure_openai_key),
        "has_search_key": bool(agent.settings.ai_search_key)
    }

@app.get("/test/embeddings")
async def test_embeddings():
    """Test embedding generation."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Test with a simple text
        test_text = ["hello world"]
        embeddings = await agent.search_client.generate_embeddings(test_text)
        
        return {
            "status": "success",
            "text": test_text[0],
            "embedding_length": len(embeddings[0]) if embeddings else 0,
            "first_few_values": embeddings[0][:5] if embeddings else []
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "endpoint": agent.settings.azure_openai_endpoint,
            "deployment": agent.settings.azure_openai_embedding_deployment
        }

@app.get("/index/stats")
async def get_index_stats():
    """Get search index statistics."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        if agent.degraded_mode:
            return {
                "status": "degraded",
                "message": "Vector Agent running in degraded mode",
                "document_count": 0
            }
        
        # Use the search client to get stats
        search_client = await agent.search_client._get_search_client()
        document_count = await search_client.get_document_count()
        
        return {
            "status": "healthy",
            "document_count": document_count,
            "index_name": agent.search_client.index_name
        }
    except Exception as e:
        logger.error(f"Error getting index stats: {e}")
        return {
            "status": "error",
            "message": str(e),
            "document_count": 0
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)