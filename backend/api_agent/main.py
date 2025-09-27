"""
API Agent for mocking external services (Plan Performance, Pershing)
"""

import asyncio
import logging
import random
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from uuid import uuid4

from common.schemas import (
    A2AMessage, PlanPerformanceKPI, PershingRealtimeData, 
    AgentType, MessageStatus
)
from common.config import get_settings, get_cors_origins
from a2a.broker import create_broker

logger = logging.getLogger(__name__)


class SyntheticDataGenerator:
    """Generate synthetic data for external APIs."""
    
    def __init__(self):
        self.rng = random.Random(42)  # Seeded for consistency
        self.last_refresh = datetime.utcnow()
        
        # Cache for consistent data within refresh window
        self._household_kpis: Dict[str, PlanPerformanceKPI] = {}
        self._account_realtime: Dict[str, PershingRealtimeData] = {}
        
        # Asset classes and their typical ranges
        self.asset_classes = {
            'Equity': (0.4, 0.7),
            'Fixed Income': (0.2, 0.4), 
            'Alternatives': (0.0, 0.15),
            'Cash': (0.02, 0.1),
            'Real Estate': (0.0, 0.1)
        }
    
    def _refresh_if_needed(self):
        """Refresh data every 30 seconds for realism."""
        if datetime.utcnow() - self.last_refresh > timedelta(seconds=30):
            self._household_kpis.clear()
            self._account_realtime.clear()
            self.last_refresh = datetime.utcnow()
    
    def generate_household_kpis(self, household_id: str) -> PlanPerformanceKPI:
        """Generate Plan Performance KPIs for a household."""
        self._refresh_if_needed()
        
        if household_id not in self._household_kpis:
            # Generate consistent AUM based on household ID hash
            base_aum = abs(hash(household_id)) % 5000000 + 500000  # 500K to 5.5M
            
            # Add some randomness but keep it stable within refresh window
            self.rng.seed(abs(hash(household_id + str(int(self.last_refresh.timestamp() / 30)))))
            
            aum_variance = self.rng.uniform(0.95, 1.05)
            total_aum = Decimal(str(int(base_aum * aum_variance)))
            
            # Generate target allocation
            target_allocation = {}
            remaining = 1.0
            
            for i, (asset_class, (min_pct, max_pct)) in enumerate(self.asset_classes.items()):
                if i == len(self.asset_classes) - 1:
                    # Last asset class gets remaining
                    target_allocation[asset_class] = remaining
                else:
                    pct = self.rng.uniform(min_pct, min(max_pct, remaining))
                    target_allocation[asset_class] = pct
                    remaining -= pct
            
            # Generate current allocation with some drift
            current_allocation = {}
            for asset_class, target_pct in target_allocation.items():
                drift = self.rng.uniform(-0.15, 0.15)  # Up to 15% drift
                current_pct = max(0, min(1, target_pct + drift))
                current_allocation[asset_class] = current_pct
            
            # Normalize current allocation to sum to 1.0
            total_current = sum(current_allocation.values())
            if total_current > 0:
                for asset_class in current_allocation:
                    current_allocation[asset_class] /= total_current
            
            # Calculate drift analysis
            drift_analysis = {}
            for asset_class in target_allocation:
                drift = current_allocation[asset_class] - target_allocation[asset_class]
                drift_analysis[asset_class] = drift
            
            self._household_kpis[household_id] = PlanPerformanceKPI(
                household_id=household_id,
                total_aum=total_aum,
                target_allocation=target_allocation,
                current_allocation=current_allocation,
                drift_analysis=drift_analysis,
                last_updated=datetime.utcnow()
            )
        
        return self._household_kpis[household_id]
    
    def generate_account_realtime(self, account_id: str) -> PershingRealtimeData:
        """Generate Pershing real-time data for an account."""
        self._refresh_if_needed()
        
        if account_id not in self._account_realtime:
            # Generate consistent base data
            base_balance = abs(hash(account_id)) % 1000000 + 50000  # 50K to 1.05M
            
            # Add time-based variance
            self.rng.seed(abs(hash(account_id + str(int(self.last_refresh.timestamp() / 30)))))
            
            balance_variance = self.rng.uniform(0.98, 1.02)
            current_balance = Decimal(str(int(base_balance * balance_variance)))
            
            # Generate other fields
            pending_trades = self.rng.randint(0, 5)
            cash_pct = self.rng.uniform(0.02, 0.15)
            cash_available = current_balance * Decimal(str(cash_pct))
            
            margin_excess = Decimal('0')
            if self.rng.random() > 0.8:  # 20% chance of margin account
                margin_excess = current_balance * Decimal(str(self.rng.uniform(0.1, 0.3)))
            
            # Generate flags
            flags = []
            if pending_trades > 2:
                flags.append("HIGH_TRADE_VOLUME")
            if cash_pct < 0.05:
                flags.append("LOW_CASH")
            if current_balance > 1000000:
                flags.append("HIGH_VALUE_ACCOUNT")
            if margin_excess > 0:
                flags.append("MARGIN_ACCOUNT")
            if self.rng.random() > 0.9:
                flags.append("REQUIRES_ATTENTION")
            
            self._account_realtime[account_id] = PershingRealtimeData(
                account_id=account_id,
                current_balance=current_balance,
                pending_trades=pending_trades,
                cash_available=cash_available,
                margin_excess=margin_excess,
                flags=flags,
                last_updated=datetime.utcnow()
            )
        
        return self._account_realtime[account_id]


