// Mock data for multiple households with diverse family structures and financial situations

export interface Household {
  id: string;
  name: string;
  primaryContact: string;
  totalAssets: number;
  totalCash: number;
  accountsCount: number;
  lastActivity: string;
  riskProfile: 'Conservative' | 'Moderate' | 'Aggressive' | 'Ultra-Conservative';
  advisorName: string;
  status: 'Active' | 'Onboarding' | 'Review Required' | 'Inactive';
  householdType: 'Individual' | 'Joint' | 'Trust' | 'Corporation' | 'Foundation';
  location: string;
  joinDate: string;
  ytdPerformance: number;
  monthlyIncome: number;
  recentAlerts: number;
  nextReview: string;
  avatar?: string;
}

export const mockHouseholds: Household[] = [
  {
    id: 'johnson-family-trust',
    name: 'The Johnson Family Trust',
    primaryContact: 'Robert & Sarah Johnson',
    totalAssets: 2850000,
    totalCash: 425000,
    accountsCount: 12,
    lastActivity: '2025-09-25',
    riskProfile: 'Moderate',
    advisorName: 'Michael Chen',
    status: 'Active',
    householdType: 'Trust',
    location: 'San Francisco, CA',
    joinDate: '2019-03-15',
    ytdPerformance: 8.7,
    monthlyIncome: 35000,
    recentAlerts: 2,
    nextReview: '2025-10-15',
  },
  {
    id: 'martinez-family',
    name: 'Martinez Family Wealth',
    primaryContact: 'Elena & Carlos Martinez',
    totalAssets: 4200000,
    totalCash: 620000,
    accountsCount: 18,
    lastActivity: '2025-09-26',
    riskProfile: 'Aggressive',
    advisorName: 'Sarah Williams',
    status: 'Active',
    householdType: 'Joint',
    location: 'Austin, TX',
    joinDate: '2020-07-22',
    ytdPerformance: 12.3,
    monthlyIncome: 48000,
    recentAlerts: 0,
    nextReview: '2025-11-08',
  },
  {
    id: 'chen-enterprises',
    name: 'Chen Enterprises LLC',
    primaryContact: 'David Chen',
    totalAssets: 8750000,
    totalCash: 1200000,
    accountsCount: 25,
    lastActivity: '2025-09-24',
    riskProfile: 'Moderate',
    advisorName: 'Jennifer Park',
    status: 'Active',
    householdType: 'Corporation',
    location: 'Seattle, WA',
    joinDate: '2018-01-10',
    ytdPerformance: 9.8,
    monthlyIncome: 125000,
    recentAlerts: 1,
    nextReview: '2025-10-30',
  },
  {
    id: 'wilson-retirement',
    name: 'Wilson Retirement Fund',
    primaryContact: 'James & Margaret Wilson',
    totalAssets: 1650000,
    totalCash: 180000,
    accountsCount: 8,
    lastActivity: '2025-09-23',
    riskProfile: 'Conservative',
    advisorName: 'Robert Davis',
    status: 'Active',
    householdType: 'Joint',
    location: 'Denver, CO',
    joinDate: '2021-09-05',
    ytdPerformance: 6.2,
    monthlyIncome: 12000,
    recentAlerts: 3,
    nextReview: '2025-10-12',
  },
  {
    id: 'garcia-foundation',
    name: 'Garcia Family Foundation',
    primaryContact: 'Maria Garcia',
    totalAssets: 12500000,
    totalCash: 850000,
    accountsCount: 15,
    lastActivity: '2025-09-25',
    riskProfile: 'Moderate',
    advisorName: 'Michael Chen',
    status: 'Active',
    householdType: 'Foundation',
    location: 'Miami, FL',
    joinDate: '2017-11-30',
    ytdPerformance: 10.5,
    monthlyIncome: 95000,
    recentAlerts: 0,
    nextReview: '2025-12-01',
  },
  {
    id: 'thompson-individual',
    name: 'Dr. Amanda Thompson',
    primaryContact: 'Amanda Thompson, MD',
    totalAssets: 950000,
    totalCash: 125000,
    accountsCount: 6,
    lastActivity: '2025-09-22',
    riskProfile: 'Aggressive',
    advisorName: 'Sarah Williams',
    status: 'Review Required',
    householdType: 'Individual',
    location: 'Boston, MA',
    joinDate: '2022-04-18',
    ytdPerformance: 15.2,
    monthlyIncome: 28000,
    recentAlerts: 4,
    nextReview: '2025-09-28',
  },
  {
    id: 'young-professionals',
    name: 'The Lee-Kim Partnership',
    primaryContact: 'Alex Lee & Jordan Kim',
    totalAssets: 580000,
    totalCash: 95000,
    accountsCount: 4,
    lastActivity: '2025-09-26',
    riskProfile: 'Aggressive',
    advisorName: 'Jennifer Park',
    status: 'Onboarding',
    householdType: 'Joint',
    location: 'New York, NY',
    joinDate: '2025-08-15',
    ytdPerformance: 18.7,
    monthlyIncome: 22000,
    recentAlerts: 1,
    nextReview: '2025-10-05',
  },
  {
    id: 'retired-educators',
    name: 'Brown Educator Pension',
    primaryContact: 'Thomas & Linda Brown',
    totalAssets: 1200000,
    totalCash: 85000,
    accountsCount: 10,
    lastActivity: '2025-09-20',
    riskProfile: 'Ultra-Conservative',
    advisorName: 'Robert Davis',
    status: 'Active',
    householdType: 'Joint',
    location: 'Portland, OR',
    joinDate: '2020-02-14',
    ytdPerformance: 4.8,
    monthlyIncome: 8500,
    recentAlerts: 2,
    nextReview: '2025-11-20',
  },
  {
    id: 'startup-founder',
    name: 'Patel Ventures',
    primaryContact: 'Ravi Patel',
    totalAssets: 3200000,
    totalCash: 680000,
    accountsCount: 14,
    lastActivity: '2025-09-26',
    riskProfile: 'Aggressive',
    advisorName: 'Jennifer Park',
    status: 'Active',
    householdType: 'Individual',
    location: 'San Jose, CA',
    joinDate: '2023-06-08',
    ytdPerformance: 22.1,
    monthlyIncome: 85000,
    recentAlerts: 0,
    nextReview: '2025-10-18',
  },
  {
    id: 'multigenerational-wealth',
    name: 'The Anderson Legacy Trust',
    primaryContact: 'William Anderson III',
    totalAssets: 15800000,
    totalCash: 2100000,
    accountsCount: 32,
    lastActivity: '2025-09-24',
    riskProfile: 'Conservative',
    advisorName: 'Michael Chen',
    status: 'Active',
    householdType: 'Trust',
    location: 'Charleston, SC',
    joinDate: '2015-10-01',
    ytdPerformance: 7.9,
    monthlyIncome: 180000,
    recentAlerts: 1,
    nextReview: '2025-11-30',
  },
  {
    id: 'divorced-single-parent',
    name: 'Jennifer Walsh Family',
    primaryContact: 'Jennifer Walsh',
    totalAssets: 750000,
    totalCash: 120000,
    accountsCount: 7,
    lastActivity: '2025-09-21',
    riskProfile: 'Moderate',
    advisorName: 'Sarah Williams',
    status: 'Active',
    householdType: 'Individual',
    location: 'Phoenix, AZ',
    joinDate: '2022-01-30',
    ytdPerformance: 9.1,
    monthlyIncome: 15000,
    recentAlerts: 2,
    nextReview: '2025-10-25',
  },
  {
    id: 'real-estate-investors',
    name: 'Morrison Property Holdings',
    primaryContact: 'Jack & Susan Morrison',
    totalAssets: 5600000,
    totalCash: 450000,
    accountsCount: 22,
    lastActivity: '2025-09-25',
    riskProfile: 'Moderate',
    advisorName: 'Robert Davis',
    status: 'Active',
    householdType: 'Joint',
    location: 'Nashville, TN',
    joinDate: '2019-08-12',
    ytdPerformance: 11.4,
    monthlyIncome: 67000,
    recentAlerts: 1,
    nextReview: '2025-11-15',
  },
  {
    id: 'international-family',
    name: 'Singh Global Family Office',
    primaryContact: 'Arjun & Priya Singh',
    totalAssets: 25000000,
    totalCash: 3500000,
    accountsCount: 45,
    lastActivity: '2025-09-26',
    riskProfile: 'Moderate',
    advisorName: 'Michael Chen',
    status: 'Active',
    householdType: 'Trust',
    location: 'Los Angeles, CA',
    joinDate: '2016-05-20',
    ytdPerformance: 8.3,
    monthlyIncome: 295000,
    recentAlerts: 0,
    nextReview: '2025-12-15',
  },
  {
    id: 'young-inheritance',
    name: 'Taylor Trust Beneficiary',
    primaryContact: 'Madison Taylor',
    totalAssets: 1850000,
    totalCash: 320000,
    accountsCount: 9,
    lastActivity: '2025-09-19',
    riskProfile: 'Conservative',
    advisorName: 'Jennifer Park',
    status: 'Review Required',
    householdType: 'Individual',
    location: 'Chicago, IL',
    joinDate: '2024-03-01',
    ytdPerformance: 5.7,
    monthlyIncome: 18000,
    recentAlerts: 5,
    nextReview: '2025-09-30',
  },
  {
    id: 'tech-executive',
    name: 'White Executive Portfolio',
    primaryContact: 'Kevin & Lisa White',
    totalAssets: 6800000,
    totalCash: 890000,
    accountsCount: 19,
    lastActivity: '2025-09-26',
    riskProfile: 'Aggressive',
    advisorName: 'Sarah Williams',
    status: 'Active',
    householdType: 'Joint',
    location: 'Bellevue, WA',
    joinDate: '2021-11-05',
    ytdPerformance: 14.6,
    monthlyIncome: 98000,
    recentAlerts: 0,
    nextReview: '2025-11-12',
  }
];

