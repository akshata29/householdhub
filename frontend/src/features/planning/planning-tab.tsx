"use client";

import * as React from "react";
import { usePlanning } from "@/lib/queries";
import { KPICard } from "@/components/ui/kpi-card";
import { 
  Calendar,
  Users,
  Clock,
  AlertTriangle,
  CheckCircle,
  FileText,
  Plus,
  DollarSign,
  User,
  ClipboardList,
} from "lucide-react";
import { formatCurrency, formatDate, getDaysRemaining, getUrgencyLevel } from "@/lib/utils";

interface PlanningTabProps {
  householdId: string;
}

function RMDCard({ rmd }: { rmd: any }) {
  const daysRemaining = getDaysRemaining(rmd.dueDate);
  const urgency = getUrgencyLevel(daysRemaining);
  const completionPercent = (rmd.completedAmount / rmd.requiredAmount) * 100;

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'critical':
        return 'negative';
      case 'warning':
        return 'warning';
      default:
        return 'normal';
    }
  };

  return (
    <div className="planning-card rmd-card">
      <div className="planning-card-header">
        <div className="rmd-header">
          <div className="rmd-account">
            <h4 className="rmd-account-name">{rmd.accountName}</h4>
            <p className="rmd-owner">{rmd.owner}</p>
          </div>
          <div className="rmd-status">
            <span className={`status-pill status-${rmd.status}`}>
              {rmd.status}
            </span>
            {daysRemaining <= 30 && (
              <span className={`status-pill status-${getUrgencyColor(urgency)}`}>
                <Clock className="pill-icon" />
                {daysRemaining === 0 ? 'Due today' : `${daysRemaining} days`}
              </span>
            )}
          </div>
        </div>
        
        <div className="progress-section">
          <div className="progress-header">
            <span className="progress-label">Progress</span>
            <span className="progress-value">{completionPercent.toFixed(1)}%</span>
          </div>
          <div className="progress-bar">
            <div 
              className={`progress-fill ${completionPercent === 100 ? 'complete' : completionPercent > 50 ? 'partial' : 'minimal'}`}
              style={{ width: `${Math.min(completionPercent, 100)}%` }}
            />
          </div>
        </div>
      </div>
      
      <div className="rmd-details">
        <div className="rmd-detail-row">
          <span className="detail-label">Required Amount:</span>
          <span className="detail-value">{formatCurrency(rmd.requiredAmount)}</span>
        </div>
        <div className="rmd-detail-row">
          <span className="detail-label">Completed:</span>
          <span className="detail-value">{formatCurrency(rmd.completedAmount)}</span>
        </div>
        <div className="rmd-detail-row">
          <span className="detail-label">Due Date:</span>
          <span className="detail-value">{formatDate(rmd.dueDate)}</span>
        </div>
      </div>
      
      <div className="planning-card-actions">
        <button className="btn btn-primary">
          {rmd.status === 'completed' ? 'View Details' : 'Process RMD'}
        </button>
      </div>
    </div>
  );
}

function BeneficiaryCard({ beneficiary }: { beneficiary: any }) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'complete':
        return 'positive';
      case 'incomplete':
        return 'warning';
      case 'review-needed':
        return 'negative';
      default:
        return 'normal';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'complete':
        return CheckCircle;
      case 'incomplete':
        return AlertTriangle;
      case 'review-needed':
        return AlertTriangle;
      default:
        return FileText;
    }
  };

  const StatusIcon = getStatusIcon(beneficiary.status);

  return (
    <div className="planning-card beneficiary-card">
      <div className="beneficiary-header">
        <div className="beneficiary-info">
          <div className="beneficiary-icon">
            <Users className="icon" />
          </div>
          <div className="beneficiary-details">
            <h4 className="beneficiary-account-name">{beneficiary.accountName}</h4>
            <p className="beneficiary-account-type">{beneficiary.accountType}</p>
          </div>
        </div>
        <div className="beneficiary-status">
          <StatusIcon className="status-icon" />
          <span className={`status-pill status-${getStatusColor(beneficiary.status)}`}>
            {beneficiary.status.replace('-', ' ')}
          </span>
        </div>
      </div>

      <div className="beneficiary-details-grid">
        <div className="beneficiary-detail">
          <span className="detail-label">Primary Beneficiary</span>
          <span className={`detail-badge ${beneficiary.hasPrimary ? 'positive' : 'negative'}`}>
            {beneficiary.hasPrimary ? 'Assigned' : 'Missing'}
          </span>
        </div>
        <div className="beneficiary-detail">
          <span className="detail-label">Contingent Beneficiary</span>
          <span className={`detail-badge ${beneficiary.hasContingent ? 'positive' : 'warning'}`}>
            {beneficiary.hasContingent ? 'Assigned' : 'Not Set'}
          </span>
        </div>
        {beneficiary.lastReviewed && (
          <div className="beneficiary-detail">
            <span className="detail-label">Last Reviewed</span>
            <span className="detail-value">{formatDate(beneficiary.lastReviewed)}</span>
          </div>
        )}
      </div>

      <div className="planning-card-actions">
        <button className="btn btn-secondary">
          {beneficiary.status === 'complete' ? 'Review' : 'Update Beneficiaries'}
        </button>
      </div>
    </div>
  );
}

