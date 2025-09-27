'use client';

import React, { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api-client';
import { Database, FileText, Wifi, WifiOff, AlertCircle, CheckCircle2, ChevronDown } from 'lucide-react';

interface DataSourceStatus {
  useDataService: boolean;
  dataServiceUrl: string;
  mode: 'database' | 'mock' | 'hybrid';
  health?: {
    healthy: boolean;
    status: string;
    fallback: boolean;
  };
}

interface DataSourceIndicatorProps {
  className?: string;
  showDetails?: boolean;
}

export function DataSourceIndicator({ 
  className = '', 
  showDetails = false 
}: DataSourceIndicatorProps) {
  const [status, setStatus] = useState<DataSourceStatus | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkStatus = async () => {
      setIsLoading(true);
      try {
        const sourceStatus = apiClient.getDataSourceStatus();
        let health = undefined;

        // Only check health if data service is enabled
        if (sourceStatus.useDataService) {
          try {
            health = await apiClient.checkHealth();
          } catch (error) {
            health = {
              healthy: false,
              status: 'Service unavailable',
              fallback: true,
            };
          }
        }

        setStatus({
          ...sourceStatus,
          health,
        });
      } catch (error) {
        console.error('Failed to check data source status:', error);
      } finally {
        setIsLoading(false);
      }
    };

    checkStatus();
    
    // Check status every 30 seconds if data service is enabled
    const interval = setInterval(() => {
      if (status?.useDataService) {
        checkStatus();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [status?.useDataService]);

  if (isLoading || !status) {
    return (
      <div className={`data-source-indicator-loading ${className}`}>
        <div className="data-source-loading-dot"></div>
        <span className="data-source-loading-text">Checking...</span>
      </div>
    );
  }

  const getStatusInfo = () => {
    if (!status.useDataService) {
      return {
        icon: FileText,
        color: 'text-blue-600 bg-blue-100',
        label: 'Mock Data',
        description: 'Using local mock data for development',
        status: 'development'
      };
    }

    if (status.health?.healthy && !status.health.fallback) {
      return {
        icon: Database,
        color: 'text-green-600 bg-green-100',
        label: 'Database',
        description: 'Connected to production database',
        status: 'connected'
      };
    }

    if (status.health?.healthy && status.health.fallback) {
      return {
        icon: AlertCircle,
        color: 'text-yellow-600 bg-yellow-100',
        label: 'Fallback Mode',
        description: 'Data service running but using fallback data',
        status: 'fallback'
      };
    }

    return {
      icon: WifiOff,
      color: 'text-red-600 bg-red-100',
      label: 'Service Down',
      description: 'Data service unavailable, using mock data',
      status: 'error'
    };
  };

  const statusInfo = getStatusInfo();
  const Icon = statusInfo.icon;

  const handleClick = () => {
    if (showDetails) {
      setIsExpanded(!isExpanded);
    }
  };

  return (
    <div className={`data-source-indicator ${className}`}>
      <div 
        className="data-source-indicator-container"
        onClick={handleClick}
        title={statusInfo.description}
      >
        <div className={`data-source-icon-container ${statusInfo.color}`}>
          <Icon className="data-source-icon" />
        </div>
        
        <span className="data-source-label">
          {statusInfo.label}
        </span>

        {status.useDataService && status.health && (
          <div>
            {status.health.healthy ? (
              <CheckCircle2 className="data-source-health-icon text-green-500" />
            ) : (
              <WifiOff className="data-source-health-icon text-red-500" />
            )}
          </div>
        )}

        {showDetails && (
          <svg 
            className={`data-source-dropdown-icon ${isExpanded ? 'expanded' : ''}`}
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        )}
      </div>

      {showDetails && isExpanded && (
        <div className="mt-2 p-3 bg-gray-50 rounded-lg border text-sm">
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Mode:</span>
              <span className="font-medium">{status.mode}</span>
            </div>
            
            {status.useDataService && (
              <>
                <div className="flex justify-between">
                  <span className="text-gray-600">Service URL:</span>
                  <span className="font-mono text-xs">{status.dataServiceUrl}</span>
                </div>
                
                {status.health && (
                  <>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Health:</span>
                      <span className={`font-medium ${
                        status.health.healthy ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {status.health.healthy ? 'Healthy' : 'Unhealthy'}
                      </span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-gray-600">Status:</span>
                      <span className="font-medium">{status.health.status}</span>
                    </div>

                    {status.health.fallback && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Data Source:</span>
                        <span className="font-medium text-yellow-600">Fallback</span>
                      </div>
                    )}
                  </>
                )}
              </>
            )}

            <div className="pt-2 border-t border-gray-200">
              <p className="text-xs text-gray-500">
                {statusInfo.description}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Compact version for headers/toolbars
export function DataSourceBadge({ className = '' }: { className?: string }) {
  return <DataSourceIndicator className={className} showDetails={false} />;
}

// Compact expandable panel version with modern styling
export function DataSourcePanel({ className = '' }: { className?: string }) {
  const [status, setStatus] = useState<DataSourceStatus | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkStatus = async () => {
      setIsLoading(true);
      try {
        const sourceStatus = apiClient.getDataSourceStatus();
        let health = undefined;

        if (sourceStatus.useDataService) {
          try {
            health = await apiClient.checkHealth();
          } catch (error) {
            health = {
              healthy: false,
              status: 'Service unavailable',
              fallback: true,
            };
          }
        }

        setStatus({
          ...sourceStatus,
          mode: sourceStatus.useDataService 
            ? (health?.healthy && !health?.fallback ? 'database' : 'hybrid')
            : 'mock',
          health
        });
      } catch (error) {
        setStatus({
          useDataService: false,
          dataServiceUrl: 'http://localhost:8010',
          mode: 'mock'
        });
      }
      setIsLoading(false);
    };

    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  if (isLoading || !status) {
    return (
      <div className={`data-source-panel-loading ${className}`}>
        <div className="data-source-loading-dot" />
        <span className="data-source-loading-text">Checking...</span>
      </div>
    );
  }

  const getStatusInfo = () => {
    if (!status.useDataService) {
      return {
        icon: FileText,
        dot: <div className="w-2 h-2 bg-orange-400 rounded-full" />,
        label: 'Mock',
        bgColor: 'bg-orange-50',
        textColor: 'text-orange-700',
        borderColor: 'border-orange-200',
        description: 'Using mock data for development'
      };
    }

    if (status.health?.healthy && !status.health.fallback) {
      return {
        icon: Database,
        dot: <div className="w-2 h-2 bg-green-500 rounded-full" />,
        label: 'Database',
        bgColor: 'bg-green-50',
        textColor: 'text-green-700',
        borderColor: 'border-green-200',
        description: 'Connected to production database'
      };
    }

    if (status.health?.healthy && status.health.fallback) {
      return {
        icon: AlertCircle,
        dot: <div className="w-2 h-2 bg-yellow-500 rounded-full" />,
        label: 'Hybrid',
        bgColor: 'bg-yellow-50',
        textColor: 'text-yellow-700',
        borderColor: 'border-yellow-200',
        description: 'Service running but using fallback data'
      };
    }

    return {
      icon: WifiOff,
      dot: <div className="w-2 h-2 bg-red-500 rounded-full" />,
      label: 'Offline',
      bgColor: 'bg-red-50',
      textColor: 'text-red-700',
      borderColor: 'border-red-200',
      description: 'Data service unavailable, using mock data'
    };
  };

  const statusInfo = getStatusInfo();
  const Icon = statusInfo.icon;

  const handleClick = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className={`data-source-panel ${className}`}>
      <div 
        className={`data-source-panel-container ${statusInfo.bgColor} ${statusInfo.textColor} ${statusInfo.borderColor}`}
        onClick={handleClick}
        title={statusInfo.description}
      >
        <div className="data-source-panel-icon-group">
          {statusInfo.dot}
          <Icon className="data-source-panel-icon" />
        </div>
        
        <span className="data-source-panel-label">{statusInfo.label}</span>

        {status.health && (
          <CheckCircle2 className="data-source-panel-health-icon text-green-500" />
        )}

        <ChevronDown className={`data-source-panel-dropdown ${isExpanded ? 'expanded' : ''}`} />
      </div>

      {isExpanded && (
        <div className="data-source-panel-expanded">
          <div className="data-source-panel-details">
            <div className="data-source-detail-row">
              <span className="data-source-detail-label">Mode:</span>
              <span className="data-source-detail-value">{status.mode}</span>
            </div>
            
            {status.useDataService && (
              <>
                <div className="data-source-detail-row">
                  <span className="data-source-detail-label">Service URL:</span>
                  <span className="data-source-detail-url">{status.dataServiceUrl}</span>
                </div>
                
                {status.health && (
                  <>
                    <div className="data-source-detail-row">
                      <span className="data-source-detail-label">Health:</span>
                      <span className={`data-source-detail-value ${
                        status.health.healthy ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {status.health.healthy ? 'Healthy' : 'Unhealthy'}
                      </span>
                    </div>
                    
                    <div className="data-source-detail-row">
                      <span className="data-source-detail-label">Status:</span>
                      <span className="data-source-detail-value">{status.health.status}</span>
                    </div>

                    {status.health.fallback && (
                      <div className="data-source-detail-row">
                        <span className="data-source-detail-label">Data Source:</span>
                        <span className="data-source-detail-value text-yellow-600">Fallback</span>
                      </div>
                    )}
                  </>
                )}
              </>
            )}

            <div className="data-source-detail-description">
              <p>{statusInfo.description}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}