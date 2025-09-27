import * as React from "react";
import { LucideIcon } from "lucide-react";
import { formatCurrency, formatPercentage } from "@/lib/utils";

interface KPICardProps {
  label: string;
  value: number | string;
  delta?: {
    value: number;
    label?: string;
    type?: "currency" | "percentage";
  };
  icon?: LucideIcon;
  trend?: "up" | "down" | "neutral";
  format?: "currency" | "percentage" | "number" | "text";
  loading?: boolean;
  className?: string;
}

export function KPICard({
  label,
  value,
  delta,
  icon: Icon,
  trend,
  format = "currency",
  loading = false,
  className,
}: KPICardProps) {
  const formatValue = (val: number | string) => {
    if (typeof val === "string") return val;
    
    switch (format) {
      case "currency":
        return formatCurrency(val, { compact: val > 1000000 });
      case "percentage":
        return formatPercentage(val);
      case "number":
        return new Intl.NumberFormat("en-US").format(val);
      default:
        return String(val);
    }
  };

  const formatDelta = (deltaVal: number, type: "currency" | "percentage" = "percentage") => {
    if (type === "currency") {
      const sign = deltaVal >= 0 ? "+" : "";
      return sign + formatCurrency(Math.abs(deltaVal));
    }
    return formatPercentage(deltaVal, { showSign: true });
  };

  const getDeltaClass = () => {
    if (!delta) return "";
    
    if (delta.value > 0) {
      return "positive";
    } else if (delta.value < 0) {
      return "negative";
    }
    return "neutral";
  };

  if (loading) {
    return (
      <div className="kpi-card">
        <div className="loading-state">Loading...</div>
      </div>
    );
  }

  return (
    <div className={`kpi-card ${className || ''}`}>
      {Icon && (
        <div className="kpi-icon">
          <Icon className="icon" />
        </div>
      )}
      <div className="kpi-content">
        <div className="kpi-label">{label}</div>
        <div className="kpi-value font-tabular">
          {formatValue(value)}
        </div>
        {delta && (
          <div className={`kpi-delta ${getDeltaClass()}`}>
            {formatDelta(delta.value, delta.type)}
            {delta.label && ` ${delta.label}`}
          </div>
        )}
      </div>
    </div>
  );
}