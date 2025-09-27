import { getHouseholdById } from './mock-households';
import type { 
  OverviewResponse, 
  PerformanceResponse, 
  AllocationResponse, 
  ActivityResponse, 
  CashResponse,
  PlanningResponse,
  PositionsResponse,
  ReportsResponse
} from './schemas';

export function getMockOverview(householdId: string): OverviewResponse {
  const household = getHouseholdById(householdId);
  if (!household) throw new Error('Household not found');

  return {
    household: {
      id: household.id,
      name: household.name,
      primaryAdvisor: household.advisorName,
      riskProfile: household.riskProfile === 'Ultra-Conservative' ? 'Conservative' : household.riskProfile as any,
      lastSync: new Date().toISOString(),
    },
    totalAssets: household.totalAssets,
    ytdReturn: household.ytdPerformance,
    benchmarkReturn: household.ytdPerformance * 0.9,
    accountsCount: household.accountsCount,
    totalCash: household.totalCash,
    avgCashYield: 2.5,
    executiveSummary: [
      `Portfolio performance of ${household.ytdPerformance}% YTD`,
      `Total assets under management: $${(household.totalAssets / 1000000).toFixed(1)}M`,
      `Risk profile aligned with ${household.riskProfile.toLowerCase()} strategy`
    ],
    lastUpdated: new Date().toISOString(),
  };
}

export function getMockPerformance(householdId: string, range: string): PerformanceResponse {
  console.log(`🔄 Generating performance data for ${householdId}, range: ${range}`);
  
  const household = getHouseholdById(householdId);
  if (!household) throw new Error('Household not found');

  const validRanges = ['3M', '6M', '1Y', '3Y', '5Y'] as const;
  const validRange = validRanges.includes(range as any) ? range as any : '6M';

  // Generate performance data based on the selected range
  const rangeConfig: Record<typeof validRange, { days: number; points: number }> = {
    '3M': { days: 90, points: 30 },
    '6M': { days: 180, points: 60 },
    '1Y': { days: 365, points: 120 },
    '3Y': { days: 365 * 3, points: 150 },
    '5Y': { days: 365 * 5, points: 200 },
  };

  const config = rangeConfig[validRange];
  const data = [];
  
  // Create more distinct patterns for each range
  const baseValue = household.totalAssets;
  const baseReturn = household.ytdPerformance / 100;
  
  for (let i = 0; i < config.points; i++) {
    const date = new Date();
    date.setDate(date.getDate() - (config.days - (i * config.days / config.points)));
    
    const progress = i / config.points;
    
    // Different performance patterns for different ranges
    let performanceMultiplier = 0.5; // Default
    let volatilityFactor = 0.03; // Default
    
    switch (validRange) {
      case '3M':
        performanceMultiplier = 0.2; // 20% of YTD performance
        volatilityFactor = 0.02; // Lower volatility for short term
        break;
      case '6M':
        performanceMultiplier = 0.5; // 50% of YTD performance
        volatilityFactor = 0.03;
        break;
      case '1Y':
        performanceMultiplier = 1.0; // Full YTD performance
        volatilityFactor = 0.04;
        break;
      case '3Y':
        performanceMultiplier = 2.5; // Annualized over 3 years
        volatilityFactor = 0.06;
        break;
      case '5Y':
        performanceMultiplier = 4.0; // Annualized over 5 years
        volatilityFactor = 0.08;
        break;
    }
    
    // Add consistent but noticeable volatility
    const seed = (householdId.charCodeAt(0) + i * 7 + validRange.charCodeAt(0)) % 100;
    const volatility = Math.sin((seed + i) * 0.1) * volatilityFactor;
    
    // Create trending performance with volatility
    const trendReturn = baseReturn * performanceMultiplier * progress;
    const finalValue = baseValue * (1 + trendReturn + volatility);
    const benchmarkValue = baseValue * (1 + trendReturn * 0.85 + volatility * 0.3);
    
    data.push({
      date: date.toISOString().split('T')[0],
      value: Math.round(finalValue),
      benchmark: Math.round(benchmarkValue),
    });
  }

  const rangeMultiplierMap: Record<typeof validRange, number> = {
    '3M': 0.2,
    '6M': 0.5,
    '1Y': 1.0,
    '3Y': 2.5,
    '5Y': 4.0,
  };
  
  const multiplier = rangeMultiplierMap[validRange];
  
  return {
    data,
    range: validRange,
    totalReturn: household.ytdPerformance * multiplier,
    benchmarkReturn: household.ytdPerformance * multiplier * 0.8,
    volatility: 12.5,
    sharpeRatio: 1.2,
  };
}

