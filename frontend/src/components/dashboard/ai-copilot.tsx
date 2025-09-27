'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
// Removed heroicons dependency - using emoji icons instead

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
}

const quickActions = [
  { id: 'portfolio', icon: '📊', label: 'Portfolio Analysis', query: 'Analyze my portfolio performance this quarter' },
  { id: 'cash', icon: '💰', label: 'Cash Optimization', query: 'How can I optimize my cash allocation?' },
  { id: 'rebalance', icon: '⚖️', label: 'Rebalancing', query: 'Should I rebalance my portfolio?' },
  { id: 'tax', icon: '📋', label: 'Tax Strategy', query: 'What tax strategies should I consider?' }
]

const mockSuggestions = [
  "Your portfolio is overweight in tech stocks. Consider rebalancing.",
  "Cash yields are attractive - move excess cash to high-yield accounts.",
  "Tax-loss harvesting opportunities available in your taxable accounts.",
  "Consider increasing 401k contributions before year-end."
]

export function AICopilot({ householdId }: { householdId: string }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: 'Hi! I\'m your WealthOps AI assistant. I can help you analyze your portfolio, optimize allocations, and answer questions about your financial plan.',
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState('')

  const handleQuickAction = (query: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: query,
      timestamp: new Date()
    }
    
    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: 'assistant',
      content: `I'd be happy to help with that! ${mockSuggestions[Math.floor(Math.random() * mockSuggestions.length)]}`,
      timestamp: new Date()
    }
    
    setMessages(prev => [...prev, userMessage, assistantMessage])
  }

  const handleSendMessage = () => {
    if (!inputValue.trim()) return
    
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    }
    
    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: 'assistant',
      content: "Thanks for your question! I'm analyzing your data and will provide insights based on your current portfolio and market conditions.",
      timestamp: new Date()
    }
    
    setMessages(prev => [...prev, userMessage, assistantMessage])
    setInputValue('')
  }

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            className="mb-4 w-96 bg-white rounded-xl shadow-xl border border-gray-200 overflow-hidden"
          >
            {/* Header */}
            <div className="bg-blue-600 text-white p-4">
              <div className="flex items-center space-x-2">
                <span className="text-xl">✨</span>
                <h3 className="font-semibold">WealthOps AI Copilot</h3>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="p-4 border-b border-gray-200">
              <div className="text-sm font-medium text-gray-700 mb-2">Quick Actions</div>
              <div className="grid grid-cols-2 gap-2">
                {quickActions.map((action) => (
                  <button
                    key={action.id}
                    onClick={() => handleQuickAction(action.query)}
                    className="flex items-center space-x-2 p-2 text-xs text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
                  >
                    <span className="text-sm">{action.icon}</span>
                    <span>{action.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Messages */}
            <div className="h-64 overflow-y-auto p-4 space-y-3">
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs rounded-lg px-3 py-2 text-sm ${
                      message.type === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    {message.content}
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Input */}
            <div className="p-4 border-t border-gray-200">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Ask about your portfolio..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={handleSendMessage}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors"
                >
                  Send
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Toggle Button */}
      <motion.button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-12 h-12 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-colors flex items-center justify-center"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <span className="text-2xl">💬</span>
      </motion.button>
    </div>
  )
}