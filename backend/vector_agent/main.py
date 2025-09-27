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
from openai import AsyncAzureOpenAI

from common.schemas import (
    A2AMessage, VectorSearchRequest, VectorSearchResponse, 
    VectorSearchResult, PointOfInterest, AgentType
)
from common.config import get_settings, get_cors_origins
from common.auth import get_credential, get_search_access_token, get_openai_access_token
from a2a.broker import create_broker

logger = logging.getLogger(__name__)


class AzureSearchClient:
    """Client for Azure AI Search with vector capabilities."""
    
    def __init__(self):
        self.settings = get_settings()
        self.credential = get_credential()
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
                credential=self.credential
            )
        return self._search_client
    
    async def _get_index_client(self) -> SearchIndexClient:
        """Get or create index client."""
        if self._index_client is None:
            self._index_client = SearchIndexClient(
                endpoint=self.settings.ai_search_endpoint,
                credential=self.credential
            )
        return self._index_client
    
    async def _get_openai_client(self) -> AsyncAzureOpenAI:
        """Get or create OpenAI client."""
        if self._openai_client is None:
            # Use access token for authentication
            access_token = get_openai_access_token()
            
            self._openai_client = AsyncAzureOpenAI(
                azure_endpoint=self.settings.azure_openai_endpoint,
                api_version=self.settings.azure_openai_api_version,
                azure_ad_token=access_token
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
            # Generate query embedding
            query_embedding = await self.generate_embeddings([query])
            
            search_client = await self._get_search_client()
            
            # Create vector query
            vector_query = VectorizedQuery(
                vector=query_embedding[0],
                k_nearest_neighbors=top_k * 2,  # Get more candidates for reranking
                fields="content_vector"
            )
            
            # Perform search
            results = await search_client.search(
                search_text=query,
                vector_queries=[vector_query],
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
    
    async def extract_points_of_interest(self, results: List[VectorSearchResult]) -> List[PointOfInterest]:
        """Extract points of interest from search results."""
        if self.degraded_mode:
            return [
                PointOfInterest(
                    text="Mock point of interest from degraded mode",
                    importance=0.8,
                    category="mock",
                    source_id="mock-1"
                )
            ]
        
        # Extract key points from the search results
        pois = []
        for result in results:
            if result.score > 0.7:  # High relevance threshold
                pois.append(PointOfInterest(
                    text=result.text[:200] + "..." if len(result.text) > 200 else result.text,
                    importance=result.score,
                    category="crm_note",
                    source_id=result.id
                ))
        
        return pois
    
    async def handle_exec_summary(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle executive summary queries."""
        try:
            household_id = message.context.household_id
            query = message.payload.get('query', 'executive summary key points')
            
            # Search for relevant CRM notes
            filter_str = f"household_id eq '{household_id}'" if household_id else None
            
            results = await self.search_client.hybrid_search(
                query=query,
                top_k=10,
                filters=filter_str
            )
            
            # Summarize findings
            summary = await self.generate_summary(results, household_id)
            
            return {
                'query': query,
                'summary': summary,
                'supporting_notes': [result.model_dump() for result in results[:5]],
                'total_notes_reviewed': len(results)
            }
            
        except Exception as e:
            logger.error(f"Executive summary query failed: {e}")
            raise
    
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


@app.get("/index/stats")
async def get_index_stats():
    """Get search index statistics."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    # TODO: Implement index statistics
    return {"message": "Index statistics not yet implemented"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)