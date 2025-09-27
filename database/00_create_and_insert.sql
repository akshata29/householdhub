-- WealthOps Complete Fresh Start - Azure SQL Edition
-- This script drops and recreates all tables with complete data
-- For Azure SQL Database (cannot drop/create database)
-- Version: 2.0 - Azure SQL Compatible
-- Date: 2025-09-27

USE householdhub;
GO

-- =====================================================
-- DROP ALL TABLES (in correct dependency order)
-- =====================================================

-- Drop views first
IF OBJECT_ID('vw_HouseholdSummary', 'V') IS NOT NULL
    DROP VIEW vw_HouseholdSummary;

-- Drop tables with foreign keys first (child tables)
IF OBJECT_ID('Beneficiaries', 'U') IS NOT NULL
    DROP TABLE Beneficiaries;

IF OBJECT_ID('RMDs', 'U') IS NOT NULL
    DROP TABLE RMDs;

IF OBJECT_ID('Activities', 'U') IS NOT NULL
    DROP TABLE Activities;

IF OBJECT_ID('CashTrendData', 'U') IS NOT NULL
    DROP TABLE CashTrendData;

IF OBJECT_ID('PerformanceData', 'U') IS NOT NULL
    DROP TABLE PerformanceData;

IF OBJECT_ID('Positions', 'U') IS NOT NULL
    DROP TABLE Positions;

IF OBJECT_ID('Securities', 'U') IS NOT NULL
    DROP TABLE Securities;

IF OBJECT_ID('Accounts', 'U') IS NOT NULL
    DROP TABLE Accounts;

IF OBJECT_ID('Households', 'U') IS NOT NULL
    DROP TABLE Households;

-- Drop reference tables (parent tables)
IF OBJECT_ID('ActivityTypes', 'U') IS NOT NULL
    DROP TABLE ActivityTypes;

IF OBJECT_ID('Institutions', 'U') IS NOT NULL
    DROP TABLE Institutions;

IF OBJECT_ID('AssetClasses', 'U') IS NOT NULL
    DROP TABLE AssetClasses;

IF OBJECT_ID('AccountTypes', 'U') IS NOT NULL
    DROP TABLE AccountTypes;

IF OBJECT_ID('Advisors', 'U') IS NOT NULL
    DROP TABLE Advisors;

IF OBJECT_ID('HouseholdTypes', 'U') IS NOT NULL
    DROP TABLE HouseholdTypes;

IF OBJECT_ID('RiskProfiles', 'U') IS NOT NULL
    DROP TABLE RiskProfiles;

-- =====================================================
-- CREATE SCHEMA AND TABLES
-- =====================================================

-- Risk Profile lookup
CREATE TABLE RiskProfiles (
    RiskProfileID INT IDENTITY(1,1) PRIMARY KEY,
    ProfileName NVARCHAR(50) NOT NULL UNIQUE,
    Description NVARCHAR(500),
    CreatedAt DATETIME2(7) DEFAULT GETUTCDATE(),
    IsActive BIT DEFAULT 1
);

-- Household Types
CREATE TABLE HouseholdTypes (
    HouseholdTypeID INT IDENTITY(1,1) PRIMARY KEY,
    TypeName NVARCHAR(50) NOT NULL UNIQUE,
    Description NVARCHAR(500),
    CreatedAt DATETIME2(7) DEFAULT GETUTCDATE(),
    IsActive BIT DEFAULT 1
);

-- Advisor information
CREATE TABLE Advisors (
    AdvisorID INT IDENTITY(1,1) PRIMARY KEY,
    AdvisorCode NVARCHAR(20) NOT NULL UNIQUE,
    FirstName NVARCHAR(100) NOT NULL,
    LastName NVARCHAR(100) NOT NULL,
    Email NVARCHAR(255),
    Phone NVARCHAR(20),
    Department NVARCHAR(100),
    CreatedAt DATETIME2(7) DEFAULT GETUTCDATE(),
    IsActive BIT DEFAULT 1,
    INDEX IX_Advisor_Code (AdvisorCode),
    INDEX IX_Advisor_Name (LastName, FirstName)
);

-- Account Types
CREATE TABLE AccountTypes (
    AccountTypeID INT IDENTITY(1,1) PRIMARY KEY,
    TypeName NVARCHAR(50) NOT NULL UNIQUE,
    Category NVARCHAR(50), -- 'cash', 'investment', 'retirement'
    Description NVARCHAR(500),
    IsActive BIT DEFAULT 1
);

-- Asset Classes
CREATE TABLE AssetClasses (
    AssetClassID INT IDENTITY(1,1) PRIMARY KEY,
    ClassName NVARCHAR(50) NOT NULL UNIQUE,
    Description NVARCHAR(500),
    SortOrder INT,
    IsActive BIT DEFAULT 1
);

-- Financial Institutions
CREATE TABLE Institutions (
    InstitutionID INT IDENTITY(1,1) PRIMARY KEY,
    InstitutionCode NVARCHAR(20) NOT NULL UNIQUE,
    Name NVARCHAR(200) NOT NULL,
    ShortName NVARCHAR(50),
    Website NVARCHAR(500),
    IsActive BIT DEFAULT 1,
    INDEX IX_Institution_Code (InstitutionCode)
);

-- Activity Types
CREATE TABLE ActivityTypes (
    ActivityTypeID INT IDENTITY(1,1) PRIMARY KEY,
    TypeName NVARCHAR(100) NOT NULL UNIQUE,
    Description NVARCHAR(500),
    DefaultPriority NVARCHAR(20) DEFAULT 'medium',
    CreatedAt DATETIME2(7) DEFAULT GETUTCDATE(),
    IsActive BIT DEFAULT 1
);

-- Households (Core entity)
CREATE TABLE Households (
    HouseholdID INT IDENTITY(1,1) PRIMARY KEY,
    HouseholdCode NVARCHAR(50) NOT NULL UNIQUE, -- External friendly ID
    Name NVARCHAR(200) NOT NULL,
    PrimaryContact NVARCHAR(200),
    HouseholdTypeID INT NOT NULL,
    RiskProfileID INT NOT NULL,
    PrimaryAdvisorID INT NOT NULL,
    Status NVARCHAR(20) NOT NULL DEFAULT 'Active', -- Active, Inactive, Onboarding, Review Required
    Location NVARCHAR(200),
    JoinDate DATE,
    NextReviewDate DATE,
    MonthlyIncome DECIMAL(18,2),
    RecentAlerts INT DEFAULT 0,
    CreatedAt DATETIME2(7) DEFAULT GETUTCDATE(),
    UpdatedAt DATETIME2(7) DEFAULT GETUTCDATE(),
    IsActive BIT DEFAULT 1,
    
    CONSTRAINT FK_Household_Type FOREIGN KEY (HouseholdTypeID) REFERENCES HouseholdTypes(HouseholdTypeID),
    CONSTRAINT FK_Household_RiskProfile FOREIGN KEY (RiskProfileID) REFERENCES RiskProfiles(RiskProfileID),
    CONSTRAINT FK_Household_Advisor FOREIGN KEY (PrimaryAdvisorID) REFERENCES Advisors(AdvisorID),
    
    INDEX IX_Household_Code (HouseholdCode),
    INDEX IX_Household_Status (Status),
    INDEX IX_Household_Advisor (PrimaryAdvisorID)
);

