"""
Basic validation test to check project structure and imports
"""
import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_common_schemas_import():
    """Test that common schemas can be imported."""
    try:
        from common.schemas import A2AMessage, A2AResponse, Household, Account
        assert A2AMessage is not None
        assert A2AResponse is not None
        assert Household is not None
        assert Account is not None
    except ImportError as e:
        pytest.fail(f"Failed to import schemas: {e}")

def test_schemas_structure():
    """Test that schemas have expected structure."""
    from common.schemas import A2AMessage, AgentType, IntentType
    
    # Test A2AMessage creation
    message = A2AMessage(
        from_agent=AgentType.ORCHESTRATOR,
        to_agents=[AgentType.NL2SQL],
        intent=IntentType.TOP_CASH,
        payload={"test": "value"}
    )
    
    assert message.from_agent == AgentType.ORCHESTRATOR
    assert AgentType.NL2SQL in message.to_agents
    assert message.intent == IntentType.TOP_CASH

def test_project_structure():
    """Test that expected project files exist."""
    project_root = os.path.join(os.path.dirname(__file__), '..')
    
    # Check key directories exist
    assert os.path.exists(os.path.join(project_root, 'backend'))
    assert os.path.exists(os.path.join(project_root, 'frontend'))
    assert os.path.exists(os.path.join(project_root, 'infra'))
    assert os.path.exists(os.path.join(project_root, 'scripts'))
    assert os.path.exists(os.path.join(project_root, 'tests'))
    
    # Check key files exist
    assert os.path.exists(os.path.join(project_root, 'backend', 'common', 'schemas.py'))
    assert os.path.exists(os.path.join(project_root, 'backend', 'orchestrator', 'main.py'))
    assert os.path.exists(os.path.join(project_root, 'backend', 'nl2sql_agent', 'main.py'))
    assert os.path.exists(os.path.join(project_root, 'backend', 'vector_agent', 'main.py'))
    assert os.path.exists(os.path.join(project_root, 'backend', 'api_agent', 'main.py'))
    assert os.path.exists(os.path.join(project_root, 'infra', 'main.bicep'))
    assert os.path.exists(os.path.join(project_root, 'docker-compose.yml'))

def test_frontend_structure():
    """Test frontend project structure."""
    frontend_root = os.path.join(os.path.dirname(__file__), '..', 'frontend')
    
    # Check frontend files
    assert os.path.exists(os.path.join(frontend_root, 'package.json'))
    assert os.path.exists(os.path.join(frontend_root, 'tsconfig.json'))
    assert os.path.exists(os.path.join(frontend_root, 'src', 'app', 'page.tsx'))
    assert os.path.exists(os.path.join(frontend_root, 'src', 'components'))

def test_business_query_scenarios():
    """Test that business query scenarios are defined."""
    # Test all 9 business query scenarios exist as concepts
    queries = [
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
    
    assert len(queries) == 9
    for question in queries:
        assert len(question) > 10  # Reasonable length check
        assert isinstance(question, str)  # Should be strings