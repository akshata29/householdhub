"use client";

import * as React from "react";
import { OverviewTab } from "@/features/overview/overview-tab";
import { PortfolioTab } from "@/features/portfolio/portfolio-tab";
import { CashTab } from "@/features/cash/cash-tab";
import { PlanningTab } from "@/features/planning/planning-tab";
import { ReportsTab } from "@/features/reports/reports-tab";
import { CopilotPanel } from "@/components/copilot/copilot-panel";
import { getHouseholdById } from "@/lib/mock-households";

interface DashboardProps {
  householdId: string;
}

export function Dashboard({ householdId }: DashboardProps) {
  const household = getHouseholdById(householdId);
  
  // Default to Johnson Family Trust if household not found
  const householdName = household?.name || "The Johnson Family Trust";
  const [activeTab, setActiveTab] = React.useState("overview");

  const renderTabContent = () => {
    switch (activeTab) {
      case "overview":
        return <OverviewTab householdId={householdId} />;
      case "portfolio":
        return <PortfolioTab householdId={householdId} />;
      case "cash":
        return <CashTab householdId={householdId} />;
      case "planning":
        return <PlanningTab householdId={householdId} />;
      case "reports":
        return <ReportsTab householdId={householdId} />;
      default:
        return <OverviewTab householdId={householdId} />;
    }
  };

  return (
    <div>
      <div className="app-bar">
        <div className="dashboard-container">
          <div className="app-bar-content">
            <div className="household-header-left">
              <button 
                className="home-button"
                onClick={() => window.location.href = '/'}
                title="Back to Households"
              >
                <svg 
                  width="20" 
                  height="20" 
                  viewBox="0 0 24 24" 
                  fill="none" 
                  stroke="currentColor" 
                  strokeWidth="2" 
                  strokeLinecap="round" 
                  strokeLinejoin="round"
                >
                  <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                  <polyline points="9,22 9,12 15,12 15,22"/>
                </svg>
              </button>
              <div>
                <h1 className="household-title">{householdName}</h1>
                <p className="page-subtitle">Last updated: {new Date().toLocaleString()}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="dashboard-container">
        <div className="tabs-container">
          <div className="tabs-list">
            <button 
              className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveTab('overview')}
            >
              Overview
            </button>
            <button 
              className={`tab-button ${activeTab === 'portfolio' ? 'active' : ''}`}
              onClick={() => setActiveTab('portfolio')}
            >
              Portfolio
            </button>
            <button 
              className={`tab-button ${activeTab === 'cash' ? 'active' : ''}`}
              onClick={() => setActiveTab('cash')}
            >
              Cash Management
            </button>
            <button 
              className={`tab-button ${activeTab === 'planning' ? 'active' : ''}`}
              onClick={() => setActiveTab('planning')}
            >
              Planning
            </button>
            <button 
              className={`tab-button ${activeTab === 'reports' ? 'active' : ''}`}
              onClick={() => setActiveTab('reports')}
            >
              Reports
            </button>
          </div>
          
          <div className="tab-content">
            {renderTabContent()}
          </div>
        </div>
      </div>
      
      {/* AI Copilot Panel */}
      <CopilotPanel householdId={householdId} />
    </div>
  );
}