function NextInteractionCard({ nextInteraction }: { nextInteraction: any }) {
  if (!nextInteraction) return null;

  return (
    <div className="next-interaction-card">
      <div className="interaction-header">
        <div className="interaction-icon">
          <Calendar className="icon" />
        </div>
        <div className="interaction-details">
          <h4 className="interaction-title">Next Scheduled Interaction</h4>
          <p className="interaction-type">{nextInteraction.type}</p>
        </div>
      </div>
      <div className="interaction-description">
        <p>{nextInteraction.description}</p>
      </div>
      <div className="interaction-date">
        <span className="date-label">Scheduled for:</span>
        <span className="date-value">{formatDate(nextInteraction.date)}</span>
      </div>
      <div className="interaction-actions">
        <button className="btn btn-primary">Reschedule</button>
        <button className="btn btn-secondary">View Details</button>
      </div>
    </div>
  );
}

export function PlanningTab({ householdId }: PlanningTabProps) {
  const { 
    data: planningData, 
    isLoading: planningLoading, 
    error: planningError 
  } = usePlanning(householdId);

  if (planningLoading) {
    return (
      <div className="planning-container">
        <div className="loading-state">Loading planning data...</div>
      </div>
    );
  }

  if (planningError) {
    return (
      <div className="planning-container">
        <div className="error-state">
          <h3>Failed to Load Planning Data</h3>
          <p>{planningError.message}</p>
        </div>
      </div>
    );
  }

  if (!planningData) {
    return (
      <div className="planning-container">
        <div className="empty-state">
          <h3>No Planning Data Available</h3>
          <p>Financial planning data could not be loaded.</p>
        </div>
      </div>
    );
  }

  // Calculate summary statistics
  const totalRMDs = planningData.rmds?.length || 0;
  const pendingRMDs = planningData.rmds?.filter(rmd => rmd.status === 'pending').length || 0;
  const totalRMDAmount = planningData.rmds?.reduce((sum, rmd) => sum + rmd.requiredAmount, 0) || 0;
  const incompleteBeneficiaries = planningData.beneficiaries?.filter(ben => ben.status !== 'complete').length || 0;

  return (
    <div className="planning-container">
      {/* Header */}
      <div className="planning-header">
        <h1 className="planning-title">Financial Planning</h1>
        <p className="planning-subtitle">Estate planning, RMDs, and beneficiary management</p>
      </div>

      {/* Summary KPIs */}
      <div className="kpi-grid">
        <KPICard
          label="Total RMDs Required"
          value={totalRMDAmount}
          format="currency"
          icon={DollarSign}
        />
        <KPICard
          label="Pending RMDs"
          value={`${pendingRMDs} of ${totalRMDs}`}
          format="text"
          icon={ClipboardList}
        />
        <KPICard
          label="Beneficiaries Needing Review"
          value={incompleteBeneficiaries}
          format="number"
          icon={Users}
        />
      </div>

      {/* Next Interaction */}
      {planningData.nextInteraction && (
        <NextInteractionCard nextInteraction={planningData.nextInteraction} />
      )}

      {/* Planning Sections */}
      <div className="planning-sections">
        {/* Required Minimum Distributions */}
        <div className="planning-section">
          <div className="section-header">
            <h3 className="section-title">Required Minimum Distributions (RMDs)</h3>
            <p className="section-description">Mandatory withdrawals from retirement accounts</p>
            <button className="btn btn-secondary">
              <Plus className="btn-icon" />
              Add RMD
            </button>
          </div>
          
          {planningData.rmds && planningData.rmds.length > 0 ? (
            <div className="planning-grid">
              {planningData.rmds.map((rmd) => (
                <RMDCard key={rmd.id} rmd={rmd} />
              ))}
            </div>
          ) : (
            <div className="empty-section">
              <p>No RMDs scheduled for this year</p>
            </div>
          )}
        </div>

        {/* Beneficiary Designations */}
        <div className="planning-section">
          <div className="section-header">
            <h3 className="section-title">Beneficiary Designations</h3>
            <p className="section-description">Estate planning and account beneficiaries</p>
            <button className="btn btn-secondary">
              <Plus className="btn-icon" />
              Update Beneficiaries
            </button>
          </div>
          
          {planningData.beneficiaries && planningData.beneficiaries.length > 0 ? (
            <div className="planning-grid">
              {planningData.beneficiaries.map((beneficiary) => (
                <BeneficiaryCard key={beneficiary.id} beneficiary={beneficiary} />
              ))}
            </div>
          ) : (
            <div className="empty-section">
              <p>No beneficiary information available</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}