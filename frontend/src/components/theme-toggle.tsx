'use client';

import React from 'react';
import { Moon, Sun, Monitor } from 'lucide-react';
import { useTheme } from '@/design/theme-provider';

export function ThemeToggle() {
  const { theme, setTheme, resolvedTheme } = useTheme();

  const cycleTheme = () => {
    if (theme === 'light') {
      setTheme('dark');
    } else if (theme === 'dark') {
      setTheme('system');
    } else {
      setTheme('light');
    }
  };

  const getIcon = () => {
    if (theme === 'system') {
      return <Monitor className="theme-icon" />;
    } else if (resolvedTheme === 'dark') {
      return <Moon className="theme-icon" />;
    } else {
      return <Sun className="theme-icon" />;
    }
  };

  const getTooltipText = () => {
    if (theme === 'system') {
      return 'System theme';
    } else if (theme === 'dark') {
      return 'Dark theme';
    } else {
      return 'Light theme';
    }
  };

  return (
    <button
      onClick={cycleTheme}
      className="theme-toggle"
      title={getTooltipText()}
      aria-label={getTooltipText()}
    >
      {getIcon()}
    </button>
  );
}