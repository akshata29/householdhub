"use client"

import { useEffect, useState } from 'react'

export function ThemeToggle() {
  const [isDark, setIsDark] = useState(false)

  useEffect(() => {
    const prefersDark = typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
    const stored = typeof window !== 'undefined' ? localStorage.getItem('theme') : null
    if (stored) setIsDark(stored === 'dark')
    else setIsDark(prefersDark)
  }, [])

  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.classList.toggle('dark', isDark)
      localStorage.setItem('theme', isDark ? 'dark' : 'light')
    }
  }, [isDark])

  return (
    <button
      aria-label="Toggle theme"
      className="theme-toggle"
      onClick={() => setIsDark((v) => !v)}
      title={isDark ? 'Switch to light' : 'Switch to dark'}
    >
      {/* Simple text icons instead of SVGs to avoid any vector scaling issues */}
      <span className="text-lg leading-none">{isDark ? '☀' : '🌙'}</span>
    </button>
  )
}
