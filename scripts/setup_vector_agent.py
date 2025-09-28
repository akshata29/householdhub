"""
Configuration script for Vector Agent setup
This script helps configure the required environment variables and dependencies
"""

import os
import json
import subprocess
import sys
from typing import Dict, Any

def check_python_packages():
    """Check if required Python packages are installed."""
    required_packages = [
        'azure-search-documents',
        'azure-identity',
        'azure-core',
        'openai',
        'pyodbc',
        'fastapi',
        'uvicorn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    else:
        print("✅ All required Python packages are installed")
        return True

def check_environment_variables() -> Dict[str, Any]:
    """Check and validate environment variables."""
    required_vars = {
        'AZURE_SEARCH_ENDPOINT': {
            'description': 'Azure AI Search service endpoint',
            'example': 'https://your-search-service.search.windows.net',
            'required': True
        },
        'AZURE_SEARCH_KEY': {
            'description': 'Azure AI Search admin key (for index creation)',
            'example': 'your-admin-key-here',
            'required': True
        },
        'AZURE_SEARCH_INDEX_NAME': {
            'description': 'Name for the CRM search index',
            'example': 'householdhub-crm-index',
            'required': False,
            'default': 'householdhub-crm-index'
        },
        'AZURE_OPENAI_ENDPOINT': {
            'description': 'Azure OpenAI service endpoint',
            'example': 'https://your-openai-service.openai.azure.com',
            'required': True
        },
        'AZURE_OPENAI_KEY': {
            'description': 'Azure OpenAI API key',
            'example': 'your-openai-key-here',
            'required': True
        },
        'AZURE_OPENAI_API_VERSION': {
            'description': 'Azure OpenAI API version',
            'example': '2024-02-01',
            'required': False,
            'default': '2024-02-01'
        },
        'AZURE_OPENAI_EMBEDDING_DEPLOYMENT': {
            'description': 'Name of your text-embedding-3-small deployment',
            'example': 'text-embedding-3-small',
            'required': True
        },
        'AZURE_OPENAI_CHAT_DEPLOYMENT': {
            'description': 'Name of your GPT deployment for summaries',
            'example': 'gpt-4o',
            'required': True
        }
    }
    
    status = {'missing': [], 'present': [], 'using_default': []}
    
    print("\n🔧 Environment Variable Check:")
    print("=" * 50)
    
    for var_name, var_info in required_vars.items():
        value = os.getenv(var_name)
        
        if value:
            status['present'].append(var_name)
            print(f"✅ {var_name}: {'*' * 20}")  # Mask sensitive values
        elif not var_info.get('required', True):
            default_val = var_info.get('default', '')
            status['using_default'].append((var_name, default_val))
            print(f"⚠️  {var_name}: Using default '{default_val}'")
        else:
            status['missing'].append(var_name)
            print(f"❌ {var_name}: MISSING")
            print(f"   Description: {var_info['description']}")
            print(f"   Example: {var_info['example']}")
    
    return status

def generate_env_template():
    """Generate a .env template file."""
    template = """# Azure AI Search Configuration
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_KEY=your-admin-key-here
AZURE_SEARCH_INDEX_NAME=householdhub-crm-index

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-openai-service.openai.azure.com
AZURE_OPENAI_KEY=your-openai-key-here
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o

# Optional: Database Configuration (if not using Windows Auth)
# DB_CONNECTION_STRING=your-connection-string-here
"""
    
    with open('.env.template', 'w') as f:
        f.write(template)
    
    print(f"\n📄 Created .env.template file")
    print("Copy to .env and fill in your actual values")

def check_database_connection():
    """Check database connectivity."""
    try:
        import pyodbc
        
        # Try to connect to the database
        connection_strings = [
            (
                "Driver={ODBC Driver 17 for SQL Server};"
                "Server=localhost;"
                "Database=householdhub;"
                "Trusted_Connection=yes;"
            ),
            (
                "Driver={ODBC Driver 17 for SQL Server};"
                "Server=(localdb)\\MSSQLLocalDB;"
                "Database=householdhub;"
                "Trusted_Connection=yes;"
            )
        ]
        
        for i, conn_str in enumerate(connection_strings):
            try:
                conn = pyodbc.connect(conn_str)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM Households WHERE IsActive = 1")
                count = cursor.fetchone()[0]
                conn.close()
                
                print(f"✅ Database connection successful")
                print(f"   Found {count} active households")
                return True
                
            except pyodbc.Error as e:
                if i == len(connection_strings) - 1:  # Last attempt
                    print(f"❌ Database connection failed: {e}")
                    return False
                continue
                
    except ImportError:
        print(f"❌ pyodbc package not installed")
        return False

def create_sample_config():
    """Create a sample configuration file for testing."""
    config = {
        "search_endpoint": "https://your-search.search.windows.net",
        "search_key": "your-key",
        "index_name": "householdhub-crm-index",
        "openai_endpoint": "https://your-openai.openai.azure.com",
        "openai_key": "your-key",
        "embedding_model": "text-embedding-3-small",
        "chat_model": "gpt-4o",
        "batch_size": 10
    }
    
    with open('vector_agent_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("📄 Created vector_agent_config.json template")

def print_next_steps(env_status: Dict[str, Any]):
    """Print next steps for setup."""
    print("\n🚀 Next Steps:")
    print("=" * 50)
    
    if env_status['missing']:
        print("1. Set up missing environment variables:")
        for var in env_status['missing']:
            print(f"   - {var}")
        print("\n   You can:")
        print("   a) Set them in your shell: export VAR_NAME=value")
        print("   b) Create a .env file and load it")
        print("   c) Set them in your IDE/deployment environment")
    
    if not os.path.exists('crm_notes_synthetic.json'):
        print("\n2. Generate synthetic CRM data:")
        print("   python scripts/generate_crm_data.py")
    else:
        print("✅ CRM data file exists")
    
    print("\n3. Create AI Search index and ingest data:")
    print("   python scripts/ingest_crm_data.py")
    
    print("\n4. Start the Vector Agent:")
    print("   cd backend/vector_agent")
    print("   python main.py")
    
    print("\n5. Test the Vector Agent:")
    print("   curl http://localhost:8000/health")
    print("   curl http://localhost:8000/index/stats")

def main():
    """Main setup check function."""
    print("🏠 HouseholdHub Vector Agent Setup Check")
    print("=" * 50)
    
    # Check Python packages
    packages_ok = check_python_packages()
    
    # Check environment variables
    env_status = check_environment_variables()
    
    # Check database connection
    print("\n💾 Database Connection Check:")
    print("=" * 50)
    db_ok = check_database_connection()
    
    # Generate template files
    print("\n📄 Template Files:")
    print("=" * 50)
    generate_env_template()
    create_sample_config()
    
    # Print summary
    print("\n📊 Setup Summary:")
    print("=" * 50)
    print(f"Python packages: {'✅' if packages_ok else '❌'}")
    print(f"Environment vars: {'✅' if not env_status['missing'] else '❌'}")
    print(f"Database connection: {'✅' if db_ok else '❌'}")
    
    # Print next steps
    print_next_steps(env_status)
    
    # Overall status
    if packages_ok and not env_status['missing'] and db_ok:
        print("\n🎉 Setup looks good! You're ready to run the Vector Agent.")
    else:
        print("\n⚠️  Some setup items need attention. See above for details.")

if __name__ == "__main__":
    main()