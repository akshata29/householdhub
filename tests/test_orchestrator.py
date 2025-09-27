"""
Tests for the Orchestrator Agent - main entry point for multi-agent coordination
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
from datetime import datetime

# Import the orchestrator components
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from orchestrator.main import OrchestratorAgent, IntentRouter, ResponseComposer
from common.schemas import A2ARequest, A2AResponse, BusinessQuery, QueryResult

class TestIntentRouter:
    """Test intent routing logic."""
    
    def setup_method(self):
        self.router = IntentRouter()
    
    def test_route_cash_position_query(self):
        """Test routing of cash position queries."""
        query = "What is the total cash position for household HH001?"
        intent = self.router.determine_intent(query)
        
        assert intent.primary_agent == "nl2sql"
        assert intent.secondary_agents == []
        assert "cash" in intent.keywords
        assert "household" in intent.keywords
    
    def test_route_top_households_query(self):
        """Test routing of top households queries."""
        query = "Show me the top 3 households by assets under management"
        intent = self.router.determine_intent(query)
        
        assert intent.primary_agent == "nl2sql"
        assert intent.secondary_agents == []
        assert "top" in intent.keywords
        assert "households" in intent.keywords
    
    def test_route_crm_notes_query(self):
        """Test routing of CRM notes queries."""
        query = "What are the recent CRM notes for John Doe?"
        intent = self.router.determine_intent(query)
        
        assert intent.primary_agent == "vector"
        assert intent.secondary_agents == []
        assert "crm" in intent.keywords
        assert "notes" in intent.keywords
    
    def test_route_plan_performance_query(self):
        """Test routing of plan performance queries."""
        query = "How did the Conservative Growth portfolio perform last quarter?"
        intent = self.router.determine_intent(query)
        
        assert intent.primary_agent == "api"
        assert intent.secondary_agents == []
        assert "performance" in intent.keywords
        assert "portfolio" in intent.keywords
    
    def test_route_complex_executive_summary(self):
        """Test routing of complex queries requiring multiple agents."""
        query = "Generate an executive summary for household HH001"
        intent = self.router.determine_intent(query)
        
        assert intent.primary_agent == "nl2sql"
        assert "vector" in intent.secondary_agents
        assert "api" in intent.secondary_agents
        assert "executive" in intent.keywords
        assert "summary" in intent.keywords

@pytest.mark.asyncio
class TestResponseComposer:
    """Test response composition logic."""
    
    def setup_method(self):
        with patch('orchestrator.main.AzureOpenAI'):
            self.composer = ResponseComposer()
    
    async def test_compose_single_agent_response(self):
        """Test composing response from single agent."""
        primary_result = QueryResult(
            agent="nl2sql",
            data={"total_cash": 125000.00, "household_id": "HH001"},
            metadata={"query": "SELECT SUM(cash_balance) FROM accounts WHERE household_id = 'HH001'"},
            citations=["Database: accounts table"],
            confidence=0.95
        )
        
        query = BusinessQuery(
            query_id="test-001",
            question="What is the cash position for HH001?",
            context={"household_id": "HH001"}
        )
        
        with patch.object(self.composer.client.chat.completions, 'create') as mock_create:
            mock_create.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="The total cash position for household HH001 is $125,000."))]
            )
            
            response = await self.composer.compose_response(query, primary_result, [])
            
            assert "125,000" in response
            assert "HH001" in response
            mock_create.assert_called_once()
    
    async def test_compose_multi_agent_response(self):
        """Test composing response from multiple agents."""
        primary_result = QueryResult(
            agent="nl2sql",
            data={"total_assets": 2400000.00, "household_id": "HH001"},
            metadata={},
            citations=["Database: households table"],
            confidence=0.95
        )
        
        secondary_results = [
            QueryResult(
                agent="vector",
                data={"recent_notes": ["Client concerned about market volatility", "Discussed retirement planning"]},
                metadata={},
                citations=["CRM: John Doe notes"],
                confidence=0.88
            ),
            QueryResult(
                agent="api",
                data={"ytd_performance": 8.5, "portfolio": "Conservative Growth"},
                metadata={},
                citations=["Plan Performance API"],
                confidence=0.92
            )
        ]
        
        query = BusinessQuery(
            query_id="test-002",
            question="Generate executive summary for HH001",
            context={"household_id": "HH001"}
        )
        
        with patch.object(self.composer.client.chat.completions, 'create') as mock_create:
            mock_create.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Executive Summary: HH001 has $2.4M in assets with 8.5% YTD performance."))]
            )
            
            response = await self.composer.compose_response(query, primary_result, secondary_results)
            
            assert "2.4M" in response or "2,400,000" in response
            assert "8.5%" in response
            mock_create.assert_called_once()

@pytest.mark.asyncio
class TestOrchestratorAgent:
    """Test the main orchestrator agent."""
    
    def setup_method(self):
        with patch('orchestrator.main.A2ABroker'), \
             patch('orchestrator.main.AzureOpenAI'):
            self.orchestrator = OrchestratorAgent()
    
    async def test_process_simple_query(self, sample_business_queries):
        """Test processing a simple query that requires one agent."""
        query = BusinessQuery(
            query_id="test-001",
            question=sample_business_queries[0],  # Cash position query
            context={"household_id": "HH001"}
        )
        
        # Mock the A2A broker responses
        mock_response = A2AResponse(
            request_id="test-001",
            agent="nl2sql",
            data={"total_cash": 125000.00},
            metadata={"sql_query": "SELECT SUM(cash_balance) FROM accounts WHERE household_id = 'HH001'"},
            success=True,
            citations=["Database query result"]
        )
        
        with patch.object(self.orchestrator.broker, 'publish_request') as mock_publish, \
             patch.object(self.orchestrator.broker, 'wait_for_response', return_value=mock_response), \
             patch.object(self.orchestrator.composer, 'compose_response', return_value="Total cash: $125,000"):
            
            async for chunk in self.orchestrator.process_query(query):
                if chunk.get("type") == "final_response":
                    assert "$125,000" in chunk.get("content", "")
                    break
            
            mock_publish.assert_called_once()
    
    async def test_process_complex_query(self, sample_business_queries):
        """Test processing a complex query requiring multiple agents."""
        query = BusinessQuery(
            query_id="test-002",
            question=sample_business_queries[8],  # Executive summary
            context={"household_id": "HH001"}
        )
        
        # Mock responses from multiple agents
        primary_response = A2AResponse(
            request_id="test-002",
            agent="nl2sql",
            data={"total_assets": 2400000.00},
            metadata={},
            success=True,
            citations=["Database: households"]
        )
        
        secondary_responses = [
            A2AResponse(
                request_id="test-002-vector",
                agent="vector",
                data={"recent_notes": ["Market discussion", "Retirement planning"]},
                metadata={},
                success=True,
                citations=["CRM notes"]
            )
        ]
        
        with patch.object(self.orchestrator.broker, 'publish_request'), \
             patch.object(self.orchestrator.broker, 'wait_for_response', side_effect=[primary_response] + secondary_responses), \
             patch.object(self.orchestrator.composer, 'compose_response', return_value="Comprehensive executive summary"):
            
            response_received = False
            async for chunk in self.orchestrator.process_query(query):
                if chunk.get("type") == "final_response":
                    assert "executive summary" in chunk.get("content", "").lower()
                    response_received = True
                    break
            
            assert response_received
    
    async def test_error_handling(self):
        """Test error handling in orchestrator."""
        query = BusinessQuery(
            query_id="test-error",
            question="Invalid query that should fail",
            context={}
        )
        
        # Mock a failed response
        error_response = A2AResponse(
            request_id="test-error",
            agent="nl2sql",
            data={},
            metadata={},
            success=False,
            error="SQL parsing failed"
        )
        
        with patch.object(self.orchestrator.broker, 'publish_request'), \
             patch.object(self.orchestrator.broker, 'wait_for_response', return_value=error_response):
            
            error_received = False
            async for chunk in self.orchestrator.process_query(query):
                if chunk.get("type") == "error":
                    assert "failed" in chunk.get("message", "").lower()
                    error_received = True
                    break
            
            assert error_received

    async def test_streaming_response(self):
        """Test that orchestrator streams responses properly."""
        query = BusinessQuery(
            query_id="test-stream",
            question="What is the cash position?",
            context={"household_id": "HH001"}
        )
        
        mock_response = A2AResponse(
            request_id="test-stream",
            agent="nl2sql",
            data={"total_cash": 125000.00},
            metadata={},
            success=True,
            citations=["Database"]
        )
        
        with patch.object(self.orchestrator.broker, 'publish_request'), \
             patch.object(self.orchestrator.broker, 'wait_for_response', return_value=mock_response), \
             patch.object(self.orchestrator.composer, 'compose_response', return_value="Cash position: $125,000"):
            
            chunks_received = []
            async for chunk in self.orchestrator.process_query(query):
                chunks_received.append(chunk)
            
            # Should receive status updates and final response
            assert len(chunks_received) >= 2
            assert any(chunk.get("type") == "status" for chunk in chunks_received)
            assert any(chunk.get("type") == "final_response" for chunk in chunks_received)