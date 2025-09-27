import { z } from "zod";

// Base schemas
export const HouseholdSchema = z.object({
  id: z.string(),
  name: z.string(),
  primaryAdvisor: z.string(),
  riskProfile: z.enum(["Conservative", "Moderate", "Aggressive"]),
  lastSync: z.string().datetime(),
});

export const AccountSchema = z.object({
  id: z.string(),
  name: z.string(),
  institution: z.string().optional(),
  type: z.enum(["checking", "savings", "money-market", "cd", "investment", "retirement"]),
  balance: z.number(),
  apy: z.number().optional(),
  isActive: z.boolean().default(true),
});

export const PositionSchema = z.object({
  id: z.string(),
  symbol: z.string(),
  name: z.string(),
  assetClass: z.enum(["Equity", "Fixed Income", "Alternative", "Cash", "Real Estate"]),
  quantity: z.number(),
  marketValue: z.number(),
  costBasis: z.number(),
  weight: z.number(),
  sector: z.string().optional(),
  lastPrice: z.number(),
});

export const PerformanceDataSchema = z.object({
  date: z.string(),
  value: z.number(),
  benchmark: z.number().optional(),
});

export const ActivityItemSchema = z.object({
  id: z.string(),
  type: z.enum(["meeting", "call", "email", "review", "trade"]),
  priority: z.enum(["high", "medium", "low"]),
  date: z.string().datetime(),
  title: z.string(),
  description: z.string().optional(),
  tags: z.array(z.string()).default([]),
  author: z.string(),
  status: z.enum(["completed", "pending", "scheduled"]).default("pending"),
});

export const AllocationItemSchema = z.object({
  name: z.string(),
  value: z.number(),
  percentage: z.number(),
  target: z.number().optional(),
  color: z.string().optional(),
});

export const RMDItemSchema = z.object({
  id: z.string(),
  accountName: z.string(),
  owner: z.string(),
  dueDate: z.string().datetime(),
  requiredAmount: z.number(),
  completedAmount: z.number().default(0),
  status: z.enum(["pending", "partial", "completed", "overdue"]),
});

export const BeneficiaryItemSchema = z.object({
  id: z.string(),
  accountName: z.string(),
  accountType: z.string(),
  hasPrimary: z.boolean(),
  hasContingent: z.boolean(),
  lastReviewed: z.string().datetime().optional(),
  status: z.enum(["complete", "incomplete", "review-needed"]),
});

// API Response schemas
export const OverviewResponseSchema = z.object({
  household: HouseholdSchema,
  totalAssets: z.number(),
  ytdReturn: z.number(),
  benchmarkReturn: z.number(),
  accountsCount: z.number(),
  totalCash: z.number(),
  avgCashYield: z.number(),
  executiveSummary: z.array(z.string()).max(3),
  lastUpdated: z.string().datetime(),
});

export const PerformanceResponseSchema = z.object({
  data: z.array(PerformanceDataSchema),
  range: z.enum(["3M", "6M", "1Y", "3Y", "5Y"]),
  totalReturn: z.number(),
  benchmarkReturn: z.number(),
  volatility: z.number(),
  sharpeRatio: z.number(),
});

export const AllocationResponseSchema = z.object({
  allocation: z.array(AllocationItemSchema),
  policyDrift: z.number(), // percentage points from policy
  rebalanceNeeded: z.boolean(),
  lastRebalance: z.string().datetime(),
});

export const ActivityResponseSchema = z.object({
  activities: z.array(ActivityItemSchema),
  totalCount: z.number(),
  hasMore: z.boolean(),
});

export const CashResponseSchema = z.object({
  accounts: z.array(AccountSchema.extend({
    type: z.enum(["checking", "savings", "money-market", "cd"]),
    apy: z.number(),
  })),
  totalBalance: z.number(),
  avgYield: z.number(),
  trendData: z.array(z.object({
    date: z.string(),
    balance: z.number(),
    checking: z.number(),
    savings: z.number(),
    cd: z.number(),
  })),
  alerts: z.array(z.object({
    type: z.enum(["concentration", "yield", "liquidity"]),
    message: z.string(),
    severity: z.enum(["info", "warning", "error"]),
  })).default([]),
});

export const PlanningResponseSchema = z.object({
  rmds: z.array(RMDItemSchema),
  beneficiaries: z.array(BeneficiaryItemSchema),
  nextInteraction: z.object({
    date: z.string().datetime(),
    type: z.string(),
    description: z.string(),
  }).optional(),
  custodialTransitions: z.array(z.object({
    childName: z.string(),
    currentAge: z.number(),
    transitionDate: z.string().datetime(),
    accountsAffected: z.number(),
  })).default([]),
});

export const PositionsResponseSchema = z.object({
  positions: z.array(PositionSchema),
  summary: z.object({
    totalMarketValue: z.number(),
    totalCostBasis: z.number(),
    totalGainLoss: z.number(),
    totalGainLossPercent: z.number(),
    positionsCount: z.number(),
  }),
});

export const ReportsResponseSchema = z.object({
  statements: z.array(z.object({
    id: z.string(),
    name: z.string(),
    type: z.enum(["monthly", "quarterly", "annual", "tax", "performance"]),
    date: z.string().datetime(),
    size: z.string(),
    url: z.string(),
  })),
  analytics: z.array(z.object({
    id: z.string(),
    name: z.string(),
    description: z.string(),
    generatedDate: z.string().datetime(),
    url: z.string(),
  })),
});

// Export types
export type Household = z.infer<typeof HouseholdSchema>;
export type Account = z.infer<typeof AccountSchema>;
export type Position = z.infer<typeof PositionSchema>;
export type PerformanceData = z.infer<typeof PerformanceDataSchema>;
export type ActivityItem = z.infer<typeof ActivityItemSchema>;
export type AllocationItem = z.infer<typeof AllocationItemSchema>;
export type RMDItem = z.infer<typeof RMDItemSchema>;
export type BeneficiaryItem = z.infer<typeof BeneficiaryItemSchema>;

export type OverviewResponse = z.infer<typeof OverviewResponseSchema>;
export type PerformanceResponse = z.infer<typeof PerformanceResponseSchema>;
export type AllocationResponse = z.infer<typeof AllocationResponseSchema>;
export type ActivityResponse = z.infer<typeof ActivityResponseSchema>;
export type CashResponse = z.infer<typeof CashResponseSchema>;
export type PlanningResponse = z.infer<typeof PlanningResponseSchema>;
export type PositionsResponse = z.infer<typeof PositionsResponseSchema>;
export type ReportsResponse = z.infer<typeof ReportsResponseSchema>;