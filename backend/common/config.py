"""
Configuration management for WealthOps MVP
"""

import os
from functools import lru_cache
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Azure Configuration
    azure_tenant_id: Optional[str] = Field(default=None, env="AZURE_TENANT_ID")
    azure_subscription_id: Optional[str] = Field(default=None, env="AZURE_SUBSCRIPTION_ID")
    azure_resource_group: Optional[str] = Field(default=None, env="AZURE_RESOURCE_GROUP")
    
    # Database
    azure_sql_connection_string: Optional[str] = Field(default=None, env="AZURE_SQL_CONNECTION_STRING")
    sql_query_timeout: int = Field(default=30, env="SQL_QUERY_TIMEOUT")
    sql_max_pool_size: int = Field(default=10, env="SQL_MAX_POOL_SIZE")
    
    # Azure AI Search
    ai_search_endpoint: Optional[str] = Field(default=None, env="AI_SEARCH_ENDPOINT")
    ai_search_key: Optional[str] = Field(default=None, env="AI_SEARCH_KEY")  # Optional for MSI
    ai_search_index_name: str = Field(default="crm-notes", env="AI_SEARCH_INDEX_NAME")
    
    # Azure OpenAI
    azure_openai_endpoint: Optional[str] = Field(default=None, env="AZURE_OPENAI_ENDPOINT")
    azure_openai_key: Optional[str] = Field(default=None, env="AZURE_OPENAI_KEY")  # Optional for MSI
    azure_openai_deployment: str = Field(default="gpt-4o-mini", env="AZURE_OPENAI_DEPLOYMENT")
    azure_openai_embedding_deployment: str = Field(default="text-embedding-3-small", env="AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    azure_openai_api_version: str = Field(default="2024-02-01", env="AZURE_OPENAI_API_VERSION")
    
    # Service Bus
    service_bus_namespace: Optional[str] = Field(default=None, env="SERVICE_BUS_NAMESPACE")
    service_bus_connection_string: Optional[str] = Field(default=None, env="SERVICE_BUS_CONNECTION_STRING")
    service_bus_topic: str = Field(default="a2a-messages", env="SERVICE_BUS_TOPIC")
    service_bus_subscription_prefix: str = Field(default="", env="SERVICE_BUS_SUBSCRIPTION_PREFIX")
    
    # Storage
    storage_account_name: Optional[str] = Field(default=None, env="STORAGE_ACCOUNT_NAME")
    storage_container_name: str = Field(default="audit-logs", env="STORAGE_CONTAINER_NAME")
    
    # Key Vault
    key_vault_uri: Optional[str] = Field(default=None, env="KEY_VAULT_URI")
    
    # Authentication
    allowed_tenant: Optional[str] = Field(default=None, env="ALLOWED_TENANT")
    
    # Frontend
    frontend_url: str = Field(default="http://localhost:3000", env="FRONTEND_URL")
    cors_origins: list[str] = Field(default=["http://localhost:3000"], env="CORS_ORIGINS")
    
    # Agent Configuration
    agent_name: str = Field(default="unknown", env="AGENT_NAME")
    max_retry_attempts: int = Field(default=3, env="MAX_RETRY_ATTEMPTS")
    message_timeout_seconds: int = Field(default=30, env="MESSAGE_TIMEOUT_SECONDS")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    application_insights_connection_string: Optional[str] = Field(default=None, env="APPLICATIONINSIGHTS_CONNECTION_STRING")
    
    # Performance
    max_concurrent_requests: int = Field(default=100, env="MAX_CONCURRENT_REQUESTS")
    request_timeout_seconds: int = Field(default=60, env="REQUEST_TIMEOUT_SECONDS")
    
    class Config:
        env_file = [".env", "../.env"]  # Look for .env in current dir and parent dir
        case_sensitive = False
        extra = "ignore"  # Allow extra environment variables to be ignored


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Environment-specific configurations
def is_production() -> bool:
    """Check if running in production environment."""
    return get_settings().environment.lower() == "production"


def is_development() -> bool:
    """Check if running in development environment."""
    return get_settings().environment.lower() == "development"


def get_cors_origins() -> list[str]:
    """Get CORS origins based on environment."""
    settings = get_settings()
    if is_development():
        return ["http://localhost:3000", "http://127.0.0.1:3000", settings.frontend_url]
    return settings.cors_origins


def get_database_url() -> str:
    """Get database connection URL."""
    return get_settings().azure_sql_connection_string


def get_service_bus_connection_string() -> str:
    """Get Service Bus connection string for Managed Identity."""
    settings = get_settings()
    return f"{settings.service_bus_namespace}"


def get_ai_search_endpoint() -> str:
    """Get Azure AI Search endpoint."""
    return get_settings().ai_search_endpoint


def get_azure_openai_endpoint() -> str:
    """Get Azure OpenAI endpoint."""
    return get_settings().azure_openai_endpoint