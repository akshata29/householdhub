"use client";

import * as React from "react";
import { ErrorState } from "@/components/ui/error-state";
import {
  Search,
  Filter,
  Calendar,
  User,
  FileText,
  MessageSquare,
  AlertCircle,
  TrendingUp,
  DollarSign,
  Shield,
  GraduationCap,
  Building,
  Clock,
  Tag,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  RefreshCw,
  Download
} from "lucide-react";
import { formatCurrency, formatDate } from "@/lib/utils";
import { useCrmNotes, useCrmCategories, useCrmSummary } from "@/lib/queries";

interface CrmNote {
  id: string;
  text: string;
  author: string;
  created_at: string;
  metadata?: {
    category?: string;
    client_id?: string;
    meeting_type?: string;
  };
  tags?: string[];
  score?: number;
}

interface CrmSummary {
  overview: string;
  key_insights: string[];
  action_items: string[];
  opportunities: string[];
  total_notes: number;
  date_range: string;
  categories: { [key: string]: number };
}

interface CrmTabProps {
  householdId: string;
}

// Category icon mapping
const getCategoryIcon = (category: string) => {
  const iconMap: { [key: string]: React.ReactNode } = {
    investment_review: <TrendingUp className="icon-sm" />,
    financial_planning: <DollarSign className="icon-sm" />,
    client_communication: <MessageSquare className="icon-sm" />,
    account_management: <User className="icon-sm" />,
    compliance_review: <Shield className="icon-sm" />,
    market_events: <AlertCircle className="icon-sm" />,
    education_funding: <GraduationCap className="icon-sm" />,
    tax_planning: <Building className="icon-sm" />,
    default: <FileText className="icon-sm" />
  };
  return iconMap[category] || iconMap.default;
};

// Category class mapping
const getCategoryClass = (category: string) => {
  const classMap: { [key: string]: string } = {
    'investment_review': 'status-pill info',
    'financial_planning': 'status-pill success',
    'client_communication': 'status-pill warning',
    'account_management': 'status-pill default',
    'compliance_review': 'status-pill error',
    'market_events': 'status-pill warning',
    'education_funding': 'status-pill info',
    'tax_planning': 'status-pill default',
    'default': 'status-pill default'
  };
  return classMap[category] || classMap.default;
};

