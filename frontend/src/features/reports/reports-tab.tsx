"use client";

import * as React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  FileText, 
  Download, 
  Calendar,
  TrendingUp,
  PieChart,
  BarChart3,
  Calculator,
  DollarSign,
  Clock,
  Filter,
  Search,
  Eye,
  Mail
} from "lucide-react";

interface ReportsTabProps {
  householdId: string;
}

// Mock data for reports
const generateReportsData = () => {
  return {
    standardReports: [
      {
        id: 1,
        name: "Portfolio Performance Summary",
        description: "Comprehensive analysis of portfolio returns, asset allocation, and performance metrics",
        category: "Performance",
        frequency: "Monthly",
        lastGenerated: "2025-09-25",
        format: "PDF",
        status: "Ready",
        size: "2.3 MB"
      },
      {
        id: 2,
        name: "Tax Loss Harvesting Report",
        description: "Analysis of realized and unrealized gains/losses for tax optimization",
        category: "Tax",
        frequency: "Quarterly",
        lastGenerated: "2025-09-20",
        format: "PDF",
        status: "Ready",
        size: "1.8 MB"
      },
      {
        id: 3,
        name: "Asset Allocation Analysis",
        description: "Current vs target allocation with rebalancing recommendations",
        category: "Allocation",
        frequency: "Monthly",
        lastGenerated: "2025-09-24",
        format: "PDF",
        status: "Ready",
        size: "1.5 MB"
      },
      {
        id: 4,
        name: "Cash Flow Analysis",
        description: "Income, expenses, and cash flow projections with trend analysis",
        category: "Cash Flow",
        frequency: "Monthly",
        lastGenerated: "2025-09-23",
        format: "Excel",
        status: "Processing",
        size: "850 KB"
      },
      {
        id: 5,
        name: "Fee Analysis Report",
        description: "Detailed breakdown of all fees, expenses, and cost analysis",
        category: "Fees",
        frequency: "Quarterly",
        lastGenerated: "2025-09-15",
        format: "PDF",
        status: "Ready",
        size: "1.2 MB"
      },
      {
        id: 6,
        name: "Risk Assessment Report",
        description: "Portfolio risk metrics, volatility analysis, and stress testing",
        category: "Risk",
        frequency: "Quarterly",
        lastGenerated: "2025-09-10",
        format: "PDF",
        status: "Ready",
        size: "2.1 MB"
      }
    ],
    customReports: [
      {
        id: 7,
        name: "Retirement Readiness Analysis",
        description: "Comprehensive retirement planning analysis with projections",
        category: "Planning",
        requestedBy: "Sarah Johnson",
        requestDate: "2025-09-22",
        deliveryDate: "2025-09-28",
        status: "In Progress",
        format: "PDF + Excel"
      },
      {
        id: 8,
        name: "ESG Investment Analysis",
        description: "Environmental, Social, and Governance impact assessment",
        category: "ESG",
        requestedBy: "Michael Chen",
        requestDate: "2025-09-18",
        deliveryDate: "2025-09-26",
        status: "Ready",
        format: "PDF"
      }
    ],
    recentActivity: [
      {
        id: 1,
        action: "Downloaded Portfolio Performance Summary",
        user: "Sarah Johnson",
        timestamp: "2025-09-25 14:30",
        reportName: "Portfolio Performance Summary - Sept 2025"
      },
      {
        id: 2,
        action: "Requested Custom Report",
        user: "Michael Chen",
        timestamp: "2025-09-25 11:15",
        reportName: "Retirement Readiness Analysis"
      },
      {
        id: 3,
        action: "Emailed Report",
        user: "David Wilson",
        timestamp: "2025-09-24 16:45",
        reportName: "Tax Loss Harvesting Report - Q3 2025"
      },
      {
        id: 4,
        action: "Generated Report",
        user: "System",
        timestamp: "2025-09-24 09:00",
        reportName: "Asset Allocation Analysis - Sept 2025"
      }
    ]
  };
};

const useReports = () => {
  const [data] = React.useState(() => generateReportsData());
  return { data, isLoading: false };
};

const ReportCard: React.FC<{report: any, type: 'standard' | 'custom'}> = ({ report, type }) => {
  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'ready':
        return <div className="status-dot ready"></div>;
      case 'processing':
      case 'in progress':
        return <div className="status-dot processing"></div>;
      default:
        return <div className="status-dot pending"></div>;
    }
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      'Performance': 'category-performance',
      'Tax': 'category-tax',
      'Allocation': 'category-allocation',
      'Cash Flow': 'category-cash-flow',
      'Fees': 'category-fees',
      'Risk': 'category-risk',
      'Planning': 'category-planning',
      'ESG': 'category-esg'
    };
    return colors[category] || 'category-default';
  };

  return (
    <div className="report-card">
      <div className="report-header">
        <div className="report-icon">
          <FileText className="icon" />
        </div>
        <div className="report-info">
          <h3 className="report-name">{report.name}</h3>
          <p className="report-description">{report.description}</p>
        </div>
        <div className="report-status">
          {getStatusIcon(report.status)}
          <span className="status-text">{report.status}</span>
        </div>
      </div>

      <div className="report-meta">
        <div className="meta-item">
          <span className={`category-badge ${getCategoryColor(report.category)}`}>
            {report.category}
          </span>
        </div>
        {type === 'standard' && (
          <>
            <div className="meta-item">
              <Calendar className="meta-icon" />
              <span>{report.frequency}</span>
            </div>
            <div className="meta-item">
              <Clock className="meta-icon" />
              <span>Last: {new Date(report.lastGenerated).toLocaleDateString()}</span>
            </div>
            <div className="meta-item">
              <span className="file-size">{report.format} • {report.size}</span>
            </div>
          </>
        )}
        {type === 'custom' && (
          <>
            <div className="meta-item">
              <span>Requested by: {report.requestedBy}</span>
            </div>
            <div className="meta-item">
              <Clock className="meta-icon" />
              <span>Due: {new Date(report.deliveryDate).toLocaleDateString()}</span>
            </div>
            <div className="meta-item">
              <span className="file-format">{report.format}</span>
            </div>
          </>
        )}
      </div>

      <div className="report-actions">
        {report.status.toLowerCase() === 'ready' && (
          <>
            <Button size="sm" variant="outline" className="action-btn">
              <Eye className="btn-icon" />
              Preview
            </Button>
            <Button size="sm" variant="outline" className="action-btn">
              <Download className="btn-icon" />
              Download
            </Button>
            <Button size="sm" variant="outline" className="action-btn">
              <Mail className="btn-icon" />
              Email
            </Button>
          </>
        )}
        {report.status.toLowerCase() === 'processing' && (
          <Button size="sm" variant="outline" disabled className="action-btn">
            <Clock className="btn-icon" />
            Processing...
          </Button>
        )}
        {report.status.toLowerCase() === 'in progress' && (
          <Button size="sm" variant="outline" className="action-btn">
            <Eye className="btn-icon" />
            View Progress
          </Button>
        )}
      </div>
    </div>
  );
};