// Helper functions for data aggregation
export const getHouseholdStats = () => {
  const totalAssets = mockHouseholds.reduce((sum, h) => sum + h.totalAssets, 0);
  const totalCash = mockHouseholds.reduce((sum, h) => sum + h.totalCash, 0);
  const totalAccounts = mockHouseholds.reduce((sum, h) => sum + h.accountsCount, 0);
  const averagePerformance = mockHouseholds.reduce((sum, h) => sum + h.ytdPerformance, 0) / mockHouseholds.length;
  
  return {
    totalHouseholds: mockHouseholds.length,
    totalAssets,
    totalCash,
    totalAccounts,
    averagePerformance
  };
};

export const getHouseholdById = (id: string) => {
  return mockHouseholds.find(h => h.id === id);
};

export const getHouseholdsByAdvisor = (advisorName: string) => {
  return mockHouseholds.filter(h => h.advisorName === advisorName);
};

export const getHouseholdsByStatus = (status: Household['status']) => {
  return mockHouseholds.filter(h => h.status === status);
};

export const getRecentActivity = (days: number = 7) => {
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - days);
  
  return mockHouseholds.filter(h => {
    const activityDate = new Date(h.lastActivity);
    return activityDate >= cutoffDate;
  });
};

export default mockHouseholds;