-- Accounts
CREATE TABLE Accounts (
    AccountID INT IDENTITY(1,1) PRIMARY KEY,
    AccountCode NVARCHAR(50) NOT NULL UNIQUE,
    HouseholdID INT NOT NULL,
    AccountTypeID INT NOT NULL,
    InstitutionID INT NOT NULL,
    Name NVARCHAR(200) NOT NULL,
    Balance DECIMAL(18,2) DEFAULT 0.00,
    APY DECIMAL(5,4) DEFAULT 0.0000,
    OpenDate DATE,
    Status NVARCHAR(20) DEFAULT 'Active',
    CreatedAt DATETIME2(7) DEFAULT GETUTCDATE(),
    UpdatedAt DATETIME2(7) DEFAULT GETUTCDATE(),
    IsActive BIT DEFAULT 1,
    
    CONSTRAINT FK_Account_Household FOREIGN KEY (HouseholdID) REFERENCES Households(HouseholdID),
    CONSTRAINT FK_Account_Type FOREIGN KEY (AccountTypeID) REFERENCES AccountTypes(AccountTypeID),
    CONSTRAINT FK_Account_Institution FOREIGN KEY (InstitutionID) REFERENCES Institutions(InstitutionID),
    
    INDEX IX_Account_Code (AccountCode),
    INDEX IX_Account_Household (HouseholdID),
    INDEX IX_Account_Type (AccountTypeID)
);

-- Securities
CREATE TABLE Securities (
    SecurityID INT IDENTITY(1,1) PRIMARY KEY,
    Symbol NVARCHAR(20) NOT NULL UNIQUE,
    Name NVARCHAR(200) NOT NULL,
    AssetClassID INT NOT NULL,
    Sector NVARCHAR(100),
    LastPrice DECIMAL(18,4),
    LastPriceDate DATE,
    CreatedAt DATETIME2(7) DEFAULT GETUTCDATE(),
    IsActive BIT DEFAULT 1,
    
    CONSTRAINT FK_Security_AssetClass FOREIGN KEY (AssetClassID) REFERENCES AssetClasses(AssetClassID),
    
    INDEX IX_Security_Symbol (Symbol),
    INDEX IX_Security_AssetClass (AssetClassID)
);

-- Positions
CREATE TABLE Positions (
    PositionID INT IDENTITY(1,1) PRIMARY KEY,
    AccountID INT NOT NULL,
    SecurityID INT NOT NULL,
    Quantity DECIMAL(18,4) NOT NULL,
    CostBasis DECIMAL(18,2),
    MarketValue DECIMAL(18,2),
    AsOfDate DATE NOT NULL,
    CreatedAt DATETIME2(7) DEFAULT GETUTCDATE(),
    
    CONSTRAINT FK_Position_Account FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID),
    CONSTRAINT FK_Position_Security FOREIGN KEY (SecurityID) REFERENCES Securities(SecurityID),
    
    INDEX IX_Position_Account (AccountID),
    INDEX IX_Position_Security (SecurityID),
    INDEX IX_Position_Date (AsOfDate)
);

-- Performance Data
CREATE TABLE PerformanceData (
    PerformanceID INT IDENTITY(1,1) PRIMARY KEY,
    HouseholdID INT NOT NULL,
    AsOfDate DATE NOT NULL,
    PortfolioValue DECIMAL(18,2),
    BenchmarkValue DECIMAL(18,2),
    TotalReturn DECIMAL(8,4),
    BenchmarkReturn DECIMAL(8,4),
    CreatedAt DATETIME2(7) DEFAULT GETUTCDATE(),
    
    CONSTRAINT FK_Performance_Household FOREIGN KEY (HouseholdID) REFERENCES Households(HouseholdID),
    
    INDEX IX_Performance_Household (HouseholdID),
    INDEX IX_Performance_Date (AsOfDate)
);

-- Cash Trend Data
CREATE TABLE CashTrendData (
    CashTrendID INT IDENTITY(1,1) PRIMARY KEY,
    HouseholdID INT NOT NULL,
    AsOfDate DATE NOT NULL,
    TotalCashBalance DECIMAL(18,2),
    CheckingBalance DECIMAL(18,2),
    SavingsBalance DECIMAL(18,2),
    MoneyMarketBalance DECIMAL(18,2),
    CDBalance DECIMAL(18,2),
    CreatedAt DATETIME2(7) DEFAULT GETUTCDATE(),
    
    CONSTRAINT FK_CashTrend_Household FOREIGN KEY (HouseholdID) REFERENCES Households(HouseholdID),
    
    INDEX IX_CashTrend_Household (HouseholdID),
    INDEX IX_CashTrend_Date (AsOfDate)
);

-- Activities
CREATE TABLE Activities (
    ActivityID INT IDENTITY(1,1) PRIMARY KEY,
    HouseholdID INT NOT NULL,
    ActivityTypeID INT NOT NULL,
    Title NVARCHAR(200) NOT NULL,
    Description NVARCHAR(1000),
    Priority NVARCHAR(20) DEFAULT 'medium',
    Status NVARCHAR(50) DEFAULT 'pending',
    Author NVARCHAR(200),
    DueDate DATETIME2(7),
    CompletedDate DATETIME2(7),
    Tags NVARCHAR(500),
    CreatedAt DATETIME2(7) DEFAULT GETUTCDATE(),
    UpdatedAt DATETIME2(7) DEFAULT GETUTCDATE(),
    
    CONSTRAINT FK_Activity_Household FOREIGN KEY (HouseholdID) REFERENCES Households(HouseholdID),
    CONSTRAINT FK_Activity_Type FOREIGN KEY (ActivityTypeID) REFERENCES ActivityTypes(ActivityTypeID),
    
    INDEX IX_Activity_Household (HouseholdID),
    INDEX IX_Activity_Status (Status),
    INDEX IX_Activity_DueDate (DueDate)
);

-- RMDs (Required Minimum Distributions)
CREATE TABLE RMDs (
    RMDID INT IDENTITY(1,1) PRIMARY KEY,
    HouseholdID INT NOT NULL,
    AccountID INT NOT NULL,
    TaxYear INT NOT NULL,
    RequiredAmount DECIMAL(18,2) NOT NULL,
    CompletedAmount DECIMAL(18,2) DEFAULT 0.00,
    DueDate DATE NOT NULL,
    Status NVARCHAR(50) DEFAULT 'pending',
    CreatedAt DATETIME2(7) DEFAULT GETUTCDATE(),
    UpdatedAt DATETIME2(7) DEFAULT GETUTCDATE(),
    
    CONSTRAINT FK_RMD_Household FOREIGN KEY (HouseholdID) REFERENCES Households(HouseholdID),
    CONSTRAINT FK_RMD_Account FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID),
    
    INDEX IX_RMD_Household (HouseholdID),
    INDEX IX_RMD_TaxYear (TaxYear),
    INDEX IX_RMD_Status (Status)
);

