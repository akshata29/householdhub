"""
Integration tests for end-to-end business query scenarios
Tests the complete flow from query input to final response
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import json

# Import all components for integration testing
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from orchestrator.main import OrchestratorAgent
from nl2sql_agent.main import NL2SQLAgent
from vector_agent.main import VectorAgent
from api_agent.main import APIAgent
from a2a.broker import A2ABroker
from common.schemas import BusinessQuery, A2ARequest, A2AResponse

@pytest.mark.asyncio
class TestEndToEndBusinessQueries:
    """Test complete end-to-end query processing for all 9 business scenarios."""
    
    def setup_method(self):
        """Set up mock agents and broker for integration testing."""
        self.mock_broker = AsyncMock(spec=A2ABroker)
        
        # Create agent instances with mocked dependencies
        with patch('backend.orchestrator.main.A2ABroker', return_value=self.mock_broker), \
             patch('backend.orchestrator.main.AzureOpenAI'):
            self.orchestrator = OrchestratorAgent()
        
        with patch('backend.nl2sql_agent.main.A2ABroker', return_value=self.mock_broker), \
             patch('backend.nl2sql_agent.main.MCPClient'):
            self.nl2sql_agent = NL2SQLAgent()
        
        with patch('backend.vector_agent.main.A2ABroker', return_value=self.mock_broker), \
             patch('backend.vector_agent.main.SearchClient'), \
             patch('backend.vector_agent.main.AzureOpenAI'):
            self.vector_agent = VectorAgent()
        
        with patch('backend.api_agent.main.A2ABroker', return_value=self.mock_broker), \
             patch('backend.api_agent.main.SyntheticDataGenerator'):
            self.api_agent = APIAgent()
    
    async def test_query_1_cash_position_e2e(self):
        """Test: What is the total cash position for household HH001?"""
        query = BusinessQuery(
            query_id="e2e-001",
            question="What is the total cash position for household HH001?",
            context={"household_id": "HH001"}
        )
        
        # Mock SQL agent response
        sql_response = A2AResponse(
            request_id="e2e-001",
            agent="nl2sql",
            data={"total_cash": 125000.00, "household_id": "HH001"},
            metadata={"sql_query": "SELECT SUM(cash_balance) FROM accounts WHERE household_id = 'HH001'"},
            success=True,
            citations=["Database: accounts table"]
        )
        
        # Mock orchestrator response composition
        with patch.object(self.orchestrator.broker, 'publish_request') as mock_publish, \
             patch.object(self.orchestrator.broker, 'wait_for_response', return_value=sql_response), \
             patch.object(self.orchestrator.composer, 'compose_response', 
                         return_value="The total cash position for household HH001 is $125,000."):
            
            final_response = None
            async for chunk in self.orchestrator.process_query(query):
                if chunk.get("type") == "final_response":
                    final_response = chunk.get("content")
                    break
            
            assert final_response is not None
            assert "$125,000" in final_response
            assert "HH001" in final_response
    
    async def test_query_2_top_households_e2e(self):
        """Test: Show me the top 3 households by assets under management"""
        query = BusinessQuery(
            query_id="e2e-002", 
            question="Show me the top 3 households by assets under management",
            context={}
        )
        
        # Mock SQL response with top households
        sql_response = A2AResponse(
            request_id="e2e-002",
            agent="nl2sql",
            data=[
                {"household_id": "HH001", "total_assets": 2400000.00, "primary_advisor": "Jane Smith"},
                {"household_id": "HH002", "total_assets": 1800000.00, "primary_advisor": "Bob Johnson"},
                {"household_id": "HH003", "total_assets": 1500000.00, "primary_advisor": "Alice Brown"}
            ],
            metadata={"sql_query": "SELECT TOP 3 household_id, total_assets, primary_advisor FROM households ORDER BY total_assets DESC"},
            success=True,
            citations=["Database: households table"]
        )
        
        with patch.object(self.orchestrator.broker, 'publish_request'), \
             patch.object(self.orchestrator.broker, 'wait_for_response', return_value=sql_response), \
             patch.object(self.orchestrator.composer, 'compose_response',
                         return_value="Top 3 households: HH001 ($2.4M), HH002 ($1.8M), HH003 ($1.5M)"):
            
            final_response = None
            async for chunk in self.orchestrator.process_query(query):
                if chunk.get("type") == "final_response":
                    final_response = chunk.get("content")
                    break
            
            assert final_response is not None
            assert "HH001" in final_response
            assert "$2.4M" in final_response or "2400000" in final_response
    
    async def test_query_3_rmd_due_e2e(self):
        """Test: Which clients have RMDs due this year?"""
        query = BusinessQuery(
            query_id="e2e-003",
            question="Which clients have RMDs due this year?",
            context={}
        )
        
        # Mock SQL response for RMDs
        sql_response = A2AResponse(
            request_id="e2e-003",
            agent="nl2sql",
            data=[
                {"household_id": "HH001", "client_name": "John Doe", "rmd_amount": 45000.00, "account_id": "IRA001"},
                {"household_id": "HH003", "client_name": "Mary Johnson", "rmd_amount": 32000.00, "account_id": "IRA003"}
            ],
            metadata={"sql_query": "SELECT * FROM rmd_requirements WHERE year = 2024"},
            success=True,
            citations=["Database: rmd_requirements table"]
        )
        
        with patch.object(self.orchestrator.broker, 'publish_request'), \
             patch.object(self.orchestrator.broker, 'wait_for_response', return_value=sql_response), \
             patch.object(self.orchestrator.composer, 'compose_response',
                         return_value="Clients with RMDs due: John Doe ($45,000), Mary Johnson ($32,000)"):
            
            final_response = None
            async for chunk in self.orchestrator.process_query(query):
                if chunk.get("type") == "final_response":
                    final_response = chunk.get("content")
                    break
            
            assert final_response is not None
            assert "John Doe" in final_response
            assert "45,000" in final_response
    
    async def test_query_4_crm_notes_e2e(self):
        """Test: What are the recent CRM notes for John Doe?"""
        query = BusinessQuery(
            query_id="e2e-004",
            question="What are the recent CRM notes for John Doe?",
            context={"client_name": "John Doe"}
        )
        
        # Mock vector search response
        vector_response = A2AResponse(
            request_id="e2e-004",
            agent="vector",
            data=[
                {
                    "note_id": "NOTE001",
                    "client_name": "John Doe",
                    "advisor": "Jane Smith",
                    "note_text": "Discussed retirement planning options and 401k rollover strategies",
                    "created_date": "2024-01-15T10:30:00Z",
                    "tags": ["retirement", "401k"]
                },
                {
                    "note_id": "NOTE002", 
                    "client_name": "John Doe",
                    "advisor": "Jane Smith",
                    "note_text": "Client expressed concerns about market volatility impact",
                    "created_date": "2024-01-10T14:20:00Z",
                    "tags": ["market", "volatility"]
                }
            ],
            metadata={"search_query": "client_name:John Doe", "total_results": 2},
            success=True,
            citations=["CRM Notes: John Doe"]
        )
        
        with patch.object(self.orchestrator.broker, 'publish_request'), \
             patch.object(self.orchestrator.broker, 'wait_for_response', return_value=vector_response), \
             patch.object(self.orchestrator.composer, 'compose_response',
                         return_value="Recent CRM notes for John Doe: retirement planning discussion, market volatility concerns"):
            
            final_response = None
            async for chunk in self.orchestrator.process_query(query):
                if chunk.get("type") == "final_response":
                    final_response = chunk.get("content")
                    break
            
            assert final_response is not None
            assert "John Doe" in final_response
            assert "retirement" in final_response.lower()
    
    async def test_query_5_plan_performance_e2e(self):
        """Test: How did the Conservative Growth portfolio perform last quarter?"""
        query = BusinessQuery(
            query_id="e2e-005", 
            question="How did the Conservative Growth portfolio perform last quarter?",
            context={"portfolio": "Conservative Growth", "period": "quarter"}
        )
        
        # Mock API response
        api_response = A2AResponse(
            request_id="e2e-005",
            agent="api",
            data={
                "portfolio_name": "Conservative Growth",
                "quarter_return": 2.1,
                "ytd_return": 8.5,
                "benchmark_return": 1.8,
                "alpha": 0.3,
                "beta": 0.85
            },
            metadata={"api_source": "plan_performance"},
            success=True,
            citations=["Plan Performance API"]
        )
        
        with patch.object(self.orchestrator.broker, 'publish_request'), \
             patch.object(self.orchestrator.broker, 'wait_for_response', return_value=api_response), \
             patch.object(self.orchestrator.composer, 'compose_response',
                         return_value="Conservative Growth portfolio returned 2.1% last quarter, outperforming benchmark by 0.3%"):
            
            final_response = None
            async for chunk in self.orchestrator.process_query(query):
                if chunk.get("type") == "final_response":
                    final_response = chunk.get("content")
                    break
            
            assert final_response is not None
            assert "2.1%" in final_response
            assert "Conservative Growth" in final_response
    
    async def test_query_6_allocation_breakdown_e2e(self):
        """Test: Show allocation breakdown for account ACC001"""
        query = BusinessQuery(
            query_id="e2e-006",
            question="Show allocation breakdown for account ACC001",
            context={"account_id": "ACC001"}
        )
        
        # Mock API response for allocation
        api_response = A2AResponse(
            request_id="e2e-006",
            agent="api",
            data={
                "account_id": "ACC001",
                "total_value": 800000.00,
                "allocations": [
                    {"asset_class": "Stocks", "percentage": 60.0, "value": 480000.00},
                    {"asset_class": "Bonds", "percentage": 30.0, "value": 240000.00}, 
                    {"asset_class": "Cash", "percentage": 10.0, "value": 80000.00}
                ]
            },
            metadata={"api_source": "plan_performance"},
            success=True,
            citations=["Plan Performance API"]
        )
        
        with patch.object(self.orchestrator.broker, 'publish_request'), \
             patch.object(self.orchestrator.broker, 'wait_for_response', return_value=api_response), \
             patch.object(self.orchestrator.composer, 'compose_response',
                         return_value="Account ACC001 allocation: 60% Stocks ($480k), 30% Bonds ($240k), 10% Cash ($80k)"):
            
            final_response = None 
            async for chunk in self.orchestrator.process_query(query):
                if chunk.get("type") == "final_response":
                    final_response = chunk.get("content")
                    break
            
            assert final_response is not None
            assert "ACC001" in final_response
            assert "60%" in final_response
            assert "480k" in final_response or "480000" in final_response
    
    async def test_query_7_pershing_positions_e2e(self):
        """Test: What Pershing positions are held by household HH001?"""
        query = BusinessQuery(
            query_id="e2e-007",
            question="What Pershing positions are held by household HH001?",
            context={"household_id": "HH001"}
        )
        
        # Mock API response for Pershing positions
        api_response = A2AResponse(
            request_id="e2e-007", 
            agent="api",
            data={
                "household_id": "HH001",
                "positions": [
                    {"symbol": "AAPL", "quantity": 1000, "market_value": 185000.00, "cusip": "037833100"},
                    {"symbol": "VTSAX", "quantity": 5000, "market_value": 595000.00, "cusip": "922908769"}
                ]
            },
            metadata={"api_source": "pershing"},
            success=True,
            citations=["Pershing API"]
        )
        
        with patch.object(self.orchestrator.broker, 'publish_request'), \
             patch.object(self.orchestrator.broker, 'wait_for_response', return_value=api_response), \
             patch.object(self.orchestrator.composer, 'compose_response',
                         return_value="HH001 Pershing positions: AAPL (1,000 shares, $185k), VTSAX (5,000 shares, $595k)"):
            
            final_response = None
            async for chunk in self.orchestrator.process_query(query):
                if chunk.get("type") == "final_response":
                    final_response = chunk.get("content")
                    break
            
            assert final_response is not None
            assert "HH001" in final_response
            assert "AAPL" in final_response
            assert "185k" in final_response or "185000" in final_response
    
    async def test_query_8_high_cash_households_e2e(self):
        """Test: Which households have cash positions above $100k?"""
        query = BusinessQuery(
            query_id="e2e-008",
            question="Which households have cash positions above $100k?",
            context={"threshold": 100000}
        )
        
        # Mock SQL response
        sql_response = A2AResponse(
            request_id="e2e-008",
            agent="nl2sql",
            data=[
                {"household_id": "HH001", "total_cash": 125000.00, "primary_advisor": "Jane Smith"},
                {"household_id": "HH002", "total_cash": 150000.00, "primary_advisor": "Bob Johnson"},
                {"household_id": "HH004", "total_cash": 110000.00, "primary_advisor": "Carol White"}
            ],
            metadata={"sql_query": "SELECT household_id, SUM(cash_balance) as total_cash FROM accounts GROUP BY household_id HAVING SUM(cash_balance) > 100000"},
            success=True,
            citations=["Database: accounts table"]
        )
        
        with patch.object(self.orchestrator.broker, 'publish_request'), \
             patch.object(self.orchestrator.broker, 'wait_for_response', return_value=sql_response), \
             patch.object(self.orchestrator.composer, 'compose_response',
                         return_value="Households with cash > $100k: HH001 ($125k), HH002 ($150k), HH004 ($110k)"):
            
            final_response = None
            async for chunk in self.orchestrator.process_query(query):
                if chunk.get("type") == "final_response":
                    final_response = chunk.get("content")
                    break
            
            assert final_response is not None
            assert "HH001" in final_response
            assert "125k" in final_response or "125000" in final_response
    
    async def test_query_9_executive_summary_e2e(self):
        """Test: Generate an executive summary for household HH001 (multi-agent)"""
        query = BusinessQuery(
            query_id="e2e-009",
            question="Generate an executive summary for household HH001",
            context={"household_id": "HH001"}
        )
        
        # Mock responses from multiple agents
        sql_response = A2AResponse(
            request_id="e2e-009-sql",
            agent="nl2sql",
            data={"household_id": "HH001", "total_assets": 2400000.00, "total_cash": 125000.00},
            metadata={},
            success=True,
            citations=["Database: households, accounts"]
        )
        
        vector_response = A2AResponse(
            request_id="e2e-009-vector",
            agent="vector",
            data=[
                {"note_text": "Client concerned about market volatility", "created_date": "2024-01-15"},
                {"note_text": "Discussed retirement planning strategies", "created_date": "2024-01-10"}
            ],
            metadata={},
            success=True,
            citations=["CRM Notes: HH001"]
        )
        
        api_response = A2AResponse(
            request_id="e2e-009-api",
            agent="api",
            data={"ytd_performance": 8.5, "portfolio": "Conservative Growth", "allocation": {"stocks": 60, "bonds": 40}},
            metadata={},
            success=True,
            citations=["Plan Performance API", "Pershing API"]
        )
        
        # Mock multi-agent orchestration
        with patch.object(self.orchestrator.broker, 'publish_request'), \
             patch.object(self.orchestrator.broker, 'wait_for_response', 
                         side_effect=[sql_response, vector_response, api_response]), \
             patch.object(self.orchestrator.composer, 'compose_response',
                         return_value="Executive Summary for HH001: $2.4M total assets, 8.5% YTD return, recent focus on retirement planning and market volatility concerns"):
            
            final_response = None
            async for chunk in self.orchestrator.process_query(query):
                if chunk.get("type") == "final_response":
                    final_response = chunk.get("content")
                    break
            
            assert final_response is not None
            assert "HH001" in final_response
            assert "2.4M" in final_response or "2400000" in final_response
            assert "8.5%" in final_response
            assert "retirement" in final_response.lower()
    
    async def test_streaming_response_chunks(self):
        """Test that responses are properly streamed with status updates."""
        query = BusinessQuery(
            query_id="e2e-stream",
            question="What is the cash position for HH001?",
            context={"household_id": "HH001"}
        )
        
        sql_response = A2AResponse(
            request_id="e2e-stream",
            agent="nl2sql", 
            data={"total_cash": 125000.00},
            metadata={},
            success=True,
            citations=["Database"]
        )
        
        with patch.object(self.orchestrator.broker, 'publish_request'), \
             patch.object(self.orchestrator.broker, 'wait_for_response', return_value=sql_response), \
             patch.object(self.orchestrator.composer, 'compose_response', return_value="Cash position: $125,000"):
            
            chunks = []
            async for chunk in self.orchestrator.process_query(query):
                chunks.append(chunk)
            
            # Should receive multiple chunks with different types
            chunk_types = [chunk.get("type") for chunk in chunks]
            assert "status" in chunk_types
            assert "final_response" in chunk_types
            
            # Final response should contain the answer
            final_chunk = next(chunk for chunk in chunks if chunk.get("type") == "final_response")
            assert "$125,000" in final_chunk.get("content", "")
    
    async def test_error_handling_e2e(self):
        """Test end-to-end error handling when agents fail."""
        query = BusinessQuery(
            query_id="e2e-error",
            question="This query will cause an error",
            context={}
        )
        
        # Mock failed response
        error_response = A2AResponse(
            request_id="e2e-error", 
            agent="nl2sql",
            data={},
            metadata={},
            success=False,
            error="Unable to process query"
        )
        
        with patch.object(self.orchestrator.broker, 'publish_request'), \
             patch.object(self.orchestrator.broker, 'wait_for_response', return_value=error_response):
            
            error_received = False
            async for chunk in self.orchestrator.process_query(query):
                if chunk.get("type") == "error":
                    error_received = True
                    assert "unable to process" in chunk.get("message", "").lower()
                    break
            
            assert error_received