function CrmNoteCard({ note, onExpand }: { note: CrmNote; onExpand: () => void }) {
  const [isExpanded, setIsExpanded] = React.useState(false);
  const category = note.metadata?.category || 'uncategorized';
  const displayText = isExpanded ? note.text : note.text.substring(0, 200) + (note.text.length > 200 ? '...' : '');

  return (
    <div className="crm-note-card">
      <div className="crm-note-header">
        <div className="crm-note-meta">
          <div className="crm-author">
            {getCategoryIcon(category)}
            <div className="author-info">
              <div className="author-name">{note.author}</div>
              <div className="crm-date-info">
                <Clock className="icon-sm" />
                <span>{formatDate(note.created_at)}</span>
                {note.score && (
                  <>
                    <span className="meta-separator">•</span>
                    <span>Relevance: {Math.round(note.score * 100)}%</span>
                  </>
                )}
              </div>
            </div>
          </div>
          <span className={getCategoryClass(category)}>
            {category.replace('_', ' ')}
          </span>
        </div>
      </div>
      
      <div className="crm-note-content">
        <p className="crm-note-text">
          {displayText}
        </p>
        
        {note.text.length > 200 && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="crm-expand-btn"
          >
            <ChevronDown className={`icon-sm crm-chevron ${isExpanded ? 'rotated' : ''}`} />
            {isExpanded ? 'Show Less' : 'Show More'}
          </button>
        )}
        
        {note.tags && note.tags.length > 0 && (
          <div className="crm-tags">
            {note.tags.map((tag, idx) => (
              <span key={idx} className="crm-tag">
                <Tag className="icon-sm" />
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function CrmSummaryCard({ summary }: { summary: CrmSummary }) {
  const [activeSection, setActiveSection] = React.useState<string>('overview');

  const sections = [
    { key: 'overview', label: 'Overview', icon: <FileText className="icon-sm" /> },
    { key: 'key_insights', label: 'Key Insights', icon: <TrendingUp className="icon-sm" /> },
    { key: 'action_items', label: 'Action Items', icon: <AlertCircle className="icon-sm" /> },
    { key: 'opportunities', label: 'Opportunities', icon: <DollarSign className="icon-sm" /> },
  ];

  const renderSectionContent = (section: string) => {
    switch (section) {
      case 'overview':
        return <p className="summary-text">{summary.overview}</p>;
      case 'key_insights':
        return (
          <ul className="summary-list">
            {summary.key_insights.map((insight, idx) => (
              <li key={idx} className="summary-list-item blue">
                <div className="list-bullet blue" />
                <span>{insight}</span>
              </li>
            ))}
          </ul>
        );
      case 'action_items':
        return (
          <ul className="summary-list">
            {summary.action_items.map((item, idx) => (
              <li key={idx} className="summary-list-item orange">
                <div className="list-bullet orange" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        );
      case 'opportunities':
        return (
          <ul className="summary-list">
            {summary.opportunities.map((opportunity, idx) => (
              <li key={idx} className="summary-list-item green">
                <div className="list-bullet green" />
                <span>{opportunity}</span>
              </li>
            ))}
          </ul>
        );
      default:
        return null;
    }
  };

  return (
    <div className="crm-summary-card">
      <div className="crm-summary-header">
        <div className="summary-title">
          <FileText className="icon-md" />
          <span>Executive Summary</span>
        </div>
      </div>
      
      <div className="crm-summary-content">
        <div className="summary-tabs">
          {sections.map((section) => (
            <button
              key={section.key}
              className={`summary-tab ${activeSection === section.key ? 'active' : ''}`}
              onClick={() => setActiveSection(section.key)}
            >
              {section.icon}
              <span>{section.label}</span>
            </button>
          ))}
        </div>
        
        <div className="summary-content">
          {renderSectionContent(activeSection)}
        </div>
      </div>
    </div>
  );
}

// Simple Input component for search
function SearchInput({ value, onChange, placeholder }: { 
  value: string; 
  onChange: (value: string) => void; 
  placeholder: string; 
}) {
  return (
    <div className="search-input-wrapper">
      <Search className="search-icon" />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="search-input"
      />
    </div>
  );
}

// Simple Select component for filtering
function FilterSelect({ value, onChange, options }: { 
  value: string; 
  onChange: (value: string) => void; 
  options: { value: string; label: string }[]; 
}) {
  return (
    <div className="filter-select-wrapper">
      <Filter className="filter-icon" />
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="filter-select"
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}

export function CrmTab({ householdId }: CrmTabProps) {
  const [searchTerm, setSearchTerm] = React.useState('');
  const [selectedCategory, setSelectedCategory] = React.useState<string>('all');

  const { 
    data: crmNotes, 
    isLoading: notesLoading, 
    error: notesError 
  } = useCrmNotes(householdId, searchTerm);

  const { 
    data: categories, 
    isLoading: categoriesLoading 
  } = useCrmCategories(householdId);

  const { 
    data: summary, 
    isLoading: summaryLoading, 
    error: summaryError 
  } = useCrmSummary(householdId);

  // Filter notes by category
  const filteredNotes = React.useMemo(() => {
    if (!crmNotes) return [];
    
    return crmNotes.filter((note: CrmNote) => {
      if (selectedCategory === 'all') return true;
      return note.metadata?.category === selectedCategory;
    });
  }, [crmNotes, selectedCategory]);

  // Category options for filter
  const categoryOptions = React.useMemo(() => {
    const options = [{ value: 'all', label: 'All Categories' }];
    
    if (categories) {
      Object.keys(categories).forEach(category => {
        options.push({
          value: category,
          label: `${category.replace('_', ' ')} (${categories[category]})`
        });
      });
    }
    
    return options;
  }, [categories]);

  if (notesError || summaryError) {
    return <ErrorState message="Failed to load CRM data. Please try again." />;
  }

  return (
    <div className="crm-container">
      {/* Header */}
      <div className="crm-header">
        <div className="crm-title">
          <MessageSquare className="icon-lg" />
          <h2>Client Relationship Management</h2>
        </div>
        <div className="crm-subtitle">
          View and search through client notes, communications, and insights
        </div>
      </div>

      {/* Summary Section */}
      {summaryLoading ? (
        <div className="loading-container">
          <div className="loading-spinner" />
          <span>Loading executive summary...</span>
        </div>
      ) : summary ? (
        <CrmSummaryCard summary={summary} />
      ) : null}

      {/* Search and Filter Controls */}
      <div className="crm-controls">
        <SearchInput
          value={searchTerm}
          onChange={setSearchTerm}
          placeholder="Search notes, communications, and insights..."
        />
        
        <FilterSelect
          value={selectedCategory}
          onChange={setSelectedCategory}
          options={categoryOptions}
        />
        
        <div className="crm-stats">
          {filteredNotes.length > 0 && (
            <span className="results-count">
              {filteredNotes.length} {filteredNotes.length === 1 ? 'note' : 'notes'} found
            </span>
          )}
        </div>
      </div>

      {/* Notes Grid */}
      <div className="crm-notes-grid">
        {notesLoading ? (
          <div className="loading-container">
            <div className="loading-spinner" />
            <span>Loading CRM notes...</span>
          </div>
        ) : filteredNotes.length > 0 ? (
          filteredNotes.map((note: CrmNote) => (
            <CrmNoteCard
              key={note.id}
              note={note}
              onExpand={() => {}}
            />
          ))
        ) : (
          <div className="empty-state">
            <MessageSquare className="empty-icon" />
            <h3>No notes found</h3>
            <p>
              {searchTerm 
                ? "Try adjusting your search terms or filters"
                : "No CRM notes are available for this household"}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}