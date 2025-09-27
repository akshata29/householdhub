import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const statusPillVariants = cva(
  "inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-medium",
  {
    variants: {
      variant: {
        success: "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400",
        warning: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400", 
        danger: "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400",
        muted: "bg-muted text-muted-foreground",
      },
    },
    defaultVariants: {
      variant: "muted",
    },
  }
);

export interface StatusPillProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof statusPillVariants> {
  icon?: React.ReactNode;
}

export function StatusPill({ 
  className, 
  variant, 
  icon,
  children,
  ...props 
}: StatusPillProps) {
  return (
    <div 
      className={cn(statusPillVariants({ variant }), className)} 
      {...props}
    >
      {icon}
      {children}
    </div>
  );
}