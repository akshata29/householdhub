import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import {
  OverviewResponse,
  PerformanceResponse,
  AllocationResponse,
  ActivityResponse,
  CashResponse,
  PlanningResponse,
  PositionsResponse,
  ReportsResponse,
} from '@/lib/schemas';
import {
  getMockOverview,
  getMockPerformance,
  getMockAllocation,
  getMockActivity,
  getMockCash,
  getMockPlanning,
  getMockPositions,
  getMockReports,
} from './mock-api-data'

// Mock fetch function that returns household-specific data
async function fetchMockData<T>(
  householdId: string,
  dataType: string,
  range?: string
): Promise<T> {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 100 + Math.random() * 200));
  
  switch (dataType) {
    case 'overview':
      return getMockOverview(householdId) as T;
    case 'performance':
      return getMockPerformance(householdId, range || '6M') as T;
    case 'allocation':
      return getMockAllocation(householdId) as T;
    case 'activity':
      return getMockActivity(householdId) as T;
    case 'cash':
      return getMockCash(householdId, range || '6M') as T;
    case 'planning':
      return getMockPlanning(householdId) as T;
    case 'positions':
      return getMockPositions(householdId) as T;
    case 'reports':
      return getMockReports(householdId) as T;
    default:
      throw new Error(`Unknown data type: ${dataType}`);
  }
}

// Query keys factory
export const queryKeys = {
  household: (id: string) => ['household', id],
  overview: (id: string) => ['household', id, 'overview'],
  performance: (id: string, range: string) => ['household', id, 'performance', range],
  allocation: (id: string) => ['household', id, 'allocation'],
  activity: (id: string, limit?: number, offset?: number) => 
    ['household', id, 'activity', { limit, offset }],
  cash: (id: string) => ['household', id, 'cash'],
  planning: (id: string) => ['household', id, 'planning'],
  positions: (id: string) => ['household', id, 'positions'],
  reports: (id: string) => ['household', id, 'reports'],
};

// Hooks
export function useOverview(
  householdId: string,
  options?: UseQueryOptions<OverviewResponse>
) {
  return useQuery({
    queryKey: queryKeys.overview(householdId),
    queryFn: () => fetchMockData<OverviewResponse>(householdId, 'overview'),
    staleTime: 5 * 60 * 1000, // 5 minutes
    ...options,
  });
}

export function usePerformance(
  householdId: string,
  range: string = '6M',
  options?: UseQueryOptions<PerformanceResponse>
) {
  return useQuery({
    queryKey: queryKeys.performance(householdId, range),
    queryFn: () => fetchMockData<PerformanceResponse>(householdId, 'performance', range),
    staleTime: 10 * 60 * 1000, // 10 minutes
    ...options,
  });
}

export function useAllocation(
  householdId: string,
  options?: UseQueryOptions<AllocationResponse>
) {
  return useQuery({
    queryKey: queryKeys.allocation(householdId),
    queryFn: () => fetchMockData<AllocationResponse>(householdId, 'allocation'),
    staleTime: 15 * 60 * 1000, // 15 minutes
    ...options,
  });
}

export function useActivity(
  householdId: string,
  limit: number = 10,
  offset: number = 0,
  options?: UseQueryOptions<ActivityResponse>
) {
  return useQuery({
    queryKey: queryKeys.activity(householdId, limit, offset),
    queryFn: () => fetchMockData<ActivityResponse>(householdId, 'activity'),
    staleTime: 2 * 60 * 1000, // 2 minutes
    ...options,
  });
}

export function useCash(
  householdId: string,
  range: string = '6M',
  options?: UseQueryOptions<CashResponse>
) {
  return useQuery({
    queryKey: [...queryKeys.cash(householdId), 'range', range],
    queryFn: () => fetchMockData<CashResponse>(householdId, 'cash', range),
    staleTime: 10 * 60 * 1000, // 10 minutes
    ...options,
  });
}

export function usePlanning(
  householdId: string,
  options?: UseQueryOptions<PlanningResponse>
) {
  return useQuery({
    queryKey: queryKeys.planning(householdId),
    queryFn: () => fetchMockData<PlanningResponse>(householdId, 'planning'),
    staleTime: 30 * 60 * 1000, // 30 minutes
    ...options,
  });
}

export function usePositions(
  householdId: string,
  options?: UseQueryOptions<PositionsResponse>
) {
  return useQuery({
    queryKey: queryKeys.positions(householdId),
    queryFn: () => fetchMockData<PositionsResponse>(householdId, 'positions'),
    staleTime: 5 * 60 * 1000, // 5 minutes
    ...options,
  });
}

export function useReports(
  householdId: string,
  options?: UseQueryOptions<ReportsResponse>
) {
  return useQuery({
    queryKey: queryKeys.reports(householdId),
    queryFn: () => fetchMockData<ReportsResponse>(householdId, 'reports'),
    staleTime: 60 * 60 * 1000, // 1 hour
    ...options,
  });
}