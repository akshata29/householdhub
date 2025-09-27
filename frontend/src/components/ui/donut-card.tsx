"use client";

import * as React from "react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCurrency, formatPercentage, cn, getChartColors } from "@/lib/utils";

interface DonutData {
  name: string;
  value: number;
  percentage: number;
  target?: number;
  color?: string;
}

interface DonutCardProps {
  title: string;
  data: DonutData[];
  loading?: boolean;
  error?: string;
  legendPlacement?: "right" | "bottom";
  className?: string;
}

function CustomTooltip({ active, payload }: any) {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="rounded-lg border bg-background p-3 shadow-md">
        <p className="font-medium text-sm mb-1">{data.name}</p>
        <p className="text-sm text-muted-foreground">
          {formatCurrency(data.value, { compact: true })} ({formatPercentage(data.percentage)})
        </p>
      </div>
    );
  }
  return null;
}

function CustomLegend({ payload, placement }: any) {
  if (!payload) return null;

  const isHorizontal = placement === "bottom";
  
  return (
    <div className={cn(
      "legend-container",
      isHorizontal ? "legend-bottom" : "legend-right"
    )}>
      {payload.map((entry: any, index: number) => {
        const item = entry.payload;
        const hasTarget = item.target !== undefined;
        
        return (
          <div key={index} className="legend-item">
            <div className="legend-indicator">
              <div
                className="legend-dot"
                style={{ backgroundColor: entry.color }}
              />
            </div>
            <div className="legend-content">
              <div className="legend-name">{entry.value}</div>
              <div className="legend-stats">
                <span className="current-percentage">
                  {formatPercentage(item.percentage)}
                </span>
                {hasTarget && (
                  <span className="target-percentage">
                    vs {formatPercentage(item.target)} target
                  </span>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function DonutCard({
  title,
  data,
  loading = false,
  error,
  legendPlacement = "right",
  className,
}: DonutCardProps) {
  // Ensure we have colors for all data points
  const chartData = React.useMemo(() => {
    const colors = getChartColors(data.length);
    return data.map((item, index) => ({
      ...item,
      color: item.color || colors[index],
    }));
  }, [data]);

  if (loading) {
    return (
      <Card className={cn("animate-fade-in", className)}>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className={cn(
            "flex gap-6",
            legendPlacement === "bottom" ? "flex-col" : "flex-col lg:flex-row"
          )}>
            <div className="flex-1">
              <div className="h-64 animate-pulse rounded-full bg-muted mx-auto w-64" />
            </div>
            {legendPlacement === "right" && (
              <div className="w-full lg:w-48 space-y-2">
                {Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <div className="h-3 w-3 animate-pulse rounded-sm bg-muted" />
                    <div className="h-3 flex-1 animate-pulse rounded bg-muted" />
                  </div>
                ))}
              </div>
            )}
          </div>
          {legendPlacement === "bottom" && (
            <div className="flex gap-4 justify-center mt-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="flex items-center gap-2">
                  <div className="h-3 w-3 animate-pulse rounded-sm bg-muted" />
                  <div className="h-3 w-16 animate-pulse rounded bg-muted" />
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={cn("border-red-200 bg-red-50/50 dark:border-red-800 dark:bg-red-950/10", className)}>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <p className="text-sm text-red-600 dark:text-red-400">
              Failed to load chart data
            </p>
            <p className="text-xs text-red-500 dark:text-red-500 mt-1">
              {error}
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!chartData.length) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8 text-center">
            <p className="text-sm text-muted-foreground">No data available</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn("animate-fade-in", className)}>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className={cn(
          "donut-chart-container",
          legendPlacement === "bottom" ? "layout-bottom" : "layout-right"
        )}>
          <div className="chart-area">
            <ResponsiveContainer 
              width="100%" 
              height={legendPlacement === "bottom" ? 280 : 240}
            >
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="45%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                {legendPlacement === "bottom" && (
                  <Legend
                    content={(props) => <CustomLegend {...props} placement="bottom" />}
                  />
                )}
              </PieChart>
            </ResponsiveContainer>
          </div>
          
          {legendPlacement === "right" && (
            <div className="w-full lg:w-48">
              <CustomLegend 
                payload={chartData.map(item => ({ 
                  value: item.name, 
                  color: item.color,
                  payload: item 
                }))} 
                placement="right"
              />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}