-- Beneficiaries
CREATE TABLE Beneficiaries (
    BeneficiaryID INT IDENTITY(1,1) PRIMARY KEY,
    AccountID INT NOT NULL,
    BeneficiaryType NVARCHAR(20) NOT NULL, -- primary, contingent
    Name NVARCHAR(200) NOT NULL,
    Relationship NVARCHAR(100),
    Percentage DECIMAL(5,2) NOT NULL,
    LastReviewed DATE,
    Status NVARCHAR(50) DEFAULT 'complete',
    CreatedAt DATETIME2(7) DEFAULT GETUTCDATE(),
    UpdatedAt DATETIME2(7) DEFAULT GETUTCDATE(),
    
    CONSTRAINT FK_Beneficiary_Account FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID),
    
    INDEX IX_Beneficiary_Account (AccountID),
    INDEX IX_Beneficiary_Type (BeneficiaryType)
);

GO

-- Summary View for Households - MATCHES BACKEND EXPECTATIONS
CREATE VIEW vw_HouseholdSummary AS
SELECT 
    h.HouseholdID,
    h.HouseholdCode,
    h.Name,
    h.PrimaryContact,
    h.Status,
    h.Location,
    h.MonthlyIncome,
    h.RecentAlerts,
    h.JoinDate,
    h.NextReviewDate,
    h.UpdatedAt,
    ht.TypeName as HouseholdType,
    rp.ProfileName as RiskProfile,
    CONCAT(a.FirstName, ' ', a.LastName) as AdvisorName,
    COALESCE(SUM(acc.Balance), 0) as TotalAssets,
    COALESCE(SUM(CASE WHEN at.Category = 'cash' THEN acc.Balance ELSE 0 END), 0) as TotalCash,
    COUNT(acc.AccountID) as AccountsCount,
    COALESCE(perf.TotalReturn, 0) as YTDPerformance
FROM Households h
    LEFT JOIN HouseholdTypes ht ON h.HouseholdTypeID = ht.HouseholdTypeID
    LEFT JOIN RiskProfiles rp ON h.RiskProfileID = rp.RiskProfileID
    LEFT JOIN Advisors a ON h.PrimaryAdvisorID = a.AdvisorID
    LEFT JOIN Accounts acc ON h.HouseholdID = acc.HouseholdID AND acc.IsActive = 1
    LEFT JOIN AccountTypes at ON acc.AccountTypeID = at.AccountTypeID
    LEFT JOIN (
        SELECT 
            HouseholdID,
            TotalReturn
        FROM PerformanceData p1
        WHERE p1.AsOfDate = (
            SELECT MAX(p2.AsOfDate) 
            FROM PerformanceData p2 
            WHERE p2.HouseholdID = p1.HouseholdID
        )
    ) perf ON h.HouseholdID = perf.HouseholdID
WHERE h.IsActive = 1
GROUP BY h.HouseholdID, h.HouseholdCode, h.Name, h.PrimaryContact, h.Status, 
         h.Location, h.MonthlyIncome, h.RecentAlerts, h.JoinDate, h.NextReviewDate, 
         h.UpdatedAt, ht.TypeName, rp.ProfileName, a.FirstName, a.LastName, perf.TotalReturn;
GO

-- =====================================================
-- INSERT REFERENCE DATA
-- =====================================================

-- Risk Profiles
INSERT INTO RiskProfiles (ProfileName, Description) VALUES
('Ultra-Conservative', 'Minimal risk tolerance, capital preservation focused'),
('Conservative', 'Low risk tolerance, stable income preference'),
('Moderate', 'Balanced approach to risk and return'),
('Aggressive', 'Higher risk tolerance for growth potential'),
('Ultra-Aggressive', 'Maximum growth potential, high risk tolerance');

-- Household Types
INSERT INTO HouseholdTypes (TypeName, Description) VALUES
('Individual', 'Single person household'),
('Joint', 'Married couple or domestic partners'),
('Trust', 'Trust or estate account'),
('Corporation', 'Corporate entity'),
('Foundation', 'Non-profit foundation');

-- Advisors
INSERT INTO Advisors (AdvisorCode, FirstName, LastName, Email, Phone, Department) VALUES
('MC001', 'Michael', 'Chen', 'mchen@wealthops.com', '555-0101', 'Private Wealth'),
('SM002', 'Sarah', 'Martinez', 'smartinez@wealthops.com', '555-0102', 'High Net Worth'),
('DJ003', 'David', 'Johnson', 'djohnson@wealthops.com', '555-0103', 'Estate Planning'),
('LW004', 'Lisa', 'Wang', 'lwang@wealthops.com', '555-0104', 'Tax Advisory'),
('RT005', 'Robert', 'Taylor', 'rtaylor@wealthops.com', '555-0105', 'Investment Management'),
('EL006', 'Emily', 'Lee', 'elee@wealthops.com', '555-0106', 'Private Wealth'),
('RP007', 'Richard', 'Parker', 'rparker@wealthops.com', '555-0107', 'Retirement Planning');

-- Account Types
INSERT INTO AccountTypes (TypeName, Category, Description) VALUES
('Checking', 'cash', 'Standard checking account'),
('Savings', 'cash', 'High-yield savings account'),
('Money Market', 'cash', 'Money market account'),
('CD', 'cash', 'Certificate of deposit'),
('Brokerage', 'investment', 'Taxable investment account'),
('Traditional IRA', 'retirement', 'Traditional Individual Retirement Account'),
('Roth IRA', 'retirement', 'Roth Individual Retirement Account'),
('401k', 'retirement', '401(k) retirement plan'),
('529 Plan', 'investment', 'Education savings plan'),
('Trust Account', 'investment', 'Trust or estate account');

-- Asset Classes
INSERT INTO AssetClasses (ClassName, Description, SortOrder) VALUES
('US Equity', 'United States stock investments', 1),
('Fixed Income', 'Bonds and other debt securities', 2),
('International Equity', 'Foreign stock investments', 3),
('Alternative Investments', 'Real estate, commodities, and other alternatives', 4),
('Cash & Cash Equivalents', 'Money market and short-term instruments', 5);

-- Institutions
INSERT INTO Institutions (InstitutionCode, Name, ShortName, Website) VALUES
('CHAS', 'JPMorgan Chase Bank', 'Chase', 'https://www.chase.com'),
('BOA', 'Bank of America', 'BofA', 'https://www.bankofamerica.com'),
('WFC', 'Wells Fargo Bank', 'Wells Fargo', 'https://www.wellsfargo.com'),
('SCHW', 'Charles Schwab Corporation', 'Schwab', 'https://www.schwab.com'),
('FID', 'Fidelity Investments', 'Fidelity', 'https://www.fidelity.com'),
('VG', 'Vanguard Group', 'Vanguard', 'https://www.vanguard.com'),
('TD', 'TD Ameritrade', 'TD Ameritrade', 'https://www.tdameritrade.com'),
('ETRD', 'E*TRADE', 'E*TRADE', 'https://www.etrade.com');

-- Activity Types
INSERT INTO ActivityTypes (TypeName, Description, DefaultPriority) VALUES
('Portfolio Review', 'Regular portfolio review and rebalancing', 'medium'),
('Tax Planning', 'Tax planning and preparation activities', 'high'),
('Estate Planning', 'Estate planning document updates', 'medium'),
('Insurance Review', 'Insurance coverage review and updates', 'low'),
('RMD Distribution', 'Required minimum distribution processing', 'high'),
('Beneficiary Update', 'Beneficiary designation updates', 'medium'),
('Risk Assessment', 'Investment risk profile assessment', 'medium'),
('Cash Management', 'Cash flow and liquidity management', 'medium'),
('Client Meeting', 'Scheduled client meetings and consultations', 'high'),
('Document Collection', 'Collection of required documents', 'low');

