"""
Tests for the API Agent - Mock external service APIs (Plan Performance, Pershing)
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
from datetime import datetime, timedelta

# Import the API agent components
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from api_agent.main import APIAgent, SyntheticDataGenerator, PlanPerformanceClient, PershingClient
from common.schemas import A2ARequest, BusinessQuery

class TestSyntheticDataGenerator:
    """Test synthetic data generation for mock APIs."""
    
    def setup_method(self):
        self.generator = SyntheticDataGenerator()
    
    def test_generate_portfolio_performance(self):
        """Test portfolio performance data generation."""
        portfolio_name = "Conservative Growth"
        performance = self.generator.generate_portfolio_performance(portfolio_name)
        
        assert "portfolio_name" in performance
        assert performance["portfolio_name"] == "Conservative Growth"
        assert "ytd_return" in performance
        assert "quarter_return" in performance
        assert "month_return" in performance
        assert isinstance(performance["ytd_return"], float)
        assert -50.0 <= performance["ytd_return"] <= 50.0  # Reasonable range
    
    def test_generate_allocation_data(self):
        """Test allocation data generation."""
        account_id = "ACC001"
        allocation = self.generator.generate_allocation_data(account_id)
        
        assert "account_id" in allocation
        assert allocation["account_id"] == "ACC001"
        assert "allocations" in allocation
        assert isinstance(allocation["allocations"], list)
        
        # Check that allocations sum to approximately 100%
        total_allocation = sum(alloc["percentage"] for alloc in allocation["allocations"])
        assert 99.0 <= total_allocation <= 101.0
    
    def test_generate_pershing_positions(self):
        """Test Pershing positions data generation."""
        household_id = "HH001"
        positions = self.generator.generate_pershing_positions(household_id)
        
        assert "household_id" in positions
        assert positions["household_id"] == "HH001"
        assert "positions" in positions
        assert isinstance(positions["positions"], list)
        assert len(positions["positions"]) > 0
        
        # Check position structure
        first_position = positions["positions"][0]
        assert "symbol" in first_position
        assert "quantity" in first_position
        assert "market_value" in first_position
        assert "cusip" in first_position
    
    def test_time_based_variance(self):
        """Test that data varies over time periods."""
        portfolio_name = "Aggressive Growth"
        
        # Generate performance for different time periods
        perf1 = self.generator.generate_portfolio_performance(portfolio_name, days_ago=0)
        perf2 = self.generator.generate_portfolio_performance(portfolio_name, days_ago=30) 
        perf3 = self.generator.generate_portfolio_performance(portfolio_name, days_ago=90)
        
        # Should have different values for different time periods
        returns1 = [perf1["ytd_return"], perf1["quarter_return"], perf1["month_return"]]
        returns2 = [perf2["ytd_return"], perf2["quarter_return"], perf2["month_return"]]
        returns3 = [perf3["ytd_return"], perf3["quarter_return"], perf3["month_return"]]
        
        assert returns1 != returns2 or returns2 != returns3
    
    def test_consistent_data_for_same_inputs(self):
        """Test that same inputs generate consistent data."""
        account_id = "ACC123"
        
        alloc1 = self.generator.generate_allocation_data(account_id)
        alloc2 = self.generator.generate_allocation_data(account_id)
        
        # Should be identical for same account_id
        assert alloc1 == alloc2

class TestPlanPerformanceClient:
    """Test Plan Performance API client."""
    
    def setup_method(self):
        with patch('backend.api_agent.main.SyntheticDataGenerator'):
            self.client = PlanPerformanceClient()
    
    async def test_get_portfolio_performance(self):
        """Test getting portfolio performance data."""
        portfolio_name = "Conservative Growth"
        
        mock_performance = {
            "portfolio_name": "Conservative Growth",
            "ytd_return": 8.5,
            "quarter_return": 2.1,
            "month_return": 0.8,
            "inception_return": 45.2,
            "benchmark_return": 7.9,
            "alpha": 0.6,
            "beta": 0.85,
            "sharpe_ratio": 1.2
        }
        
        with patch.object(self.client.data_generator, 'generate_portfolio_performance', return_value=mock_performance):
            result = await self.client.get_portfolio_performance(portfolio_name)
            
            assert result["portfolio_name"] == "Conservative Growth"
            assert result["ytd_return"] == 8.5
            assert "benchmark_return" in result
    
    async def test_get_allocation_breakdown(self):
        """Test getting allocation breakdown."""
        account_id = "ACC001"
        
        mock_allocation = {
            "account_id": "ACC001",
            "total_value": 800000.00,
            "allocations": [
                {"asset_class": "Stocks", "percentage": 60.0, "value": 480000.00},
                {"asset_class": "Bonds", "percentage": 30.0, "value": 240000.00},
                {"asset_class": "Cash", "percentage": 10.0, "value": 80000.00}
            ]
        }
        
        with patch.object(self.client.data_generator, 'generate_allocation_data', return_value=mock_allocation):
            result = await self.client.get_allocation_breakdown(account_id)
            
            assert result["account_id"] == "ACC001"
            assert len(result["allocations"]) == 3
            assert result["total_value"] == 800000.00

class TestPershingClient:
    """Test Pershing API client."""
    
    def setup_method(self):
        with patch('backend.api_agent.main.SyntheticDataGenerator'):
            self.client = PershingClient()
    
    async def test_get_household_positions(self):
        """Test getting household positions."""
        household_id = "HH001"
        
        mock_positions = {
            "household_id": "HH001",
            "as_of_date": "2024-01-25",
            "positions": [
                {
                    "account_id": "ACC001",
                    "symbol": "AAPL",
                    "cusip": "037833100", 
                    "quantity": 1000,
                    "market_value": 185000.00,
                    "cost_basis": 150000.00
                },
                {
                    "account_id": "ACC002",
                    "symbol": "VTSAX",
                    "cusip": "922908769",
                    "quantity": 5000,
                    "market_value": 595000.00, 
                    "cost_basis": 520000.00
                }
            ]
        }
        
        with patch.object(self.client.data_generator, 'generate_pershing_positions', return_value=mock_positions):
            result = await self.client.get_household_positions(household_id)
            
            assert result["household_id"] == "HH001"
            assert len(result["positions"]) == 2
            assert result["positions"][0]["symbol"] == "AAPL"
    
    async def test_get_account_positions(self):
        """Test getting positions for specific account."""
        account_id = "ACC001"
        
        mock_positions = {
            "account_id": "ACC001",
            "positions": [
                {
                    "symbol": "MSFT",
                    "cusip": "594918104",
                    "quantity": 500,
                    "market_value": 195000.00
                }
            ]
        }
        
        with patch.object(self.client.data_generator, 'generate_account_positions', return_value=mock_positions):
            result = await self.client.get_account_positions(account_id)
            
            assert result["account_id"] == "ACC001"
            assert result["positions"][0]["symbol"] == "MSFT"

@pytest.mark.asyncio
class TestAPIAgent:
    """Test the main API agent functionality."""
    
    def setup_method(self):
        with patch('backend.api_agent.main.A2ABroker'), \
             patch('backend.api_agent.main.SyntheticDataGenerator'):
            self.agent = APIAgent()
    
    async def test_process_plan_performance_request(self):
        """Test processing plan performance request."""
        request = A2ARequest(
            request_id="test-001",
            source_agent="orchestrator",
            target_agent="api", 
            query=BusinessQuery(
                query_id="test-001",
                question="How did the Conservative Growth portfolio perform last quarter?",
                context={"portfolio": "Conservative Growth", "period": "quarter"}
            ),
            metadata={}
        )
        
        mock_performance = {
            "portfolio_name": "Conservative Growth",
            "quarter_return": 2.1,
            "ytd_return": 8.5,
            "benchmark_return": 1.8
        }
        
        with patch.object(self.agent.plan_performance_client, 'get_portfolio_performance', return_value=mock_performance):
            response = await self.agent.process_request(request)
            
            assert response.success is True
            assert response.data["portfolio_name"] == "Conservative Growth"
            assert response.data["quarter_return"] == 2.1
            assert "Plan Performance API" in response.citations[0]
    
    async def test_process_allocation_request(self):
        """Test processing allocation breakdown request."""
        request = A2ARequest(
            request_id="test-002",
            source_agent="orchestrator",
            target_agent="api",
            query=BusinessQuery(
                query_id="test-002", 
                question="Show allocation breakdown for account ACC001",
                context={"account_id": "ACC001"}
            ),
            metadata={}
        )
        
        mock_allocation = {
            "account_id": "ACC001",
            "allocations": [
                {"asset_class": "Stocks", "percentage": 60.0},
                {"asset_class": "Bonds", "percentage": 40.0}
            ]
        }
        
        with patch.object(self.agent.plan_performance_client, 'get_allocation_breakdown', return_value=mock_allocation):
            response = await self.agent.process_request(request)
            
            assert response.success is True
            assert response.data["account_id"] == "ACC001"
            assert len(response.data["allocations"]) == 2
    
    async def test_process_pershing_positions_request(self):
        """Test processing Pershing positions request."""
        request = A2ARequest(
            request_id="test-003",
            source_agent="orchestrator",
            target_agent="api",
            query=BusinessQuery(
                query_id="test-003",
                question="What Pershing positions are held by household HH001?", 
                context={"household_id": "HH001"}
            ),
            metadata={}
        )
        
        mock_positions = {
            "household_id": "HH001",
            "positions": [
                {"symbol": "AAPL", "quantity": 1000, "market_value": 185000.00},
                {"symbol": "VTSAX", "quantity": 5000, "market_value": 595000.00}
            ]
        }
        
        with patch.object(self.agent.pershing_client, 'get_household_positions', return_value=mock_positions):
            response = await self.agent.process_request(request)
            
            assert response.success is True
            assert response.data["household_id"] == "HH001"
            assert len(response.data["positions"]) == 2
            assert "Pershing API" in response.citations[0]
    
    async def test_process_unknown_api_request(self):
        """Test handling of unknown API requests."""
        request = A2ARequest(
            request_id="test-004",
            source_agent="orchestrator",
            target_agent="api",
            query=BusinessQuery(
                query_id="test-004",
                question="Get data from unknown external API",
                context={}
            ),
            metadata={}
        )
        
        response = await self.agent.process_request(request)
        
        assert response.success is False
        assert "unable to determine" in response.error.lower()
    
    async def test_process_api_error(self):
        """Test handling of API errors."""
        request = A2ARequest(
            request_id="test-005",
            source_agent="orchestrator",
            target_agent="api",
            query=BusinessQuery(
                query_id="test-005", 
                question="Get portfolio performance",
                context={"portfolio": "Test Portfolio"}
            ),
            metadata={}
        )
        
        with patch.object(self.agent.plan_performance_client, 'get_portfolio_performance', side_effect=Exception("API unavailable")):
            response = await self.agent.process_request(request)
            
            assert response.success is False
            assert "api unavailable" in response.error.lower()
    
    async def test_request_routing_logic(self):
        """Test that requests are routed to correct API clients."""
        # Plan Performance request
        perf_request = A2ARequest(
            request_id="test-perf",
            source_agent="orchestrator", 
            target_agent="api",
            query=BusinessQuery(
                query_id="test-perf",
                question="Portfolio performance data",
                context={"request_type": "performance"}
            ),
            metadata={}
        )
        
        # Pershing request
        pershing_request = A2ARequest(
            request_id="test-pershing",
            source_agent="orchestrator",
            target_agent="api", 
            query=BusinessQuery(
                query_id="test-pershing",
                question="Pershing position data",
                context={"request_type": "positions"}
            ),
            metadata={}
        )
        
        with patch.object(self.agent.plan_performance_client, 'get_portfolio_performance') as mock_perf, \
             patch.object(self.agent.pershing_client, 'get_household_positions') as mock_pershing:
            
            mock_perf.return_value = {"portfolio_name": "Test"}
            mock_pershing.return_value = {"household_id": "HH001", "positions": []}
            
            # Process performance request
            await self.agent.process_request(perf_request)
            mock_perf.assert_called_once()
            
            # Process Pershing request  
            await self.agent.process_request(pershing_request)
            mock_pershing.assert_called_once()
    
    async def test_data_consistency(self):
        """Test that repeated requests return consistent data."""
        request = A2ARequest(
            request_id="test-consistency",
            source_agent="orchestrator",
            target_agent="api",
            query=BusinessQuery(
                query_id="test-consistency",
                question="Get allocation for ACC001", 
                context={"account_id": "ACC001"}
            ),
            metadata={}
        )
        
        mock_allocation = {
            "account_id": "ACC001",
            "allocations": [{"asset_class": "Stocks", "percentage": 70.0}]
        }
        
        with patch.object(self.agent.plan_performance_client, 'get_allocation_breakdown', return_value=mock_allocation):
            response1 = await self.agent.process_request(request)
            response2 = await self.agent.process_request(request)
            
            assert response1.data == response2.data