"""
WealthOps Data Service API
Production data layer for retrieving household wealth management data from Azure SQL
Provides fallback to mock data API when database is unavailable
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import pyodbc
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any, Union
import os
from pydantic import BaseModel, Field
import logging
import asyncio
from functools import lru_cache

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =====================================================
# CONFIGURATION
# =====================================================

class DatabaseConfig:
    """Database connection configuration"""
    def __init__(self):
        self.server = os.getenv("SQL_SERVER", "localhost")
        self.database = os.getenv("SQL_DATABASE", "WealthOpsDB")
        self.username = os.getenv("SQL_USERNAME", "sa")
        self.password = os.getenv("SQL_PASSWORD", "")
        self.driver = "{ODBC Driver 18 for SQL Server}"
        self.connection_timeout = 30
        self.command_timeout = 30
        
    @property
    def connection_string(self) -> str:
        return (
            f"DRIVER={self.driver};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=yes;"
            f"Connection Timeout={self.connection_timeout};"
        )

# =====================================================
# RESPONSE MODELS (matching frontend schemas)
# =====================================================

class HouseholdInfo(BaseModel):
    id: str
    name: str
    primary_advisor: str = Field(alias="primaryAdvisor")
    risk_profile: str = Field(alias="riskProfile")
    last_sync: str = Field(alias="lastSync")

class OverviewResponse(BaseModel):
    household: HouseholdInfo
    total_assets: float = Field(alias="totalAssets")
    ytd_return: float = Field(alias="ytdReturn")
    benchmark_return: float = Field(alias="benchmarkReturn")
    accounts_count: int = Field(alias="accountsCount")
    total_cash: float = Field(alias="totalCash")
    avg_cash_yield: float = Field(alias="avgCashYield")
    executive_summary: List[str] = Field(alias="executiveSummary")
    last_updated: str = Field(alias="lastUpdated")

class PerformanceDataPoint(BaseModel):
    date: str
    value: float
    benchmark: Optional[float] = None

class PerformanceResponse(BaseModel):
    data: List[PerformanceDataPoint]
    range: str
    total_return: float = Field(alias="totalReturn")
    benchmark_return: float = Field(alias="benchmarkReturn")
    volatility: float
    sharpe_ratio: float = Field(alias="sharpeRatio")

class Account(BaseModel):
    id: str
    name: str
    type: str
    balance: float
    apy: Optional[float] = None
    is_active: bool = Field(alias="isActive")
    institution: Optional[str] = None

class CashTrendDataPoint(BaseModel):
    date: str
    value: float

class CashResponse(BaseModel):
    accounts: List[Account]
    total_balance: float = Field(alias="totalBalance")
    avg_yield: float = Field(alias="avgYield")
    trend_data: List[CashTrendDataPoint] = Field(alias="trendData")
    alerts: List[Dict[str, Any]] = []

class HouseholdSummary(BaseModel):
    id: str
    name: str
    primary_contact: str = Field(alias="primaryContact")
    total_assets: float = Field(alias="totalAssets")
    total_cash: float = Field(alias="totalCash")
    accounts_count: int = Field(alias="accountsCount")
    last_activity: str = Field(alias="lastActivity")
    risk_profile: str = Field(alias="riskProfile")
    advisor_name: str = Field(alias="advisorName")
    status: str
    household_type: str = Field(alias="householdType")
    location: str
    join_date: str = Field(alias="joinDate")
    ytd_performance: float = Field(alias="ytdPerformance")
    monthly_income: float = Field(alias="monthlyIncome")
    recent_alerts: int = Field(alias="recentAlerts")
    next_review: str = Field(alias="nextReview")

class HouseholdsListResponse(BaseModel):
    households: List[HouseholdSummary]
    total_count: int = Field(alias="totalCount")
    summary_stats: Dict[str, Any] = Field(alias="summaryStats")

# =====================================================
# DATABASE CONNECTION AND UTILITIES
# =====================================================

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._connection_pool: List[pyodbc.Connection] = []
        self._pool_size = 5
        self._initialized = False
    
    async def initialize(self):
        """Initialize the connection pool"""
        if self._initialized:
            return
            
        logger.info("Initializing database connection pool...")
        try:
            # Test connection first
            conn = pyodbc.connect(self.config.connection_string)
            conn.close()
            self._initialized = True
            logger.info("Database connection successful")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def get_connection(self) -> pyodbc.Connection:
        """Get a database connection"""
        try:
            return pyodbc.connect(self.config.connection_string)
        except Exception as e:
            logger.error(f"Failed to get database connection: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dictionaries"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            # Get column names
            columns = [column[0] for column in cursor.description]
            
            # Fetch all rows and convert to dictionaries
            rows = cursor.fetchall()
            results = []
            
            for row in rows:
                row_dict = {}
                for i, value in enumerate(row):
                    # Handle datetime objects
                    if isinstance(value, datetime):
                        row_dict[columns[i]] = value.isoformat()
                    elif isinstance(value, date):
                        row_dict[columns[i]] = value.isoformat()
                    else:
                        row_dict[columns[i]] = value
                results.append(row_dict)
            
            return results
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
        finally:
            if conn:
                conn.close()

# =====================================================
# MOCK DATA FALLBACK
# =====================================================

class MockDataFallback:
    """Fallback to mock data when database is unavailable"""
    
    @staticmethod
    def get_overview(household_id: str) -> OverviewResponse:
        """Get mock overview data"""
        # This would import from your existing mock data
        mock_data = {
            "household": {
                "id": household_id,
                "name": "Mock Household",
                "primaryAdvisor": "Mock Advisor",
                "riskProfile": "Moderate",
                "lastSync": datetime.utcnow().isoformat()
            },
            "totalAssets": 2850000.00,
            "ytdReturn": 8.7,
            "benchmarkReturn": 7.8,
            "accountsCount": 12,
            "totalCash": 425000.00,
            "avgCashYield": 2.8,
            "executiveSummary": [
                "Mock data: Portfolio performance of 8.7% YTD",
                "Mock data: Total assets under management: $2.9M",
                "Mock data: Risk profile aligned with moderate strategy"
            ],
            "lastUpdated": datetime.utcnow().isoformat()
        }
        return OverviewResponse(**mock_data)
    
    @staticmethod
    def get_performance(household_id: str, range_period: str) -> PerformanceResponse:
        """Get mock performance data"""
        # Generate mock time series data
        days_map = {"3M": 90, "6M": 180, "1Y": 365, "3Y": 1095, "5Y": 1825}
        days = days_map.get(range_period, 180)
        
        data_points = []
        base_value = 2850000
        for i in range(min(days, 100)):  # Limit to 100 points
            date_point = datetime.now() - timedelta(days=days-i)
            volatility = (i * 0.001) + (i % 10) * 0.002
            value = base_value * (1 + volatility)
            benchmark = base_value * (1 + volatility * 0.9)
            
            data_points.append(PerformanceDataPoint(
                date=date_point.date().isoformat(),
                value=value,
                benchmark=benchmark
            ))
        
        return PerformanceResponse(
            data=data_points,
            range=range_period,
            totalReturn=8.7,
            benchmarkReturn=7.8,
            volatility=12.5,
            sharpeRatio=0.65
        )
    
    @staticmethod
    def get_cash(household_id: str, range_period: str) -> CashResponse:
        """Get mock cash data"""
        accounts = [
            Account(
                id=f"{household_id}-checking",
                name="Mock Checking Account",
                type="checking",
                balance=170000.00,
                apy=0.1,
                isActive=True,
                institution="Mock Bank"
            ),
            Account(
                id=f"{household_id}-savings",
                name="Mock Savings Account", 
                type="savings",
                balance=255000.00,
                apy=4.5,
                isActive=True,
                institution="Mock Savings"
            )
        ]
        
        # Generate trend data
        days_map = {"3M": 90, "6M": 180, "1Y": 365}
        days = days_map.get(range_period, 180)
        trend_data = []
        
        for i in range(min(days, 50)):  # Limit to 50 points
            date_point = datetime.now() - timedelta(days=days-i)
            value = 425000 + (i * 100) + ((i % 7) * 2000)
            trend_data.append(CashTrendDataPoint(
                date=date_point.date().isoformat(),
                value=value
            ))
        
        return CashResponse(
            accounts=accounts,
            totalBalance=425000.00,
            avgYield=2.8,
            trendData=trend_data,
            alerts=[]
        )

# =====================================================
# DATA ACCESS LAYER
# =====================================================

class DataService:
    """Main data service with database operations and fallback"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.fallback = MockDataFallback()
        self.use_fallback = False
    
    async def get_overview(self, household_id: str) -> OverviewResponse:
        """Get household overview data"""
        if self.use_fallback:
            logger.warning(f"Using fallback data for overview: {household_id}")
            return self.fallback.get_overview(household_id)
        
        try:
            query = """
            SELECT 
                h.HouseholdCode as id,
                h.Name,
                h.AdvisorName,
                h.RiskProfile,
                h.UpdatedAt as LastSync,
                h.TotalAssets,
                h.RecentAlerts,
                h.AccountsCount
            FROM vw_HouseholdSummary h
            WHERE h.HouseholdCode = ?
            """
            
            results = self.db.execute_query(query, (household_id,))
            
            if not results:
                raise HTTPException(status_code=404, detail="Household not found")
            
            row = results[0]
            
            # Get latest performance data
            perf_query = """
            SELECT TOP 1 TotalReturn, BenchmarkReturn 
            FROM PerformanceData 
            WHERE HouseholdID = (SELECT HouseholdID FROM Households WHERE HouseholdCode = ?)
            ORDER BY AsOfDate DESC
            """
            perf_results = self.db.execute_query(perf_query, (household_id,))
            
            ytd_return = perf_results[0]['TotalReturn'] if perf_results else 0.0
            benchmark_return = perf_results[0]['BenchmarkReturn'] if perf_results else 0.0
            
            # Get cash total
            cash_query = """
            SELECT ISNULL(SUM(a.Balance), 0) as TotalCash
            FROM Accounts a
                INNER JOIN AccountTypes at ON a.AccountTypeID = at.AccountTypeID
                INNER JOIN Households h ON a.HouseholdID = h.HouseholdID
            WHERE h.HouseholdCode = ? AND at.Category = 'cash' AND a.IsActive = 1
            """
            cash_results = self.db.execute_query(cash_query, (household_id,))
            total_cash = cash_results[0]['TotalCash'] if cash_results else 0.0
            
            household_info = HouseholdInfo(
                id=row['id'],
                name=row['Name'],
                primaryAdvisor=row['AdvisorName'] or 'Unknown',
                riskProfile=row['RiskProfile'] or 'Moderate',
                lastSync=row['LastSync'] or datetime.utcnow().isoformat()
            )
            
            return OverviewResponse(
                household=household_info,
                totalAssets=float(row['TotalAssets'] or 0),
                ytdReturn=float(ytd_return),
                benchmarkReturn=float(benchmark_return),
                accountsCount=int(row['AccountsCount'] or 0),
                totalCash=float(total_cash),
                avgCashYield=2.8,  # Could calculate from actual data
                executiveSummary=[
                    f"Portfolio performance of {ytd_return:.1f}% YTD",
                    f"Total assets under management: ${(row['TotalAssets'] or 0)/1000000:.1f}M",
                    f"Risk profile aligned with {row['RiskProfile'] or 'moderate'} strategy"
                ],
                lastUpdated=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Database error in get_overview: {e}")
            logger.warning(f"Falling back to mock data for: {household_id}")
            self.use_fallback = True
            return self.fallback.get_overview(household_id)
    
    async def get_performance(self, household_id: str, range_period: str = "6M") -> PerformanceResponse:
        """Get household performance data"""
        if self.use_fallback:
            return self.fallback.get_performance(household_id, range_period)
        
        try:
            # Calculate date range
            days_map = {"3M": 90, "6M": 180, "1Y": 365, "3Y": 1095, "5Y": 1825}
            days = days_map.get(range_period, 180)
            start_date = datetime.now() - timedelta(days=days)
            
            query = """
            SELECT 
                pd.AsOfDate as date,
                pd.PortfolioValue as value,
                pd.BenchmarkValue as benchmark,
                pd.TotalReturn,
                pd.BenchmarkReturn
            FROM PerformanceData pd
                INNER JOIN Households h ON pd.HouseholdID = h.HouseholdID
            WHERE h.HouseholdCode = ? AND pd.AsOfDate >= ?
            ORDER BY pd.AsOfDate
            """
            
            results = self.db.execute_query(query, (household_id, start_date.date()))
            
            if not results:
                logger.warning(f"No performance data found for {household_id}, using fallback")
                return self.fallback.get_performance(household_id, range_period)
            
            data_points = []
            for row in results:
                data_points.append(PerformanceDataPoint(
                    date=row['date'],
                    value=float(row['value']),
                    benchmark=float(row['benchmark']) if row['benchmark'] else None
                ))
            
            # Calculate metrics from the data
            latest_return = results[-1]['TotalReturn'] if results else 0.0
            latest_benchmark = results[-1]['BenchmarkReturn'] if results else 0.0
            
            # Simple volatility calculation (could be more sophisticated)
            if len(results) > 1:
                returns = [(results[i]['TotalReturn'] - results[i-1]['TotalReturn']) for i in range(1, len(results))]
                volatility = (sum([(r - sum(returns)/len(returns))**2 for r in returns]) / len(returns))**0.5 * 100
            else:
                volatility = 0.0
            
            sharpe_ratio = (latest_return - 2.0) / volatility if volatility > 0 else 0.0  # Assuming 2% risk-free rate
            
            return PerformanceResponse(
                data=data_points,
                range=range_period,
                totalReturn=float(latest_return),
                benchmarkReturn=float(latest_benchmark),
                volatility=float(volatility),
                sharpeRatio=float(sharpe_ratio)
            )
            
        except Exception as e:
            logger.error(f"Database error in get_performance: {e}")
            return self.fallback.get_performance(household_id, range_period)
    
    async def get_cash(self, household_id: str, range_period: str = "6M") -> CashResponse:
        """Get household cash data"""
        if self.use_fallback:
            return self.fallback.get_cash(household_id, range_period)
        
        try:
            # Get cash accounts
            accounts_query = """
            SELECT 
                CONCAT(h.HouseholdCode, '-', a.AccountCode) as id,
                a.Name,
                at.TypeName as type,
                a.Balance,
                a.APY as apy,
                a.IsActive,
                i.Name as institution
            FROM Accounts a
                INNER JOIN Households h ON a.HouseholdID = h.HouseholdID
                INNER JOIN AccountTypes at ON a.AccountTypeID = at.AccountTypeID
                LEFT JOIN Institutions i ON a.InstitutionID = i.InstitutionID
            WHERE h.HouseholdCode = ? AND at.Category = 'cash' AND a.IsActive = 1
            """
            
            account_results = self.db.execute_query(accounts_query, (household_id,))
            
            accounts = []
            total_balance = 0.0
            
            for row in account_results:
                account = Account(
                    id=row['id'],
                    name=row['Name'],
                    type=row['type'].lower().replace(' ', '-'),
                    balance=float(row['Balance']),
                    apy=float(row['apy']) if row['apy'] else None,
                    isActive=bool(row['IsActive']),
                    institution=row['institution']
                )
                accounts.append(account)
                total_balance += account.balance
            
            # Get trend data
            days_map = {"3M": 90, "6M": 180, "1Y": 365}
            days = days_map.get(range_period, 180)
            start_date = datetime.now() - timedelta(days=days)
            
            trend_query = """
            SELECT 
                ct.AsOfDate as date,
                ct.TotalCashBalance as value
            FROM CashTrendData ct
                INNER JOIN Households h ON ct.HouseholdID = h.HouseholdID
            WHERE h.HouseholdCode = ? AND ct.AsOfDate >= ?
            ORDER BY ct.AsOfDate
            """
            
            trend_results = self.db.execute_query(trend_query, (household_id, start_date.date()))
            
            trend_data = []
            for row in trend_results:
                trend_data.append(CashTrendDataPoint(
                    date=row['date'],
                    value=float(row['value'])
                ))
            
            # Calculate average yield
            weighted_yield = sum(acc.apy * acc.balance for acc in accounts if acc.apy) 
            avg_yield = weighted_yield / total_balance if total_balance > 0 else 0.0
            
            return CashResponse(
                accounts=accounts,
                totalBalance=total_balance,
                avgYield=avg_yield,
                trendData=trend_data,
                alerts=[]
            )
            
        except Exception as e:
            logger.error(f"Database error in get_cash: {e}")
            return self.fallback.get_cash(household_id, range_period)
    
    async def get_households(self) -> HouseholdsListResponse:
        """Get list of all households with summary information"""        
        try:
            query = """
            SELECT 
                HouseholdCode as id,
                Name,
                PrimaryContact,
                TotalAssets,
                TotalCash,
                AccountsCount,
                UpdatedAt as LastActivity,
                RiskProfile,
                AdvisorName,
                Status,
                HouseholdType,
                Location,
                JoinDate,
                YTDPerformance,
                MonthlyIncome,
                RecentAlerts,
                NextReviewDate
            FROM vw_HouseholdSummary
            ORDER BY TotalAssets DESC
            """
            
            results = self.db.execute_query(query)
            
            logger.info(f"Found {len(results)} households in database")
            
            households = []
            for row in results:
                households.append(HouseholdSummary(
                    id=row['id'],
                    name=row['Name'],
                    primaryContact=row['PrimaryContact'] or '',
                    totalAssets=float(row['TotalAssets'] or 0),
                    totalCash=float(row['TotalCash'] or 0),
                    accountsCount=int(row['AccountsCount'] or 0),
                    lastActivity=row['LastActivity'] or datetime.utcnow().isoformat(),
                    riskProfile=row['RiskProfile'] or 'Moderate',
                    advisorName=row['AdvisorName'] or 'Unknown',
                    status=row['Status'] or 'Active',
                    householdType=row['HouseholdType'] or 'Individual',
                    location=row['Location'] or '',
                    joinDate=row['JoinDate'] or '',
                    ytdPerformance=float(row['YTDPerformance'] or 0),
                    monthlyIncome=float(row['MonthlyIncome'] or 0),
                    recentAlerts=int(row['RecentAlerts'] or 0),
                    nextReview=row['NextReviewDate'] or ''
                ))
            
            # Calculate summary stats
            total_assets = sum(h.total_assets for h in households)
            total_cash = sum(h.total_cash for h in households)
            avg_performance = sum(h.ytd_performance for h in households) / len(households) if households else 0
            
            summary_stats = {
                "totalHouseholds": len(households),
                "totalAssets": total_assets,
                "totalCash": total_cash,
                "averagePerformance": avg_performance
            }
            
            return HouseholdsListResponse(
                households=households,
                totalCount=len(households),
                summaryStats=summary_stats
            )
            
        except Exception as e:
            logger.error(f"Database error in get_households: {e}")
            logger.warning("Falling back to mock data for households list")
            self.use_fallback = True
            return self._get_mock_households_list()
    
    def _get_mock_households_list(self) -> HouseholdsListResponse:
        """Generate mock households list response"""
        
        # Mock data for fallback - simplified version
        mock_households = [
            HouseholdSummary(
                id="international-family",
                name="Singh Global Family Office", 
                primaryContact="Arjun & Priya Singh",
                totalAssets=25000000.00,
                totalCash=3500000.00,
                accountsCount=45,
                lastActivity=datetime.utcnow().isoformat(),
                riskProfile="Moderate",
                advisorName="Michael Chen",
                status="Active",
                householdType="Trust",
                location="Los Angeles, CA",
                joinDate="2016-05-20",
                ytdPerformance=8.3,
                monthlyIncome=295000.00,
                recentAlerts=0,
                nextReview="2025-12-15"
            ),
            HouseholdSummary(
                id="johnson-family-trust",
                name="The Johnson Family Trust",
                primaryContact="Robert & Sarah Johnson",
                totalAssets=2850000.00,
                totalCash=425000.00,
                accountsCount=12,
                lastActivity=datetime.utcnow().isoformat(),
                riskProfile="Moderate",
                advisorName="Michael Chen",
                status="Active",
                householdType="Trust",
                location="San Francisco, CA",
                joinDate="2019-03-15",
                ytdPerformance=8.7,
                monthlyIncome=35000.00,
                recentAlerts=2,
                nextReview="2025-10-15"
            )
        ]
        
        total_assets = sum(h.total_assets for h in mock_households)
        total_cash = sum(h.total_cash for h in mock_households)
        avg_performance = sum(h.ytd_performance for h in mock_households) / len(mock_households)
        
        return HouseholdsListResponse(
            households=mock_households,
            totalCount=len(mock_households),
            summaryStats={
                "totalHouseholds": len(mock_households),
                "totalAssets": total_assets,
                "totalCash": total_cash,
                "averagePerformance": avg_performance
            }
        )

# =====================================================
# FASTAPI APPLICATION
# =====================================================

# Global instances
config = DatabaseConfig()
db_manager = DatabaseManager(config)
data_service = DataService(db_manager)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    try:
        await db_manager.initialize()
        logger.info("Data service started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        logger.warning("Starting in fallback mode")
        data_service.use_fallback = True
    
    yield
    
    # Shutdown
    logger.info("Data service shutting down")

app = FastAPI(
    title="WealthOps Data Service",
    description="Production data layer for household wealth management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# =====================================================
# API ENDPOINTS
# =====================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "WealthOps Data Service",
        "version": "1.0.0",
        "status": "healthy",
        "fallback_mode": data_service.use_fallback,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test database connection
        if not data_service.use_fallback:
            db_manager.execute_query("SELECT 1 as test")
            db_status = "connected"
        else:
            db_status = "fallback_mode"
            
        return {
            "status": "healthy",
            "database": db_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "degraded",
            "database": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/api/households", response_model=HouseholdsListResponse)
async def get_households():
    """Get list of all households with summary information"""
    return await data_service.get_households()

@app.get("/api/households/{household_id}/overview", response_model=OverviewResponse)
async def get_household_overview(household_id: str):
    """Get household overview data"""
    return await data_service.get_overview(household_id)

@app.get("/api/households/{household_id}/performance", response_model=PerformanceResponse)
async def get_household_performance(household_id: str, range: str = "6M"):
    """Get household performance data"""
    return await data_service.get_performance(household_id, range)

@app.get("/api/households/{household_id}/cash", response_model=CashResponse)
async def get_household_cash(household_id: str, range: str = "6M"):
    """Get household cash data"""
    return await data_service.get_cash(household_id, range)

# =====================================================
# MAIN (for development)
# =====================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8010,
        reload=True,
        log_level="info"
    )