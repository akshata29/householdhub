"""
Tests for the Vector Agent - Azure AI Search integration for CRM notes retrieval
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

# Import the Vector agent components
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from vector_agent.main import VectorAgent, AzureSearchClient
from common.schemas import A2ARequest, BusinessQuery

@pytest.mark.asyncio
class TestAzureSearchClient:
    """Test Azure AI Search client functionality."""
    
    def setup_method(self):
        with patch('backend.vector_agent.main.SearchClient'), \
             patch('backend.vector_agent.main.AzureOpenAI'):
            self.client = AzureSearchClient()
    
    async def test_generate_embeddings(self):
        """Test embedding generation for queries."""
        query = "Recent CRM notes for John Doe"
        
        mock_embedding = [0.1, 0.2, 0.3, 0.4] * 384  # 1536 dimensions
        
        with patch.object(self.client.embeddings_client.embeddings, 'create') as mock_create:
            mock_create.return_value = MagicMock(
                data=[MagicMock(embedding=mock_embedding)]
            )
            
            embedding = await self.client.generate_embeddings(query)
            
            assert len(embedding) == 1536
            assert embedding == mock_embedding
            mock_create.assert_called_once()
    
    async def test_search_crm_notes_by_client(self):
        """Test searching CRM notes by client name."""
        client_name = "John Doe"
        
        mock_search_results = [
            {
                "note_id": "NOTE001", 
                "client_name": "John Doe",
                "advisor": "Jane Smith",
                "note_text": "Discussed retirement planning options and 401k rollover",
                "created_date": "2024-01-15T10:30:00Z",
                "tags": ["retirement", "401k"],
                "@search.score": 0.95
            },
            {
                "note_id": "NOTE002",
                "client_name": "John Doe", 
                "advisor": "Jane Smith",
                "note_text": "Client concerned about market volatility impact on portfolio",
                "created_date": "2024-01-10T14:20:00Z",
                "tags": ["market", "volatility"],
                "@search.score": 0.88
            }
        ]
        
        with patch.object(self.client.search_client, 'search', return_value=mock_search_results):
            results = await self.client.search_crm_notes(client_name=client_name)
            
            assert len(results) == 2
            assert results[0]["client_name"] == "John Doe"
            assert results[0]["@search.score"] == 0.95
            assert "retirement" in results[0]["note_text"].lower()
    
    async def test_search_crm_notes_by_keywords(self):
        """Test searching CRM notes by keywords."""
        keywords = "retirement planning"
        
        mock_search_results = [
            {
                "note_id": "NOTE003",
                "client_name": "Mary Johnson",
                "advisor": "Bob Wilson", 
                "note_text": "Comprehensive retirement planning session - reviewed IRA distributions",
                "created_date": "2024-01-12T16:45:00Z",
                "tags": ["retirement", "IRA"],
                "@search.score": 0.92
            }
        ]
        
        with patch.object(self.client.search_client, 'search', return_value=mock_search_results):
            results = await self.client.search_crm_notes(keywords=keywords)
            
            assert len(results) == 1
            assert "retirement" in results[0]["note_text"].lower()
            assert results[0]["@search.score"] == 0.92
    
    async def test_hybrid_search(self):
        """Test hybrid search combining vector and keyword search."""
        query = "Recent discussions about market volatility"
        
        mock_embedding = [0.1] * 1536
        mock_search_results = [
            {
                "note_id": "NOTE004",
                "client_name": "Alice Brown",
                "note_text": "Client expressed concerns about recent market volatility and portfolio performance",
                "created_date": "2024-01-20T11:15:00Z",
                "@search.score": 0.94
            }
        ]
        
        with patch.object(self.client, 'generate_embeddings', return_value=mock_embedding), \
             patch.object(self.client.search_client, 'search', return_value=mock_search_results):
            
            results = await self.client.hybrid_search(query)
            
            assert len(results) == 1
            assert "volatility" in results[0]["note_text"].lower()
    
    async def test_extract_entities(self):
        """Test entity extraction from CRM notes."""
        note_text = "Discussed 401k rollover for John Doe's account ACC123, targeting Conservative Growth portfolio"
        
        entities = self.client.extract_entities(note_text)
        
        assert "John Doe" in entities["people"]
        assert "ACC123" in entities["accounts"] 
        assert "Conservative Growth" in entities["portfolios"]
        assert "401k" in entities["products"]
    
    async def test_search_error_handling(self):
        """Test error handling in search operations."""
        with patch.object(self.client.search_client, 'search', side_effect=Exception("Search service unavailable")):
            results = await self.client.search_crm_notes(client_name="Test Client")
            
            assert results == []

@pytest.mark.asyncio 
class TestVectorAgent:
    """Test the main Vector agent functionality."""
    
    def setup_method(self):
        with patch('backend.vector_agent.main.A2ABroker'), \
             patch('backend.vector_agent.main.SearchClient'), \
             patch('backend.vector_agent.main.AzureOpenAI'):
            self.agent = VectorAgent()
    
    async def test_process_crm_notes_request_by_client(self):
        """Test processing CRM notes request by client name."""
        request = A2ARequest(
            request_id="test-001",
            source_agent="orchestrator",
            target_agent="vector",
            query=BusinessQuery(
                query_id="test-001", 
                question="What are the recent CRM notes for John Doe?",
                context={"client_name": "John Doe"}
            ),
            metadata={}
        )
        
        mock_notes = [
            {
                "note_id": "NOTE001",
                "client_name": "John Doe",
                "advisor": "Jane Smith",
                "note_text": "Discussed retirement planning and portfolio rebalancing",
                "created_date": "2024-01-15T10:30:00Z",
                "tags": ["retirement", "rebalancing"],
                "@search.score": 0.95
            },
            {
                "note_id": "NOTE002", 
                "client_name": "John Doe",
                "advisor": "Jane Smith",
                "note_text": "Follow-up on market volatility concerns", 
                "created_date": "2024-01-10T14:20:00Z",
                "tags": ["market", "volatility"],
                "@search.score": 0.88
            }
        ]
        
        with patch.object(self.agent.search_client, 'search_crm_notes', return_value=mock_notes):
            response = await self.agent.process_request(request)
            
            assert response.success is True
            assert len(response.data) == 2
            assert response.data[0]["client_name"] == "John Doe" 
            assert "CRM" in response.citations[0]
    
    async def test_process_crm_notes_request_by_keywords(self):
        """Test processing CRM notes request by keywords."""
        request = A2ARequest(
            request_id="test-002",
            source_agent="orchestrator",
            target_agent="vector",
            query=BusinessQuery(
                query_id="test-002",
                question="Find CRM notes about retirement planning discussions",
                context={"keywords": "retirement planning"}
            ),
            metadata={}
        )
        
        mock_notes = [
            {
                "note_id": "NOTE003",
                "client_name": "Mary Johnson", 
                "note_text": "Comprehensive retirement planning session covering IRA strategies",
                "created_date": "2024-01-12T16:45:00Z",
                "@search.score": 0.92
            }
        ]
        
        with patch.object(self.agent.search_client, 'search_crm_notes', return_value=mock_notes):
            response = await self.agent.process_request(request)
            
            assert response.success is True
            assert len(response.data) == 1
            assert "retirement" in response.data[0]["note_text"].lower()
    
    async def test_process_hybrid_search_request(self):
        """Test processing hybrid search request."""
        request = A2ARequest(
            request_id="test-003",
            source_agent="orchestrator",
            target_agent="vector",
            query=BusinessQuery(
                query_id="test-003", 
                question="Recent client discussions about market concerns",
                context={}
            ),
            metadata={}
        )
        
        mock_notes = [
            {
                "note_id": "NOTE004",
                "client_name": "Alice Brown",
                "note_text": "Client expressed concerns about recent market volatility",
                "created_date": "2024-01-20T11:15:00Z",
                "@search.score": 0.94
            }
        ]
        
        with patch.object(self.agent.search_client, 'hybrid_search', return_value=mock_notes):
            response = await self.agent.process_request(request)
            
            assert response.success is True
            assert len(response.data) == 1
            assert "market" in response.data[0]["note_text"].lower()
    
    async def test_process_entity_extraction(self):
        """Test entity extraction from search results."""
        request = A2ARequest(
            request_id="test-004",
            source_agent="orchestrator", 
            target_agent="vector",
            query=BusinessQuery(
                query_id="test-004",
                question="Find notes mentioning specific accounts or portfolios",
                context={"extract_entities": True}
            ),
            metadata={}
        )
        
        mock_notes = [
            {
                "note_id": "NOTE005",
                "client_name": "Bob Smith",
                "note_text": "Reviewed performance of Conservative Growth portfolio in account ACC123",
                "created_date": "2024-01-18T09:30:00Z",
                "@search.score": 0.89
            }
        ]
        
        with patch.object(self.agent.search_client, 'search_crm_notes', return_value=mock_notes):
            response = await self.agent.process_request(request)
            
            assert response.success is True
            assert "entities" in response.metadata
            entities = response.metadata["entities"]
            assert "Bob Smith" in str(entities)
            assert "ACC123" in str(entities)
            assert "Conservative Growth" in str(entities)
    
    async def test_process_no_results(self):
        """Test handling when no CRM notes are found."""
        request = A2ARequest(
            request_id="test-005",
            source_agent="orchestrator",
            target_agent="vector", 
            query=BusinessQuery(
                query_id="test-005",
                question="Find notes for nonexistent client",
                context={"client_name": "Nonexistent Client"}
            ),
            metadata={}
        )
        
        with patch.object(self.agent.search_client, 'search_crm_notes', return_value=[]):
            response = await self.agent.process_request(request)
            
            assert response.success is True
            assert len(response.data) == 0
            assert "no notes found" in response.metadata.get("message", "").lower()
    
    async def test_process_search_error(self):
        """Test error handling in search operations."""
        request = A2ARequest(
            request_id="test-error",
            source_agent="orchestrator",
            target_agent="vector",
            query=BusinessQuery(
                query_id="test-error",
                question="Search that will fail",
                context={}
            ),
            metadata={}
        )
        
        with patch.object(self.agent.search_client, 'search_crm_notes', side_effect=Exception("Search failed")):
            response = await self.agent.process_request(request)
            
            assert response.success is False
            assert "search failed" in response.error.lower()
    
    async def test_relevance_filtering(self):
        """Test that low-relevance results are filtered out."""
        request = A2ARequest(
            request_id="test-006",
            source_agent="orchestrator",
            target_agent="vector",
            query=BusinessQuery(
                query_id="test-006",
                question="Find highly relevant notes only", 
                context={}
            ),
            metadata={}
        )
        
        mock_notes = [
            {"note_id": "NOTE_HIGH", "@search.score": 0.95, "note_text": "High relevance note"},
            {"note_id": "NOTE_MED", "@search.score": 0.75, "note_text": "Medium relevance note"},
            {"note_id": "NOTE_LOW", "@search.score": 0.45, "note_text": "Low relevance note"}
        ]
        
        with patch.object(self.agent.search_client, 'search_crm_notes', return_value=mock_notes):
            response = await self.agent.process_request(request)
            
            # Should filter out low relevance results (score < 0.5)
            assert response.success is True
            assert len(response.data) == 2
            assert all(note["@search.score"] >= 0.5 for note in response.data)
    
    async def test_result_ranking(self):
        """Test that results are properly ranked by relevance."""
        request = A2ARequest(
            request_id="test-007",
            source_agent="orchestrator",
            target_agent="vector",
            query=BusinessQuery(
                query_id="test-007", 
                question="Find ranked results",
                context={}
            ),
            metadata={}
        )
        
        mock_notes = [
            {"note_id": "NOTE_B", "@search.score": 0.85, "note_text": "Second best"},
            {"note_id": "NOTE_A", "@search.score": 0.95, "note_text": "Best match"},
            {"note_id": "NOTE_C", "@search.score": 0.75, "note_text": "Third best"}
        ]
        
        with patch.object(self.agent.search_client, 'search_crm_notes', return_value=mock_notes):
            response = await self.agent.process_request(request)
            
            assert response.success is True
            # Results should be sorted by score descending
            scores = [note["@search.score"] for note in response.data]
            assert scores == sorted(scores, reverse=True)
            assert response.data[0]["note_id"] == "NOTE_A"