import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Combines class names using clsx and tailwind-merge
 * This ensures Tailwind classes are properly merged and overridden
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format currency values with proper locale and precision
 */
export function formatCurrency(
  amount: number,
  options: {
    locale?: string;
    currency?: string;
    minimumFractionDigits?: number;
    maximumFractionDigits?: number;
    compact?: boolean;
  } = {}
): string {
  const {
    locale = "en-US",
    currency = "USD",
    minimumFractionDigits = 0,
    maximumFractionDigits = 2,
    compact = false,
  } = options;

  const formatter = new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
    minimumFractionDigits,
    maximumFractionDigits,
    notation: compact ? "compact" : "standard",
    compactDisplay: compact ? "short" : undefined,
  });

  return formatter.format(amount);
}

/**
 * Format percentage values
 */
export function formatPercentage(
  value: number,
  options: {
    minimumFractionDigits?: number;
    maximumFractionDigits?: number;
    showSign?: boolean;
  } = {}
): string {
  const {
    minimumFractionDigits = 1,
    maximumFractionDigits = 2,
    showSign = false,
  } = options;

  const formatter = new Intl.NumberFormat("en-US", {
    style: "percent",
    minimumFractionDigits,
    maximumFractionDigits,
    signDisplay: showSign ? "always" : "auto",
  });

  return formatter.format(value / 100);
}

/**
 * Format large numbers with compact notation (e.g., 1.2M, 1.5B)
 */
export function formatCompactNumber(
  value: number,
  options: {
    minimumFractionDigits?: number;
    maximumFractionDigits?: number;
  } = {}
): string {
  const {
    minimumFractionDigits = 0,
    maximumFractionDigits = 1,
  } = options;

  const formatter = new Intl.NumberFormat("en-US", {
    notation: "compact",
    minimumFractionDigits,
    maximumFractionDigits,
  });

  return formatter.format(value);
}

/**
 * Format dates for display
 */
export function formatDate(
  date: Date | string,
  options: {
    style?: "short" | "medium" | "long" | "relative";
    includeTime?: boolean;
  } = {}
): string {
  const { style = "medium", includeTime = false } = options;
  const dateObj = typeof date === "string" ? new Date(date) : date;

  if (style === "relative") {
    const now = new Date();
    const diffMs = now.getTime() - dateObj.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    return `${Math.floor(diffDays / 365)} years ago`;
  }

  const formatOptions: Intl.DateTimeFormatOptions = {};
  
  switch (style) {
    case "short":
      formatOptions.month = "short";
      formatOptions.day = "numeric";
      formatOptions.year = "2-digit";
      break;
    case "medium":
      formatOptions.month = "short";
      formatOptions.day = "numeric";
      formatOptions.year = "numeric";
      break;
    case "long":
      formatOptions.weekday = "long";
      formatOptions.month = "long";
      formatOptions.day = "numeric";
      formatOptions.year = "numeric";
      break;
  }

  if (includeTime) {
    formatOptions.hour = "numeric";
    formatOptions.minute = "2-digit";
    formatOptions.hour12 = true;
  }

  return new Intl.DateTimeFormat("en-US", formatOptions).format(dateObj);
}

/**
 * Calculate days remaining until a date
 */
export function getDaysRemaining(date: Date | string): number {
  const targetDate = typeof date === "string" ? new Date(date) : date;
  const now = new Date();
  const diffMs = targetDate.getTime() - now.getTime();
  return Math.ceil(diffMs / (1000 * 60 * 60 * 24));
}

/**
 * Get urgency level based on days remaining
 */
export function getUrgencyLevel(daysRemaining: number): "critical" | "warning" | "normal" {
  if (daysRemaining <= 7) return "critical";
  if (daysRemaining <= 30) return "warning";
  return "normal";
}

/**
 * Generate chart colors based on data length
 */
export function getChartColors(length: number): string[] {
  const colors = [
    "rgb(var(--chart-1))",
    "rgb(var(--chart-2))",
    "rgb(var(--chart-3))",
    "rgb(var(--chart-4))",
    "rgb(var(--chart-5))",
    "rgb(var(--chart-6))",
  ];
  
  // Repeat colors if we need more than 6
  const result = [];
  for (let i = 0; i < length; i++) {
    result.push(colors[i % colors.length]);
  }
  
  return result;
}

/**
 * Debounce function for search inputs
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

/**
 * Generate consistent status pill variants
 */
export function getStatusVariant(
  status: string
): "success" | "warning" | "danger" | "muted" {
  const statusLower = status.toLowerCase();
  
  if (statusLower.includes("complete") || statusLower.includes("ok") || statusLower.includes("active")) {
    return "success";
  }
  
  if (statusLower.includes("pending") || statusLower.includes("review") || statusLower.includes("due")) {
    return "warning";
  }
  
  if (statusLower.includes("missing") || statusLower.includes("error") || statusLower.includes("overdue")) {
    return "danger";
  }
  
  return "muted";
}

/**
 * Safely parse JSON with fallback
 */
export function safeJsonParse<T>(json: string, fallback: T): T {
  try {
    return JSON.parse(json);
  } catch {
    return fallback;
  }
}

/**
 * Create a stable key for React components
 */
export function createKey(...parts: (string | number)[]): string {
  return parts.join("-");
}