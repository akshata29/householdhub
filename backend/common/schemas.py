"""
Common schemas and models for the WealthOps Multi-Agent MVP
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any, Literal
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from enum import Enum


class AgentType(str, Enum):
    ORCHESTRATOR = "orchestrator"
    NL2SQL = "nl2sql"
    VECTOR = "vector"
    API = "api"
    FRONTEND = "frontend"


class IntentType(str, Enum):
    TOP_CASH = "TopCash"
    CASH_BALANCE = "CashBalance"  # New intent for specific cash balance queries
    CRM_POI = "CRMPOI"
    CUSTODIAL_18 = "Custodial18"
    RECON = "Recon"
    EXEC_SUMMARY = "ExecSummary"
    MISSING_BEN = "MissingBen"
    RMD = "RMD"
    IRA_REMINDER = "IRAReminder"
    PERF_SUMMARY = "PerfSummary"


class MessageStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    ERROR = "error"


# A2A Protocol Models
class A2AContext(BaseModel):
    household_id: Optional[str] = None
    account_id: Optional[str] = None
    auth: Dict[str, Any] = Field(default_factory=dict)


class A2AMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    from_agent: AgentType
    to_agents: List[AgentType]
    intent: IntentType
    payload: Dict[str, Any] = Field(default_factory=dict)
    context: A2AContext = Field(default_factory=A2AContext)
    status: MessageStatus = MessageStatus.PENDING


class A2AResponse(BaseModel):
    message_id: str
    correlation_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    from_agent: AgentType
    to_agent: AgentType
    status: MessageStatus
    result: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


# Business Domain Models
class Household(BaseModel):
    household_id: str
    name: str
    primary_advisor_id: Optional[str] = None


class Person(BaseModel):
    person_id: str
    household_id: str
    name: str
    relation: str
    dob: Optional[date] = None


class Account(BaseModel):
    account_id: str
    household_id: str
    type: str
    name: str
    cash: Decimal
    mv: Decimal  # market value
    currency: str = "USD"


class Position(BaseModel):
    account_id: str
    symbol: str
    qty: Decimal
    mv: Decimal
    asset_class: str


class AllocationTarget(BaseModel):
    household_id: str
    asset_class: str
    target_pct: float
    band_low: float
    band_high: float


class Beneficiary(BaseModel):
    account_id: str
    name: str
    relation: str
    pct: float
    status: str


class Contribution(BaseModel):
    account_id: str
    year: int
    ytd_contribution: Decimal
    limit: Decimal


class Performance(BaseModel):
    account_id: str
    date: date
    value: Decimal


class CRMNote(BaseModel):
    id: str
    account_id: Optional[str] = None
    household_id: Optional[str] = None
    text: str
    author: str
    created_at: datetime
    tags: List[str] = Field(default_factory=list)


# Query Request/Response Models
class QueryRequest(BaseModel):
    query: str
    household_id: Optional[str] = None
    account_id: Optional[str] = None
    user_context: Dict[str, Any] = Field(default_factory=dict)


class Citation(BaseModel):
    source: str  # e.g., "sql:households" or "search:crm-notes:abc123"
    description: str
    confidence: Optional[float] = None


class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    sql_generated: Optional[str] = None
    execution_time_ms: int
    agent_calls: List[str] = Field(default_factory=list)


class StreamingUpdate(BaseModel):
    type: Literal["status", "partial", "complete", "error"]
    content: str
    agent: Optional[AgentType] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# NL2SQL Agent Models
class NL2SQLRequest(BaseModel):
    query: str
    household_id: Optional[str] = None
    account_id: Optional[str] = None
    schema_hint: Optional[str] = None


class NL2SQLResponse(BaseModel):
    sql_query: str
    results: List[Dict[str, Any]]
    tables_used: List[str]
    row_count: int
    execution_time_ms: int


# Vector Agent Models
class VectorSearchRequest(BaseModel):
    query: str
    household_id: Optional[str] = None
    account_id: Optional[str] = None
    top_k: int = 5
    filters: Dict[str, Any] = Field(default_factory=dict)


class VectorSearchResult(BaseModel):
    id: str
    text: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VectorSearchResponse(BaseModel):
    results: List[VectorSearchResult]
    total_found: int
    query_time_ms: int


class PointOfInterest(BaseModel):
    date: date
    author: str
    poi: str
    why: str


# API Agent Models
class PlanPerformanceKPI(BaseModel):
    household_id: str
    total_aum: Decimal
    target_allocation: Dict[str, float]
    current_allocation: Dict[str, float]
    drift_analysis: Dict[str, float]
    last_updated: datetime


class PershingRealtimeData(BaseModel):
    account_id: str
    current_balance: Decimal
    pending_trades: int
    cash_available: Decimal
    margin_excess: Decimal
    flags: List[str] = Field(default_factory=list)
    last_updated: datetime


# Configuration Models
class DatabaseConfig(BaseModel):
    connection_string: str
    max_pool_size: int = 10
    query_timeout: int = 30


class AzureConfig(BaseModel):
    tenant_id: str
    subscription_id: str
    resource_group: str
    ai_search_endpoint: str
    azure_openai_endpoint: str
    service_bus_namespace: str
    storage_account_name: str
    key_vault_uri: str


class AppConfig(BaseModel):
    environment: str = "development"
    debug: bool = False
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    database: DatabaseConfig
    azure: AzureConfig