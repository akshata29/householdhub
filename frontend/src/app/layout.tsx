import type { Metadata } from 'next'
import '@/styles/dashboard.css'
import { Providers } from '@/components/providers'

export const metadata: Metadata = {
  title: 'WealthOps - Professional Wealth Dashboard',
  description: 'Modern, responsive wealth management dashboard with comprehensive portfolio analytics',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}