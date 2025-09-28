// WealthOps API Client
// Handles requests to both the new data service API and fallback to mock data

import {
  OverviewResponse,
  PerformanceResponse,
  CashResponse,
} from '@/lib/schemas';
import {
  getMockOverview,
  getMockPerformance,
  getMockCash,
  getMockAllocation,
  getMockActivity,
  getMockPlanning,
  getMockPositions,
  getMockReports,
} from './mock-api-data';

// Configuration
const DATA_SERVICE_BASE_URL = process.env.NEXT_PUBLIC_DATA_SERVICE_URL || 'http://localhost:8010';
const USE_DATA_SERVICE = process.env.NEXT_PUBLIC_USE_DATA_SERVICE === 'true';
const REQUEST_TIMEOUT = 10000; // 10 seconds

// Types for API responses
interface ApiResponse<T> {
  data: T;
  source: 'database' | 'mock';
  timestamp: string;
}

class ApiError extends Error {
  status?: number;
  source: 'api' | 'network' | 'timeout';
  
  constructor(options: { message: string; status?: number; source: 'api' | 'network' | 'timeout' }) {
    super(options.message);
    this.name = 'ApiError';
    this.status = options.status;
    this.source = options.source;
  }
}

class ApiClient {
  private baseUrl: string;
  private useDataService: boolean;

  constructor() {
    this.baseUrl = DATA_SERVICE_BASE_URL;
    this.useDataService = USE_DATA_SERVICE;
  }

