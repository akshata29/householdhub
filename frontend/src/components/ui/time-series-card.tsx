"use client";

import * as React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { formatCurrency, formatDate, cn } from "@/lib/utils";

interface TimeSeriesData {
  date: string;
  value: number;
  benchmark?: number;
}

interface TimeSeriesCardProps {
  title: string;
  data: TimeSeriesData[];
  loading?: boolean;
  error?: string;
  height?: number;
  rangeOptions?: string[];
  selectedRange?: string;
  onRangeChange?: (range: string) => void;
  unit?: "currency" | "percentage";
  className?: string;
}

function CustomTooltip({ active, payload, label }: any) {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background: '#ffffff',
        border: '1px solid #e2e8f0',
        borderRadius: '8px',
        padding: '12px',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
      }}>
        <p style={{
          fontWeight: '600',
          fontSize: '14px',
          marginBottom: '4px',
          color: '#334155'
        }}>
          {formatDate(new Date(label), { style: "short" })}
        </p>
        {payload.map((entry: any, index: number) => (
          <p
            key={index}
            style={{
              fontSize: '13px',
              color: entry.color,
              fontWeight: '500'
            }}
          >
            {entry.dataKey === "benchmark" ? "Benchmark" : "Portfolio"}:{" "}
            {formatCurrency(entry.value, { compact: true })}
          </p>
        ))}
      </div>
    );
  }
  return null;
}

export function TimeSeriesCard({
  title,
  data,
  loading = false,
  error,
  height = 260,
  rangeOptions = [],
  selectedRange,
  onRangeChange,
  unit = "currency",
  className,
}: TimeSeriesCardProps) {
  const formatYAxis = (value: number) => {
    if (unit === "currency") {
      return formatCurrency(value, { compact: true });
    }
    return `${value}%`;
  };

  if (loading) {
    return (
      <Card className={cn("animate-fade-in", className)}>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>{title}</CardTitle>
          {rangeOptions.length > 0 && (
            <div className="flex gap-1">
              {rangeOptions.map((range) => (
                <div
                  key={range}
                  className="h-8 w-12 animate-pulse rounded bg-muted"
                />
              ))}
            </div>
          )}
        </CardHeader>
        <CardContent>
          <div
            className="animate-pulse rounded bg-muted"
            style={{ height }}
          />
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

  if (!data.length) {
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
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>{title}</CardTitle>
        {rangeOptions.length > 0 && (
          <div className="flex gap-1">
            {rangeOptions.map((range) => (
              <Button
                key={range}
                variant={selectedRange === range ? "default" : "ghost"}
                size="sm"
                onClick={() => onRangeChange?.(range)}
                className="h-8 px-3 text-xs"
              >
                {range}
              </Button>
            ))}
          </div>
        )}
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={height}>
          <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid 
              strokeDasharray="3 3" 
              className="stroke-muted" 
              opacity={0.3}
            />
            <XAxis
              dataKey="date"
              tickFormatter={(value) => {
                const date = new Date(value);
                return date.toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric"
                });
              }}
              className="text-xs fill-muted-foreground"
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tickFormatter={formatYAxis}
              className="text-xs fill-muted-foreground"
              axisLine={false}
              tickLine={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type="monotone"
              dataKey="value"
              stroke="#0f766e"
              strokeWidth={3}
              dot={false}
              activeDot={{ r: 6, fill: "#0f766e", stroke: "#ffffff", strokeWidth: 2 }}
            />
            {data.some(d => d.benchmark !== undefined) && (
              <Line
                type="monotone"
                dataKey="benchmark"
                stroke="#64748b"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                activeDot={{ r: 4, fill: "#64748b", stroke: "#ffffff", strokeWidth: 2 }}
              />
            )}
            {data.some(d => d.benchmark !== undefined) && (
              <Legend
                wrapperStyle={{ fontSize: "12px" }}
                iconType="line"
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}