'use client'

import { PortfolioChart } from '@/components/ui/portfolio-chart'

interface TopCashCardProps {
  householdId: string
}

const mockCashData = [
  { name: 'Checking', value: 85000, account: 'BOA-001', yield: 0.1 },
  { name: 'High-Yield Savings', value: 125000, account: 'MS-002', yield: 4.2 },
  { name: 'Money Market', value: 90000, account: 'FID-003', yield: 3.8 },
  { name: 'CD (6-month)', value: 50000, account: 'CS-004', yield: 4.5 }
]

const mockCashTrend = [
  { name: 'Jul', value: 320000 },
  { name: 'Aug', value: 335000 },
  { name: 'Sep', value: 350000 }
]

export function TopCashCard({ householdId }: TopCashCardProps) {
  const totalCash = mockCashData.reduce((sum, item) => sum + item.value, 0)
  const avgYield = mockCashData.reduce((sum, item) => sum + (item.value * item.yield), 0) / totalCash

  return (
    <div className="chart-container animate-fade-in">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between mb-8">
        <div className="flex items-center gap-4 mb-4 lg:mb-0">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center shadow-lg">
            <span className="text-2xl">💵</span>
          </div>
          <div>
            <h3 className="text-2xl font-bold text-slate-900 dark:text-white">
              Cash Positions
            </h3>
            <p className="text-slate-600 dark:text-slate-400">Liquid assets & yield optimization</p>
          </div>
        </div>
        
        {/* Summary Stats */}
        <div className="flex items-center gap-8">
          <div className="text-center">
            <div className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">
              ${(totalCash / 1000).toFixed(0)}K
            </div>
            <div className="text-sm font-medium text-slate-500 dark:text-slate-400">Total Cash</div>
          </div>
          <div className="w-px h-12 bg-slate-200 dark:bg-slate-700"></div>
          <div className="text-center">
            <div className="text-2xl font-bold text-slate-900 dark:text-white">
              {avgYield.toFixed(1)}%
            </div>
            <div className="text-sm font-medium text-slate-500 dark:text-slate-400">Avg Yield</div>
          </div>
        </div>
      </div>

      {/* Cash Breakdown */}
      <div className="grid gap-4 mb-8">
        {mockCashData.map((item, index) => (
          <div key={index} className="group bg-slate-50/80 dark:bg-slate-800/50 rounded-2xl p-5 border border-slate-200/50 dark:border-slate-700/50 hover:border-emerald-300 dark:hover:border-emerald-600 transition-all duration-300 hover:shadow-md">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <div className={`w-3 h-3 rounded-full ${
                    index === 0 ? 'bg-gradient-to-r from-blue-500 to-blue-600' :
                    index === 1 ? 'bg-gradient-to-r from-emerald-500 to-emerald-600' :
                    index === 2 ? 'bg-gradient-to-r from-purple-500 to-purple-600' :
                    'bg-gradient-to-r from-orange-500 to-orange-600'
                  }`}></div>
                  <div className="font-semibold text-slate-900 dark:text-white">{item.name}</div>
                </div>
                <div className="text-sm text-slate-600 dark:text-slate-400 font-medium">Account: {item.account}</div>
              </div>
              
              <div className="text-right">
                <div className="text-xl font-bold text-slate-900 dark:text-white mb-1">
                  ${(item.value / 1000).toFixed(0)}K
                </div>
                <div className="inline-flex items-center gap-1 px-3 py-1 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 text-sm font-semibold rounded-full">
                  {item.yield}% APY
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Cash Trend Chart */}
      <div className="bg-slate-50/50 dark:bg-slate-800/30 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-lg font-semibold text-slate-900 dark:text-white">Cash Trend</h4>
          <span className="text-sm text-slate-500 dark:text-slate-400 font-medium">Last 3 months</span>
        </div>
        <PortfolioChart
          data={mockCashTrend}
          type="line"
          height={160}
          dataKey="value"
          xDataKey="name"
          color="#10B981"
        />
      </div>
    </div>
  )
}