  /**
   * Generic HTTP request handler with timeout and error handling
   */
  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error: unknown) {
      clearTimeout(timeoutId);

      if (error instanceof Error && error.name === 'AbortError') {
        throw new ApiError({
          message: 'Request timeout',
          source: 'timeout',
        });
      }

      if (error instanceof TypeError) {
        throw new ApiError({
          message: 'Network error - data service unavailable',
          source: 'network',
        });
      }

      const errorMessage = error instanceof Error ? error.message : 'API request failed';
      const errorStatus = (error as any)?.status;
      
      throw new ApiError({
        message: errorMessage,
        source: 'api',
        status: errorStatus,
      });
    }
  }

  /**
   * Get household overview data
   */
  async getOverview(householdId: string): Promise<ApiResponse<OverviewResponse>> {
    if (!this.useDataService) {
      console.log('🔄 Using mock data for overview (data service disabled)');
      return {
        data: getMockOverview(householdId),
        source: 'mock',
        timestamp: new Date().toISOString(),
      };
    }

    try {
      console.log(`🌐 Fetching overview from data service: ${householdId}`);
      const data = await this.makeRequest<OverviewResponse>(
        `/api/households/${householdId}/overview`
      );

      return {
        data,
        source: 'database',
        timestamp: new Date().toISOString(),
      };
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.warn('⚠️ Data service unavailable, falling back to mock data:', errorMessage);
      
      return {
        data: getMockOverview(householdId),
        source: 'mock',
        timestamp: new Date().toISOString(),
      };
    }
  }

  /**
   * Get household performance data
   */
  async getPerformance(
    householdId: string,
    range: string = '6M'
  ): Promise<ApiResponse<PerformanceResponse>> {
    if (!this.useDataService) {
      console.log('🔄 Using mock data for performance (data service disabled)');
      return {
        data: getMockPerformance(householdId, range),
        source: 'mock',
        timestamp: new Date().toISOString(),
      };
    }

    try {
      console.log(`🌐 Fetching performance from data service: ${householdId}, range: ${range}`);
      const data = await this.makeRequest<PerformanceResponse>(
        `/api/households/${householdId}/performance?range=${range}`
      );

      return {
        data,
        source: 'database',
        timestamp: new Date().toISOString(),
      };
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.warn('⚠️ Data service unavailable, falling back to mock data:', errorMessage);
      
      return {
        data: getMockPerformance(householdId, range),
        source: 'mock',
        timestamp: new Date().toISOString(),
      };
    }
  }

  /**
   * Get household cash data
   */
  async getCash(
    householdId: string,
    range: string = '6M'
  ): Promise<ApiResponse<CashResponse>> {
    if (!this.useDataService) {
      console.log('🔄 Using mock data for cash (data service disabled)');
      return {
        data: getMockCash(householdId, range),
        source: 'mock',
        timestamp: new Date().toISOString(),
      };
    }

    try {
      console.log(`🌐 Fetching cash data from data service: ${householdId}, range: ${range}`);
      const data = await this.makeRequest<CashResponse>(
        `/api/households/${householdId}/cash?range=${range}`
      );

      return {
        data,
        source: 'database',
        timestamp: new Date().toISOString(),
      };
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.warn('⚠️ Data service unavailable, falling back to mock data:', errorMessage);
      
      return {
        data: getMockCash(householdId, range),
        source: 'mock',
        timestamp: new Date().toISOString(),
      };
    }
  }

  /**
   * Get list of all households
   */
  async getHouseholds(): Promise<ApiResponse<any>> {
    if (!this.useDataService) {
      // Import mock households for fallback
      const { mockHouseholds, getHouseholdStats } = await import('./mock-households');
      const stats = getHouseholdStats();
      
      return {
        data: {
          households: mockHouseholds,
          totalCount: mockHouseholds.length,
          summaryStats: {
            totalHouseholds: stats.totalHouseholds,
            totalAssets: stats.totalAssets,
            totalCash: stats.totalCash,
            averagePerformance: stats.averagePerformance
          }
        },
        source: 'mock',
        timestamp: new Date().toISOString()
      };
    }

    try {
      console.log('🌐 Fetching households list from data service');
      const data = await this.makeRequest<any>('/api/households');
      
      return {
        data,
        source: 'database',
        timestamp: new Date().toISOString()
      };
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.warn(`Failed to fetch households from data service: ${errorMessage}, using fallback`);
      
      // Fallback to mock data
      const { mockHouseholds, getHouseholdStats } = await import('./mock-households');
      const stats = getHouseholdStats();
      
      return {
        data: {
          households: mockHouseholds,
          totalCount: mockHouseholds.length,
          summaryStats: {
            totalHouseholds: stats.totalHouseholds,
            totalAssets: stats.totalAssets,
            totalCash: stats.totalCash,
            averagePerformance: stats.averagePerformance
          }
        },
        source: 'mock',
        timestamp: new Date().toISOString()
      };
    }
  }

  /**
   * Health check for the data service
   */
  async checkHealth(): Promise<{ healthy: boolean; status: string; fallback: boolean }> {
    if (!this.useDataService) {
      return {
        healthy: true,
        status: 'Mock data mode',
        fallback: true,
      };
    }

    try {
      const health = await this.makeRequest<any>('/health');
      return {
        healthy: health.status === 'healthy',
        status: health.status,
        fallback: health.database === 'fallback_mode',
      };
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return {
        healthy: false,
        status: `Service unavailable: ${errorMessage}`,
        fallback: true,
      };
    }
  }

  /**
   * Get current data source configuration
   */
  getDataSourceStatus(): { 
    useDataService: boolean; 
    dataServiceUrl: string; 
    mode: 'database' | 'mock' | 'hybrid' 
  } {
    return {
      useDataService: this.useDataService,
      dataServiceUrl: this.baseUrl,
      mode: this.useDataService ? 'hybrid' : 'mock'
    };
  }

  // Mock data methods for non-implemented endpoints
  // These will continue to use mock data until we implement them in the data service

  async getAllocation(householdId: string) {
    console.log('🔄 Using mock data for allocation (not yet implemented in data service)');
    return {
      data: getMockAllocation(householdId),
      source: 'mock' as const,
      timestamp: new Date().toISOString(),
    };
  }

  async getActivity(householdId: string) {
    console.log('🔄 Using mock data for activity (not yet implemented in data service)');
    return {
      data: getMockActivity(householdId),
      source: 'mock' as const,
      timestamp: new Date().toISOString(),
    };
  }

  async getPlanning(householdId: string) {
    console.log('🔄 Using mock data for planning (not yet implemented in data service)');
    return {
      data: getMockPlanning(householdId),
      source: 'mock' as const,
      timestamp: new Date().toISOString(),
    };
  }

  async getPositions(householdId: string) {
    console.log('🔄 Using mock data for positions (not yet implemented in data service)');
    return {
      data: getMockPositions(householdId),
      source: 'mock' as const,
      timestamp: new Date().toISOString(),
    };
  }

  async getReports(householdId: string) {
    console.log('🔄 Using mock data for reports (not yet implemented in data service)');
    return {
      data: getMockReports(householdId),
      source: 'mock' as const,
      timestamp: new Date().toISOString(),
    };
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Utility function for backwards compatibility
export async function fetchData<T>(
  householdId: string,
  dataType: string,
  range?: string
): Promise<T> {
  let response: ApiResponse<T>;

  switch (dataType) {
    case 'overview':
      response = await apiClient.getOverview(householdId) as ApiResponse<T>;
      break;
    case 'performance':
      response = await apiClient.getPerformance(householdId, range || '6M') as ApiResponse<T>;
      break;
    case 'cash':
      response = await apiClient.getCash(householdId, range || '6M') as ApiResponse<T>;
      break;
    case 'allocation':
      response = await apiClient.getAllocation(householdId) as ApiResponse<T>;
      break;
    case 'activity':
      response = await apiClient.getActivity(householdId) as ApiResponse<T>;
      break;
    case 'planning':
      response = await apiClient.getPlanning(householdId) as ApiResponse<T>;
      break;
    case 'positions':
      response = await apiClient.getPositions(householdId) as ApiResponse<T>;
      break;
    case 'reports':
      response = await apiClient.getReports(householdId) as ApiResponse<T>;
      break;
    default:
      throw new Error(`Unknown data type: ${dataType}`);
  }

  // Log data source for debugging
  if (response.source === 'database') {
    console.log(`✅ ${dataType} data loaded from database`);
  } else {
    console.log(`📋 ${dataType} data loaded from mock (fallback)`);
  }

  return response.data;
}