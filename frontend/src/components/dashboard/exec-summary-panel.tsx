import { PortfolioChart } from '@/components/ui/portfolio-chart'

const mockPerformanceData = [
  { name: 'Jan', value: 2200000, benchmark: 2180000 },
  { name: 'Feb', value: 2250000, benchmark: 2220000 },
  { name: 'Mar', value: 2180000, benchmark: 2200000 },
  { name: 'Apr', value: 2320000, benchmark: 2280000 },
  { name: 'May', value: 2380000, benchmark: 2340000 },
  { name: 'Jun', value: 2400000, benchmark: 2360000 }
]

const mockAllocation = [
  { name: 'Stocks', value: 1440000 }, // 60%
  { name: 'Bonds', value: 720000 },   // 30%
  { name: 'Cash', value: 240000 }     // 10%
]

export function ExecSummaryPanel({ householdId }: { householdId: string }) {
  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="flex-shrink-0 w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
                {/* icon intentionally kept simple - replaced by heroicon in parent */}
          </div>
          <h3 className="text-xl font-semibold text-gray-900">
            Executive Summary
          </h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="text-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200">
            <div className="text-3xl font-bold text-gray-900 mb-1">$2.4M</div>
            <div className="text-sm text-gray-600 mb-2">Total Assets</div>
            <div className="text-green-600 text-sm font-medium">+2.3% MTD</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200">
            <div className="text-3xl font-bold text-green-600 mb-1">+8.5%</div>
            <div className="text-sm text-gray-600 mb-2">YTD Return</div>
            <div className="text-blue-600 text-sm font-medium">vs 7.2% benchmark</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200">
            <div className="text-3xl font-bold text-blue-600 mb-1">4</div>
            <div className="text-sm text-gray-600 mb-2">Active Accounts</div>
            <div className="text-amber-600 text-sm font-medium">Moderate Risk</div>
          </div>
        </div>
        
        {/* Recent Activity */}
        <div className="border-t pt-4">
          <h4 className="font-medium text-gray-900 mb-3">Recent Activity</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Portfolio Rebalancing</span>
              <span className="text-gray-500">Sep 20, 2024</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Quarterly Review Meeting</span>
              <span className="text-gray-500">Sep 15, 2024</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">IRA Contribution</span>
              <span className="text-gray-500">Sep 10, 2024</span>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Chart */}
      <PortfolioChart
        data={mockPerformanceData}
        type="area"
        title="Portfolio Performance (6M)"
        height={250}
        dataKey="value"
        xDataKey="name"
        color="#3B82F6"
      />

      {/* Asset Allocation */}
      <PortfolioChart
        data={mockAllocation}
        type="pie"
        title="Asset Allocation"
        height={300}
        dataKey="value"
      />
    </div>
  )
}