const ActivityCard: React.FC<{activity: any}> = ({ activity }) => {
  const getActionIcon = (action: string) => {
    if (action.includes('Downloaded')) return <Download className="activity-icon download" />;
    if (action.includes('Requested')) return <FileText className="activity-icon request" />;
    if (action.includes('Emailed')) return <Mail className="activity-icon email" />;
    if (action.includes('Generated')) return <TrendingUp className="activity-icon generate" />;
    return <FileText className="activity-icon" />;
  };

  return (
    <div className="activity-item">
      <div className="activity-content">
        {getActionIcon(activity.action)}
        <div className="activity-details">
          <div className="activity-action">{activity.action}</div>
          <div className="activity-report">{activity.reportName}</div>
          <div className="activity-meta">
            <span className="activity-user">{activity.user}</span>
            <span className="activity-time">{activity.timestamp}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export function ReportsTab({ householdId }: ReportsTabProps) {
  const { data, isLoading } = useReports();
  const [searchTerm, setSearchTerm] = React.useState("");
  const [selectedCategory, setSelectedCategory] = React.useState("All");

  if (isLoading) {
    return <div className="loading-state">Loading reports...</div>;
  }

  const categories = ["All", "Performance", "Tax", "Allocation", "Cash Flow", "Fees", "Risk", "Planning", "ESG"];

  const filteredStandardReports = data.standardReports.filter(report => {
    const matchesSearch = report.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         report.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === "All" || report.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const filteredCustomReports = data.customReports.filter(report => {
    const matchesSearch = report.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         report.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === "All" || report.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="reports-tab">
      {/* Reports Header */}
      <div className="reports-header">
        <div className="header-content">
          <h1 className="page-title">Reports & Analytics</h1>
          <p className="page-description">
            Access comprehensive reports and analytics for your portfolio performance, tax planning, and financial insights.
          </p>
        </div>
        <div className="header-actions">
          <Button className="primary-btn">
            <FileText className="btn-icon" />
            Request Custom Report
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="reports-stats">
        <div className="stat-card">
          <div className="stat-icon">
            <FileText className="icon" />
          </div>
          <div className="stat-content">
            <div className="stat-value">12</div>
            <div className="stat-label">Total Reports</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <Download className="icon" />
          </div>
          <div className="stat-content">
            <div className="stat-value">8</div>
            <div className="stat-label">Ready to Download</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <Clock className="icon" />
          </div>
          <div className="stat-content">
            <div className="stat-value">2</div>
            <div className="stat-label">In Progress</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <Calendar className="icon" />
          </div>
          <div className="stat-content">
            <div className="stat-value">6</div>
            <div className="stat-label">This Month</div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="reports-filters">
        <div className="search-section">
          <div className="search-input">
            <Search className="search-icon" />
            <input
              type="text"
              placeholder="Search reports..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
        <div className="filter-section">
          <Filter className="filter-icon" />
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="category-filter"
          >
            {categories.map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="reports-content">
        {/* Standard Reports */}
        <div className="reports-section">
          <div className="section-header">
            <div className="section-title-content">
              <h2 className="section-title">Standard Reports</h2>
              <p className="section-description">
                Regularly generated reports with key financial insights and performance metrics.
              </p>
            </div>
            <Badge variant="secondary" className="reports-count">
              {filteredStandardReports.length} reports
            </Badge>
          </div>
          
          <div className="reports-grid">
            {filteredStandardReports.map(report => (
              <ReportCard key={report.id} report={report} type="standard" />
            ))}
          </div>
        </div>

        {/* Custom Reports */}
        <div className="reports-section">
          <div className="section-header">
            <div className="section-title-content">
              <h2 className="section-title">Custom Reports</h2>
              <p className="section-description">
                Specially requested reports tailored to specific analysis needs and requirements.
              </p>
            </div>
            <Badge variant="secondary" className="reports-count">
              {filteredCustomReports.length} reports
            </Badge>
          </div>
          
          <div className="reports-grid">
            {filteredCustomReports.map(report => (
              <ReportCard key={report.id} report={report} type="custom" />
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="reports-section">
          <div className="section-header">
            <div className="section-title-content">
              <h2 className="section-title">Recent Activity</h2>
              <p className="section-description">
                Latest report activities including downloads, requests, and generation updates.
              </p>
            </div>
          </div>
          
          <div className="activity-list">
            {data.recentActivity.map(activity => (
              <ActivityCard key={activity.id} activity={activity} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ReportsTab;