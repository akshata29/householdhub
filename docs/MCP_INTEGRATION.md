# MCP Server Integration for NL2SQL Agent

This implementation integrates the Model Context Protocol (MCP) architecture into the HouseholdHub NL2SQL agent, following the patterns established by Microsoft's MSSQL MCP Server.

## Architecture Overview

```
User Query → Orchestrator → NL2SQL Agent → MCP Server → SQL Database
     ↓            ↓            ↓           ↓           ↓
   Intent     Route to     Translate    Execute    Return
 Detection    Agent        to SQL       Tools      Results
```

## Key Components

### 1. MCP Client (`common/mcp_client.py`)
- **MCPSQLServer**: Main MCP server implementation
- **MCPSQLTool**: Base class for MCP tools
- **ReadDataTool**: Secure SQL SELECT operations
- **ListTablesTool**: Database schema discovery
- **DescribeTableTool**: Table structure analysis
- **MCPConnectionFactory**: Database connection management

### 2. Enhanced NL2SQL Agent (`nl2sql_agent/main.py`)
- **NL2SQLAgent**: Core agent with MCP integration
- **NL2SQLAgentService**: Service wrapper with A2A messaging
- Intent detection and SQL generation
- Secure query validation and execution

### 3. Updated Orchestrator (`orchestrator/main.py`)
- Enhanced intent detection with `CASH_BALANCE` support
- Improved agent routing and response composition
- Integration with MCP-based NL2SQL agent

## MCP Tools

### ReadDataTool
```python
await mcp_server.call_tool("read_data", {
    "query": "SELECT TOP 10 * FROM dbo.Households"
})
```
- **Purpose**: Execute SELECT queries safely
- **Security**: Validates queries, prevents SQL injection
- **Features**: Result sanitization, row limiting, execution timing

### ListTablesTool
```python
await mcp_server.call_tool("list_tables", {})
```
- **Purpose**: Discover available database tables
- **Returns**: Schema names, table names, table types
- **Use Case**: Dynamic schema exploration

### DescribeTableTool
```python
await mcp_server.call_tool("describe_table", {
    "table_name": "Households",
    "schema_name": "dbo"
})
```
- **Purpose**: Get detailed table schema information
- **Returns**: Columns, data types, primary keys, foreign keys
- **Use Case**: SQL generation context

## Intent Detection

The system now recognizes specific intents for better SQL generation:

| Intent | Description | Example Query |
|--------|-------------|---------------|
| `CASH_BALANCE` | Specific cash balance queries | "What is the cash balance for Singh Global Family Office?" |
| `TOP_CASH` | Ranking by cash amounts | "Show me top 10 households by cash" |
| `ALLOCATION_DRIFT` | Portfolio allocation analysis | "Which households have allocation mismatches?" |
| `BENEFICIARY_MISSING` | Missing beneficiary detection | "Which accounts are missing beneficiaries?" |

## Security Features

### Query Validation
- **Keyword Detection**: Blocks destructive operations (DELETE, DROP, etc.)
- **Multiple Statements**: Prevents SQL injection via semicolons
- **Length Limits**: Prevents DoS via extremely long queries
- **Comment Removal**: Strips SQL comments before analysis

### Result Sanitization
- **Row Limiting**: Maximum 10,000 rows returned
- **Column Name Cleaning**: Removes dangerous characters
- **Error Message Filtering**: Prevents information leakage

### Connection Security
- **Managed Identity**: Uses Azure AD authentication
- **Connection Pooling**: Efficient database connections
- **Timeout Handling**: Prevents hanging connections

## Usage Examples

### Direct MCP Usage
```python
from common.mcp_client import MCPSQLServer

# Initialize MCP server
mcp_server = MCPSQLServer(connection_string)

# List available tools
tools = await mcp_server.list_tools()

# Execute SQL query
result = await mcp_server.call_tool("read_data", {
    "query": "SELECT TOP 5 name, SUM(cash) as total_cash FROM dbo.Households h JOIN dbo.Accounts a ON h.household_id = a.household_id GROUP BY h.name ORDER BY total_cash DESC"
})
```

### NL2SQL Agent Usage
```python
from nl2sql_agent.main import NL2SQLAgent

# Initialize agent
agent = NL2SQLAgent(connection_string)

# Process natural language query
result = await agent.translate_nl_to_sql(
    "What is the cash balance for Singh Global Family Office?"
)

# Result includes:
# - success: bool
# - sql_query: str
# - results: List[Dict]
# - intent: str
# - execution_time_ms: int
```

