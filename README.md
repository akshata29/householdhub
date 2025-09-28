# WealthOps - Intelligent Wealth Management Platform

<div align="center">

**An enterprise-grade wealth management platform powered by Azure multi-agent AI orchestration**

[![Azure](https://img.shields.io/badge/Azure-0078D4?style=for-the-badge&logo=microsoft-azure&logoColor=white)](https://azure.microsoft.com/)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

</div>

---

## 🌟 Business Overview

WealthOps transforms wealth management through intelligent AI-driven insights and comprehensive financial data orchestration. Designed for financial advisors, wealth managers, and family offices, the platform delivers real-time portfolio analytics, automated compliance monitoring, and personalized client intelligence.

### Key Business Value Propositions

- **🎯 Intelligent Query Processing**: Natural language interface for complex financial queries
- **📊 Real-Time Portfolio Analytics**: Instant insights across households, accounts, and investment positions
- **🔍 Advanced Client Intelligence**: AI-powered CRM analysis and relationship management
- **⚡ Sub-3-Second Response Times**: High-performance architecture for time-sensitive decisions
- **🛡️ Enterprise Security**: Azure-native security with private endpoints and managed identity
- **📈 Scalable Architecture**: Cloud-native microservices designed for growing wealth management firms

## 🚀 Platform Features & Screenshots

### 📱 Modern Dashboard Interface
![Homepage Overview](docs/images/homepage.jpg)
*Clean, intuitive interface providing quick access to all platform features with real-time data visualization*

### 💰 Cash Management & Liquidity Analysis
![Cash Management](docs/images/CashManagement.jpg)
*Comprehensive cash position tracking, liquidity analysis, and cash flow projections across all household accounts*

### 📈 Portfolio & Asset Management
![Portfolio Management](docs/images/Portfolio.jpg)
*Detailed portfolio analytics including allocation breakdowns, performance metrics, and risk assessment tools*

### 📊 Advanced Reporting & Analytics
![Reports Dashboard](docs/images/Reports.jpg)
*Sophisticated reporting capabilities with customizable dashboards and automated compliance reporting*

### 🎯 Financial Planning Tools
![Financial Planning](docs/images/Planning.jpg)
*Integrated planning modules for retirement planning, tax optimization, and goal-based wealth management*

### 📋 Executive Overview Dashboard
![Executive Overview](docs/images/Overview.jpg)
*High-level executive dashboard providing key performance indicators and portfolio summaries*

### 🤖 AI-Powered Copilot Assistant
![AI Copilot](docs/images/Copilot.jpg)
*Natural language query interface powered by multi-agent AI for instant financial insights and analysis*

![Copilot Response](docs/images/CopilotResponse.jpg)
*Intelligent response generation with contextual financial data and actionable recommendations*

![Copilot Citations](docs/images/CopilotCitation.jpg)
*Transparent AI responses with source citations and data provenance for compliance and verification*

## 🏗️ Technical Architecture

### Multi-Agent AI Orchestration
- **Orchestrator Agent**: Semantic Kernel-based intent routing and response composition
- **NL2SQL Agent**: Natural language to SQL translation using Model Context Protocol (MCP)
- **Vector Search Agent**: RAG-enabled CRM notes and document search
- **API Integration Agent**: External service integration and data enrichment

### Technology Stack
- **Frontend**: Next.js 14 with TypeScript, Tailwind CSS, and Azure AD MSAL authentication
- **Backend**: Python FastAPI microservices with Azure AI Agent Service integration
- **Infrastructure**: Azure Container Apps, SQL Database, AI Search, OpenAI, Service Bus
- **Data Layer**: Azure SQL warehouse with comprehensive financial data schema
- **Messaging**: Agent-to-Agent (A2A) protocol using Azure Service Bus with idempotent processing

## 🚀 Getting Started

### Prerequisites

Ensure you have the following tools and services ready before beginning:

- **Azure Subscription** with appropriate permissions for Container Apps, SQL Database, AI Services
- **Docker Desktop** for local containerized development
- **Python 3.11+** with pip package manager
- **Node.js 18+** with npm for frontend development
- **Azure CLI** for infrastructure deployment and management

### Local Development Setup

#### 1. Repository Setup
```powershell
# Clone the repository
git clone <repository-url>
cd wealthops
```

#### 2. Backend Environment Setup
```powershell
# Navigate to backend directory
cd backend

# Create and activate Python virtual environment
python -m venv venv
venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

#### 3. Frontend Environment Setup
```powershell
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Return to root directory
cd ..
```

#### 4. Environment Configuration
```powershell
# Copy environment template and configure
cp .env.example .env
# Edit .env file with your Azure credentials and service endpoints
```

#### 5. Local Development Launch
```powershell
# Start all backend services using Docker Compose
cd backend/start-all.ps1

# Load synthetic financial data
database/00_create_and_insert.sql
database/01_add_remaining_household_data.sql
```

#### 6. Verify Installation
- **Frontend**: Navigate to `http://localhost:3000`
- **Backend API**: Access `http://localhost:9000/docs` for FastAPI documentation
- **Health Checks**: All services should report healthy status

## 📁 Project Structure

```
wealthops/
├── 📁 infra/                    # Azure Bicep infrastructure as code
│   ├── main.bicep              # Main infrastructure template
│   ├── containerapp.bicep      # Container Apps configuration
│   └── main.parameters.bicep   # Environment-specific parameters
│
├── 📁 backend/                 # Python microservices ecosystem
│   ├── orchestrator/           # Multi-agent orchestration service
│   ├── nl2sql_agent/          # Natural language to SQL translation
│   ├── vector_agent/          # CRM search and RAG capabilities
│   ├── api_agent/             # External API integration service
│   ├── data_service/          # Data access and management layer
│   ├── a2a/                   # Agent-to-Agent messaging protocol
│   └── common/                # Shared utilities and configurations
│
├── 📁 frontend/               # Next.js wealth management dashboard
│   ├── src/app/              # Application routing and pages
│   ├── src/components/       # Reusable UI components
│   ├── src/features/         # Feature-specific modules
│   └── public/               # Static assets and resources
│
├── 📁 database/              # SQL schema and sample data
├── 📁 scripts/               # Data loading and utility scripts
├── 📁 tests/                 # Comprehensive test suite
├── 📁 docs/                  # Documentation and architecture guides
│   ├── images/               # UI screenshots and diagrams
│   └── *.md                  # Technical documentation
│
├── docker-compose.yml        # Local development environment
├── azure.yaml               # Azure Developer CLI configuration
└── pyproject.toml           # Python project configuration
```

## �️ Core Platform Capabilities

### 🤖 Intelligent AI Orchestration
- **Multi-Agent Coordination**: Semantic Kernel-powered orchestrator managing specialized AI agents
- **Natural Language Processing**: Advanced NLP for financial query interpretation and response generation
- **Real-Time Streaming**: WebSocket-enabled streaming responses for immediate user feedback
- **Context-Aware Routing**: Intelligent query classification and agent selection

### 📊 Advanced Data Integration
- **Azure SQL Warehouse**: Comprehensive financial data schema supporting complex household hierarchies
- **Vector Search Engine**: Azure AI Search with hybrid retrieval for CRM notes and documents
- **Synthetic Data Generation**: Realistic financial data sets for development and testing

### Enhanced Client Service
- **Proactive Insights**: AI-driven identification of portfolio optimization opportunities
- **Instant Analytics**: Real-time portfolio performance and risk assessment
- **Comprehensive Views**: Unified household perspective across all accounts and relationships
- **Compliance Automation**: Automated RMD monitoring and regulatory requirement tracking
