// Synthetic data generators for realistic wealth management scenarios

export function generateHousehold(id: string) {
  return {
    id,
    name: "The Johnson Family Trust",
    primaryAdvisor: "Sarah Mitchell, CFP®",
    riskProfile: "Moderate" as const,
    lastSync: new Date().toISOString(),
  };
}

export function generateOverviewData(householdId: string) {
  const totalAssets = 2847530;
  const ytdReturn = 8.7;
  const benchmarkReturn = 7.2;
  
  return {
    household: generateHousehold(householdId),
    totalAssets,
    ytdReturn,
    benchmarkReturn,
    accountsCount: 8,
    totalCash: 142750,
    avgCashYield: 4.25,
    executiveSummary: [
      "Portfolio performing well above benchmark with strong equity allocation",
      "Cash position elevated at 5.0% - consider rebalancing opportunities",
      "Q4 tax-loss harvesting completed, saving approximately $8,200"
    ],
    lastUpdated: new Date().toISOString(),
  };
}

export function generatePerformanceData(range: string) {
  const baseValue = 2500000;
  const dataPoints = range === "3M" ? 90 : range === "6M" ? 180 : 365;
  
  const data = Array.from({ length: dataPoints }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - (dataPoints - i));
    
    // Simulate realistic market performance with some volatility
    const trend = 0.08 / 365; // 8% annual return
    const volatility = 0.15 / Math.sqrt(365); // 15% annual volatility
    const randomReturn = (Math.random() - 0.5) * volatility * 2;
    
    const portfolioReturn = trend + randomReturn;
    const benchmarkReturn = trend + randomReturn * 0.8; // Benchmark is less volatile
    
    return {
      date: date.toISOString().split('T')[0],
      value: baseValue * (1 + portfolioReturn * i),
      benchmark: baseValue * (1 + benchmarkReturn * i),
    };
  });

  return {
    data,
    range: range as "3M" | "6M" | "1Y",
    totalReturn: 8.7,
    benchmarkReturn: 7.2,
    volatility: 12.3,
    sharpeRatio: 1.24,
  };
}

export function generateAllocationData() {
  return {
    allocation: [
      { name: "US Equity", value: 1423265, percentage: 50.0, target: 50.0, color: "rgb(var(--chart-1))" },
      { name: "International Equity", value: 455860, percentage: 16.0, target: 20.0, color: "rgb(var(--chart-2))" },
      { name: "Fixed Income", value: 711882.5, percentage: 25.0, target: 25.0, color: "rgb(var(--chart-3))" },
      { name: "Alternatives", value: 113901, percentage: 4.0, target: 3.0, color: "rgb(var(--chart-4))" },
      { name: "Cash", value: 142376.25, percentage: 5.0, target: 2.0, color: "rgb(var(--chart-6))" },
    ],
    policyDrift: 2.3,
    rebalanceNeeded: true,
    lastRebalance: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString(),
  };
}

export function generateActivityData() {
  const activities = [
    {
      id: "1",
      type: "meeting" as const,
      priority: "high" as const,
      date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      title: "Q3 Portfolio Review Meeting",
      description: "Comprehensive review of portfolio performance and rebalancing strategy",
      tags: ["quarterly", "review", "rebalancing"],
      author: "Sarah Mitchell",
      status: "completed" as const,
    },
    {
      id: "2", 
      type: "call" as const,
      priority: "medium" as const,
      date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
      title: "Tax-Loss Harvesting Discussion",
      tags: ["tax-planning", "harvesting"],
      author: "Sarah Mitchell",
      status: "completed" as const,
    },
    {
      id: "3",
      type: "email" as const,
      priority: "low" as const,
      date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      title: "Market Commentary: September 2025",
      tags: ["market-update", "commentary"],
      author: "Research Team",
      status: "completed" as const,
    },
    {
      id: "4",
      type: "review" as const,
      priority: "medium" as const,
      date: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
      title: "Annual Estate Plan Review",
      tags: ["estate-planning", "annual"],
      author: "Sarah Mitchell",
      status: "scheduled" as const,
    }
  ];

  return {
    activities,
    totalCount: 25,
    hasMore: true,
  };
}

export function generateCashData() {
  const accounts = [
    {
      id: "cash-1",
      name: "Goldman Sachs Bank Savings",
      institution: "Goldman Sachs Bank",
      type: "savings" as const,
      balance: 75000,
      apy: 4.50,
      isActive: true,
    },
    {
      id: "cash-2", 
      name: "Fidelity Government MMF",
      institution: "Fidelity",
      type: "money-market" as const,
      balance: 45000,
      apy: 4.25,
      isActive: true,
    },
    {
      id: "cash-3",
      name: "Chase Premier Checking",
      institution: "JPMorgan Chase",
      type: "checking" as const,
      balance: 15750,
      apy: 0.01,
      isActive: true,
    },
    {
      id: "cash-4",
      name: "Marcus 12-Month CD",
      institution: "Goldman Sachs Bank",
      type: "cd" as const,
      balance: 50000,
      apy: 4.75,
      isActive: true,
    }
  ];

  const trendData = Array.from({ length: 90 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - (90 - i));
    
    return {
      date: date.toISOString().split('T')[0],
      balance: 142750 + Math.sin(i / 10) * 15000,
      checking: 15750 + Math.random() * 5000,
      savings: 75000 + Math.sin(i / 15) * 10000,
      cd: 50000,
    };
  });

  return {
    accounts,
    totalBalance: 185750,
    avgYield: 4.25,
    trendData,
    alerts: [
      {
        type: "concentration" as const,
        message: "Cash concentration high in 2 accounts (65% of total cash)",
        severity: "warning" as const,
      }
    ],
  };
}

