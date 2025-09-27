"""
Azure authentication utilities using Managed Identity
"""

import logging
from typing import Optional
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.core.credentials import TokenCredential
from azure.keyvault.secrets import SecretClient
from common.config import get_settings

logger = logging.getLogger(__name__)


class AzureAuthManager:
    """Manages Azure authentication using Managed Identity."""
    
    def __init__(self):
        self.settings = get_settings()
        self._credential: Optional[TokenCredential] = None
        self._secret_client: Optional[SecretClient] = None
    
    @property
    def credential(self) -> TokenCredential:
        """Get Azure credential (Managed Identity preferred)."""
        if self._credential is None:
            try:
                # Try Managed Identity first (for Azure environments)
                self._credential = ManagedIdentityCredential()
                # Test the credential
                token = self._credential.get_token("https://management.azure.com/.default")
                logger.info("Successfully authenticated with Managed Identity")
            except Exception as e:
                logger.warning(f"Managed Identity failed, falling back to DefaultAzureCredential: {e}")
                # Fallback to DefaultAzureCredential (for local development)
                self._credential = DefaultAzureCredential()
        
        return self._credential
    
    @property
    def secret_client(self) -> SecretClient:
        """Get Key Vault secret client."""
        if self._secret_client is None:
            self._secret_client = SecretClient(
                vault_url=self.settings.key_vault_uri,
                credential=self.credential
            )
        return self._secret_client
    
    def get_secret(self, secret_name: str) -> Optional[str]:
        """Get secret from Key Vault."""
        try:
            secret = self.secret_client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            logger.error(f"Failed to get secret '{secret_name}': {e}")
            return None
    
    def get_access_token(self, scope: str) -> Optional[str]:
        """Get access token for specific scope."""
        try:
            token = self.credential.get_token(scope)
            return token.token
        except Exception as e:
            logger.error(f"Failed to get access token for scope '{scope}': {e}")
            return None


# Global instance
_auth_manager: Optional[AzureAuthManager] = None


def get_auth_manager() -> AzureAuthManager:
    """Get global Azure authentication manager."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AzureAuthManager()
    return _auth_manager


def get_credential() -> TokenCredential:
    """Get Azure credential."""
    return get_auth_manager().credential


def get_secret(secret_name: str) -> Optional[str]:
    """Get secret from Key Vault."""
    return get_auth_manager().get_secret(secret_name)


def get_sql_access_token() -> Optional[str]:
    """Get access token for SQL Database."""
    return get_auth_manager().get_access_token("https://database.windows.net/.default")


def get_search_access_token() -> Optional[str]:
    """Get access token for Azure AI Search."""
    return get_auth_manager().get_access_token("https://search.azure.com/.default")


def get_openai_access_token() -> Optional[str]:
    """Get access token for Azure OpenAI."""
    return get_auth_manager().get_access_token("https://cognitiveservices.azure.com/.default")