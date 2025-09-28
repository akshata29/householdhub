"""
Script to delete and recreate the AI Search index with correct schema
"""

import os
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Get configuration
    search_endpoint = os.getenv('AI_SEARCH_ENDPOINT')
    search_key = os.getenv('AI_SEARCH_KEY')
    index_name = os.getenv('AI_SEARCH_INDEX_NAME', 'crm-notes')
    
    # Initialize client
    credential = AzureKeyCredential(search_key)
    index_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)
    
    try:
        # Check if index exists
        try:
            existing_index = index_client.get_index(index_name)
            print(f"Found existing index: {index_name}")
            print("Current fields:")
            for field in existing_index.fields:
                print(f"  - {field.name}: {field.type}")
            
            # Delete the index
            index_client.delete_index(index_name)
            print(f"✅ Deleted index: {index_name}")
            
        except Exception as e:
            if "not found" in str(e).lower():
                print(f"Index {index_name} does not exist")
            else:
                print(f"Error checking index: {e}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()