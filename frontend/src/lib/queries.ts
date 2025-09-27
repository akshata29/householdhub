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
import { fetchData, apiClient } from './api-client';

// Enhanced fetch function that uses the new API client with database and fallback support
async function fetchDataWithFallback<T>(
  householdId: string,
  dataType: string,
  range?: string
): Promise<T> {
  // Add a small delay to simulate network activity (can be removed in production)
  await new Promise(resolve => setTimeout(resolve, 50 + Math.random() * 100));
  
  return fetchData<T>(householdId, dataType, range);
}

// Query keys factory
export const queryKeys = {
  households: () => ['households'],
  household: (id: string) => ['household', id],
  overview: (id: string) => ['household', id, 'overview'],
  performance: (id: string, range: string) => ['household', id, 'performance', range],
  allocation: (id: string) => ['household', id, 'allocation'],
  activity: (id: string, limit?: number, offset?: number) => 
    ['household', id, 'activity', { limit, offset }],
  cash: (id: string, range: string) => ['household', id, 'cash', range],
  planning: (id: string) => ['household', id, 'planning'],
  positions: (id: string) => ['household', id, 'positions'],
  reports: (id: string) => ['household', id, 'reports'],
};

// Hooks
export function useHouseholds(options?: UseQueryOptions<any>) {
  return useQuery({
    queryKey: queryKeys.households(),
    queryFn: async () => {
      const response = await apiClient.getHouseholds();
      return response.data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    ...options,
  });
}

export function useOverview(
  householdId: string,
  options?: UseQueryOptions<OverviewResponse>
) {
  return useQuery({
    queryKey: queryKeys.overview(householdId),
    queryFn: () => fetchDataWithFallback<OverviewResponse>(householdId, 'overview'),
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
    queryFn: () => fetchDataWithFallback<PerformanceResponse>(householdId, 'performance', range),
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
    queryFn: () => fetchDataWithFallback<AllocationResponse>(householdId, 'allocation'),
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
    queryFn: () => fetchDataWithFallback<ActivityResponse>(householdId, 'activity'),
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
    queryKey: queryKeys.cash(householdId, range),
    queryFn: () => fetchDataWithFallback<CashResponse>(householdId, 'cash', range),
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
    queryFn: () => fetchDataWithFallback<PlanningResponse>(householdId, 'planning'),
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
    queryFn: () => fetchDataWithFallback<PositionsResponse>(householdId, 'positions'),
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
    queryFn: () => fetchDataWithFallback<ReportsResponse>(householdId, 'reports'),
    staleTime: 60 * 60 * 1000, // 1 hour
    ...options,
  });
}