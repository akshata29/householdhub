@description('Location for all resources')
param location string = resourceGroup().location

@description('Tags to apply to all resources')
param tags object = {}

@description('Resource token for unique naming')
param resourceToken string

@description('Principal ID for role assignments')
param principalId string = ''

// Virtual Network for private endpoints
resource vnet 'Microsoft.Network/virtualNetworks@2023-09-01' = {
  name: 'vnet-wealthops-${resourceToken}'
  location: location
  tags: tags
  properties: {
    addressSpace: {
      addressPrefixes: ['10.0.0.0/16']
    }
    subnets: [
      {
        name: 'subnet-containerapp'
        properties: {
          addressPrefix: '10.0.0.0/23'
          delegations: [
            {
              name: 'Microsoft.App.environments'
              properties: {
                serviceName: 'Microsoft.App/environments'
              }
            }
          ]
        }
      }
      {
        name: 'subnet-private-endpoints'
        properties: {
          addressPrefix: '10.0.2.0/24'
          privateEndpointNetworkPolicies: 'Disabled'
        }
      }
    ]
  }
}

// Log Analytics Workspace
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'log-wealthops-${resourceToken}'
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-wealthops-${resourceToken}'
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

// Container Apps Environment
resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: 'cae-wealthops-${resourceToken}'
  location: location
  tags: tags
  properties: {
    vnetConfiguration: {
      infrastructureSubnetId: vnet.properties.subnets[0].id
    }
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

// Container Registry
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: 'acrwealthops${resourceToken}'
  location: location
  tags: tags
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

// Storage Account
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'stwealthops${resourceToken}'
  location: location
  tags: tags
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    isHnsEnabled: true // Enable Data Lake Gen2
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

// Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: 'kv-wealthops-${resourceToken}'
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: tenant().tenantId
    enableRbacAuthorization: true
    enabledForDeployment: false
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: false
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Deny'
    }
  }
}

// SQL Server
resource sqlServer 'Microsoft.Sql/servers@2023-05-01-preview' = {
  name: 'sql-wealthops-${resourceToken}'
  location: location
  tags: tags
  properties: {
    administratorLogin: 'sqladmin'
    administratorLoginPassword: 'P@ssw0rd123!' // In production, use Key Vault
    minimalTlsVersion: '1.2'
    publicNetworkAccess: 'Disabled'
  }
  
  resource database 'databases@2023-05-01-preview' = {
    name: 'wealthops-db'
    location: location
    tags: tags
    sku: {
      name: 'S1' // Standard tier for demo
      tier: 'Standard'
    }
    properties: {
      collation: 'SQL_Latin1_General_CP1_CI_AS'
      maxSizeBytes: 268435456000 // 250GB
    }
  }
}

// Azure AI Search
resource aiSearch 'Microsoft.Search/searchServices@2023-11-01' = {
  name: 'aisrch-wealthops-${resourceToken}'
  location: location
  tags: tags
  sku: {
    name: 'basic'
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
    publicNetworkAccess: 'disabled'
    networkRuleSet: {
      ipRules: []
    }
  }
}

// Azure OpenAI / AI Services
resource aiServices 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: 'ai-wealthops-${resourceToken}'
  location: location
  tags: tags
  kind: 'AIServices'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: 'ai-wealthops-${resourceToken}'
    publicNetworkAccess: 'Disabled'
    networkAcls: {
      defaultAction: 'Deny'
      virtualNetworkRules: []
      ipRules: []
    }
  }
  
  resource gpt4oMiniDeployment 'deployments@2023-05-01' = {
    name: 'gpt-4o-mini'
    properties: {
      model: {
        format: 'OpenAI'
        name: 'gpt-4o-mini'
        version: '2024-07-18'
      }
      raiPolicyName: 'Microsoft.Default'
      versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
    }
    sku: {
      name: 'Standard'
      capacity: 10
    }
  }
  
  resource embeddingDeployment 'deployments@2023-05-01' = {
    name: 'text-embedding-3-small'
    properties: {
      model: {
        format: 'OpenAI'
        name: 'text-embedding-3-small'
        version: '1'
      }
      raiPolicyName: 'Microsoft.Default'
      versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
    }
    sku: {
      name: 'Standard'
      capacity: 10
    }
  }
}

