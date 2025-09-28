"""
Synchronous version of AI Search index creation and data ingestion
This version avoids Windows async event loop issues
"""

import json
import logging
import os
from typing import List, Dict, Any
from datetime import datetime
import requests

from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SearchField, SearchFieldDataType, 
    VectorSearch, HnswAlgorithmConfiguration, VectorSearchProfile,
    SemanticConfiguration, SemanticSearch, SemanticField, SemanticPrioritizedFields
)
from azure.core.credentials import AzureKeyCredential
import openai

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configuration
CONFIG = {
    'search_endpoint': os.getenv('AI_SEARCH_ENDPOINT', 'https://your-search-service.search.windows.net'),
    'search_key': os.getenv('AI_SEARCH_KEY', 'your-search-key'),
    'index_name': os.getenv('AI_SEARCH_INDEX_NAME', 'crm-notes'),
    
    'openai_endpoint': os.getenv('AZURE_OPENAI_ENDPOINT', 'https://your-openai-service.openai.azure.com'),
    'openai_key': os.getenv('AZURE_OPENAI_KEY', 'your-openai-key'),
    'openai_api_version': os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-01'),
    'embedding_model': os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 'embedding'),
    
    'input_file': 'crm_notes_synthetic.json',
    'batch_size': 10
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SyncAISearchIndexManager:
    """Synchronous version of AI Search index manager."""
    
    def __init__(self):
        self.search_credential = AzureKeyCredential(CONFIG['search_key'])
        self.search_endpoint = CONFIG['search_endpoint']
        self.index_name = CONFIG['index_name']
        
        # Initialize clients
        self.index_client = SearchIndexClient(
            endpoint=self.search_endpoint,
            credential=self.search_credential
        )
        
        self.search_client = SearchClient(
            endpoint=self.search_endpoint,
            index_name=self.index_name,
            credential=self.search_credential
        )
        
        # Set up OpenAI client
        openai.api_type = "azure"
        openai.api_base = CONFIG['openai_endpoint']
        openai.api_version = CONFIG['openai_api_version']
        openai.api_key = CONFIG['openai_key']
    
    def create_index(self):
        """Create the AI Search index with vector and semantic search capabilities."""
        try:
            logger.info(f"Creating search index: {self.index_name}")
            
            # Define index schema
            fields = [
                SearchField(name="id", type=SearchFieldDataType.String, key=True, searchable=False),
                SearchField(name="household_id", type=SearchFieldDataType.String, filterable=True, searchable=False),
                SearchField(name="household_code", type=SearchFieldDataType.String, filterable=True, searchable=True),
                SearchField(name="account_id", type=SearchFieldDataType.String, filterable=True, searchable=False),
                SearchField(name="text", type=SearchFieldDataType.String, searchable=True, analyzer_name="en.microsoft"),
                SearchField(name="author", type=SearchFieldDataType.String, filterable=True, searchable=True),
                SearchField(name="category", type=SearchFieldDataType.String, filterable=True, searchable=True),
                SearchField(name="created_at", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True),
                SearchField(name="tags", type=SearchFieldDataType.Collection(SearchFieldDataType.String), filterable=True, searchable=True),
                SearchField(
                    name="content_vector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=1536,
                    vector_search_profile_name="default-vector-profile"
                )
            ]
            
            # Vector search configuration
            vector_search = VectorSearch(
                algorithms=[
                    HnswAlgorithmConfiguration(
                        name="default-hnsw",
                        parameters={
                            "m": 4,
                            "efConstruction": 400,
                            "efSearch": 500,
                            "metric": "cosine"
                        }
                    )
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
            
            semantic_search = SemanticSearch(configurations=[semantic_config])
            
            # Create index
            index = SearchIndex(
                name=self.index_name,
                fields=fields,
                vector_search=vector_search,
                semantic_search=semantic_search
            )
            
            try:
                result = self.index_client.create_index(index)
                logger.info(f"Successfully created search index: {self.index_name}")
                return result
            except Exception as e:
                error_msg = str(e).lower()
                if "already exists" in error_msg or "conflict" in error_msg:
                    logger.info(f"Index {self.index_name} already exists")
                elif "quota" in error_msg or "exceeded" in error_msg:
                    logger.warning(f"Index quota exceeded. You may need to delete unused indexes.")
                    raise
                else:
                    logger.error(f"Failed to create index: {e}")
                    raise
                    
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API."""
        try:
            logger.debug(f"Generating embeddings for {len(texts)} texts")
            
            # Use requests to call OpenAI API directly to avoid async issues
            headers = {
                'api-key': CONFIG['openai_key'],
                'Content-Type': 'application/json'
            }
            
            url = f"{CONFIG['openai_endpoint']}/openai/deployments/{CONFIG['embedding_model']}/embeddings?api-version={CONFIG['openai_api_version']}"
            
            data = {
                'input': texts,
                'model': CONFIG['embedding_model']
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            embeddings = [item['embedding'] for item in result['data']]
            
            logger.debug(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def prepare_documents(self, raw_documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare documents for ingestion by generating embeddings."""
        try:
            logger.info(f"Preparing {len(raw_documents)} documents for ingestion")
            
            # Extract texts for embedding generation
            texts = [doc['text'] for doc in raw_documents]
            
            # Generate embeddings in batches
            all_embeddings = []
            for i in range(0, len(texts), CONFIG['batch_size']):
                batch_texts = texts[i:i + CONFIG['batch_size']]
                batch_embeddings = self.generate_embeddings(batch_texts)
                all_embeddings.extend(batch_embeddings)
                logger.info(f"Generated embeddings for batch {i//CONFIG['batch_size'] + 1}")
            
            # Prepare documents with embeddings
            prepared_docs = []
            for doc, embedding in zip(raw_documents, all_embeddings):
                prepared_doc = {
                    'id': doc['id'],
                    'household_id': doc['household_id'],
                    'household_code': doc['household_code'],
                    'account_id': doc.get('account_id'),
                    'text': doc['text'],
                    'author': doc['author'],
                    'category': doc['category'],
                    'created_at': doc['created_at'],
                    'tags': doc['tags'],
                    'content_vector': embedding
                }
                prepared_docs.append(prepared_doc)
            
            logger.info(f"Prepared {len(prepared_docs)} documents with embeddings")
            return prepared_docs
            
        except Exception as e:
            logger.error(f"Error preparing documents: {e}")
            raise
    
    def ingest_documents(self, documents: List[Dict[str, Any]]):
        """Ingest documents into the search index."""
        try:
            logger.info(f"Ingesting {len(documents)} documents into index: {self.index_name}")
            
            # Upload in batches
            for i in range(0, len(documents), CONFIG['batch_size']):
                batch = documents[i:i + CONFIG['batch_size']]
                result = self.search_client.upload_documents(batch)
                
                # Check for any failures
                if result:
                    failed = [r for r in result if not r.succeeded]
                    if failed:
                        logger.warning(f"Failed to ingest {len(failed)} documents in batch")
                        for failure in failed:
                            logger.warning(f"Failed document {failure.key}: {failure.error_message}")
                    else:
                        logger.info(f"Successfully ingested batch {i//CONFIG['batch_size'] + 1} ({len(batch)} documents)")
            
            logger.info(f"Document ingestion completed")
            
        except Exception as e:
            logger.error(f"Error ingesting documents: {e}")
            raise
    
    def verify_index(self):
        """Verify the index was created successfully and contains data."""
        try:
            # Get index statistics
            index_stats = self.search_client.get_document_count()
            logger.info(f"Index {self.index_name} contains {index_stats} documents")
            
            # Test search functionality
            test_results = self.search_client.search(
                search_text="portfolio performance",
                top=3,
                select=["id", "text", "author", "created_at"]
            )
            
            results_list = list(test_results)
            logger.info(f"Test search returned {len(results_list)} results")
            if results_list:
                sample = results_list[0]
                logger.info(f"Sample result - ID: {sample['id']}, Author: {sample['author']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Index verification failed: {e}")
            return False

def load_crm_data(filename: str) -> List[Dict[str, Any]]:
    """Load CRM data from JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Loaded {len(data)} CRM notes from {filename}")
        return data
        
    except FileNotFoundError:
        logger.error(f"File {filename} not found. Please run generate_crm_data.py first.")
        raise
    except Exception as e:
        logger.error(f"Error loading CRM data: {e}")
        raise

def main():
    """Main function to create index and ingest data."""
    logger.info("Starting AI Search index creation and data ingestion (Synchronous version)")
    
    # Validate configuration
    required_configs = ['search_endpoint', 'search_key', 'openai_endpoint', 'openai_key']
    missing_configs = []
    for config_key in required_configs:
        if not CONFIG[config_key] or CONFIG[config_key].startswith('your-'):
            missing_configs.append(config_key)
    
    if missing_configs:
        logger.error(f"Missing required configuration: {', '.join(missing_configs)}")
        logger.error("Please check your .env file configuration.")
        return
    
    try:
        # Initialize manager
        manager = SyncAISearchIndexManager()
        
        # Step 1: Create the search index
        manager.create_index()
        
        # Step 2: Load CRM data
        raw_data = load_crm_data(CONFIG['input_file'])
        
        # Step 3: Prepare documents (generate embeddings)
        prepared_docs = manager.prepare_documents(raw_data)
        
        # Step 4: Ingest documents
        manager.ingest_documents(prepared_docs)
        
        # Step 5: Verify the index
        success = manager.verify_index()
        
        if success:
            logger.info("✅ AI Search index creation and data ingestion completed successfully!")
            logger.info(f"Index name: {CONFIG['index_name']}")
            logger.info(f"Documents ingested: {len(prepared_docs)}")
            logger.info("The Vector Agent can now use this index for CRM data retrieval.")
        else:
            logger.warning("⚠️ Index creation completed but verification failed")
        
    except Exception as e:
        logger.error(f"❌ Process failed: {e}")
        raise

if __name__ == "__main__":
    main()