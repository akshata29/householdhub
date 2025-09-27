"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  Search, 
  Filter, 
  SortAsc, 
  SortDesc,
  Users,
  DollarSign,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  Calendar,
  Building,
  User,
  Shield,
  Landmark,
  Heart,
  Eye,
  ArrowRight,
  BarChart3,
  Wallet
} from "lucide-react";
import { mockHouseholds, getHouseholdStats, type Household } from "@/lib/mock-households";
import { CopilotPanel } from "@/components/copilot/copilot-panel";

type SortField = 'name' | 'totalAssets' | 'ytdPerformance' | 'lastActivity' | 'nextReview';
type SortDirection = 'asc' | 'desc';
type ViewMode = 'cards' | 'table';

const HouseholdTypeIcons = {
  Individual: User,
  Joint: Users,
  Trust: Shield,
  Corporation: Building,
  Foundation: Heart
};

const StatusColors = {
  'Active': 'bg-green-100 text-green-800 border-green-200',
  'Onboarding': 'bg-blue-100 text-blue-800 border-blue-200',
  'Review Required': 'bg-yellow-100 text-yellow-800 border-yellow-200',
  'Inactive': 'bg-gray-100 text-gray-800 border-gray-200'
};

const RiskColors = {
  'Ultra-Conservative': 'bg-purple-50 text-purple-700',
  'Conservative': 'bg-blue-50 text-blue-700',
  'Moderate': 'bg-green-50 text-green-700',
  'Aggressive': 'bg-orange-50 text-orange-700'
};

