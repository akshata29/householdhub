"""
Tests for the NL2SQL Agent - natural language to SQL translation using MCP
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

# Import the NL2SQL components
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from nl2sql_agent.main import NL2SQLAgent, MCPSQLClient, SQLPatternMatcher
from common.schemas import A2ARequest, BusinessQuery

class TestSQLPatternMatcher:
    """Test SQL pattern matching and template logic."""
    
    def setup_method(self):
        self.matcher = SQLPatternMatcher()
    
    def test_cash_position_pattern(self):
        """Test pattern matching for cash position queries."""
        query = "What is the total cash position for household HH001?"
        
        pattern = self.matcher.match_pattern(query)
        
        assert pattern is not None
        assert pattern["type"] == "cash_position"
        assert "household_id" in pattern["params"]
        
        sql = self.matcher.generate_sql(pattern)
        assert "SELECT" in sql.upper()
        assert "CASH" in sql.upper()
        assert "SUM" in sql.upper()
    
    def test_top_households_pattern(self):
        """Test pattern matching for top households queries."""
        query = "Show me the top 3 households by assets under management"
        
        pattern = self.matcher.match_pattern(query)
        
        assert pattern is not None
        assert pattern["type"] == "top_households"
        assert pattern["params"]["limit"] == 3
        
        sql = self.matcher.generate_sql(pattern)
        assert "ORDER BY" in sql.upper()
        assert "TOP 3" in sql.upper() or "LIMIT 3" in sql.upper()
    
    def test_rmd_due_pattern(self):
        """Test pattern matching for RMD queries."""
        query = "Which clients have RMDs due this year?"
        
        pattern = self.matcher.match_pattern(query)
        
        assert pattern is not None
        assert pattern["type"] == "rmd_due"
        
        sql = self.matcher.generate_sql(pattern)
        assert "RMD" in sql.upper() or "REQUIRED_MINIMUM" in sql.upper()
        assert str(2024) in sql  # Current year
    
    def test_account_allocation_pattern(self):
        """Test pattern matching for allocation queries."""
        query = "Show allocation breakdown for account ACC001"
        
        pattern = self.matcher.match_pattern(query)
        
        assert pattern is not None
        assert pattern["type"] == "account_allocation"
        assert pattern["params"]["account_id"] == "ACC001"
        
        sql = self.matcher.generate_sql(pattern)
        assert "ACC001" in sql
        assert "ALLOCATION" in sql.upper() or "POSITION" in sql.upper()
    
    def test_high_cash_pattern(self):
        """Test pattern matching for high cash position queries."""
        query = "Which households have cash positions above $100k?"
        
        pattern = self.matcher.match_pattern(query)
        
        assert pattern is not None
        assert pattern["type"] == "high_cash_households"
        assert pattern["params"]["threshold"] == 100000
        
        sql = self.matcher.generate_sql(pattern)
        assert "100000" in sql
        assert "CASH" in sql.upper()
        assert ">" in sql or "GREATER" in sql.upper()
    
    def test_unknown_pattern(self):
        """Test handling of unknown query patterns."""
        query = "This is a completely random query about unicorns"
        
        pattern = self.matcher.match_pattern(query)
        
        # Should return generic pattern or None
        assert pattern is None or pattern["type"] == "generic"

@pytest.mark.asyncio
class TestMCPSQLClient:
    """Test MCP SQL client functionality."""
    
    def setup_method(self):
        with patch('backend.nl2sql_agent.main.MCPClient'):
            self.client = MCPSQLClient()
    
    async def test_get_schema_info(self):
        """Test schema information retrieval."""
        mock_schema = {
            "tables": [
                {"name": "households", "columns": ["household_id", "primary_advisor", "total_assets"]},
                {"name": "accounts", "columns": ["account_id", "household_id", "account_type", "balance"]},
                {"name": "positions", "columns": ["position_id", "account_id", "symbol", "quantity", "market_value"]}
            ]
        }
        
        with patch.object(self.client, '_call_mcp', return_value=mock_schema):
            schema = await self.client.get_schema_info()
            
            assert "tables" in schema
            assert len(schema["tables"]) == 3
            assert any(table["name"] == "households" for table in schema["tables"])
    
    async def test_execute_query_success(self):
        """Test successful query execution."""
        sql = "SELECT SUM(balance) as total_cash FROM accounts WHERE account_type = 'Cash'"
        
        mock_result = {
            "success": True,
            "data": [{"total_cash": 125000.00}],
            "row_count": 1
        }
        
        with patch.object(self.client, '_call_mcp', return_value=mock_result):
            result = await self.client.execute_query(sql)
            
            assert result["success"] is True
            assert result["data"][0]["total_cash"] == 125000.00
    
    async def test_execute_query_security_check(self):
        """Test security validation of SQL queries."""
        dangerous_sql = "DROP TABLE households; SELECT * FROM accounts"
        
        with pytest.raises(ValueError, match="Potentially dangerous"):
            await self.client.execute_query(dangerous_sql)
    
    async def test_execute_query_error(self):
        """Test error handling in query execution."""
        invalid_sql = "INVALID SQL STATEMENT"
        
        mock_error = {
            "success": False,
            "error": "SQL syntax error",
            "data": []
        }
        
        with patch.object(self.client, '_call_mcp', return_value=mock_error):
            result = await self.client.execute_query(invalid_sql)
            
            assert result["success"] is False
            assert "error" in result

@pytest.mark.asyncio
class TestNL2SQLAgent:
    """Test the main NL2SQL agent functionality."""
    
    def setup_method(self):
        with patch('backend.nl2sql_agent.main.A2ABroker'), \
             patch('backend.nl2sql_agent.main.MCPClient'):
            self.agent = NL2SQLAgent()
    
    async def test_process_cash_position_request(self, sample_household_data):
        """Test processing cash position request."""
        request = A2ARequest(
            request_id="test-001",
            source_agent="orchestrator",
            target_agent="nl2sql",
            query=BusinessQuery(
                query_id="test-001",
                question="What is the total cash position for household HH001?",
                context={"household_id": "HH001"}
            ),
            metadata={}
        )
        
        mock_sql_result = {
            "success": True,
            "data": [{"total_cash": 125000.00}],
            "row_count": 1
        }
        
        with patch.object(self.agent.sql_client, 'execute_query', return_value=mock_sql_result):
            response = await self.agent.process_request(request)
            
            assert response.success is True
            assert response.data["total_cash"] == 125000.00
            assert "Database" in response.citations[0]
    
    async def test_process_top_households_request(self):
        """Test processing top households request."""
        request = A2ARequest(
            request_id="test-002",
            source_agent="orchestrator", 
            target_agent="nl2sql",
            query=BusinessQuery(
                query_id="test-002",
                question="Show me the top 3 households by assets under management",
                context={}
            ),
            metadata={}
        )
        
        mock_sql_result = {
            "success": True,
            "data": [
                {"household_id": "HH001", "total_assets": 2400000.00, "primary_advisor": "Jane Smith"},
                {"household_id": "HH002", "total_assets": 1800000.00, "primary_advisor": "Bob Johnson"},
                {"household_id": "HH003", "total_assets": 1500000.00, "primary_advisor": "Alice Brown"}
            ],
            "row_count": 3
        }
        
        with patch.object(self.agent.sql_client, 'execute_query', return_value=mock_sql_result):
            response = await self.agent.process_request(request)
            
            assert response.success is True
            assert len(response.data) == 3
            assert response.data[0]["household_id"] == "HH001"
            assert response.data[0]["total_assets"] == 2400000.00
    
    async def test_process_rmd_request(self):
        """Test processing RMD due request."""
        request = A2ARequest(
            request_id="test-003",
            source_agent="orchestrator",
            target_agent="nl2sql", 
            query=BusinessQuery(
                query_id="test-003",
                question="Which clients have RMDs due this year?",
                context={}
            ),
            metadata={}
        )
        
        mock_sql_result = {
            "success": True,
            "data": [
                {"household_id": "HH001", "client_name": "John Doe", "rmd_amount": 45000.00, "account_id": "IRA001"},
                {"household_id": "HH003", "client_name": "Mary Johnson", "rmd_amount": 32000.00, "account_id": "IRA003"}
            ],
            "row_count": 2
        }
        
        with patch.object(self.agent.sql_client, 'execute_query', return_value=mock_sql_result):
            response = await self.agent.process_request(request)
            
            assert response.success is True
            assert len(response.data) == 2
            assert response.data[0]["rmd_amount"] == 45000.00
    
    async def test_process_invalid_request(self):
        """Test handling of invalid SQL requests."""
        request = A2ARequest(
            request_id="test-error",
            source_agent="orchestrator",
            target_agent="nl2sql",
            query=BusinessQuery(
                query_id="test-error", 
                question="This query cannot be converted to SQL",
                context={}
            ),
            metadata={}
        )
        
        # Mock pattern matcher returning no match
        with patch.object(self.agent.pattern_matcher, 'match_pattern', return_value=None):
            response = await self.agent.process_request(request)
            
            assert response.success is False
            assert "unable to generate" in response.error.lower()
    
    async def test_process_sql_error(self):
        """Test handling of SQL execution errors."""
        request = A2ARequest(
            request_id="test-sql-error",
            source_agent="orchestrator",
            target_agent="nl2sql",
            query=BusinessQuery(
                query_id="test-sql-error",
                question="What is the cash position for HH001?",
                context={}
            ),
            metadata={}
        )
        
        mock_sql_error = {
            "success": False,
            "error": "Table 'accounts' doesn't exist",
            "data": []
        }
        
        with patch.object(self.agent.sql_client, 'execute_query', return_value=mock_sql_error):
            response = await self.agent.process_request(request)
            
            assert response.success is False
            assert "doesn't exist" in response.error
    
    async def test_security_validation(self):
        """Test SQL security validation."""
        dangerous_queries = [
            "DROP TABLE households",
            "DELETE FROM accounts WHERE 1=1", 
            "UPDATE positions SET market_value = 0",
            "INSERT INTO accounts (account_id) VALUES ('HACK')"
        ]
        
        for dangerous_query in dangerous_queries:
            request = A2ARequest(
                request_id="test-security",
                source_agent="orchestrator",
                target_agent="nl2sql",
                query=BusinessQuery(
                    query_id="test-security",
                    question=dangerous_query,
                    context={}
                ),
                metadata={}
            )
            
            # Should be rejected by security validation
            response = await self.agent.process_request(request)
            assert response.success is False
            assert "security" in response.error.lower() or "dangerous" in response.error.lower()
    
    async def test_schema_caching(self):
        """Test that schema information is properly cached."""
        # First call should fetch schema
        with patch.object(self.agent.sql_client, 'get_schema_info') as mock_get_schema:
            mock_get_schema.return_value = {"tables": []}
            
            await self.agent._ensure_schema_cached()
            assert mock_get_schema.call_count == 1
            
            # Second call should use cache
            await self.agent._ensure_schema_cached()
            assert mock_get_schema.call_count == 1  # Still 1, not 2