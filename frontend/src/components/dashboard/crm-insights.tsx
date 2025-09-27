
const mockCRMData = [
  {
    id: 1,
    date: '2024-09-25T14:30:00Z',
    advisor: 'Jane Smith',
    type: 'Phone Call',
    summary: 'Discussed quarterly performance and upcoming rebalancing strategy',
    priority: 'high',
    tags: ['performance', 'rebalancing', 'quarterly-review']
  },
  {
    id: 2,
    date: '2024-09-20T10:15:00Z',
    advisor: 'Jane Smith',
    type: 'Meeting',
    summary: 'Reviewed retirement planning timeline and RMD projections',
    priority: 'medium',
    tags: ['retirement', 'RMD', 'planning']
  },
  {
    id: 3,
    date: '2024-09-15T16:45:00Z',
    advisor: 'Bob Wilson',
    type: 'Email',
    summary: 'Follow-up on estate planning documents and beneficiary updates',
    priority: 'low',
    tags: ['estate-planning', 'beneficiaries', 'documents']
  }
]

export function CRMInsights({ householdId }: { householdId: string }) {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200'
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'low': return 'bg-green-100 text-green-800 border-green-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="flex-shrink-0 w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center">
            <span className="text-white text-lg">👥</span>
          </div>
          <h3 className="text-xl font-semibold text-gray-900">
            Recent CRM Activity
          </h3>
        </div>
        <button className="bg-purple-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-purple-600 transition-colors">
          View All →
        </button>
      </div>

      <div className="space-y-4">
        {mockCRMData.map((item) => (
          <div key={item.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getPriorityColor(item.priority)}`}>
                  {item.priority}
                </span>
                <span className="text-sm text-gray-600">{item.type}</span>
              </div>
              <div className="text-sm text-gray-500">
                {new Date(item.date).toLocaleDateString()}
              </div>
            </div>
            
            <p className="text-gray-900 mb-2 font-medium">{item.summary}</p>
            
            <div className="flex items-center justify-between">
              <div className="flex flex-wrap gap-1">
                {item.tags.map((tag, index) => (
                  <span key={index} className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-50 text-blue-700">
                    {tag}
                  </span>
                ))}
              </div>
              <div className="text-sm text-gray-600">
                by {item.advisor}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Next scheduled interaction</span>
          <span className="font-medium text-gray-900">Oct 15, 2024 - Quarterly Review</span>
        </div>
      </div>
    </div>
  )
}

export function ReconTable({ householdId }: { householdId: string }) {
  return <div className="bg-white rounded-lg shadow p-6">Recon Table for {householdId}</div>
}

export function RMDList({ householdId }: { householdId: string }) {
  return <div className="bg-white rounded-lg shadow p-6">RMD List for {householdId}</div>
}

export function ExecSummaryPanel({ householdId }: { householdId: string }) {
  return <div className="bg-white rounded-lg shadow p-6">Executive Summary for {householdId}</div>
}