// Service Bus Namespace
resource serviceBusNamespace 'Microsoft.ServiceBus/namespaces@2022-10-01-preview' = {
  name: 'sb-wealthops-${resourceToken}'
  location: location
  tags: tags
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }
  properties: {
    minimumTlsVersion: '1.2'
    publicNetworkAccess: 'Disabled'
  }
  
  resource a2aTopic 'topics@2022-10-01-preview' = {
    name: 'a2a-messages'
    properties: {
      defaultMessageTimeToLive: 'PT1H'
      maxSizeInMegabytes: 1024
      enableBatchedOperations: true
    }
    
    resource orchestratorSub 'subscriptions@2022-10-01-preview' = {
      name: 'orchestrator'
      properties: {
        defaultMessageTimeToLive: 'PT1H'
        maxDeliveryCount: 3
        enableBatchedOperations: true
      }
    }
    
    resource nl2sqlSub 'subscriptions@2022-10-01-preview' = {
      name: 'nl2sql'
      properties: {
        defaultMessageTimeToLive: 'PT1H'
        maxDeliveryCount: 3
        enableBatchedOperations: true
      }
    }
    
    resource vectorSub 'subscriptions@2022-10-01-preview' = {
      name: 'vector'
      properties: {
        defaultMessageTimeToLive: 'PT1H'
        maxDeliveryCount: 3
        enableBatchedOperations: true
      }
    }
    
    resource apiSub 'subscriptions@2022-10-01-preview' = {
      name: 'api'
      properties: {
        defaultMessageTimeToLive: 'PT1H'
        maxDeliveryCount: 3
        enableBatchedOperations: true
      }
    }
  }
}

// Static Web App for Frontend
resource staticWebApp 'Microsoft.Web/staticSites@2023-01-01' = {
  name: 'swa-wealthops-${resourceToken}'
  location: location
  tags: tags
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }
  properties: {
    repositoryUrl: 'https://github.com/your-repo/wealthops-mvp'
    branch: 'main'
    buildProperties: {
      appLocation: '/frontend'
      outputLocation: 'out'
    }
  }
}

// Managed Identity for Container Apps
resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-wealthops-${resourceToken}'
  location: location
  tags: tags
}

// Role assignments for Managed Identity
resource sqlDbContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(sqlServer.id, managedIdentity.id, 'b24988ac-6180-42a0-ab88-20f7382dd24c')
  scope: sqlServer::database
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'b24988ac-6180-42a0-ab88-20f7382dd24c') // SQL DB Contributor
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource searchContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aiSearch.id, managedIdentity.id, '8ebe5a00-799e-43f5-93ac-243d3dce84a7')
  scope: aiSearch
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '8ebe5a00-799e-43f5-93ac-243d3dce84a7') // Search Service Contributor
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource aiServicesUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aiServices.id, managedIdentity.id, 'a97b65f3-24c7-4388-baec-2e87135dc908')
  scope: aiServices
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a97b65f3-24c7-4388-baec-2e87135dc908') // Cognitive Services User
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource serviceBusDataOwnerRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(serviceBusNamespace.id, managedIdentity.id, '090c5cfd-751d-490a-894a-3ce6f1109419')
  scope: serviceBusNamespace
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '090c5cfd-751d-490a-894a-3ce6f1109419') // Service Bus Data Owner
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource storageContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, managedIdentity.id, 'b7e6dc6d-f1e8-4753-8033-0f276bb0955b')
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'b7e6dc6d-f1e8-4753-8033-0f276bb0955b') // Storage Blob Data Owner
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource keyVaultSecretsUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, managedIdentity.id, '4633458b-17de-408a-b874-0445c86b69e6')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6') // Key Vault Secrets User
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Container Apps
module orchestratorApp 'containerapp.bicep' = {
  name: 'orchestrator'
  params: {
    name: 'orchestrator-${resourceToken}'
    location: location
    tags: tags
    containerAppsEnvironmentId: containerAppsEnvironment.id
    containerRegistryName: containerRegistry.name
    userAssignedIdentityId: managedIdentity.id
    environmentVariables: [
      {
        name: 'AZURE_SQL_CONNECTION_STRING'
        secretRef: 'sql-connection-string'
      }
      {
        name: 'AI_SEARCH_ENDPOINT'
        value: 'https://${aiSearch.name}.search.windows.net'
      }
      {
        name: 'AZURE_OPENAI_ENDPOINT'
        value: aiServices.properties.endpoint
      }
      {
        name: 'SERVICE_BUS_NAMESPACE'
        value: '${serviceBusNamespace.name}.servicebus.windows.net'
      }
      {
        name: 'STORAGE_ACCOUNT_NAME'
        value: storageAccount.name
      }
      {
        name: 'KEY_VAULT_URI'
        value: keyVault.properties.vaultUri
      }
    ]
    secrets: [
      {
        name: 'sql-connection-string'
        value: 'Server=${sqlServer.properties.fullyQualifiedDomainName};Database=${sqlServer::database.name};Authentication=Active Directory Managed Identity;'
      }
    ]
  }
}

