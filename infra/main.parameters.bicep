targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment that can be used as part of naming resource convention')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Id of the principal to assign database and application roles')
param principalId string = ''

// Tags that should be applied to all resources.
var tags = {
  'azd-env-name': environmentName
  'app': 'wealthops-mvp'
}

// Generate a unique token to be used in naming resources
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))

// Name of the resource group to create
var resourceGroupName = 'rg-wealthops-${environmentName}'

resource rg 'Microsoft.Resources/resourceGroups@2022-09-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

module resources 'main.bicep' = {
  scope: rg
  params: {
    location: location
    tags: tags
    resourceToken: resourceToken
    principalId: principalId
  }
}

// App service plan outputs
output AZURE_CONTAINER_APPS_ENVIRONMENT_ID string = resources.outputs.AZURE_CONTAINER_APPS_ENVIRONMENT_ID
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = resources.outputs.AZURE_CONTAINER_REGISTRY_ENDPOINT
output AZURE_CONTAINER_REGISTRY_NAME string = resources.outputs.AZURE_CONTAINER_REGISTRY_NAME

// Application outputs
output ORCHESTRATOR_URL string = resources.outputs.ORCHESTRATOR_URL
output NL2SQL_AGENT_URL string = resources.outputs.NL2SQL_AGENT_URL  
output VECTOR_AGENT_URL string = resources.outputs.VECTOR_AGENT_URL
output API_AGENT_URL string = resources.outputs.API_AGENT_URL
output FRONTEND_URL string = resources.outputs.FRONTEND_URL

// Azure resource outputs
output AZURE_SQL_CONNECTION_STRING string = resources.outputs.AZURE_SQL_CONNECTION_STRING
output AI_SEARCH_ENDPOINT string = resources.outputs.AI_SEARCH_ENDPOINT
output AZURE_OPENAI_ENDPOINT string = resources.outputs.AZURE_OPENAI_ENDPOINT
output SERVICE_BUS_NAMESPACE string = resources.outputs.SERVICE_BUS_NAMESPACE
output STORAGE_ACCOUNT_NAME string = resources.outputs.STORAGE_ACCOUNT_NAME
output KEY_VAULT_URI string = resources.outputs.KEY_VAULT_URI
