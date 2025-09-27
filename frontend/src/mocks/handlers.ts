import { http, HttpResponse } from 'msw';
import {
  generateOverviewData,
  generatePerformanceData,
  generateAllocationData,
  generateActivityData,
  generateCashData,
  generatePlanningData,
  generatePositionsData,
  generateReportsData,
} from './data';

// Simulate realistic network delay
const delay = () => new Promise(resolve => setTimeout(resolve, Math.random() * 800 + 200));

export const handlers = [
  // Overview data
  http.get('/api/households/:id/overview', async ({ params }) => {
    await delay();
    const householdId = params.id as string;
    const data = generateOverviewData(householdId);
    return HttpResponse.json(data);
  }),

  // Performance data
  http.get('/api/households/:id/performance', async ({ request }) => {
    await delay();
    const url = new URL(request.url);
    const range = url.searchParams.get('range') || '6M';
    const data = generatePerformanceData(range);
    return HttpResponse.json(data);
  }),

  // Asset allocation
  http.get('/api/households/:id/allocation', async () => {
    await delay();
    const data = generateAllocationData();
    return HttpResponse.json(data);
  }),

  // Activity feed
  http.get('/api/households/:id/activity', async ({ request }) => {
    await delay();
    const url = new URL(request.url);
    const limit = parseInt(url.searchParams.get('limit') || '10');
    const offset = parseInt(url.searchParams.get('offset') || '0');
    
    const allData = generateActivityData();
    const activities = allData.activities.slice(offset, offset + limit);
    
    return HttpResponse.json({
      ...allData,
      activities,
    });
  }),

  // Cash management
  http.get('/api/households/:id/cash', async () => {
    await delay();
    const data = generateCashData();
    return HttpResponse.json(data);
  }),

  // Planning data (RMDs, beneficiaries)
  http.get('/api/households/:id/planning', async () => {
    await delay();
    const data = generatePlanningData();
    return HttpResponse.json(data);
  }),

  // Portfolio positions
  http.get('/api/households/:id/positions', async () => {
    await delay();
    const data = generatePositionsData();
    return HttpResponse.json(data);
  }),

  // Reports and statements
  http.get('/api/households/:id/reports', async () => {
    await delay();
    const data = generateReportsData();
    return HttpResponse.json(data);
  }),

  // Simulate occasional errors for error state testing
  http.get('/api/households/:id/error-test', async () => {
    await delay();
    return HttpResponse.json(
      { message: 'Service temporarily unavailable' },
      { status: 503 }
    );
  }),
];