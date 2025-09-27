"""
Test configuration and fixtures for WealthOps MVP
"""
import pytest
import asyncio
import os
from unittest.mock import AsyncMock, MagicMock
from typing import AsyncGenerator

# Pytest configuration
pytest_plugins = ['pytest_asyncio']

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_azure_credentials():
    """Mock Azure credentials for testing."""
    return {
        "tenant_id": "test-tenant-id",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret"
    }

@pytest.fixture
def mock_database_config():
    """Mock database configuration."""
    return {
        "server": "test-server.database.windows.net",
        "database": "test-wealthops-db",
        "driver": "{ODBC Driver 18 for SQL Server}"
    }

@pytest.fixture
def mock_service_bus_config():
    """Mock Service Bus configuration."""
    return {
        "namespace": "test-wealthops-sb.servicebus.windows.net",
        "topic": "agent-messages"
    }

@pytest.fixture
def mock_ai_search_config():
    """Mock AI Search configuration."""
    return {
        "endpoint": "https://test-wealthops-search.search.windows.net",
        "index": "crm-notes"
    }

@pytest.fixture
def sample_household_data():
    """Sample household data for testing."""
    return {
        "household_id": "HH001",
        "primary_advisor": "Jane Smith",
        "total_assets": 2400000.00,
        "accounts": [
            {"account_id": "ACC001", "type": "401k", "balance": 800000.00},
            {"account_id": "ACC002", "type": "IRA", "balance": 600000.00},
            {"account_id": "ACC003", "type": "Taxable", "balance": 1000000.00}
        ]
    }

@pytest.fixture
def sample_business_queries():
    """Sample business queries that the system should handle."""
    return [
        "What is the total cash position for household HH001?",
        "Show me the top 3 households by assets under management",
        "Which clients have RMDs due this year?",
        "What are the recent CRM notes for John Doe?",
        "How did the Conservative Growth portfolio perform last quarter?",
        "Show allocation breakdown for account ACC001",
        "What Pershing positions are held by household HH001?",
        "Which households have cash positions above $100k?",
        "Generate an executive summary for household HH001"
    ]

@pytest.fixture
async def mock_a2a_broker():
    """Mock A2A broker for testing."""
    broker = AsyncMock()
    broker.publish_request = AsyncMock()
    broker.wait_for_response = AsyncMock()
    broker.subscribe_to_requests = AsyncMock()
    return broker

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    client = AsyncMock()
    client.chat.completions.create = AsyncMock()
    return client

@pytest.fixture
def mock_search_client():
    """Mock Azure AI Search client."""
    client = AsyncMock()
    client.search = AsyncMock()
    client.upload_documents = AsyncMock()
    return client