module nl2sqlAgentApp 'containerapp.bicep' = {
  name: 'nl2sql-agent'
  params: {
    name: 'nl2sql-agent-${resourceToken}'
    location: location
    tags: tags
    containerAppsEnvironmentId: containerAppsEnvironment.id
    containerRegistryName: containerRegistry.name
    userAssignedIdentityId: managedIdentity.id
    environmentVariables: [
      {
        name: 'AZURE_SQL_CONNECTION_STRING'
        secretRef: 'sql-connection-string'
      }
      {
        name: 'SERVICE_BUS_NAMESPACE'
        value: '${serviceBusNamespace.name}.servicebus.windows.net'
      }
    ]
    secrets: [
      {
        name: 'sql-connection-string'
        value: 'Server=${sqlServer.properties.fullyQualifiedDomainName};Database=${sqlServer::database.name};Authentication=Active Directory Managed Identity;'
      }
    ]
  }
}

module vectorAgentApp 'containerapp.bicep' = {
  name: 'vector-agent'
  params: {
    name: 'vector-agent-${resourceToken}'
    location: location
    tags: tags
    containerAppsEnvironmentId: containerAppsEnvironment.id
    containerRegistryName: containerRegistry.name
    userAssignedIdentityId: managedIdentity.id
    environmentVariables: [
      {
        name: 'AI_SEARCH_ENDPOINT'
        value: 'https://${aiSearch.name}.search.windows.net'
      }
      {
        name: 'AZURE_OPENAI_ENDPOINT'
        value: aiServices.properties.endpoint
      }
      {
        name: 'SERVICE_BUS_NAMESPACE'
        value: '${serviceBusNamespace.name}.servicebus.windows.net'
      }
    ]
    secrets: []
  }
}

module apiAgentApp 'containerapp.bicep' = {
  name: 'api-agent'
  params: {
    name: 'api-agent-${resourceToken}'
    location: location
    tags: tags
    containerAppsEnvironmentId: containerAppsEnvironment.id
    containerRegistryName: containerRegistry.name
    userAssignedIdentityId: managedIdentity.id
    environmentVariables: [
      {
        name: 'SERVICE_BUS_NAMESPACE'
        value: '${serviceBusNamespace.name}.servicebus.windows.net'
      }
    ]
    secrets: []
  }
}

// Outputs
output AZURE_CONTAINER_APPS_ENVIRONMENT_ID string = containerAppsEnvironment.id
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.properties.loginServer
output AZURE_CONTAINER_REGISTRY_NAME string = containerRegistry.name

output ORCHESTRATOR_URL string = 'https://${orchestratorApp.outputs.fqdn}'
output NL2SQL_AGENT_URL string = 'https://${nl2sqlAgentApp.outputs.fqdn}'
output VECTOR_AGENT_URL string = 'https://${vectorAgentApp.outputs.fqdn}'
output API_AGENT_URL string = 'https://${apiAgentApp.outputs.fqdn}'
output FRONTEND_URL string = 'https://${staticWebApp.properties.defaultHostname}'

output AZURE_SQL_CONNECTION_STRING string = 'Server=${sqlServer.properties.fullyQualifiedDomainName};Database=${sqlServer::database.name};Authentication=Active Directory Managed Identity;'
output AI_SEARCH_ENDPOINT string = 'https://${aiSearch.name}.search.windows.net'
output AZURE_OPENAI_ENDPOINT string = aiServices.properties.endpoint
output SERVICE_BUS_NAMESPACE string = '${serviceBusNamespace.name}.servicebus.windows.net'
output STORAGE_ACCOUNT_NAME string = storageAccount.name
output KEY_VAULT_URI string = keyVault.properties.vaultUri
