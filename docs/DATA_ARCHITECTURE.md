# WealthOps Data Architecture

This document describes the production data architecture for WealthOps, including database schema, API services, and frontend integration.

## 🏗️ Architecture Overview

```
Frontend (React/Next.js)
    ↓ API calls
API Client (TypeScript)
    ↓ HTTP requests
Data Service (FastAPI/Python)
    ↓ SQL queries
Azure SQL Database
    ↓ fallback
Mock Data (local/development)
```

## 📊 Database Schema

### Core Tables

- **Households**: Main entity storing household information
- **Accounts**: Bank/investment accounts belonging to households
- **Securities**: Master data for stocks, bonds, ETFs
- **Positions**: Holdings within accounts
- **PerformanceData**: Time-series portfolio performance
- **CashTrendData**: Cash balance trends over time
- **Activities**: Tasks, meetings, and interactions
- **RMDs**: Required minimum distributions
- **Beneficiaries**: Beneficiary designations

### Reference Tables

- **RiskProfiles**: Conservative, Moderate, Aggressive
- **HouseholdTypes**: Individual, Joint, Trust, Corporation, Foundation
- **Advisors**: Financial advisors and their information
- **AccountTypes**: Checking, Savings, Investment, Retirement, etc.
- **AssetClasses**: Equity, Fixed Income, Cash, Real Estate, Alternative
- **Institutions**: Financial institutions (banks, brokers)

## 🚀 Getting Started

### Prerequisites

- SQL Server or Azure SQL Database
- Python 3.11+
- Node.js 18+
- ODBC Driver 18 for SQL Server

### 1. Database Setup

#### Create Azure SQL Database (Production)

```bash
# Using Azure CLI
az sql server create --name wealthops-sql --resource-group wealthops-rg --location "East US" --admin-user wealthopsadmin --admin-password "YourSecurePassword123!"

az sql db create --server wealthops-sql --resource-group wealthops-rg --name WealthOpsDB --service-objective S2
```

#### Run Schema Creation

```sql
-- Run in Azure SQL or SQL Server Management Studio
-- File: database/01_create_schema.sql
-- This creates all tables, indexes, and views
```

#### Insert Synthetic Data

```sql 
-- Run after schema creation
-- File: database/02_insert_synthetic_data.sql
-- This populates tables with realistic test data
```

### 2. Data Service Setup

#### Install Dependencies

```bash
cd backend/data_service
pip install -r requirements.txt
```

#### Configure Environment

```bash
# Copy and edit configuration
cp .env.example .env

# Update .env with your database details:
SQL_SERVER=your-server.database.windows.net
SQL_DATABASE=WealthOpsDB  
SQL_USERNAME=your-username
SQL_PASSWORD=your-password
```

#### Start the Service

```bash
# Linux/Mac
./start.sh

# Windows PowerShell
./start.ps1

# Or directly with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Verify Service

- Health Check: http://localhost:8000/health
- API Documentation: http://localhost:8000/docs
- Interactive API: http://localhost:8000/redoc

### 3. Frontend Configuration

#### Enable Data Service

```bash
cd frontend

# Copy environment file
cp .env.example .env.local

# Edit .env.local to enable data service:
NEXT_PUBLIC_USE_DATA_SERVICE=true
NEXT_PUBLIC_DATA_SERVICE_URL=http://localhost:8000
```

#### Start Frontend

```bash
npm run dev
```

## 🔄 Data Flow

### 1. Frontend Request
```typescript
// Component makes data request
const { data, error, isLoading } = useOverview(householdId);
```

### 2. API Client Processing
```typescript
// API client handles request with fallback
const response = await apiClient.getOverview(householdId);
// Returns: { data, source: 'database' | 'mock', timestamp }
```

### 3. Data Service Query
```python
# Data service queries database
async def get_overview(household_id: str):
    query = """
    SELECT h.Name, h.TotalAssets, ...
    FROM vw_HouseholdSummary h 
    WHERE h.HouseholdCode = ?
    """
    return db.execute_query(query, (household_id,))
```

### 4. Database Response
```sql
-- Optimized view returns aggregated data
SELECT 
    h.HouseholdCode as id,
    h.Name,
    SUM(acc.Balance) as TotalAssets,
    COUNT(acc.AccountID) as AccountsCount
FROM Households h
LEFT JOIN Accounts acc ON h.HouseholdID = acc.HouseholdID
GROUP BY h.HouseholdCode, h.Name
```

## 🛡️ Fallback Strategy

The system implements a robust fallback mechanism:

1. **Primary**: Database via Data Service API
2. **Secondary**: Mock data when database unavailable
3. **Graceful**: Automatic failover with user notification
4. **Development**: Can be forced to mock mode for development

### Fallback Triggers

- Network connectivity issues
- Database server unavailable  
- Data service crashes
- Query timeouts
- Authentication failures

## 📈 Performance Optimizations

### Database Level

- **Indexes**: Strategic indexes on key lookup columns
- **Views**: Pre-computed aggregations for summary data
- **Partitioning**: Time-series data partitioned by date
- **Connection Pooling**: Managed connection pool for scalability

### API Level

- **Caching**: Response caching with appropriate TTL
- **Async**: Asynchronous request handling
- **Compression**: Response compression for large datasets
- **Health Checks**: Proactive health monitoring

### Frontend Level

- **React Query**: Intelligent caching and background updates
- **Lazy Loading**: On-demand data fetching
- **Optimistic Updates**: Immediate UI feedback
- **Error Boundaries**: Graceful error handling

## 🔧 Configuration Options

### Environment Variables

#### Data Service
```bash
SQL_SERVER=your-server.database.windows.net
SQL_DATABASE=WealthOpsDB
SQL_USERNAME=your-username  
SQL_PASSWORD=your-password
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8000
LOG_LEVEL=INFO
```

#### Frontend
```bash
NEXT_PUBLIC_USE_DATA_SERVICE=true
NEXT_PUBLIC_DATA_SERVICE_URL=http://localhost:8000
NEXT_PUBLIC_ENABLE_DEBUG_LOGS=true
NEXT_PUBLIC_API_TIMEOUT=10000
```

## 🧪 Testing

### Data Service Testing

```bash
cd backend/data_service

