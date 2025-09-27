import { motion } from 'framer-motion'
import numeral from 'numeral'

interface MetricCardProps {
  title: string
  value: number
  change?: number
  changeType?: 'positive' | 'negative' | 'neutral'
  format?: 'currency' | 'percentage' | 'number'
  icon?: string
  subtitle?: string
  loading?: boolean
  gradient?: boolean
}

const iconMap: Record<string, string> = {
  chart: '📊',
  trending: '📈',
  currency: '💰',
  users: '👥',
  clock: '⏰',
  portfolio: '📈',
  cash: '💵',
  growth: '🚀',
  performance: '🎯'
}

export function MetricCard({ 
  title, 
  value, 
  change, 
  changeType = 'neutral',
  format = 'number',
  icon,
  subtitle,
  loading = false,
  gradient = false
}: MetricCardProps) {
  const formatValue = (val: number) => {
    switch (format) {
      case 'currency':
        return numeral(val).format('$0,0[.]00a')
      case 'percentage':
        return numeral(val / 100).format('0.00%')
      default:
        return numeral(val).format('0,0')
    }
  }

  const getChangeStyles = () => {
    switch (changeType) {
      case 'positive':
        return 'text-emerald-600 bg-emerald-50 dark:text-emerald-400 dark:bg-emerald-900/20'
      case 'negative':
        return 'text-red-600 bg-red-50 dark:text-red-400 dark:bg-red-900/20'
      default:
        return 'text-slate-600 bg-slate-50 dark:text-slate-400 dark:bg-slate-800'
    }
  }

  const getTrendIcon = () => {
    if (!change) return ''
    return changeType === 'positive' ? '↗' : '↘'
  }

  const getGradientClass = () => {
    if (!gradient) return ''
    switch (changeType) {
      case 'positive':
        return 'bg-gradient-to-br from-emerald-50 to-green-100 dark:from-emerald-900/20 dark:to-green-900/10 border-emerald-200 dark:border-emerald-800'
      case 'negative':
        return 'bg-gradient-to-br from-red-50 to-orange-100 dark:from-red-900/20 dark:to-orange-900/10 border-red-200 dark:border-red-800'
      default:
        return 'bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-blue-900/20 dark:to-indigo-900/10 border-blue-200 dark:border-blue-800'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      whileHover={{ scale: 1.02 }}
      className={`metric-card ${gradient ? getGradientClass() : ''} group`}
    >
      {/* Top accent bar */}
      <div 
        className={`absolute top-0 left-0 right-0 h-1 rounded-t-2xl ${
          changeType === 'positive' 
            ? 'bg-gradient-to-r from-emerald-500 to-green-400' 
            : changeType === 'negative'
            ? 'bg-gradient-to-r from-red-500 to-orange-400'
            : 'bg-gradient-to-r from-blue-500 to-indigo-400'
        }`}
      />

      <div className="relative">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            {icon && (
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-xl transition-all duration-200 group-hover:scale-110 ${
                changeType === 'positive' 
                  ? 'bg-emerald-100 dark:bg-emerald-900/30' 
                  : changeType === 'negative'
                  ? 'bg-red-100 dark:bg-red-900/30'
                  : 'bg-blue-100 dark:bg-blue-900/30'
              }`}>
                {iconMap[icon] || icon}
              </div>
            )}
            <div>
              <h3 className="text-sm font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                {title}
              </h3>
              {subtitle && (
                <p className="text-xs text-slate-500 dark:text-slate-500 mt-0.5">
                  {subtitle}
                </p>
              )}
            </div>
          </div>
        </div>
        
        {loading ? (
          <div className="animate-pulse space-y-3">
            <div className="h-10 bg-slate-200 dark:bg-slate-700 rounded-lg w-32"></div>
            <div className="h-6 bg-slate-200 dark:bg-slate-700 rounded w-24"></div>
          </div>
        ) : (
          <>
            {/* Main value */}
            <div className={`text-4xl font-bold mb-3 ${gradient ? 'text-slate-900 dark:text-white' : 'text-slate-900 dark:text-white'}`}>
              {formatValue(value)}
            </div>
            
            {/* Change indicator */}
            {change !== undefined && (
              <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium ${getChangeStyles()}`}>
                <span className="text-base">{getTrendIcon()}</span>
                <span>
                  {changeType === 'positive' ? '+' : ''}
                  {numeral(Math.abs(change) / 100).format('0.00%')}
                  <span className="text-xs ml-1 opacity-75">vs last period</span>
                </span>
              </div>
            )}
          </>
        )}
      </div>
      
      {/* Subtle background pattern */}
      <div className="absolute top-0 right-0 w-20 h-20 opacity-5 overflow-hidden">
        <div className="absolute top-2 right-2 w-16 h-16 border-2 border-current rounded-full transform rotate-12"></div>
        <div className="absolute top-4 right-4 w-8 h-8 border border-current rounded-full transform -rotate-12"></div>
      </div>
    </motion.div>
  )
}