-- Securities
INSERT INTO Securities (Symbol, Name, AssetClassID, Sector, LastPrice, LastPriceDate) VALUES
-- US Equity ETFs
('SPY', 'SPDR S&P 500 ETF', 1, 'Large Cap Blend', 445.67, '2025-09-26'),
('VTI', 'Vanguard Total Stock Market ETF', 1, 'Total Market', 234.89, '2025-09-26'),
('QQQ', 'Invesco QQQ ETF', 1, 'Technology', 389.12, '2025-09-26'),
('IWM', 'iShares Russell 2000 ETF', 1, 'Small Cap', 198.45, '2025-09-26'),
('VTV', 'Vanguard Value ETF', 1, 'Large Cap Value', 156.78, '2025-09-26'),
('VUG', 'Vanguard Growth ETF', 1, 'Large Cap Growth', 298.34, '2025-09-26'),

-- International Equity ETFs
('VEA', 'Vanguard Developed Markets ETF', 3, 'International Developed', 45.23, '2025-09-26'),
('VWO', 'Vanguard Emerging Markets ETF', 3, 'Emerging Markets', 39.67, '2025-09-26'),
('IEFA', 'iShares Core MSCI EAFE ETF', 3, 'International Developed', 67.89, '2025-09-26'),

-- Fixed Income ETFs
('AGG', 'iShares Core US Aggregate Bond ETF', 2, 'Aggregate Bond', 102.45, '2025-09-26'),
('BND', 'Vanguard Total Bond Market ETF', 2, 'Total Bond Market', 78.12, '2025-09-26'),
('TLT', 'iShares 20+ Year Treasury Bond ETF', 2, 'Long-Term Treasury', 89.34, '2025-09-26'),
('HYG', 'iShares iBoxx High Yield Corporate Bond ETF', 2, 'High Yield', 82.67, '2025-09-26'),
('LQD', 'iShares iBoxx Investment Grade Corporate Bond ETF', 2, 'Investment Grade Corporate', 118.90, '2025-09-26'),

-- Alternative Investments
('VNQ', 'Vanguard Real Estate ETF', 4, 'Real Estate', 87.45, '2025-09-26'),
('GLD', 'SPDR Gold Shares', 4, 'Commodities', 189.23, '2025-09-26'),
('IAU', 'iShares Gold Trust', 4, 'Commodities', 37.89, '2025-09-26'),

-- Individual Stocks
('AAPL', 'Apple Inc.', 1, 'Technology', 178.35, '2025-09-26'),
('MSFT', 'Microsoft Corporation', 1, 'Technology', 334.12, '2025-09-26'),
('GOOGL', 'Alphabet Inc.', 1, 'Technology', 134.67, '2025-09-26'),
('AMZN', 'Amazon.com Inc.', 1, 'Consumer Discretionary', 128.45, '2025-09-26'),
('TSLA', 'Tesla Inc.', 1, 'Consumer Discretionary', 251.89, '2025-09-26'),
('NVDA', 'NVIDIA Corporation', 1, 'Technology', 456.78, '2025-09-26'),
('JPM', 'JPMorgan Chase & Co.', 1, 'Financial Services', 156.23, '2025-09-26'),
('JNJ', 'Johnson & Johnson', 1, 'Healthcare', 162.45, '2025-09-26'),
('PG', 'Procter & Gamble Co.', 1, 'Consumer Staples', 145.67, '2025-09-26'),
('KO', 'The Coca-Cola Company', 1, 'Consumer Staples', 58.90, '2025-09-26');

-- =====================================================
-- INSERT HOUSEHOLDS
-- =====================================================

INSERT INTO Households (HouseholdCode, Name, PrimaryContact, HouseholdTypeID, RiskProfileID, PrimaryAdvisorID, Status, Location, JoinDate, NextReviewDate, MonthlyIncome, RecentAlerts) VALUES

-- Major Households with complete data
('international-family', 'Singh Global Family Office', 'Arjun & Priya Singh',
 (SELECT HouseholdTypeID FROM HouseholdTypes WHERE TypeName = 'Trust'),
 (SELECT RiskProfileID FROM RiskProfiles WHERE ProfileName = 'Moderate'),
 (SELECT AdvisorID FROM Advisors WHERE AdvisorCode = 'MC001'),
 'Active', 'Los Angeles, CA', '2016-05-20', '2025-12-15', 295000.00, 0),

('young-professionals', 'The Lee-Kim Partnership', 'Alex Lee & Jordan Kim',
 (SELECT HouseholdTypeID FROM HouseholdTypes WHERE TypeName = 'Joint'),
 (SELECT RiskProfileID FROM RiskProfiles WHERE ProfileName = 'Aggressive'),
 (SELECT AdvisorID FROM Advisors WHERE AdvisorCode = 'EL006'),
 'Onboarding', 'New York, NY', '2025-08-15', '2025-10-05', 22000.00, 1),

('tech-executive', 'White Executive Portfolio', 'Kevin & Lisa White',
 (SELECT HouseholdTypeID FROM HouseholdTypes WHERE TypeName = 'Joint'),
 (SELECT RiskProfileID FROM RiskProfiles WHERE ProfileName = 'Aggressive'),
 (SELECT AdvisorID FROM Advisors WHERE AdvisorCode = 'SM002'),
 'Active', 'San Francisco, CA', '2020-03-15', '2025-11-01', 185000.00, 2),

('johnson-family-trust', 'Johnson Family Trust', 'Robert & Mary Johnson',
 (SELECT HouseholdTypeID FROM HouseholdTypes WHERE TypeName = 'Trust'),
 (SELECT RiskProfileID FROM RiskProfiles WHERE ProfileName = 'Conservative'),
 (SELECT AdvisorID FROM Advisors WHERE AdvisorCode = 'DJ003'),
 'Active', 'Houston, TX', '2019-07-12', '2025-10-20', 95000.00, 1),

-- Additional households for complete data set
('chen-enterprises', 'Chen Enterprises LLC', 'David Chen',
 (SELECT HouseholdTypeID FROM HouseholdTypes WHERE TypeName = 'Corporation'),
 (SELECT RiskProfileID FROM RiskProfiles WHERE ProfileName = 'Moderate'),
 (SELECT AdvisorID FROM Advisors WHERE AdvisorCode = 'EL006'),
 'Active', 'Seattle, WA', '2018-01-10', '2025-10-30', 125000.00, 1),

('wilson-retirement', 'Wilson Retirement Fund', 'James & Margaret Wilson',
 (SELECT HouseholdTypeID FROM HouseholdTypes WHERE TypeName = 'Joint'),
 (SELECT RiskProfileID FROM RiskProfiles WHERE ProfileName = 'Conservative'),
 (SELECT AdvisorID FROM Advisors WHERE AdvisorCode = 'RP007'),
 'Active', 'Denver, CO', '2021-09-05', '2025-10-12', 12000.00, 3),

('garcia-foundation', 'Garcia Family Foundation', 'Maria Garcia',
 (SELECT HouseholdTypeID FROM HouseholdTypes WHERE TypeName = 'Foundation'),
 (SELECT RiskProfileID FROM RiskProfiles WHERE ProfileName = 'Moderate'),
 (SELECT AdvisorID FROM Advisors WHERE AdvisorCode = 'MC001'),
 'Active', 'Miami, FL', '2017-11-30', '2025-12-01', 95000.00, 0),

