"use client"

import { useEffect } from 'react'
import { createRoot } from 'react-dom/client'
import { ThemeToggle } from './theme-toggle'

export function mountThemeToggle(rootId = 'theme-toggle-root') {
  useEffect(() => {
    const el = document.getElementById(rootId)
    if (!el) return
    // clear existing content then mount
    el.innerHTML = ''
    const root = createRoot(el)
    root.render(<ThemeToggle />)
    return () => root.unmount()
  }, [rootId])
  return null
}