export function getMockAllocation(householdId: string): AllocationResponse {
  const household = getHouseholdById(householdId);
  if (!household) throw new Error('Household not found');

  return {
    allocation: [
      { name: 'US Equity', value: 50, percentage: 50, color: '#0f766e' },
      { name: 'International Equity', value: 20, percentage: 20, color: '#3b82f6' },
      { name: 'Fixed Income', value: 25, percentage: 25, color: '#10b981' },
      { name: 'Alternatives', value: 5, percentage: 5, color: '#f59e0b' },
    ],
    policyDrift: 2.3,
    rebalanceNeeded: false,
    lastRebalance: '2025-08-15T00:00:00Z',
  };
}

export function getMockActivity(householdId: string): ActivityResponse {
  const household = getHouseholdById(householdId);
  if (!household) throw new Error('Household not found');

  return {
    activities: [
      {
        id: `${householdId}-1`,
        type: 'meeting' as const,
        priority: 'high' as const,
        status: 'completed' as const,
        date: new Date().toISOString(),
        title: `Quarterly Review - ${household.name}`,
        description: `Portfolio review and planning discussion for ${household.name}`,
        tags: ['review', 'quarterly', household.riskProfile.toLowerCase()],
        author: household.advisorName,
      },
      {
        id: `${householdId}-2`,
        type: 'trade' as const,
        priority: 'medium' as const,
        status: 'completed' as const,
        date: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        title: `Portfolio Rebalancing - ${household.name}`,
        description: 'Executed rebalancing trades to maintain target allocation',
        tags: ['rebalancing', 'trade'],
        author: household.advisorName,
      }
    ],
    totalCount: 2,
    hasMore: false,
  };
}

function generateCashTrendData(householdId: string, range: string, totalCash: number) {
  const validRanges = ['3M', '6M', '1Y'] as const;
  const validRange = validRanges.includes(range as any) ? range as any : '6M';
  
  const rangeConfig: Record<typeof validRange, { days: number; points: number }> = {
    '3M': { days: 90, points: 20 },
    '6M': { days: 180, points: 30 },
    '1Y': { days: 365, points: 50 },
  };

  const config = rangeConfig[validRange];
  const data = [];
  
  for (let i = 0; i < config.points; i++) {
    const date = new Date();
    date.setDate(date.getDate() - (config.days - (i * config.days / config.points)));
    
    // Generate gradual trend with some variation
    const progress = i / config.points;
    const seed = (householdId.charCodeAt(0) + i) % 100;
    const variation = (seed - 50) / 500; // Small variations
    
    const balance = totalCash * (0.9 + 0.1 * progress + variation);
    
    data.push({
      date: date.toISOString().split('T')[0],
      balance: Math.max(0, balance),
      checking: Math.max(0, balance * 0.4),
      savings: Math.max(0, balance * 0.6),
      cd: 0,
    });
  }
  
  return data;
}

export function getMockCash(householdId: string, range: string = '6M'): CashResponse {
  const household = getHouseholdById(householdId);
  if (!household) throw new Error('Household not found');

  const checkingBalance = household.totalCash * 0.4;
  const savingsBalance = household.totalCash * 0.6;

  return {
    accounts: [
      {
        id: `${householdId}-checking`,
        name: `${household.name} Checking`,
        type: 'checking' as const,
        balance: checkingBalance,
        apy: 0.1,
        isActive: true,
        institution: 'Chase Bank',
      },
      {
        id: `${householdId}-savings`,
        name: `${household.name} High Yield Savings`,
        type: 'savings' as const,
        balance: savingsBalance,
        apy: 4.5,
        isActive: true,
        institution: 'Marcus by Goldman Sachs',
      }
    ],
    totalBalance: household.totalCash,
    avgYield: 2.8,
    trendData: generateCashTrendData(householdId, range, household.totalCash),
    alerts: [],
  };
}

