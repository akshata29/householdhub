"use client"
import { ThemeToggle } from '@/components/ui/theme-toggle'

interface HouseholdHeaderProps {
  householdId: string
}

interface HouseholdData {
  householdId: string
  name: string
  primaryAdvisor: string
  totalAssets: number
  lastActivity: string
  riskProfile: string
  accountsCount: number
}

const mockHouseholdData: Record<string, HouseholdData> = {
  HH001: {
    householdId: 'HH001',
    name: 'John & Sarah Mitchell',
    primaryAdvisor: 'Jane Smith',
    totalAssets: 2400000,
    lastActivity: '2024-09-25',
    riskProfile: 'Moderate',
    accountsCount: 4
  }
}

export function HouseholdHeader({ householdId }: HouseholdHeaderProps) {
  const household = mockHouseholdData[householdId] || mockHouseholdData.HH001

  return (
    <div className="bg-white border-b border-gray-200 px-6 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center">
            <span className="text-white font-bold">W</span>
          </div>
          <div>
            <div className="text-sm font-semibold text-gray-900">WealthOPS</div>
            <div className="text-xs text-gray-500">{household.primaryAdvisor} • {household.householdId}</div>
          </div>
        </div>

        <div className="flex items-center gap-8">
          <div className="text-right">
            <div className="text-sm text-gray-500">Total Assets</div>
            <div className="text-lg font-semibold text-gray-900">${(household.totalAssets / 1000000).toFixed(2)}M</div>
          </div>

          <div className="text-right">
            <div className="text-sm text-gray-500">YTD Return</div>
            <div className="text-lg font-semibold text-green-600">+8.7%</div>
          </div>

          <div className="text-right">
            <div className="text-sm text-gray-500">Accounts</div>
            <div className="text-lg font-semibold text-gray-900">{household.accountsCount}</div>
          </div>

          <ThemeToggle />
        </div>
      </div>
    </div>
  )
}

// no client mount helper needed anymore; ThemeToggle is a client component