### Orchestrator Integration
```python
from orchestrator.main import OrchestratorAgent
from common.schemas import QueryRequest

# Initialize orchestrator
orchestrator = OrchestratorAgent()

# Process query through orchestrator
request = QueryRequest(
    query="What is the cash balance for Singh Global Family Office?"
)
response = await orchestrator.process_query_sync(request)

# Response includes composed natural language answer with citations
```

## API Endpoints

### NL2SQL Agent (Port 8002)
- `POST /query`: Process NL2SQL requests
- `GET /schema`: Get database schema information
- `GET /tools`: List available MCP tools
- `POST /tools/{tool_name}`: Call specific MCP tool

### Example API Usage
```bash
# Process natural language query
curl -X POST "http://localhost:8002/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the cash balance for Singh Global Family Office?",
    "household_id": null,
    "account_id": null
  }'

# List MCP tools
curl -X GET "http://localhost:8002/tools"

# Call MCP tool directly
curl -X POST "http://localhost:8002/tools/read_data" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT TOP 5 * FROM dbo.Households"
  }'
```

## Testing

### Run MCP Tests
```bash
cd backend
python test_mcp_nl2sql.py
```

### Run Full Demonstration
```bash
cd backend
python demo_mcp_nl2sql.py
```

### Test Specific Query
```bash
# Start NL2SQL agent
cd backend/nl2sql_agent
python main.py

# In another terminal, test the API
curl -X POST "http://localhost:8002/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the cash balance for Singh Global Family Office?"}'
```

## Configuration

### Environment Variables
```env
# Database Connection
AZURE_SQL_CONNECTION_STRING="Server=tcp:your-server.database.windows.net,1433;Database=your-db;Authentication=Active Directory Managed Identity"

# Azure Configuration
AZURE_TENANT_ID="your-tenant-id"
AZURE_SUBSCRIPTION_ID="your-subscription-id"
AZURE_OPENAI_ENDPOINT="https://your-openai.openai.azure.com/"
AZURE_OPENAI_DEPLOYMENT="your-deployment-name"
```

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start services
python nl2sql_agent/main.py    # Port 8002
python orchestrator/main.py     # Port 8001
```

## Benefits of MCP Architecture

### Standardization
- **Consistent Interface**: All SQL operations use the same MCP tool pattern
- **Extensible Design**: Easy to add new SQL operations as MCP tools
- **Interoperability**: Compatible with other MCP clients and servers

### Security
- **Centralized Validation**: All SQL queries go through MCP security checks
- **Auditing**: Comprehensive logging of all database operations
- **Isolation**: MCP server isolates database logic from business logic

### Performance
- **Schema Caching**: Reduces repeated schema queries
- **Connection Pooling**: Efficient database connection management
- **Result Streaming**: Supports large result sets efficiently

### Maintainability
- **Clear Separation**: Database operations separated from NL processing
- **Testable Components**: Each MCP tool can be tested independently
- **Documentation**: Self-describing tools with schema definitions

## Future Enhancements

### Enhanced NL Understanding
- Integration with more sophisticated LLMs for SQL generation
- Context-aware query understanding
- Multi-turn conversation support

### Additional MCP Tools
- **WriteDataTool**: Secure INSERT/UPDATE operations (with approval workflows)
- **SchemaEvolutionTool**: Track and manage schema changes
- **QueryOptimizationTool**: Analyze and optimize generated SQL

### Monitoring & Observability
- Query performance metrics
- Usage analytics and patterns
- Error tracking and alerting

### Advanced Security
- Role-based access control (RBAC)
- Query approval workflows for sensitive operations
- Data masking for PII protection

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Check Azure SQL connection string
   - Verify Managed Identity permissions
   - Ensure firewall rules allow connections

2. **Authentication Errors**
   - Check Azure AD authentication
   - Verify service principal permissions
   - Check token expiration and refresh

3. **Query Validation Errors**
   - Review security validation rules
   - Check for forbidden SQL keywords
   - Verify query syntax and length limits

4. **Performance Issues**
   - Monitor query execution times
   - Check database connection pool settings
   - Review result set sizes and limiting

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# This will show detailed MCP operation logs
```

### Health Checks
```bash
# Check NL2SQL agent health
curl http://localhost:8002/health

# Check available tools
curl http://localhost:8002/tools

# Test basic database connectivity
curl -X POST http://localhost:8002/tools/list_tables -d '{}'
```

## References

- [Microsoft MSSQL MCP Server Blog Post](https://devblogs.microsoft.com/azure-sql/introducing-mssql-mcp-server/)
- [Microsoft MSSQL MCP Server GitHub](https://github.com/Azure-Samples/SQL-AI-samples/tree/main/MssqlMcp/Node)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Python MCP MSSQL Reference Implementation](https://github.com/amornpan/py-mcp-mssql)