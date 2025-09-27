'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { ThemeProvider } from '@/design/theme-provider'
import { useState, useEffect } from 'react'

// Initialize MSW in development
let mswPromise: Promise<void> | null = null

if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  mswPromise = import('@/mocks/browser').then(({ worker }) =>
    worker.start({ onUnhandledRequest: 'bypass' }).then(() => undefined)
  )
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 5 * 60 * 1000, // 5 minutes
        retry: 2,
        refetchOnWindowFocus: false,
      },
    },
  }))

  const [mswReady, setMswReady] = useState(false)

  useEffect(() => {
    if (!mswPromise) {
      setMswReady(true)
      return
    }
    mswPromise.then(() => setMswReady(true)).catch(() => setMswReady(true))
  }, [])

  return (
    <ThemeProvider defaultTheme="system" storageKey="wealthops-theme">
      <QueryClientProvider client={queryClient}>
        {mswReady ? children : null}
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </ThemeProvider>
  )
}