class APIAgent:
    """API Agent service for external API mocking."""
    
    def __init__(self):
        self.settings = get_settings()
        self.data_generator = SyntheticDataGenerator()
        self.broker = create_broker("api-agent")
        
        # Register message handlers
        self.broker.register_handler("PerfSummary", self.handle_performance_summary)
        self.broker.register_handler("Recon", self.handle_reconciliation_data)
    
    async def handle_performance_summary(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle performance summary requests."""
        try:
            household_id = message.context.household_id
            if not household_id:
                raise ValueError("household_id required for performance summary")
            
            # Get Plan Performance data
            kpis = self.data_generator.generate_household_kpis(household_id)
            
            # Generate performance metrics
            performance_data = {
                'household_id': household_id,
                'total_aum': float(kpis.total_aum),
                'allocation_analysis': {
                    'target': kpis.target_allocation,
                    'current': kpis.current_allocation,
                    'drift': kpis.drift_analysis
                },
                'performance_metrics': {
                    'ytd_return': random.uniform(-0.05, 0.15),
                    'qoq_return': random.uniform(-0.03, 0.08),
                    'trailing_12m': random.uniform(-0.1, 0.2),
                    'since_inception': random.uniform(0.04, 0.12)
                },
                'risk_metrics': {
                    'beta': random.uniform(0.8, 1.2),
                    'volatility': random.uniform(0.1, 0.25),
                    'sharpe_ratio': random.uniform(0.5, 1.8),
                    'max_drawdown': random.uniform(-0.15, -0.03)
                },
                'last_updated': datetime.utcnow().isoformat()
            }
            
            return performance_data
            
        except Exception as e:
            logger.error(f"Performance summary failed: {e}")
            raise
    
    async def handle_reconciliation_data(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle reconciliation data requests."""
        try:
            household_id = message.context.household_id
            account_ids = message.payload.get('account_ids', [])
            
            if not household_id:
                raise ValueError("household_id required for reconciliation")
            
            # Get household KPIs
            kpis = self.data_generator.generate_household_kpis(household_id)
            
            # Get account-level data if requested
            account_data = []
            for account_id in account_ids[:10]:  # Limit to 10 accounts
                realtime_data = self.data_generator.generate_account_realtime(account_id)
                account_data.append({
                    'account_id': account_id,
                    'current_balance': float(realtime_data.current_balance),
                    'cash_available': float(realtime_data.cash_available),
                    'pending_trades': realtime_data.pending_trades,
                    'flags': realtime_data.flags,
                    'last_updated': realtime_data.last_updated.isoformat()
                })
            
            return {
                'household_id': household_id,
                'household_summary': {
                    'total_aum': float(kpis.total_aum),
                    'allocation_drift': kpis.drift_analysis,
                    'largest_drift': max(kpis.drift_analysis.values(), key=abs) if kpis.drift_analysis else 0
                },
                'account_details': account_data,
                'reconciliation_flags': [
                    flag for account in account_data 
                    for flag in account.get('flags', [])
                ],
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Reconciliation data failed: {e}")
            raise


# Global agent instance
agent: Optional[APIAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    global agent
    
    # Startup
    logger.info("Starting API Agent")
    agent = APIAgent()
    
    # Start message broker in background
    asyncio.create_task(agent.broker.start_listening())
    
    yield
    
    # Shutdown
    if agent:
        await agent.broker.close()
    logger.info("API Agent stopped")


# FastAPI application
app = FastAPI(
    title="API Agent",
    description="Mock API Agent for external services (Plan Performance, Pershing)",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "agent": "api"}


# Plan Performance API endpoints
@app.get("/plan-performance/households/{household_id}/kpis", response_model=Dict[str, Any])
async def get_household_kpis(
    household_id: str = Path(..., description="Household ID")
):
    """Get Plan Performance KPIs for a household."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        kpis = agent.data_generator.generate_household_kpis(household_id)
        
        return {
            'household_id': kpis.household_id,
            'total_aum': float(kpis.total_aum),
            'target_allocation': kpis.target_allocation,
            'current_allocation': kpis.current_allocation,
            'drift_analysis': kpis.drift_analysis,
            'performance_summary': {
                'ytd_return_pct': random.uniform(-5, 15),
                'qoq_return_pct': random.uniform(-3, 8),
                'volatility_pct': random.uniform(10, 25),
                'sharpe_ratio': random.uniform(0.5, 1.8)
            },
            'last_updated': kpis.last_updated.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get household KPIs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/plan-performance/households/{household_id}/allocation-analysis")
async def get_allocation_analysis(household_id: str):
    """Get detailed allocation analysis for a household."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        kpis = agent.data_generator.generate_household_kpis(household_id)
        
        # Calculate detailed drift analysis
        analysis = []
        for asset_class, target_pct in kpis.target_allocation.items():
            current_pct = kpis.current_allocation[asset_class]
            drift_pct = kpis.drift_analysis[asset_class]
            
            status = "In Range"
            if abs(drift_pct) > 0.1:  # More than 10% drift
                status = "Over Threshold"
            elif abs(drift_pct) > 0.05:  # More than 5% drift
                status = "Monitor"
            
            analysis.append({
                'asset_class': asset_class,
                'target_pct': target_pct,
                'current_pct': current_pct,
                'drift_pct': drift_pct,
                'drift_amount': float(kpis.total_aum) * drift_pct,
                'status': status,
                'rebalance_required': abs(drift_pct) > 0.1
            })
        
        return {
            'household_id': household_id,
            'total_aum': float(kpis.total_aum),
            'analysis': analysis,
            'overall_status': 'Rebalance Required' if any(a['rebalance_required'] for a in analysis) else 'In Range',
            'last_updated': kpis.last_updated.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get allocation analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Pershing API endpoints
@app.get("/pershing/accounts/{account_id}/realtime", response_model=Dict[str, Any])
async def get_account_realtime(
    account_id: str = Path(..., description="Account ID")
):
    """Get Pershing real-time data for an account."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        realtime_data = agent.data_generator.generate_account_realtime(account_id)
        
        return {
            'account_id': realtime_data.account_id,
            'current_balance': float(realtime_data.current_balance),
            'pending_trades': realtime_data.pending_trades,
            'cash_available': float(realtime_data.cash_available),
            'margin_excess': float(realtime_data.margin_excess),
            'flags': realtime_data.flags,
            'market_hours': {
                'is_open': 9 <= datetime.now().hour < 16 and datetime.now().weekday() < 5,
                'next_open': 'Next business day 9:00 AM EST' if datetime.now().weekday() >= 5 else 'Today 9:00 AM EST'
            },
            'last_updated': realtime_data.last_updated.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get account realtime data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/pershing/accounts/{account_id}/positions")
async def get_account_positions(account_id: str):
    """Get account positions (mock data)."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        realtime_data = agent.data_generator.generate_account_realtime(account_id)
        
        # Generate mock positions
        symbols = ['SPY', 'QQQ', 'VTI', 'BND', 'VEA', 'VWO', 'GLD', 'CASH']
        positions = []
        
        remaining_balance = float(realtime_data.current_balance)
        
        for i, symbol in enumerate(symbols):
            if remaining_balance <= 0:
                break
                
            if symbol == 'CASH':
                # Cash position
                positions.append({
                    'symbol': 'CASH',
                    'quantity': 1,
                    'market_value': float(realtime_data.cash_available),
                    'unit_price': 1.0,
                    'asset_class': 'Cash',
                    'last_updated': datetime.utcnow().isoformat()
                })
                break
            else:
                # Generate mock position
                allocation_pct = random.uniform(0.05, 0.3)
                position_value = min(remaining_balance * allocation_pct, remaining_balance)
                
                if position_value > 1000:  # Only create position if > $1000
                    unit_price = random.uniform(50, 500)
                    quantity = position_value / unit_price
                    
                    asset_class = {
                        'SPY': 'Equity', 'QQQ': 'Equity', 'VTI': 'Equity',
                        'BND': 'Fixed Income', 'VEA': 'Equity', 'VWO': 'Equity',
                        'GLD': 'Alternatives'
                    }.get(symbol, 'Equity')
                    
                    positions.append({
                        'symbol': symbol,
                        'quantity': round(quantity, 2),
                        'market_value': round(position_value, 2),
                        'unit_price': round(unit_price, 2),
                        'asset_class': asset_class,
                        'day_change_pct': random.uniform(-3, 3),
                        'last_updated': datetime.utcnow().isoformat()
                    })
                    
                    remaining_balance -= position_value
        
        return {
            'account_id': account_id,
            'positions': positions,
            'total_market_value': float(realtime_data.current_balance),
            'position_count': len(positions),
            'last_updated': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get account positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data/refresh")
async def refresh_synthetic_data():
    """Force refresh of synthetic data."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    agent.data_generator._household_kpis.clear()
    agent.data_generator._account_realtime.clear()
    agent.data_generator.last_refresh = datetime.utcnow()
    
    return {"message": "Synthetic data refreshed", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)