('thompson-individual', 'Dr. Amanda Thompson', 'Amanda Thompson, MD',
 (SELECT HouseholdTypeID FROM HouseholdTypes WHERE TypeName = 'Individual'),
 (SELECT RiskProfileID FROM RiskProfiles WHERE ProfileName = 'Aggressive'),
 (SELECT AdvisorID FROM Advisors WHERE AdvisorCode = 'SM002'),
 'Review Required', 'Boston, MA', '2022-04-18', '2025-09-28', 28000.00, 4),

('retired-educators', 'Brown Educator Pension', 'Thomas & Linda Brown',
 (SELECT HouseholdTypeID FROM HouseholdTypes WHERE TypeName = 'Joint'),
 (SELECT RiskProfileID FROM RiskProfiles WHERE ProfileName = 'Ultra-Conservative'),
 (SELECT AdvisorID FROM Advisors WHERE AdvisorCode = 'RP007'),
 'Active', 'Portland, OR', '2020-02-14', '2025-11-20', 8500.00, 2),

('startup-founder', 'Patel Ventures', 'Ravi Patel',
 (SELECT HouseholdTypeID FROM HouseholdTypes WHERE TypeName = 'Individual'),
 (SELECT RiskProfileID FROM RiskProfiles WHERE ProfileName = 'Aggressive'),
 (SELECT AdvisorID FROM Advisors WHERE AdvisorCode = 'EL006'),
 'Active', 'San Jose, CA', '2023-06-08', '2025-10-18', 85000.00, 0),

('multigenerational-wealth', 'The Anderson Legacy Trust', 'William Anderson III',
 (SELECT HouseholdTypeID FROM HouseholdTypes WHERE TypeName = 'Trust'),
 (SELECT RiskProfileID FROM RiskProfiles WHERE ProfileName = 'Conservative'),
 (SELECT AdvisorID FROM Advisors WHERE AdvisorCode = 'MC001'),
 'Active', 'Charleston, SC', '2015-10-01', '2025-11-30', 180000.00, 1),

('divorced-single-parent', 'Jennifer Walsh Family', 'Jennifer Walsh',
 (SELECT HouseholdTypeID FROM HouseholdTypes WHERE TypeName = 'Individual'),
 (SELECT RiskProfileID FROM RiskProfiles WHERE ProfileName = 'Moderate'),
 (SELECT AdvisorID FROM Advisors WHERE AdvisorCode = 'SM002'),
 'Active', 'Phoenix, AZ', '2022-01-30', '2025-10-25', 15000.00, 2),

('real-estate-investors', 'Morrison Property Holdings', 'Jack & Susan Morrison',
 (SELECT HouseholdTypeID FROM HouseholdTypes WHERE TypeName = 'Joint'),
 (SELECT RiskProfileID FROM RiskProfiles WHERE ProfileName = 'Moderate'),
 (SELECT AdvisorID FROM Advisors WHERE AdvisorCode = 'RP007'),
 'Active', 'Nashville, TN', '2019-08-12', '2025-11-15', 67000.00, 1),

('young-inheritance', 'Taylor Trust Beneficiary', 'Madison Taylor',
 (SELECT HouseholdTypeID FROM HouseholdTypes WHERE TypeName = 'Individual'),
 (SELECT RiskProfileID FROM RiskProfiles WHERE ProfileName = 'Conservative'),
 (SELECT AdvisorID FROM Advisors WHERE AdvisorCode = 'EL006'),
 'Review Required', 'Chicago, IL', '2024-03-01', '2025-09-30', 18000.00, 5),

('energy-executive', 'Carter Energy Holdings', 'Michael & Patricia Carter',
 (SELECT HouseholdTypeID FROM HouseholdTypes WHERE TypeName = 'Joint'),
 (SELECT RiskProfileID FROM RiskProfiles WHERE ProfileName = 'Moderate'),
 (SELECT AdvisorID FROM Advisors WHERE AdvisorCode = 'RT005'),
 'Active', 'Dallas, TX', '2017-12-05', '2025-11-10', 145000.00, 2),

('healthcare-professionals', 'Davis Medical Group', 'Dr. Sarah & Dr. James Davis',
 (SELECT HouseholdTypeID FROM HouseholdTypes WHERE TypeName = 'Joint'),
 (SELECT RiskProfileID FROM RiskProfiles WHERE ProfileName = 'Conservative'),
 (SELECT AdvisorID FROM Advisors WHERE AdvisorCode = 'LW004'),
 'Active', 'Atlanta, GA', '2019-03-22', '2025-10-15', 98000.00, 1),

('military-retirees', 'Colonel Miller Family', 'Col. John & Mary Miller',
 (SELECT HouseholdTypeID FROM HouseholdTypes WHERE TypeName = 'Joint'),
 (SELECT RiskProfileID FROM RiskProfiles WHERE ProfileName = 'Conservative'),
 (SELECT AdvisorID FROM Advisors WHERE AdvisorCode = 'RP007'),
 'Active', 'San Antonio, TX', '2021-06-01', '2025-12-05', 14500.00, 0),

('entertainment-industry', 'Rodriguez Entertainment LLC', 'Carlos Rodriguez',
 (SELECT HouseholdTypeID FROM HouseholdTypes WHERE TypeName = 'Corporation'),
 (SELECT RiskProfileID FROM RiskProfiles WHERE ProfileName = 'Aggressive'),
 (SELECT AdvisorID FROM Advisors WHERE AdvisorCode = 'SM002'),
 'Active', 'Los Angeles, CA', '2020-11-18', '2025-11-25', 165000.00, 3),

('small-business-owners', 'Thompson & Associates', 'Mark & Lisa Thompson',
 (SELECT HouseholdTypeID FROM HouseholdTypes WHERE TypeName = 'Joint'),
 (SELECT RiskProfileID FROM RiskProfiles WHERE ProfileName = 'Moderate'),
 (SELECT AdvisorID FROM Advisors WHERE AdvisorCode = 'DJ003'),
 'Active', 'Minneapolis, MN', '2018-09-30', '2025-10-08', 78000.00, 1),

('legal-professionals', 'Williams Law Firm', 'Attorney Jennifer Williams',
 (SELECT HouseholdTypeID FROM HouseholdTypes WHERE TypeName = 'Individual'),
 (SELECT RiskProfileID FROM RiskProfiles WHERE ProfileName = 'Conservative'),
 (SELECT AdvisorID FROM Advisors WHERE AdvisorCode = 'LW004'),
 'Active', 'Washington, DC', '2019-05-14', '2025-11-08', 115000.00, 2),

('pharmaceutical-executives', 'Kumar Pharma Holdings', 'Dr. Raj & Priya Kumar',
 (SELECT HouseholdTypeID FROM HouseholdTypes WHERE TypeName = 'Joint'),
 (SELECT RiskProfileID FROM RiskProfiles WHERE ProfileName = 'Aggressive'),
 (SELECT AdvisorID FROM Advisors WHERE AdvisorCode = 'RT005'),
 'Active', 'New Jersey', '2016-08-25', '2025-12-20', 195000.00, 1);

