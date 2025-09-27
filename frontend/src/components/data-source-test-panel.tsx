// Test component to verify data source indicator functionality
// This can be temporarily added to test the data source switching

'use client';

import React, { useState } from 'react';
import { apiClient } from '@/lib/api-client';
import { DataSourcePanel } from '@/components/data-source-indicator';

export function DataSourceTestPanel() {
  const [testResult, setTestResult] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const testDataSource = async () => {
    setIsLoading(true);
    setTestResult('Testing...');
    
    try {
      // Test the data source status
      const status = apiClient.getDataSourceStatus();
      console.log('Data Source Status:', status);
      
      // Test health check if data service is enabled
      if (status.useDataService) {
        const health = await apiClient.checkHealth();
        console.log('Health Check:', health);
        
        setTestResult(`
📊 Data Source: ${status.mode}
🌐 Service URL: ${status.dataServiceUrl}
❤️ Health: ${health.healthy ? 'Healthy' : 'Unhealthy'}
📈 Status: ${health.status}
🔄 Fallback: ${health.fallback ? 'Yes' : 'No'}
        `);
      } else {
        setTestResult(`
📊 Data Source: Mock Mode
🔧 Development: Using local mock data
✅ Status: Ready
        `);
      }
    } catch (error) {
      console.error('Test failed:', error);
      setTestResult(`❌ Test failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const testAPI = async () => {
    setIsLoading(true);
    setTestResult('Testing API endpoints...');
    
    try {
      // Test overview endpoint
      const overview = await apiClient.getOverview('johnson-family-trust');
      console.log('Overview Response:', overview);
      
      // Test performance endpoint  
      const performance = await apiClient.getPerformance('johnson-family-trust', '6M');
      console.log('Performance Response:', performance);
      
      // Test cash endpoint
      const cash = await apiClient.getCash('johnson-family-trust', '6M');
      console.log('Cash Response:', cash);
      
      setTestResult(`
✅ Overview: ${overview.source} source (${overview.data.totalAssets} assets)
✅ Performance: ${performance.source} source (${performance.data.data.length} data points)  
✅ Cash: ${cash.source} source (${cash.data.accounts.length} accounts)
      `);
    } catch (error) {
      console.error('API test failed:', error);
      setTestResult(`❌ API test failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white border rounded-lg p-4 space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Data Source Test Panel</h3>
      
      <div className="space-y-2">
        <DataSourcePanel />
      </div>
      
      <div className="flex gap-2">
        <button
          onClick={testDataSource}
          disabled={isLoading}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {isLoading ? 'Testing...' : 'Test Data Source'}
        </button>
        
        <button
          onClick={testAPI}
          disabled={isLoading}
          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
        >
          {isLoading ? 'Testing...' : 'Test API Endpoints'}
        </button>
      </div>
      
      {testResult && (
        <div className="bg-gray-50 border rounded p-3">
          <pre className="text-sm whitespace-pre-wrap text-gray-700">{testResult}</pre>
        </div>
      )}
    </div>
  );
}