import { PortfolioChart } from '@/components/ui/portfolio-chart'

const mockPerformanceData = [
  { name: 'Jan', value: 8.2, benchmark: 7.8, market: 8.1 },
  { name: 'Feb', value: 7.9, benchmark: 7.5, market: 7.7 },
  { name: 'Mar', value: -2.1, benchmark: -1.8, market: -2.0 },
  { name: 'Apr', value: 4.3, benchmark: 4.0, market: 4.2 },
  { name: 'May', value: 2.8, benchmark: 2.5, market: 2.6 },
  { name: 'Jun', value: 1.2, benchmark: 1.0, market: 1.1 }
]

const mockPortfolios = [
  { name: 'Conservative Growth', ytdReturn: 8.5, allocation: '60/40', value: 1200000 },
  { name: 'Aggressive Growth', ytdReturn: 12.3, allocation: '80/20', value: 800000 },
  { name: 'Income Focus', ytdReturn: 4.2, allocation: '40/60', value: 400000 }
]

export function PlanPerformance({ householdId }: { householdId: string }) {
  return (
    <div className="chart-container animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg">
            <span className="text-2xl">📊</span>
          </div>
          <div>
            <h3 className="text-2xl font-bold text-slate-900 dark:text-white">
              Portfolio Performance
            </h3>
            <p className="text-slate-600 dark:text-slate-400">6-month performance analysis</p>
          </div>
        </div>
        
        {/* Legend */}
        <div className="flex items-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-gradient-to-r from-blue-500 to-blue-600 shadow-sm"></div>
            <span className="font-medium text-slate-700 dark:text-slate-300">Portfolio</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-gradient-to-r from-emerald-500 to-emerald-600 shadow-sm"></div>
            <span className="font-medium text-slate-700 dark:text-slate-300">Benchmark</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-gradient-to-r from-slate-400 to-slate-500 shadow-sm"></div>
            <span className="font-medium text-slate-700 dark:text-slate-300">Market</span>
          </div>
        </div>
      </div>

      {/* Performance Chart */}
      <div className="mb-8 bg-slate-50/50 dark:bg-slate-800/30 rounded-2xl p-6">
        <PortfolioChart
          data={mockPerformanceData}
          type="line"
          height={280}
          dataKey="value"
          xDataKey="name"
          color="#3B82F6"
        />
      </div>

      {/* Portfolio Breakdown */}
      <div className="space-y-4">
        <h4 className="text-lg font-semibold text-slate-900 dark:text-white mb-6">Portfolio Breakdown</h4>
        {mockPortfolios.map((portfolio, index) => (
          <div key={index} className="group bg-slate-50/80 dark:bg-slate-800/50 rounded-2xl p-6 border border-slate-200/50 dark:border-slate-700/50 hover:border-blue-300 dark:hover:border-blue-600 transition-all duration-300 hover:shadow-lg">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <div className={`w-3 h-3 rounded-full ${
                    index === 0 ? 'bg-gradient-to-r from-blue-500 to-blue-600' :
                    index === 1 ? 'bg-gradient-to-r from-purple-500 to-purple-600' :
                    'bg-gradient-to-r from-emerald-500 to-emerald-600'
                  }`}></div>
                  <div className="font-semibold text-slate-900 dark:text-white text-lg">{portfolio.name}</div>
                </div>
                <div className="text-sm text-slate-600 dark:text-slate-400 font-medium">{portfolio.allocation} Stock/Bond Allocation</div>
              </div>
              
              <div className="flex items-center gap-8">
                <div className="text-center">
                  <div className="text-2xl font-bold text-slate-900 dark:text-white">
                    ${(portfolio.value / 1000000).toFixed(1)}M
                  </div>
                  <div className="text-sm text-slate-500 dark:text-slate-400 font-medium">Portfolio Value</div>
                </div>
                
                <div className="text-right">
                  <div className={`text-2xl font-bold ${
                    portfolio.ytdReturn >= 0 
                      ? 'text-emerald-600 dark:text-emerald-400' 
                      : 'text-red-600 dark:text-red-400'
                  }`}>
                    {portfolio.ytdReturn >= 0 ? '+' : ''}{portfolio.ytdReturn}%
                  </div>
                  <div className="text-sm text-slate-500 dark:text-slate-400 font-medium">YTD Return</div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="mt-8 pt-8 border-t border-slate-200 dark:border-slate-700">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-6 bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-900/30 dark:to-emerald-900/10 rounded-2xl border border-emerald-200 dark:border-emerald-800">
            <div className="text-3xl font-bold text-emerald-700 dark:text-emerald-300 mb-2">+8.7%</div>
            <div className="text-sm font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wide">Average Return</div>
          </div>
          <div className="text-center p-6 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/30 dark:to-blue-900/10 rounded-2xl border border-blue-200 dark:border-blue-800">
            <div className="text-3xl font-bold text-blue-700 dark:text-blue-300 mb-2">1.15</div>
            <div className="text-sm font-semibold text-blue-600 dark:text-blue-400 uppercase tracking-wide">Sharpe Ratio</div>
          </div>
          <div className="text-center p-6 bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800/50 dark:to-slate-800/30 rounded-2xl border border-slate-200 dark:border-slate-700">
            <div className="text-3xl font-bold text-slate-700 dark:text-slate-300 mb-2">0.85</div>
            <div className="text-sm font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wide">Beta Coefficient</div>
          </div>
        </div>
      </div>
    </div>
  )
}