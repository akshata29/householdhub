"use client";

import * as React from "react";
import { 
  Calendar,
  Phone,
  Mail,
  FileText,
  TrendingUp,
  ExternalLink,
} from "lucide-react";
import { formatDate } from "@/lib/utils";
import { ActivityItem } from "@/lib/schemas";

interface FeedCardProps {
  title?: string;
  items: ActivityItem[];
  loading?: boolean;
  error?: string;
  showViewAll?: boolean;
  onViewAll?: () => void;
  className?: string;
}

function getActivityIcon(type: ActivityItem['type']) {
  switch (type) {
    case 'meeting':
      return Calendar;
    case 'call':
      return Phone;
    case 'email':
      return Mail;
    case 'review':
      return FileText;
    case 'trade':
      return TrendingUp;
    default:
      return FileText;
  }
}

function getActivityColor(type: ActivityItem['type']) {
  switch (type) {
    case 'meeting':
      return '#0f766e';
    case 'call':
      return '#059669';
    case 'email':
      return '#d97706';
    case 'review':
      return '#6366f1';
    case 'trade':
      return '#8b5a2b';
    default:
      return '#64748b';
  }
}

function getPriorityVariant(priority: ActivityItem['priority']) {
  switch (priority) {
    case 'high':
      return 'danger';
    case 'medium': 
      return 'warning';
    case 'low':
      return 'muted';
    default:
      return 'muted';
  }
}

export function FeedCard({
  title = "Recent Activity",
  items,
  loading = false,
  error,
  showViewAll = true,
  onViewAll,
  className,
}: FeedCardProps) {
  if (loading) {
    return (
      <div className="loading-state">Loading activities...</div>
    );
  }

  if (error) {
    return (
      <div className="empty-state">
        <h3>Failed to load activity</h3>
        <p>{error}</p>
      </div>
    );
  }

  if (!items.length) {
    return (
      <div className="empty-state">
        <h3>No recent activity</h3>
        <p>No activities to display</p>
      </div>
    );
  }

  return (
    <div className="activity-feed">
      {items.map((item, index) => {
        const Icon = getActivityIcon(item.type);
        const color = getActivityColor(item.type);
        
        return (
          <div key={index} className="activity-item">
            <div 
              className="activity-icon"
              style={{ backgroundColor: `${color}15`, color: color }}
            >
              <Icon size={16} />
            </div>
            
            <div className="activity-content">
              <div className="activity-header">
                <span className={`status-pill ${getPriorityVariant(item.priority)}`}>
                  {item.priority}
                </span>
                <span className="activity-date">
                  {formatDate(new Date(item.date), { style: "relative" })}
                </span>
              </div>
              
              <div className="activity-status">
                <span className={`status-pill ${getStatusVariant(item.status)}`}>
                  {item.status}
                </span>
              </div>
              
              <h4 className="activity-title">{item.title}</h4>
              <p className="activity-description">{item.description}</p>
              
              <div className="activity-author">
                <span>By: {item.author}</span>
              </div>
            </div>
          </div>
        );
      })}
      
      {showViewAll && onViewAll && (
        <button 
          className="btn btn-secondary" 
          onClick={onViewAll}
          style={{ width: '100%', marginTop: '16px' }}
        >
          <ExternalLink size={16} style={{ marginRight: '8px' }} />
          View All Activities
        </button>
      )}
    </div>
  );
}

function getStatusVariant(status: string) {
  switch (status.toLowerCase()) {
    case 'completed': return 'success';
    case 'in-progress': case 'scheduled': return 'info';
    case 'cancelled': case 'failed': return 'error';
    default: return 'info';
  }
}