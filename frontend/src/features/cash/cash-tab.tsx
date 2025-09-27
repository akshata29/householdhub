"use client";

import * as React from "react";
import { useCash } from "@/lib/queries";
import { TimeSeriesCard } from "@/components/ui/time-series-card";
import { AccountsList } from "@/components/ui/accounts-list";
import { KPICard } from "@/components/ui/kpi-card";
import { 
  Wallet,
  TrendingUp,
  AlertTriangle,
  DollarSign,
  Percent,
} from "lucide-react";
import { formatCurrency, formatPercentage } from "@/lib/utils";

interface CashTabProps {
  householdId: string;
}

function CashAlerts({ alerts }: { alerts: any[] }) {
  if (!alerts || alerts.length === 0) {
    return null;
  }

  return (
    <div className="alerts-container">
      {alerts.map((alert, index) => (
        <div key={index} className={`alert alert-${alert.severity}`}>
          <div className="alert-icon">
            <AlertTriangle className="icon" />
          </div>
          <div className="alert-content">
            <div className="alert-message">{alert.message}</div>
            <div className="alert-type">{alert.type}</div>
          </div>
        </div>
      ))}
    </div>
  );
}



export function CashTab({ householdId }: CashTabProps) {
  const [trendRange, setTrendRange] = React.useState("6M");
  
  const { 
    data: cashData, 
    isLoading: cashLoading, 
    error: cashError 
  } = useCash(householdId, trendRange);

  if (cashLoading) {
    return (
      <div className="cash-container">
        <div className="loading-state">Loading cash management data...</div>
      </div>
    );
  }

  if (cashError) {
    return (
      <div className="cash-container">
        <div className="error-state">
          <h3>Failed to Load Cash Data</h3>
          <p>{cashError.message}</p>
        </div>
      </div>
    );
  }

  if (!cashData) {
    return (
      <div className="cash-container">
        <div className="empty-state">
          <h3>No Cash Data Available</h3>
          <p>Cash management data could not be loaded.</p>
        </div>
      </div>
    );
  }

  // Transform trend data for the chart
  const trendChartData = cashData.trendData?.map(item => ({
    date: item.date,
    value: item.balance,
    benchmark: cashData.totalBalance, // Use current total as benchmark
  })) || [];

  return (
    <div className="cash-container">
      {/* Header */}
      <div className="cash-header">
        <h1 className="cash-title">Cash Management</h1>
        <p className="cash-subtitle">Liquidity overview and cash account management</p>
      </div>

      {/* Alerts */}
      <CashAlerts alerts={cashData.alerts || []} />

      {/* KPI Cards */}
      <div className="kpi-grid">
        <KPICard
          label="Total Cash Balance"
          value={cashData.totalBalance}
          format="currency"
          icon={DollarSign}
        />
        <KPICard
          label="Average Yield"
          value={cashData.avgYield}
          format="percentage"
          icon={Percent}
        />
        <KPICard
          label="Cash Accounts"
          value={cashData.accounts?.length || 0}
          format="number"
          icon={Wallet}
        />
      </div>

      {/* Charts and Accounts Row */}
      <div className="chart-row">
        {/* Cash Balance Trend */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Cash Balance Trend</h3>
            <div className="performance-range-buttons">
              {["3M", "6M", "1Y"].map((range) => (
                <button
                  key={range}
                  className={`btn ${trendRange === range ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setTrendRange(range)}
                >
                  {range}
                </button>
              ))}
            </div>
          </div>
          <TimeSeriesCard
            title=""
            data={trendChartData}
            loading={false}
            error={undefined}
          />
        </div>

        {/* Cash Accounts */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Cash Accounts</h3>
            <p className="card-description">Your liquid accounts and CDs</p>
          </div>
          <AccountsList
            title=""
            accounts={cashData.accounts || []}
            loading={false}
            error={undefined}
          />
        </div>
      </div>

      {/* Account Type Breakdown */}
      <div className="account-breakdown">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Account Type Breakdown</h3>
            <p className="card-description">Cash allocation by account type</p>
          </div>
          <div className="breakdown-grid">
            {cashData.accounts?.reduce((acc, account) => {
              const existing = acc.find(item => item.type === account.type);
              if (existing) {
                existing.balance += account.balance;
                existing.count += 1;
              } else {
                acc.push({
                  type: account.type,
                  balance: account.balance,
                  count: 1,
                });
              }
              return acc;
            }, [] as { type: string; balance: number; count: number }[])?.map((breakdown) => (
              <div key={breakdown.type} className="breakdown-item">
                <div className="breakdown-header">
                  <span className="breakdown-type">{breakdown.type.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                  <span className="breakdown-count">{breakdown.count} account{breakdown.count !== 1 ? 's' : ''}</span>
                </div>
                <div className="breakdown-amount">
                  {formatCurrency(breakdown.balance)}
                </div>
                <div className="breakdown-percentage">
                  {formatPercentage(breakdown.balance / cashData.totalBalance)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}