export function generatePlanningData() {
  return {
    rmds: [
      {
        id: "rmd-1",
        accountName: "Traditional IRA - Vanguard",
        owner: "Robert Johnson",
        dueDate: new Date(2025, 11, 31).toISOString(),
        requiredAmount: 45750,
        completedAmount: 0,
        status: "pending" as const,
      },
      {
        id: "rmd-2",
        accountName: "401(k) Rollover IRA - Fidelity", 
        owner: "Margaret Johnson",
        dueDate: new Date(2025, 11, 31).toISOString(),
        requiredAmount: 32100,
        completedAmount: 0,
        status: "pending" as const,
      }
    ],
    beneficiaries: [
      {
        id: "ben-1",
        accountName: "Vanguard Traditional IRA",
        accountType: "IRA",
        hasPrimary: true,
        hasContingent: true,
        lastReviewed: new Date(2024, 8, 15).toISOString(),
        status: "complete" as const,
      },
      {
        id: "ben-2",
        accountName: "Fidelity 401(k) Rollover",
        accountType: "IRA", 
        hasPrimary: true,
        hasContingent: false,
        lastReviewed: new Date(2023, 5, 22).toISOString(),
        status: "incomplete" as const,
      },
      {
        id: "ben-3",
        accountName: "Schwab Taxable Account",
        accountType: "Taxable",
        hasPrimary: false,
        hasContingent: false,
        status: "review-needed" as const,
      }
    ],
    nextInteraction: {
      date: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
      type: "Annual Review Meeting",
      description: "Comprehensive annual portfolio and estate planning review",
    },
    custodialTransitions: [],
  };
}

export function generatePositionsData() {
  const positions = [
    {
      id: "pos-1",
      symbol: "VTI",
      name: "Vanguard Total Stock Market ETF",
      assetClass: "Equity" as const,
      quantity: 2500,
      marketValue: 587500,
      costBasis: 520000,
      weight: 20.6,
      sector: "Diversified",
      lastPrice: 235.00,
    },
    {
      id: "pos-2",
      symbol: "VTIAX", 
      name: "Vanguard Total International Stock",
      assetClass: "Equity" as const,
      quantity: 15000,
      marketValue: 455000,
      costBasis: 430000,
      weight: 16.0,
      sector: "International",
      lastPrice: 30.33,
    },
    {
      id: "pos-3",
      symbol: "BND",
      name: "Vanguard Total Bond Market ETF",
      assetClass: "Fixed Income" as const,
      quantity: 8500,
      marketValue: 711750,
      costBasis: 725000,
      weight: 25.0,
      lastPrice: 83.75,
    },
    {
      id: "pos-4",
      symbol: "VTEB",
      name: "Vanguard Tax-Exempt Bond ETF",
      assetClass: "Fixed Income" as const,
      quantity: 2000,
      marketValue: 108000,
      costBasis: 110000,
      weight: 3.8,
      lastPrice: 54.00,
    },
    {
      id: "pos-5",
      symbol: "VNQ",
      name: "Vanguard Real Estate ETF",
      assetClass: "Real Estate" as const,
      quantity: 1200,
      marketValue: 113760,
      costBasis: 105000,
      weight: 4.0,
      lastPrice: 94.80,
    }
  ];

  const summary = {
    totalMarketValue: positions.reduce((sum, pos) => sum + pos.marketValue, 0),
    totalCostBasis: positions.reduce((sum, pos) => sum + pos.costBasis, 0),
    totalGainLoss: positions.reduce((sum, pos) => sum + (pos.marketValue - pos.costBasis), 0),
    totalGainLossPercent: 8.2,
    positionsCount: positions.length,
  };

  return {
    positions,
    summary,
  };
}

export function generateReportsData() {
  return {
    statements: [
      {
        id: "stmt-1",
        name: "September 2025 Monthly Statement", 
        type: "monthly" as const,
        date: new Date(2025, 8, 30).toISOString(),
        size: "2.4 MB",
        url: "/statements/2025-09-monthly.pdf",
      },
      {
        id: "stmt-2",
        name: "Q3 2025 Quarterly Review",
        type: "quarterly" as const,
        date: new Date(2025, 8, 30).toISOString(), 
        size: "5.1 MB",
        url: "/statements/2025-q3-quarterly.pdf",
      },
      {
        id: "stmt-3",
        name: "2024 Annual Performance Report",
        type: "annual" as const,
        date: new Date(2024, 11, 31).toISOString(),
        size: "8.7 MB", 
        url: "/statements/2024-annual.pdf",
      }
    ],
    analytics: [
      {
        id: "ana-1",
        name: "Risk Attribution Analysis",
        description: "Detailed breakdown of portfolio risk factors and attribution",
        generatedDate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
        url: "/analytics/risk-attribution.pdf",
      },
      {
        id: "ana-2",
        name: "Tax Efficiency Report",
        description: "Analysis of tax-loss harvesting and location optimization",
        generatedDate: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
        url: "/analytics/tax-efficiency.pdf",
      }
    ],
  };
}