export function getMockPlanning(householdId: string): PlanningResponse {
  const household = getHouseholdById(householdId);
  if (!household) throw new Error('Household not found');

  const isRetirementAge = household.name.includes('Retirement') || household.riskProfile === 'Conservative';

  return {
    rmds: isRetirementAge ? [
      {
        id: `${householdId}-rmd-1`,
        accountName: 'Traditional IRA',
        owner: household.primaryContact,
        dueDate: '2025-12-31T23:59:59Z',
        requiredAmount: household.totalAssets * 0.04,
        completedAmount: 0,
        status: 'pending' as const,
      }
    ] : [],
    beneficiaries: [
      {
        id: `${householdId}-ben-1`,
        accountName: 'Primary Investment Account',
        accountType: 'Investment',
        hasPrimary: true,
        hasContingent: true,
        lastReviewed: '2025-01-15T00:00:00Z',
        status: 'complete' as const,
      }
    ],
    nextInteraction: {
      date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      type: 'review',
      description: 'Quarterly portfolio review and planning discussion',
    },
    custodialTransitions: [],
  };
}

export function getMockPositions(householdId: string): PositionsResponse {
  const household = getHouseholdById(householdId);
  if (!household) throw new Error('Household not found');

  const investedAssets = household.totalAssets - household.totalCash;
  const positions = [
    {
      id: `${householdId}-pos-1`,
      symbol: 'AAPL',
      name: 'Apple Inc.',
      assetClass: 'Equity' as const,
      quantity: Math.floor(investedAssets * 0.15 / 175),
      marketValue: investedAssets * 0.15,
      costBasis: investedAssets * 0.15 * 0.9,
      weight: 15.0,
      lastPrice: 175.25,
      sector: 'Technology',
    },
    {
      id: `${householdId}-pos-2`,
      symbol: 'VTI',
      name: 'Vanguard Total Stock Market ETF',
      assetClass: 'Equity' as const,
      quantity: Math.floor(investedAssets * 0.35 / 240),
      marketValue: investedAssets * 0.35,
      costBasis: investedAssets * 0.35 * 0.95,
      weight: 35.0,
      lastPrice: 240.15,
    },
    {
      id: `${householdId}-pos-3`,
      symbol: 'BND',
      name: 'Vanguard Total Bond Market ETF',
      assetClass: 'Fixed Income' as const,
      quantity: Math.floor(investedAssets * 0.25 / 78),
      marketValue: investedAssets * 0.25,
      costBasis: investedAssets * 0.25 * 1.02,
      weight: 25.0,
      lastPrice: 78.45,
    }
  ];

  const totalMarketValue = positions.reduce((sum, pos) => sum + pos.marketValue, 0);
  const totalCostBasis = positions.reduce((sum, pos) => sum + pos.costBasis, 0);
  const totalGainLoss = totalMarketValue - totalCostBasis;

  return {
    positions,
    summary: {
      totalMarketValue,
      totalCostBasis,
      totalGainLoss,
      totalGainLossPercent: (totalGainLoss / totalCostBasis) * 100,
      positionsCount: positions.length,
    },
  };
}

export function getMockReports(householdId: string): ReportsResponse {
  const household = getHouseholdById(householdId);
  if (!household) throw new Error('Household not found');

  return {
    statements: [
      {
        id: `${householdId}-stmt-monthly`,
        name: `Monthly Statement - ${household.name}`,
        type: 'monthly' as const,
        date: '2025-09-01T00:00:00Z',
        size: '2.3 MB',
        url: `/statements/${householdId}/monthly-2025-09.pdf`,
      },
      {
        id: `${householdId}-stmt-quarterly`,
        name: `Quarterly Performance Report - ${household.name}`,
        type: 'quarterly' as const,
        date: '2025-07-01T00:00:00Z',
        size: '1.8 MB',
        url: `/statements/${householdId}/quarterly-2025-q3.pdf`,
      }
    ],
    analytics: [
      {
        id: `${householdId}-analytics-performance`,
        name: 'Portfolio Performance Analysis',
        description: `Comprehensive performance analysis for ${household.name} including risk metrics and attribution`,
        generatedDate: '2025-09-24T00:00:00Z',
        url: `/analytics/${householdId}/performance-analysis.pdf`,
      },
      {
        id: `${householdId}-analytics-allocation`,
        name: 'Asset Allocation Review',
        description: 'Current vs target allocation with rebalancing recommendations',
        generatedDate: '2025-09-20T00:00:00Z',
        url: `/analytics/${householdId}/allocation-review.pdf`,
      }
    ],
  };
}