# Test database connection
python -c "from main import db_manager; db_manager.execute_query('SELECT 1')"

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/households/johnson-family-trust/overview
```

### Frontend Testing  

```bash
cd frontend

# Test with mock data (default)
npm run dev

# Test with data service
# Set NEXT_PUBLIC_USE_DATA_SERVICE=true in .env.local
npm run dev
```

## 🚀 Deployment

### Data Service Deployment

#### Docker
```bash
cd backend/data_service
docker build -t wealthops-data-service .
docker run -p 8000:8000 --env-file .env wealthops-data-service
```

#### Azure Container Apps
```bash
# Build and push to container registry
az acr build --registry wealthopsregistry --image data-service:latest .

# Deploy to Container Apps
az containerapp create \
  --name wealthops-data-service \
  --resource-group wealthops-rg \
  --environment wealthops-env \
  --image wealthopsregistry.azurecr.io/data-service:latest
```

### Frontend Deployment

```bash
cd frontend

# Build for production
npm run build

# Deploy to Azure Static Web Apps or Vercel
npm run deploy
```

## 📊 Monitoring and Logging

### Metrics to Monitor

- **API Response Times**: Average, P95, P99
- **Database Query Performance**: Slow query identification
- **Error Rates**: 4xx, 5xx responses
- **Cache Hit Rates**: Query cache effectiveness
- **Connection Pool Health**: Active/idle connections

### Log Levels

- **ERROR**: Database failures, API errors
- **WARN**: Fallback activations, slow queries
- **INFO**: Request logging, health checks
- **DEBUG**: Detailed query execution, cache operations

## 🔒 Security Considerations

### Database Security

- **Authentication**: SQL Authentication with strong passwords
- **Network**: Private endpoints and firewall rules
- **Encryption**: TLS in transit, TDE at rest
- **Backups**: Automated backups with point-in-time recovery

### API Security

- **CORS**: Configured for specific frontend origins
- **Input Validation**: SQL injection prevention
- **Rate Limiting**: API rate limiting (future enhancement)
- **Monitoring**: Request logging and anomaly detection

## 🛠️ Troubleshooting

### Common Issues

#### Data Service Won't Start
```bash
# Check database connectivity
telnet your-server.database.windows.net 1433

# Verify environment variables
cat .env

# Check Python dependencies
pip list
```

#### Frontend Not Loading Data
```bash
# Check environment configuration
cat frontend/.env.local

# Verify data service health
curl http://localhost:8000/health

# Check browser console for errors
```

#### Database Connection Errors
```sql
-- Test direct database connection
sqlcmd -S your-server.database.windows.net -d WealthOpsDB -U username -P password

-- Check firewall rules in Azure Portal
-- Verify connection string format
```

### Performance Issues

#### Slow Query Performance
```sql
-- Identify slow queries
SELECT * FROM sys.dm_exec_query_stats 
ORDER BY total_elapsed_time DESC;

-- Check index usage
SELECT * FROM sys.dm_db_index_usage_stats;
```

#### High Memory Usage
```bash
# Monitor data service memory
docker stats wealthops-data-service

# Check connection pool size
# Reduce pool size in configuration if needed
```

## 📚 API Reference

### Endpoints

#### GET /api/households/{id}/overview
Returns comprehensive household overview including assets, performance, and account counts.

#### GET /api/households/{id}/performance?range={3M|6M|1Y|3Y|5Y}  
Returns time-series performance data for the specified range.

#### GET /api/households/{id}/cash?range={3M|6M|1Y}
Returns cash account details and trend data.

#### GET /health
Health check endpoint with database status.

### Response Formats

All endpoints return JSON with consistent structure:
```json
{
  "data": {...},
  "source": "database|mock", 
  "timestamp": "2025-09-27T10:30:00Z"
}
```

## 🔮 Future Enhancements

### Phase 2 Features

- **Real-time Updates**: WebSocket connections for live data
- **Advanced Analytics**: Machine learning insights
- **Multi-tenancy**: Support for multiple organizations
- **Audit Trail**: Complete data change tracking
- **Performance Tuning**: Query optimization and caching layers

### Integration Opportunities

- **CRM Systems**: Salesforce, HubSpot integration
- **Custodial Data**: Direct feeds from Schwab, Fidelity
- **Market Data**: Real-time pricing and analytics
- **Reporting Tools**: Power BI, Tableau connectors

---

## 🆘 Support

For questions or issues:

1. **Check Documentation**: Review this README and API docs
2. **Health Checks**: Verify service and database health
3. **Logs**: Check application and database logs
4. **Fallback**: System automatically uses mock data if needed
5. **Contact**: Reach out to the development team

**Remember**: The system is designed to gracefully handle failures and continue operating with mock data when needed.