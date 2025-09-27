"use client";

import * as React from "react";
import { usePositions, usePerformance, useAllocation } from "@/lib/queries";
import { TimeSeriesCard } from "@/components/ui/time-series-card";
import { DonutCard } from "@/components/ui/donut-card";
import { KPICard } from "@/components/ui/kpi-card";
import { 
  ArrowUpDown,
  TrendingUp,
  TrendingDown,
  Eye,
  DollarSign,
  Target,
  Briefcase,
} from "lucide-react";
import { formatCurrency, formatPercentage } from "@/lib/utils";
import { Position } from "@/lib/schemas";

interface PortfolioTabProps {
  householdId: string;
}

function PositionsTable({ positions, loading, error }: { 
  positions: Position[], 
  loading: boolean, 
  error?: string 
}) {
  const [sortField, setSortField] = React.useState<keyof Position>('marketValue');
  const [sortDirection, setSortDirection] = React.useState<'asc' | 'desc'>('desc');
  const [selectedPosition, setSelectedPosition] = React.useState<Position | null>(null);

  const sortedPositions = React.useMemo(() => {
    return [...positions].sort((a, b) => {
      const aVal = a[sortField];
      const bVal = b[sortField];
      
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
      }
      
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return sortDirection === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      }
      
      return 0;
    });
  }, [positions, sortField, sortDirection]);

  const handleSort = (field: keyof Position) => {
    if (field === sortField) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  if (loading) {
    return (
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Portfolio Positions</h3>
        </div>
        <div className="loading-state">Loading positions...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card error-state">
        <h3>Failed to Load Positions</h3>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Portfolio Positions</h3>
      </div>
      <div className="positions-table-container">
        <table className="positions-table">
          <thead>
            <tr>
              <th className="sortable" onClick={() => handleSort('symbol')}>
                Symbol
                <ArrowUpDown className="sort-icon" />
              </th>
              <th className="sortable" onClick={() => handleSort('assetClass')}>
                Asset Class
                <ArrowUpDown className="sort-icon" />
              </th>
              <th className="sortable right-align" onClick={() => handleSort('quantity')}>
                Quantity
                <ArrowUpDown className="sort-icon" />
              </th>
              <th className="sortable right-align" onClick={() => handleSort('marketValue')}>
                Market Value
                <ArrowUpDown className="sort-icon" />
              </th>
              <th className="sortable right-align" onClick={() => handleSort('weight')}>
                Weight %
                <ArrowUpDown className="sort-icon" />
              </th>
              <th className="action-col"></th>
            </tr>
          </thead>
          <tbody>
            {sortedPositions.map((position, index) => {
              const gainLoss = position.marketValue - position.costBasis;
              const gainLossPercent = (gainLoss / position.costBasis) * 100;
              const isGain = gainLoss >= 0;
              
              return (
                <tr key={position.id} className="position-row">
                  <td>
                    <div className="position-symbol">
                      <div className="symbol-name">{position.symbol}</div>
                      <div className="position-name">{position.name}</div>
                    </div>
                  </td>
                  <td>
                    <span className="asset-class-badge">{position.assetClass}</span>
                  </td>
                  <td className="right-align">
                    <div className="number-tabular">
                      {new Intl.NumberFormat().format(position.quantity)}
                    </div>
                  </td>
                  <td className="right-align">
                    <div className="position-value">
                      <div className="market-value">{formatCurrency(position.marketValue)}</div>
                      <div className={`gain-loss ${isGain ? 'positive' : 'negative'}`}>
                        {isGain ? <TrendingUp className="trend-icon" /> : <TrendingDown className="trend-icon" />}
                        {formatPercentage(gainLossPercent, { showSign: true })}
                      </div>
                    </div>
                  </td>
                  <td className="right-align">
                    <div className="number-tabular weight-percent">
                      {formatPercentage(position.weight)}
                    </div>
                  </td>
                  <td className="action-col">
                    <button className="btn btn-ghost" onClick={() => setSelectedPosition(position)}>
                      <Eye className="icon" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function PortfolioTab({ householdId }: PortfolioTabProps) {
  const [performanceRange, setPerformanceRange] = React.useState("6M");
  
  const { 
    data: positions, 
    isLoading: positionsLoading, 
    error: positionsError 
  } = usePositions(householdId);
  
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

  return (
    <div className="portfolio-container">
      {/* Header */}
      <div className="portfolio-header">
        <h1 className="portfolio-title">Portfolio Analysis</h1>
        <p className="portfolio-subtitle">Holdings, performance, and allocation breakdown</p>
      </div>

      {/* KPI Cards */}
      {positions?.summary && (
        <div className="kpi-grid">
          <KPICard
            label="Total Market Value"
            value={positions.summary.totalMarketValue}
            format="currency"
            icon={DollarSign}
          />
          <KPICard
            label="Total Gain/Loss"
            value={positions.summary.totalGainLoss}
            format="currency"
            delta={{
              value: positions.summary.totalGainLossPercent,
              type: "percentage"
            }}
            icon={TrendingUp}
          />
          <KPICard
            label="Positions"
            value={positions.summary.positionsCount}
            format="number"
            delta={allocation?.policyDrift ? {
              value: allocation.policyDrift,
              label: "from policy",
              type: "percentage"
            } : undefined}
            icon={Briefcase}
          />
        </div>
      )}

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
          <TimeSeriesCard
            title=""
            data={performance?.data || []}
            loading={performanceLoading}
            error={performanceError?.message}
          />
        </div>

        {/* Asset Allocation vs Policy */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Asset Allocation vs Policy</h3>
            <p className="card-description">Current vs target allocation breakdown</p>
          </div>
          <DonutCard
            title=""
            data={allocation?.allocation.map(item => ({
              name: item.name,
              value: item.value,
              percentage: item.percentage,
              target: item.target,
              color: item.color
            })) || []}
            loading={allocationLoading}
            error={allocationError?.message}
            legendPlacement="bottom"
          />
        </div>
      </div>

      {/* Positions Table */}
      <PositionsTable 
        positions={positions?.positions || []}
        loading={positionsLoading}
        error={positionsError?.message}
      />
    </div>
  );
}