export function HouseholdsHomePage() {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = React.useState('');
  const [statusFilter, setStatusFilter] = React.useState<string>('all');
  const [advisorFilter, setAdvisorFilter] = React.useState<string>('all');
  const [sortField, setSortField] = React.useState<SortField>('totalAssets');
  const [sortDirection, setSortDirection] = React.useState<SortDirection>('desc');
  const [viewMode, setViewMode] = React.useState<ViewMode>('cards');

  const stats = React.useMemo(() => getHouseholdStats(), []);
  
  const uniqueAdvisors = React.useMemo(() => {
    const advisorSet = new Set(mockHouseholds.map(h => h.advisorName));
    const advisors = Array.from(advisorSet);
    return advisors.sort();
  }, []);

  const filteredAndSortedHouseholds = React.useMemo(() => {
    let filtered = mockHouseholds.filter(household => {
      const matchesSearch = 
        household.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        household.primaryContact.toLowerCase().includes(searchTerm.toLowerCase()) ||
        household.location.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesStatus = statusFilter === 'all' || household.status === statusFilter;
      const matchesAdvisor = advisorFilter === 'all' || household.advisorName === advisorFilter;
      
      return matchesSearch && matchesStatus && matchesAdvisor;
    });

    return filtered.sort((a, b) => {
      // Handle different data types
      if (sortField === 'totalAssets' || sortField === 'ytdPerformance') {
        const aValue = Number(a[sortField]);
        const bValue = Number(b[sortField]);
        
        if (sortDirection === 'asc') {
          return aValue - bValue;
        } else {
          return bValue - aValue;
        }
      } else if (sortField === 'lastActivity' || sortField === 'nextReview') {
        const aValue = new Date(a[sortField] as string).getTime();
        const bValue = new Date(b[sortField] as string).getTime();
        
        if (sortDirection === 'asc') {
          return aValue - bValue;
        } else {
          return bValue - aValue;
        }
      } else {
        const aValue = String(a[sortField]).toLowerCase();
        const bValue = String(b[sortField]).toLowerCase();
        
        if (sortDirection === 'asc') {
          return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
        } else {
          return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
        }
      }
    });
  }, [searchTerm, statusFilter, advisorFilter, sortField, sortDirection]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const navigateToHousehold = (householdId: string) => {
    router.push(`/households/${householdId}`);
  };

  const HouseholdCard = ({ household }: { household: Household }) => {
    const TypeIcon = HouseholdTypeIcons[household.householdType];
    
    return (
      <Card className="household-card" onClick={() => navigateToHousehold(household.id)}>
        <CardHeader className="household-card-header">
          <div className="card-title-row">
            <div className="household-type-icon">
              <TypeIcon className="type-icon" />
            </div>
            <div className="household-info">
              <CardTitle className="household-name">{household.name}</CardTitle>
              <p className="primary-contact">{household.primaryContact}</p>
            </div>
            <Badge className={StatusColors[household.status]}>
              {household.status}
            </Badge>
          </div>
          <div className="household-location">
            📍 {household.location}
          </div>
        </CardHeader>
        
        <CardContent className="household-card-content">
          <div className="metrics-grid">
            <div className="metric-item">
              <div className="metric-value">{formatCurrency(household.totalAssets)}</div>
              <div className="metric-label">Total Assets</div>
            </div>
            <div className="metric-item">
              <div className="metric-value">{formatCurrency(household.totalCash)}</div>
              <div className="metric-label">Cash</div>
            </div>
            <div className="metric-item">
              <div className={`metric-value ${household.ytdPerformance >= 0 ? 'positive' : 'negative'}`}>
                {formatPercentage(household.ytdPerformance)}
              </div>
              <div className="metric-label">YTD Performance</div>
            </div>
            <div className="metric-item">
              <div className="metric-value">{household.accountsCount}</div>
              <div className="metric-label">Accounts</div>
            </div>
          </div>

          <div className="card-footer">
            <div className="advisor-info">
              <span className="advisor-label">Advisor:</span>
              <span className="advisor-name">{household.advisorName}</span>
            </div>
            <div className="risk-profile">
              <Badge variant="outline" className={RiskColors[household.riskProfile]}>
                {household.riskProfile}
              </Badge>
            </div>
            {household.recentAlerts > 0 && (
              <div className="alerts-indicator">
                <AlertCircle className="alert-icon" />
                <span>{household.recentAlerts}</span>
              </div>
            )}
          </div>

          <div className="card-actions">
            <Button className="view-dashboard-btn">
              <Eye className="btn-icon" />
              View Dashboard
              <ArrowRight className="btn-icon" />
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="households-home">
      {/* Header */}
      <div className="home-header">
        <div className="header-content">
          <h1 className="home-title">WealthOps</h1>
          <p className="home-subtitle">
            Comprehensive wealth management dashboard for {stats.totalHouseholds} households
          </p>
        </div>
        
        {/* Stats Overview */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon households">
              <Users className="icon" />
            </div>
            <div className="stat-content">
              <div className="stat-value">{stats.totalHouseholds}</div>
              <div className="stat-label">Total Households</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon assets">
              <Landmark className="icon" />
            </div>
            <div className="stat-content">
              <div className="stat-value">{formatCurrency(stats.totalAssets)}</div>
              <div className="stat-label">Assets Under Management</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon cash">
              <Wallet className="icon" />
            </div>
            <div className="stat-content">
              <div className="stat-value">{formatCurrency(stats.totalCash)}</div>
              <div className="stat-label">Total Cash Positions</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon performance">
              <BarChart3 className="icon" />
            </div>
            <div className="stat-content">
              <div className={`stat-value ${stats.averagePerformance >= 0 ? 'positive' : 'negative'}`}>
                {formatPercentage(stats.averagePerformance)}
              </div>
              <div className="stat-label">Avg YTD Performance</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Controls */}
      <div className="controls-section">
        <div className="search-and-filters">
          <div className="search-input">
            <Search className="search-icon" />
            <input
              type="text"
              placeholder="Search households, contacts, or locations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          <div className="filter-controls">
            <div className="filter-group">
              <Filter className="filter-icon" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Status</option>
                <option value="Active">Active</option>
                <option value="Onboarding">Onboarding</option>
                <option value="Review Required">Review Required</option>
                <option value="Inactive">Inactive</option>
              </select>
            </div>
            
            <div className="filter-group">
              <select
                value={advisorFilter}
                onChange={(e) => setAdvisorFilter(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Advisors</option>
                {uniqueAdvisors.map(advisor => (
                  <option key={advisor} value={advisor}>{advisor}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="view-controls">
          <div className="sort-controls">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleSort('totalAssets')}
              className={sortField === 'totalAssets' ? 'active' : ''}
            >
              Assets {sortField === 'totalAssets' && (sortDirection === 'asc' ? <SortAsc className="sort-icon" /> : <SortDesc className="sort-icon" />)}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleSort('ytdPerformance')}
              className={sortField === 'ytdPerformance' ? 'active' : ''}
            >
              Performance {sortField === 'ytdPerformance' && (sortDirection === 'asc' ? <SortAsc className="sort-icon" /> : <SortDesc className="sort-icon" />)}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleSort('lastActivity')}
              className={sortField === 'lastActivity' ? 'active' : ''}
            >
              Activity {sortField === 'lastActivity' && (sortDirection === 'asc' ? <SortAsc className="sort-icon" /> : <SortDesc className="sort-icon" />)}
            </Button>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="results-section">
        <div className="results-header">
          <h2 className="results-title">
            Households ({filteredAndSortedHouseholds.length})
          </h2>
        </div>

        <div className="households-grid">
          {filteredAndSortedHouseholds.map((household) => (
            <HouseholdCard key={household.id} household={household} />
          ))}
        </div>

        {filteredAndSortedHouseholds.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">
              <Search className="icon" />
            </div>
            <h3 className="empty-title">No households found</h3>
            <p className="empty-description">
              Try adjusting your search terms or filters to find households.
            </p>
          </div>
        )}
      </div>

      {/* AI Assistant */}
      <CopilotPanel />
    </div>
  );
}

export default HouseholdsHomePage;