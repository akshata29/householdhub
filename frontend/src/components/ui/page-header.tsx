import * as React from "react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  chips?: Array<{
    label: string;
    variant?: "default" | "secondary" | "success" | "warning" | "danger" | "muted";
  }>;
  actions?: React.ReactNode;
  className?: string;
}

export function PageHeader({
  title,
  subtitle,
  chips = [],
  actions,
  className,
}: PageHeaderProps) {
  return (
    <div className={cn("flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between", className)}>
      <div className="space-y-4">
        <div className="space-y-3">
          <h1 className="text-3xl lg:text-4xl font-bold tracking-tight bg-gradient-to-r from-slate-900 to-slate-700 dark:from-slate-100 dark:to-slate-300 bg-clip-text text-transparent">
            {title}
          </h1>
          {subtitle && (
            <p className="text-lg text-slate-600 dark:text-slate-300 font-medium">{subtitle}</p>
          )}
        </div>
        {chips.length > 0 && (
          <div className="flex flex-wrap items-center gap-2">
            {chips.map((chip, index) => (
              <Badge 
                key={index} 
                variant={chip.variant || "secondary"}
                className="px-3 py-1 text-xs font-medium"
              >
                {chip.label}
              </Badge>
            ))}
          </div>
        )}
      </div>
      {actions && (
        <div className="flex gap-3">
          {actions}
        </div>
      )}
    </div>
  );
}