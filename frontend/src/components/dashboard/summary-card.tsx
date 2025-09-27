import React from 'react'

type SummaryCardProps = {
  name: string
  advisor: string
  householdId: string
  totalAssets: number
  accountsCount: number
  ytdReturn: string
}

export const SummaryCard: React.FC<SummaryCardProps> = ({
  name,
  advisor,
  householdId,
  totalAssets,
  accountsCount,
  ytdReturn
}) => {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5 shadow-sm">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <div className="text-xs text-gray-500">Household</div>
          <div className="text-lg font-semibold text-gray-900">{name}</div>
          <div className="text-xs text-gray-500">{advisor} • {householdId}</div>
        </div>

        <div className="flex items-center gap-6">
          <div className="text-right">
            <div className="text-xs text-gray-500">Total Assets</div>
            <div className="text-lg font-mono font-semibold text-gray-900">${(totalAssets / 1000000).toFixed(2)}M</div>
          </div>

          <div className="text-right">
            <div className="text-xs text-gray-500">Accounts</div>
            <div className="text-base font-semibold text-gray-900">{accountsCount}</div>
          </div>

          <div className="text-right">
            <div className="text-xs text-gray-500">YTD</div>
            <div className="text-base font-semibold text-green-600">{ytdReturn}</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SummaryCard
