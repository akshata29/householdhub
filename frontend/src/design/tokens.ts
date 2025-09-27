/**
 * Design System Tokens
 * Centralized design tokens for the WealthOps dashboard
 */

export const tokens = {
  // Colors (maps to CSS variables)
  colors: {
    // Backgrounds
    bg: 'var(--bg)',
    card: 'var(--card)',
    muted: 'var(--muted)',
    
    // Brand
    primary: 'var(--primary)',
    primaryForeground: 'var(--primary-foreground)',
    accent: 'var(--accent)',
    
    // Status
    success: 'var(--success)',
    warning: 'var(--warning)',
    danger: 'var(--danger)',
    
    // Chart palette
    chart: {
      1: 'var(--chart-1)',
      2: 'var(--chart-2)',
      3: 'var(--chart-3)',
      4: 'var(--chart-4)',
      5: 'var(--chart-5)',
      6: 'var(--chart-6)',
    },
  },

  // Typography scale
  typography: {
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif'],
      mono: ['ui-monospace', 'SFMono-Regular', 'Monaco', 'Consolas', 'monospace'],
    },
    fontSize: {
      xs: '0.75rem',    // 12px
      sm: '0.875rem',   // 14px
      base: '1rem',     // 16px
      lg: '1.25rem',    // 20px
      xl: '1.5rem',     // 24px
      '2xl': '1.875rem', // 30px
    },
    lineHeight: {
      tight: 1.2,
      normal: 1.5,
      relaxed: 1.6,
    },
  },

  // Spacing (8px units)
  spacing: {
    unit: '0.5rem', // 8px
    cardPadding: {
      mobile: '0.75rem',   // 12px (p-3)
      tablet: '1rem',      // 16px (p-4)  
      desktop: '1.25rem',  // 20px (p-5)
    },
    containerMaxWidth: '87.5rem', // 1400px
  },

  // Border radius
  radius: {
    sm: '0.25rem',   // 4px
    md: '0.5rem',    // 8px
    lg: '1rem',      // 16px
    xl: '1.5rem',    // 24px
    card: '1rem',    // 16px (rounded-2xl maps to 1rem in Tailwind)
  },

  // Shadows
  shadow: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  },

  // Icon sizes
  iconSizes: {
    xs: '1rem',      // 16px
    sm: '1.25rem',   // 20px (chips/pills)
    md: '1.5rem',    // 24px (card headers)
    lg: '2rem',      // 32px
    xl: '2.5rem',    // 40px
  },

  // Motion
  motion: {
    duration: {
      fast: 150,    // Tab transitions
      medium: 250,
      slow: 400,
    },
    easing: {
      default: 'cubic-bezier(0.4, 0, 0.2, 1)',
      bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
    },
  },

  // Breakpoints (matches Tailwind defaults)
  breakpoints: {
    sm: '640px',
    md: '768px', 
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },

  // Grid system
  grid: {
    columns: {
      mobile: 1,
      tablet: 6,
      desktop: 12,
      wide: 12,
    },
    gap: {
      mobile: '1rem',
      tablet: '1.5rem', 
      desktop: '2rem',
    },
  },
} as const;

export type Tokens = typeof tokens;