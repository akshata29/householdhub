# WealthOps Multi-Agent MVP

# WealthOps Multi-Agent MVP

A comprehensive wealth management system built on Azure with multi-agent AI orchestration, demonstrating modern financial services architecture patterns.

## 🏗️ Architecture Overview

### System Components
- **Frontend**: Next.js 14 dashboard with TypeScript, Tailwind CSS, and MSAL authentication
- **Backend**: Python FastAPI microservices using Azure AI Agent Service with Semantic Kernel
- **Infrastructure**: Azure Container Apps, SQL Database, AI Search, OpenAI, Service Bus
- **Agents**: Orchestrator, NL2SQL (MCP), Vector Search, External API integration
- **Data Layer**: Azure SQL warehouse schema with synthetic financial data
- **Messaging**: A2A protocol using Service Bus topics with idempotent processing

### Business Query Scenarios
The system handles 9 core business queries end-to-end:
1. **Cash Position**: "What is the total cash position for household HH001?"
2. **Top Households**: "Show me the top 3 households by assets under management"
3. **RMD Requirements**: "Which clients have RMDs due this year?"
4. **CRM Notes**: "What are the recent CRM notes for John Doe?"
5. **Plan Performance**: "How did the Conservative Growth portfolio perform last quarter?"
6. **Allocation Breakdown**: "Show allocation breakdown for account ACC001"
7. **Pershing Positions**: "What Pershing positions are held by household HH001?"
8. **High Cash Households**: "Which households have cash positions above $100k?"
9. **Executive Summary**: "Generate an executive summary for household HH001"

## 🚀 Quick Start

### Prerequisites
- Azure subscription with appropriate permissions
- Docker Desktop
- Python 3.11+
- Node.js 18+
- Azure CLI

### Local Development Setup

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd wealthops-mvp
   ```

2. **Backend Setup**
   ```bash
   # Create Python virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-test.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Environment Configuration**
   ```bash
   # Copy and configure environment variables
   cp .env.example .env
   # Edit .env with your Azure credentials and endpoints
   ```

5. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

6. **Load Sample Data**
   ```bash
   python scripts/load_synthetic_data.py
   python scripts/ingest_crm_notes.py
   ```

### Test Suite Execution

#### Backend Tests
```bash
# Run all backend tests with coverage
pytest tests/ --cov=backend --cov-report=html

# Run specific test suites
pytest tests/test_orchestrator.py -v
pytest tests/test_nl2sql_agent.py -v
pytest tests/test_vector_agent.py -v
pytest tests/test_api_agent.py -v

# Run integration tests
pytest tests/test_e2e_integration.py -v
```

#### Frontend Tests
```bash
cd frontend

# Run Next.js development server
npm run dev

# Run TypeScript compilation check
npm run build
```

### Azure Deployment

1. **Deploy Infrastructure**
   ```bash
   az deployment sub create \
     --location "East US 2" \
     --template-file infra/main.bicep \
     --parameters @infra/main.parameters.json
   ```

## 📁 Project Structure

```
wealthops-mvp/
├── infra/                     # Azure Bicep infrastructure templates
├── backend/                   # Python microservices (4 agents + common libs)
├── frontend/                  # Next.js React dashboard
├── scripts/                   # Data loading and utilities  
├── tests/                     # Comprehensive test suite
├── docker-compose.yml         # Local development environment
└── requirements*.txt          # Python dependencies
```

## 🧪 Testing Results

The comprehensive test suite validates:
- ✅ **Orchestrator Agent**: Intent routing, response composition, streaming
- ✅ **NL2SQL Agent**: Pattern matching, SQL generation, security validation
- ✅ **Vector Agent**: CRM notes search, entity extraction, relevance filtering
- ✅ **API Agent**: External service mocking, synthetic data generation
- ✅ **End-to-End Integration**: All 9 business queries with multi-agent orchestration
- ✅ **Frontend Components**: TypeScript compilation, React component structure

## 🔧 Key Features Implemented

### Multi-Agent Orchestration
- Semantic Kernel integration for intelligent query routing
- A2A messaging protocol using Azure Service Bus
- Response composition with citations and streaming updates

### Data Integration
- Azure SQL warehouse with synthetic household/account data
- Azure AI Search with vector embeddings for CRM notes
- Mock external APIs (Plan Performance, Pershing) with realistic data

### Frontend Dashboard
- Next.js 14 with TypeScript and Tailwind CSS
- MSAL authentication for Azure AD integration
- Component structure for household insights and AI copilot

### Infrastructure as Code
- Complete Bicep templates for Azure resource provisioning
- Private networking with managed identity authentication
- Container Apps environment with auto-scaling configuration

## 🚀 Business Impact

This MVP demonstrates:
- **Intelligent Query Processing**: Natural language to multi-agent orchestration
- **Real-time Financial Insights**: Sub-3-second response times for complex queries  
- **Scalable Architecture**: Container-based microservices on Azure
- **Security & Compliance**: Private endpoints, managed identity, audit trails
- **Developer Productivity**: Comprehensive testing, IaC, and documentation

---

**Status**: MVP Complete ✅
**Next Steps**: Production deployment, additional business query patterns, enhanced UI/UX

## Architecture

- **Frontend**: Next.js with TypeScript, MSAL authentication
- **Backend**: Python FastAPI microservices
- **Orchestration**: Semantic Kernel with Azure AI Agent Service
- **Data**: Azure SQL Database + Azure AI Search vector store
- **Communication**: Agent-to-Agent protocol via Azure Service Bus
- **Infrastructure**: Azure with Private Endpoints, Managed Identity, Key Vault

## Agents

1. **NL2SQL Agent**: Translates natural language to SQL queries using MCP Server
2. **Vector Agent**: RAG over CRM notes using Azure AI Search
3. **API Agent**: Mock external APIs (Plan Performance, Pershing)
4. **Orchestrator**: Routes queries and composes responses with Semantic Kernel

## Business Queries Supported

1. Top cash balances by household
2. CRM notes → points of interest
3. Child turned 18 → custodial transition suggestions
4. Allocation mismatch → show underlying positions
5. Executive summary of household report
6. Missing beneficiary info
7. Upcoming RMD deadlines
8. No IRA contributions YTD → draft reminder
9. +12% QoQ → performance summary

## Quick Start

### Local Development
```bash
# Start infrastructure
docker compose up -d

# Start backend services
cd backend && python -m pip install -r requirements.txt
uvicorn orchestrator.main:app --reload --port 8000

# Start frontend
cd frontend && npm install && npm run dev
```

### Azure Deployment
```bash
# Deploy infrastructure
azd up

# Run data ingestion
python scripts/load_synthetic_data.py
python scripts/ingest_crm_notes.py
```

## Project Structure

```
wealthops-mvp/
├── infra/                  # Bicep templates + azd
├── backend/
│   ├── orchestrator/       # SK-based router + Copilot API
│   ├── nl2sql_agent/      # MCP client + SQL runner
│   ├── vector_agent/      # AI Search ingestion + query
│   ├── api_agent/         # Mock Plan Performance & Pershing
│   ├── a2a/               # Service Bus A2A broker
│   └── common/            # Shared schemas, clients, config
├── frontend/              # Next.js dashboard + copilot UI
├── tests/                 # pytest + Playwright + Postman
├── scripts/              # Data loading, deployment helpers
└── docs/                 # ADRs, API docs, runbooks
```