-- =====================================================
-- INSERT ACCOUNTS
-- =====================================================

-- Get household IDs for major households
DECLARE @intl_household INT = (SELECT HouseholdID FROM Households WHERE HouseholdCode = 'international-family');
DECLARE @young_household INT = (SELECT HouseholdID FROM Households WHERE HouseholdCode = 'young-professionals');
DECLARE @tech_household INT = (SELECT HouseholdID FROM Households WHERE HouseholdCode = 'tech-executive');
DECLARE @johnson_household INT = (SELECT HouseholdID FROM Households WHERE HouseholdCode = 'johnson-family-trust');

-- International Family Accounts
INSERT INTO Accounts (AccountCode, HouseholdID, AccountTypeID, InstitutionID, Name, Balance, APY, OpenDate, Status) VALUES
('intl-fam-checking-001', @intl_household, 
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Checking'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'CHAS'),
 'Primary Checking Account', 1500000.00, 0.0150, '2016-05-20', 'Active'),

('intl-fam-savings-001', @intl_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Savings'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'CHAS'),
 'High-Yield Savings Account', 2000000.00, 0.0425, '2016-05-20', 'Active'),

('intl-fam-invest-001', @intl_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Brokerage'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'SCHW'),
 'Investment Portfolio Account', 25000000.00, 0.0000, '2016-05-20', 'Active'),

('intl-fam-ira-001', @intl_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Traditional IRA'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'SCHW'),
 'Traditional IRA Account', 8500000.00, 0.0000, '2016-06-01', 'Active');

-- Young Professionals Accounts  
INSERT INTO Accounts (AccountCode, HouseholdID, AccountTypeID, InstitutionID, Name, Balance, APY, OpenDate, Status) VALUES
('young-prof-checking-001', @young_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Checking'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'BOA'),
 'Joint Checking Account', 45000.00, 0.0100, '2025-08-15', 'Active'),

('young-prof-savings-001', @young_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Savings'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'BOA'),
 'Emergency Savings Fund', 50000.00, 0.0400, '2025-08-15', 'Active'),

('young-prof-invest-001', @young_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Brokerage'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'FID'),
 'Growth Investment Account', 580000.00, 0.0000, '2025-08-15', 'Active'),

('young-prof-401k-001', @young_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = '401k'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'FID'),
 'Employer 401(k) Plan', 125000.00, 0.0000, '2025-08-15', 'Active');

-- Tech Executive Accounts
INSERT INTO Accounts (AccountCode, HouseholdID, AccountTypeID, InstitutionID, Name, Balance, APY, OpenDate, Status) VALUES
('tech-exec-checking-001', @tech_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Checking'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'WFC'),
 'Executive Checking Account', 340000.00, 0.0125, '2020-03-15', 'Active'),

('tech-exec-mm-001', @tech_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Money Market'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'WFC'),
 'Money Market Account', 550000.00, 0.0475, '2020-03-15', 'Active'),

('tech-exec-invest-001', @tech_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Brokerage'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'VG'),
 'Tech Stock Portfolio', 6800000.00, 0.0000, '2020-03-15', 'Active'),

('tech-exec-roth-001', @tech_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Roth IRA'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'VG'),
 'Roth IRA Account', 450000.00, 0.0000, '2020-04-01', 'Active');

-- Johnson Family Trust Accounts
INSERT INTO Accounts (AccountCode, HouseholdID, AccountTypeID, InstitutionID, Name, Balance, APY, OpenDate, Status) VALUES
('johnson-trust-checking-001', @johnson_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Checking'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'CHAS'),
 'Trust Operating Account', 125000.00, 0.0150, '2019-07-12', 'Active'),

('johnson-trust-invest-001', @johnson_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Trust Account'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'SCHW'),
 'Conservative Investment Portfolio', 2850000.00, 0.0000, '2019-07-12', 'Active');

-- =====================================================
-- INSERT POSITIONS (Asset Allocation Data)
-- =====================================================

-- Get account IDs
DECLARE @intl_investment INT = (SELECT AccountID FROM Accounts WHERE AccountCode = 'intl-fam-invest-001');
DECLARE @young_investment INT = (SELECT AccountID FROM Accounts WHERE AccountCode = 'young-prof-invest-001');
DECLARE @tech_investment INT = (SELECT AccountID FROM Accounts WHERE AccountCode = 'tech-exec-invest-001');

-- International Family Portfolio (Large, diversified)
INSERT INTO Positions (AccountID, SecurityID, Quantity, CostBasis, MarketValue, AsOfDate) VALUES
(@intl_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'SPY'), 15000.00, 6500000.00, 6685050.00, '2025-09-26'),
(@intl_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'VEA'), 25000.00, 1050000.00, 1130750.00, '2025-09-26'),
(@intl_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'VWO'), 18000.00, 650000.00, 714060.00, '2025-09-26'),
(@intl_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'AGG'), 45000.00, 4500000.00, 4610250.00, '2025-09-26'),
(@intl_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'VNQ'), 12000.00, 950000.00, 1049400.00, '2025-09-26'),
(@intl_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'GLD'), 8500.00, 1500000.00, 1608455.00, '2025-09-26'),
(@intl_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'AAPL'), 25000.00, 3500000.00, 4458750.00, '2025-09-26'),
(@intl_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'MSFT'), 8000.00, 2200000.00, 2672960.00, '2025-09-26'),
(@intl_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'GOOGL'), 15000.00, 1800000.00, 2020050.00, '2025-09-26');

-- Young Professionals Portfolio (Growth-focused)
INSERT INTO Positions (AccountID, SecurityID, Quantity, CostBasis, MarketValue, AsOfDate) VALUES
(@young_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'VTI'), 1200.00, 260000.00, 281868.00, '2025-09-26'),
(@young_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'QQQ'), 350.00, 125000.00, 136192.00, '2025-09-26'),
(@young_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'VUG'), 250.00, 68000.00, 74585.00, '2025-09-26'),
(@young_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'VEA'), 800.00, 34000.00, 36184.00, '2025-09-26'),
(@young_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'BND'), 150.00, 12000.00, 11718.00, '2025-09-26'),
(@young_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'NVDA'), 120.00, 45000.00, 54813.60, '2025-09-26'),
(@young_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'TSLA'), 80.00, 18000.00, 20151.20, '2025-09-26');

-- Tech Executive Portfolio (Tech-heavy with diversification)
INSERT INTO Positions (AccountID, SecurityID, Quantity, CostBasis, MarketValue, AsOfDate) VALUES
(@tech_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'SPY'), 6800.00, 2850000.00, 3030556.00, '2025-09-26'),
(@tech_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'QQQ'), 2500.00, 900000.00, 972800.00, '2025-09-26'),
(@tech_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'VUG'), 3200.00, 850000.00, 954688.00, '2025-09-26'),
(@tech_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'AGG'), 8000.00, 820000.00, 819600.00, '2025-09-26'),
(@tech_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'VEA'), 4500.00, 195000.00, 203535.00, '2025-09-26'),
(@tech_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'AAPL'), 5500.00, 850000.00, 980925.00, '2025-09-26'),
(@tech_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'MSFT'), 2800.00, 880000.00, 935536.00, '2025-09-26'),
(@tech_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'GOOGL'), 4200.00, 520000.00, 565614.00, '2025-09-26'),
(@tech_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'NVDA'), 850.00, 350000.00, 388263.00, '2025-09-26');

