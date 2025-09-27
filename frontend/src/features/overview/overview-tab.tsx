"use client";

import * as React from "react";
import { useOverview, usePerformance, useAllocation, useActivity, useCash } from "@/lib/queries";
import { PageHeader } from "@/components/ui/page-header";
import { KPICard } from "@/components/ui/kpi-card";
import { TimeSeriesCard } from "@/components/ui/time-series-card";
import { DonutCard } from "@/components/ui/donut-card";
import { FeedCard } from "@/components/ui/feed-card";
import { AccountsList } from "@/components/ui/accounts-list";
import { ErrorState } from "@/components/ui/error-state";
import { KPISkeleton, CardSkeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  DollarSign,
  TrendingUp,
  Building2,
  Wallet,
} from "lucide-react";
import { formatCurrency, formatPercentage } from "@/lib/utils";

interface OverviewTabProps {
  householdId: string;
}

export function OverviewTab({ householdId }: OverviewTabProps) {
  const [performanceRange, setPerformanceRange] = React.useState("6M");
  
  const { 
    data: overview, 
    isLoading: overviewLoading, 
    error: overviewError,
    refetch: refetchOverview
  } = useOverview(householdId);
  
  const { 
    data: performance, 
    isLoading: performanceLoading, 
    error: performanceError 
  } = usePerformance(householdId, performanceRange);
  
  const { 
    data: allocation, 
    isLoading: allocationLoading, 
    error: allocationError 
  } = useAllocation(householdId);
  
  const { 
    data: activity, 
    isLoading: activityLoading, 
    error: activityError 
  } = useActivity(householdId, 5);
  
  const { 
    data: cash, 
    isLoading: cashLoading, 
    error: cashError 
  } = useCash(householdId, '6M');

  // If overview fails to load, show error state
  if (overviewError) {
    return (
      <div className="container-wealth overview-container">
        <ErrorState
          title="Failed to Load Overview"
          message="Unable to load household overview data. Please try again."
          onRetry={() => refetchOverview()}
          className="error-container"
        />
      </div>
    );
  }

  return (
    <div>
      {/* Header Section */}
      <div className="overview-header">
        <h2 className="overview-title">
          {overview?.household.name || "Loading..."}
        </h2>
        <p className="overview-subtitle">
          {overview?.household.primaryAdvisor}
          {overview?.household.riskProfile && (
            <>
              {" • "}
              <span className="status-pill info">{overview.household.riskProfile}</span>
            </>
          )}
        </p>
      </div>

      {/* KPI Cards Row */}
      <div className="kpi-grid overview-kpi-grid">
        {overviewLoading ? (
          <>
            <div className="kpi-card">
              <div className="loading-state">Loading...</div>
            </div>
            <div className="kpi-card">
              <div className="loading-state">Loading...</div>
            </div>
            <div className="kpi-card">
              <div className="loading-state">Loading...</div>
            </div>
            <div className="kpi-card">
              <div className="loading-state">Loading...</div>
            </div>
          </>
        ) : overview ? (
          <>
            <KPICard
              label="Total Assets"
              value={overview.totalAssets}
              format="currency"
              icon={DollarSign}
            />
            <KPICard
              label="YTD Return"
              value={overview.ytdReturn}
              format="percentage"
              delta={{
                value: overview.ytdReturn - overview.benchmarkReturn,
                label: `vs ${formatPercentage(overview.benchmarkReturn)} benchmark`,
                type: "percentage"
              }}
              icon={TrendingUp}
            />
            <KPICard
              label="Accounts"
              value={overview.accountsCount}
              format="number"
              icon={Building2}
            />
            <KPICard
              label="Cash & Equivalents"
              value={overview.totalCash}
              format="currency"
              delta={{
                value: overview.avgCashYield,
                label: "Avg yield",
                type: "percentage"
              }}
              icon={Wallet}
            />
          </>
        ) : null}
      </div>

      {/* Charts Row */}
      <div className="chart-row">
        {/* Performance Chart */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Portfolio Performance</h3>
            <div className="performance-range-buttons">
              {["3M", "6M", "1Y"].map((range) => (
                <button
                  key={range}
                  className={`btn ${performanceRange === range ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setPerformanceRange(range)}
                >
                  {range}
                </button>
              ))}
            </div>
          </div>
          {performanceLoading ? (
            <div className="loading-state">Loading chart...</div>
          ) : performanceError ? (
            <div className="empty-state">
              <p>Failed to load performance data</p>
            </div>
          ) : (
            <TimeSeriesCard
              title=""
              data={performance?.data || []}
              loading={false}
              error={undefined}
            />
          )}
        </div>

        {/* Asset Allocation */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Asset Allocation</h3>
            <p className="card-description">Current portfolio breakdown</p>
          </div>
          {allocationLoading ? (
            <div className="loading-state">Loading allocation...</div>
          ) : allocationError ? (
            <div className="empty-state">
              <p>Failed to load allocation data</p>
            </div>
          ) : (
            <DonutCard
              title=""
              data={allocation?.allocation.map(item => ({
                name: item.name,
                value: item.value,
                percentage: item.percentage,
                color: item.color
              })) || []}
              loading={false}
              error={undefined}
            />
          )}
        </div>
      </div>

      {/* Bottom Section */}
      <div className="accounts-section">
        {/* Recent Activity */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Recent Activity</h3>
            <p className="card-description">Latest transactions</p>
          </div>
          {activityLoading ? (
            <div className="loading-state">Loading activity...</div>
          ) : activityError ? (
            <div className="empty-state">
              <p>Failed to load activity</p>
            </div>
          ) : (
            <FeedCard
              title=""
              items={activity?.activities || []}
              loading={false}
              error={undefined}
            />
          )}
        </div>

        {/* Cash Accounts Summary */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Cash Accounts</h3>
            <p className="card-description">Top accounts by balance</p>
          </div>
          {cashLoading ? (
            <div className="loading-state">Loading accounts...</div>
          ) : cashError ? (
            <div className="empty-state">
              <p>Failed to load cash accounts</p>
            </div>
          ) : (
            <AccountsList
              title=""
              accounts={cash?.accounts.slice(0, 3) || []}
              loading={false}
              error={undefined}
            />
          )}
        </div>
      </div>

      {/* Executive Summary */}
      <div className="card executive-summary-card">
        <div className="card-header">
          <h3 className="card-title">Executive Summary</h3>
          <p className="card-description">Key insights and recommendations</p>
        </div>
        {overviewLoading ? (
          <div className="loading-state">Loading summary...</div>
        ) : overview?.executiveSummary ? (
          <ul className="executive-summary-list">
            {overview.executiveSummary.map((bullet, index) => (
              <li key={index} className="executive-summary-item">
                <div className="executive-summary-bullet" />
                <span className="executive-summary-text">{bullet}</span>
              </li>
            ))}
          </ul>
        ) : (
          <div className="empty-state">
            <p>No summary available</p>
          </div>
        )}
      </div>
    </div>
  );
}