-- =====================================================
-- INSERT CASH TREND DATA (Cash Management)
-- =====================================================

-- International Family Cash Trends (6 months)
INSERT INTO CashTrendData (HouseholdID, AsOfDate, TotalCashBalance, CheckingBalance, SavingsBalance, MoneyMarketBalance, CDBalance) VALUES
(@intl_household, '2025-09-26', 3500000.00, 1500000.00, 2000000.00, 0.00, 0.00),
(@intl_household, '2025-08-26', 3420000.00, 1450000.00, 1970000.00, 0.00, 0.00),
(@intl_household, '2025-07-26', 3380000.00, 1480000.00, 1900000.00, 0.00, 0.00),
(@intl_household, '2025-06-26', 3290000.00, 1390000.00, 1900000.00, 0.00, 0.00),
(@intl_household, '2025-05-26', 3250000.00, 1350000.00, 1900000.00, 0.00, 0.00),
(@intl_household, '2025-04-26', 3180000.00, 1280000.00, 1900000.00, 0.00, 0.00);

-- Young Professionals Cash Trends
INSERT INTO CashTrendData (HouseholdID, AsOfDate, TotalCashBalance, CheckingBalance, SavingsBalance, MoneyMarketBalance, CDBalance) VALUES
(@young_household, '2025-09-26', 95000.00, 45000.00, 50000.00, 0.00, 0.00),
(@young_household, '2025-08-26', 88000.00, 38000.00, 50000.00, 0.00, 0.00),
(@young_household, '2025-07-26', 82000.00, 32000.00, 50000.00, 0.00, 0.00),
(@young_household, '2025-06-26', 76000.00, 26000.00, 50000.00, 0.00, 0.00),
(@young_household, '2025-05-26', 71000.00, 21000.00, 50000.00, 0.00, 0.00),
(@young_household, '2025-04-26', 65000.00, 15000.00, 50000.00, 0.00, 0.00);

-- Tech Executive Cash Trends
INSERT INTO CashTrendData (HouseholdID, AsOfDate, TotalCashBalance, CheckingBalance, SavingsBalance, MoneyMarketBalance, CDBalance) VALUES
(@tech_household, '2025-09-26', 890000.00, 340000.00, 0.00, 550000.00, 0.00),
(@tech_household, '2025-08-26', 845000.00, 295000.00, 0.00, 550000.00, 0.00),
(@tech_household, '2025-07-26', 820000.00, 270000.00, 0.00, 550000.00, 0.00),
(@tech_household, '2025-06-26', 795000.00, 245000.00, 0.00, 550000.00, 0.00),
(@tech_household, '2025-05-26', 770000.00, 220000.00, 0.00, 550000.00, 0.00),
(@tech_household, '2025-04-26', 745000.00, 195000.00, 0.00, 550000.00, 0.00);

-- =====================================================
-- INSERT ACTIVITIES (Planning Tab)
-- =====================================================

INSERT INTO Activities (HouseholdID, ActivityTypeID, Title, Description, Priority, Status, Author, DueDate, Tags) VALUES
-- International Family Activities
(@intl_household, (SELECT ActivityTypeID FROM ActivityTypes WHERE TypeName = 'Portfolio Review'), 'Q3 Portfolio Rebalancing', 'Review asset allocation and rebalance portfolio based on market performance', 'high', 'pending', 'Michael Chen', '2025-10-15T10:00:00', '["portfolio", "rebalancing", "q3"]'),
(@intl_household, (SELECT ActivityTypeID FROM ActivityTypes WHERE TypeName = 'Tax Planning'), '2025 Tax Planning Review', 'Review tax strategies for year-end planning and harvesting opportunities', 'high', 'scheduled', 'Michael Chen', '2025-11-01T14:00:00', '["tax", "planning", "2025"]'),
(@intl_household, (SELECT ActivityTypeID FROM ActivityTypes WHERE TypeName = 'RMD Distribution'), '2025 RMD Distribution', 'Process required minimum distribution for retirement accounts', 'high', 'completed', 'Michael Chen', '2025-09-15T09:00:00', '["rmd", "distribution", "retirement"]'),
(@intl_household, (SELECT ActivityTypeID FROM ActivityTypes WHERE TypeName = 'Client Meeting'), 'Annual Review Meeting', 'Comprehensive annual review of financial goals and strategy', 'high', 'scheduled', 'Michael Chen', '2025-12-15T15:00:00', '["annual", "review", "meeting"]'),

-- Young Professionals Activities
(@young_household, (SELECT ActivityTypeID FROM ActivityTypes WHERE TypeName = 'Portfolio Review'), 'Initial Portfolio Setup', 'Set up diversified investment portfolio for long-term growth', 'medium', 'completed', 'Emily Lee', '2025-08-30T11:00:00', '["portfolio", "setup", "growth"]'),
(@young_household, (SELECT ActivityTypeID FROM ActivityTypes WHERE TypeName = 'Risk Assessment'), 'Risk Tolerance Assessment', 'Complete detailed risk tolerance questionnaire and analysis', 'medium', 'completed', 'Emily Lee', '2025-08-20T10:00:00', '["risk", "assessment", "questionnaire"]'),
(@young_household, (SELECT ActivityTypeID FROM ActivityTypes WHERE TypeName = 'Insurance Review'), 'Life Insurance Review', 'Review current life insurance coverage and recommend improvements', 'medium', 'pending', 'Emily Lee', '2025-10-30T13:00:00', '["insurance", "life", "coverage"]'),
(@young_household, (SELECT ActivityTypeID FROM ActivityTypes WHERE TypeName = 'Client Meeting'), 'Quarterly Check-in', 'Review portfolio performance and adjust contributions', 'low', 'scheduled', 'Emily Lee', '2025-10-05T16:00:00', '["quarterly", "checkin", "performance"]'),

-- Tech Executive Activities
(@tech_household, (SELECT ActivityTypeID FROM ActivityTypes WHERE TypeName = 'Portfolio Review'), 'Stock Option Strategy', 'Develop tax-efficient strategy for exercising stock options', 'high', 'pending', 'Sarah Martinez', '2025-10-01T09:00:00', '["stock", "options", "strategy"]'),
(@tech_household, (SELECT ActivityTypeID FROM ActivityTypes WHERE TypeName = 'Tax Planning'), 'RSU Tax Planning', 'Plan for restricted stock unit vesting and tax implications', 'high', 'scheduled', 'Sarah Martinez', '2025-11-15T10:00:00', '["rsu", "tax", "planning"]'),
(@tech_household, (SELECT ActivityTypeID FROM ActivityTypes WHERE TypeName = 'Estate Planning'), 'Estate Plan Update', 'Update estate planning documents to reflect increased net worth', 'medium', 'pending', 'Sarah Martinez', '2025-12-01T14:00:00', '["estate", "planning", "update"]'),
(@tech_household, (SELECT ActivityTypeID FROM ActivityTypes WHERE TypeName = 'Cash Management'), 'Cash Management Strategy', 'Optimize cash allocation across various account types', 'medium', 'completed', 'Sarah Martinez', '2025-09-10T11:00:00', '["cash", "management", "optimization"]');

-- =====================================================
-- INSERT RMDs
-- =====================================================

DECLARE @ira_account INT = (SELECT AccountID FROM Accounts WHERE AccountCode = 'intl-fam-ira-001');
DECLARE @roth_account INT = (SELECT AccountID FROM Accounts WHERE AccountCode = 'tech-exec-roth-001');

INSERT INTO RMDs (HouseholdID, AccountID, TaxYear, RequiredAmount, CompletedAmount, DueDate, Status) VALUES
(@intl_household, @ira_account, 2025, 285000.00, 285000.00, '2025-12-31', 'completed'),
(@intl_household, @ira_account, 2024, 275000.00, 275000.00, '2024-12-31', 'completed'),
(@tech_household, @roth_account, 2025, 125000.00, 0.00, '2025-12-31', 'pending');

-- =====================================================
-- INSERT BENEFICIARIES
-- =====================================================

DECLARE @intl_savings INT = (SELECT AccountID FROM Accounts WHERE AccountCode = 'intl-fam-savings-001');
DECLARE @young_invest INT = (SELECT AccountID FROM Accounts WHERE AccountCode = 'young-prof-invest-001');
DECLARE @young_savings INT = (SELECT AccountID FROM Accounts WHERE AccountCode = 'young-prof-savings-001');
DECLARE @tech_checking INT = (SELECT AccountID FROM Accounts WHERE AccountCode = 'tech-exec-checking-001');

INSERT INTO Beneficiaries (AccountID, BeneficiaryType, Name, Relationship, Percentage, LastReviewed, Status) VALUES
-- International Family beneficiaries
(@intl_investment, 'primary', 'Priya Singh', 'Spouse', 100.00, '2025-01-15', 'complete'),
(@intl_savings, 'primary', 'Priya Singh', 'Spouse', 50.00, '2025-01-15', 'complete'),
(@intl_savings, 'primary', 'Arjun Singh Jr.', 'Child', 25.00, '2025-01-15', 'complete'),
(@intl_savings, 'primary', 'Meera Singh', 'Child', 25.00, '2025-01-15', 'complete'),

-- Young Professionals beneficiaries
(@young_invest, 'primary', 'Jordan Kim', 'Partner', 100.00, '2025-08-15', 'complete'),
(@young_savings, 'primary', 'Jordan Kim', 'Partner', 100.00, '2025-08-15', 'complete'),

-- Tech Executive beneficiaries
(@tech_investment, 'primary', 'Lisa White', 'Spouse', 75.00, '2024-12-01', 'complete'),
(@tech_investment, 'primary', 'Kevin White Jr.', 'Child', 25.00, '2024-12-01', 'complete'),
(@tech_checking, 'primary', 'Lisa White', 'Spouse', 100.00, '2024-12-01', 'complete');

-- =====================================================
-- INSERT PERFORMANCE DATA (12 months for all major households)
-- =====================================================

DECLARE @current_date DATE = '2025-09-26';
DECLARE @i INT = 0;

-- International Family Performance (12 months)
WHILE @i < 12
BEGIN
    INSERT INTO PerformanceData (HouseholdID, AsOfDate, PortfolioValue, BenchmarkValue, TotalReturn, BenchmarkReturn) VALUES
    (@intl_household, 
     DATEADD(MONTH, -@i, @current_date),
     25000000 - (@i * 50000) + ((@i % 3) * 200000),
     24500000 - (@i * 45000) + ((@i % 3) * 180000),
     8.3 - (@i * 0.1) + ((@i % 2) * 0.3),
     7.8 - (@i * 0.08) + ((@i % 2) * 0.25));
    
    SET @i = @i + 1;
END;

-- Young Professionals Performance
SET @i = 0;
WHILE @i < 12
BEGIN
    INSERT INTO PerformanceData (HouseholdID, AsOfDate, PortfolioValue, BenchmarkValue, TotalReturn, BenchmarkReturn) VALUES
    (@young_household, 
     DATEADD(MONTH, -@i, @current_date),
     580000 - (@i * 8000) + ((@i % 4) * 15000),
     565000 - (@i * 7500) + ((@i % 4) * 12000),
     18.7 - (@i * 0.4) + ((@i % 3) * 1.2),
     16.2 - (@i * 0.35) + ((@i % 3) * 1.0));
    
    SET @i = @i + 1;
END;

-- Tech Executive Performance
SET @i = 0;
WHILE @i < 12
BEGIN
    INSERT INTO PerformanceData (HouseholdID, AsOfDate, PortfolioValue, BenchmarkValue, TotalReturn, BenchmarkReturn) VALUES
    (@tech_household, 
     DATEADD(MONTH, -@i, @current_date),
     6800000 - (@i * 25000) + ((@i % 3) * 80000),
     6500000 - (@i * 22000) + ((@i % 3) * 70000),
     14.6 - (@i * 0.2) + ((@i % 2) * 0.5),
     12.1 - (@i * 0.18) + ((@i % 2) * 0.4));
    
    SET @i = @i + 1;
END;

-- Johnson Family Trust Performance
SET @i = 0;
WHILE @i < 12
BEGIN
    INSERT INTO PerformanceData (HouseholdID, AsOfDate, PortfolioValue, BenchmarkValue, TotalReturn, BenchmarkReturn) VALUES
    (@johnson_household, 
     DATEADD(MONTH, -@i, @current_date),
     2850000 - (@i * 15000) + ((@i % 4) * 45000),
     2750000 - (@i * 14000) + ((@i % 4) * 40000),
     8.7 - (@i * 0.15) + ((@i % 3) * 0.4),
     7.8 - (@i * 0.12) + ((@i % 3) * 0.3));
    
    SET @i = @i + 1;
END;

-- =====================================================
-- SUMMARY AND VERIFICATION
-- =====================================================

PRINT 'WealthOps Database Created Successfully!';
PRINT '';
PRINT 'Database Summary:';
PRINT '================';

SELECT 'Households Created: ' + CAST(COUNT(*) AS VARCHAR(10)) FROM Households;
SELECT 'Accounts Created: ' + CAST(COUNT(*) AS VARCHAR(10)) FROM Accounts;  
SELECT 'Securities Available: ' + CAST(COUNT(*) AS VARCHAR(10)) FROM Securities;
SELECT 'Positions Created: ' + CAST(COUNT(*) AS VARCHAR(10)) FROM Positions;
SELECT 'Cash Trend Records: ' + CAST(COUNT(*) AS VARCHAR(10)) FROM CashTrendData;
SELECT 'Activities Created: ' + CAST(COUNT(*) AS VARCHAR(10)) FROM Activities;
SELECT 'Performance Records: ' + CAST(COUNT(*) AS VARCHAR(10)) FROM PerformanceData;
SELECT 'RMD Records: ' + CAST(COUNT(*) AS VARCHAR(10)) FROM RMDs;
SELECT 'Beneficiary Records: ' + CAST(COUNT(*) AS VARCHAR(10)) FROM Beneficiaries;

PRINT '';
PRINT 'All frontend tabs now have complete data:';
PRINT '✓ Households list (21 households)';
PRINT '✓ Asset Allocation tab (portfolio positions)';  
PRINT '✓ Cash Management tab (trend data)';
PRINT '✓ Activity/Planning tab (activities & RMDs)';
PRINT '✓ Performance data (12 months for major households)';
PRINT '';
PRINT 'Database is ready for use!';