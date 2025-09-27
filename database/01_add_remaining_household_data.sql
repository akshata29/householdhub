-- Add accounts and data for remaining households
-- This script adds accounts, positions, and other data for households 5-21
-- Run after the main database creation script

USE householdhub;
GO

-- Get household IDs for remaining households
DECLARE @chen_household INT = (SELECT HouseholdID FROM Households WHERE HouseholdCode = 'chen-enterprises');
DECLARE @wilson_household INT = (SELECT HouseholdID FROM Households WHERE HouseholdCode = 'wilson-retirement');
DECLARE @garcia_household INT = (SELECT HouseholdID FROM Households WHERE HouseholdCode = 'garcia-foundation');
DECLARE @thompson_household INT = (SELECT HouseholdID FROM Households WHERE HouseholdCode = 'thompson-individual');
DECLARE @retired_household INT = (SELECT HouseholdID FROM Households WHERE HouseholdCode = 'retired-educators');
DECLARE @startup_household INT = (SELECT HouseholdID FROM Households WHERE HouseholdCode = 'startup-founder');
DECLARE @multigenerational_household INT = (SELECT HouseholdID FROM Households WHERE HouseholdCode = 'multigenerational-wealth');
DECLARE @divorced_household INT = (SELECT HouseholdID FROM Households WHERE HouseholdCode = 'divorced-single-parent');
DECLARE @realestate_household INT = (SELECT HouseholdID FROM Households WHERE HouseholdCode = 'real-estate-investors');
DECLARE @inheritance_household INT = (SELECT HouseholdID FROM Households WHERE HouseholdCode = 'young-inheritance');
DECLARE @energy_household INT = (SELECT HouseholdID FROM Households WHERE HouseholdCode = 'energy-executive');
DECLARE @healthcare_household INT = (SELECT HouseholdID FROM Households WHERE HouseholdCode = 'healthcare-professionals');
DECLARE @military_household INT = (SELECT HouseholdID FROM Households WHERE HouseholdCode = 'military-retirees');
DECLARE @entertainment_household INT = (SELECT HouseholdID FROM Households WHERE HouseholdCode = 'entertainment-industry');
DECLARE @smallbiz_household INT = (SELECT HouseholdID FROM Households WHERE HouseholdCode = 'small-business-owners');
DECLARE @legal_household INT = (SELECT HouseholdID FROM Households WHERE HouseholdCode = 'legal-professionals');
DECLARE @pharma_household INT = (SELECT HouseholdID FROM Households WHERE HouseholdCode = 'pharmaceutical-executives');

-- Chen Enterprises Accounts
INSERT INTO Accounts (AccountCode, HouseholdID, AccountTypeID, InstitutionID, Name, Balance, APY, OpenDate, Status) VALUES
('chen-checking-001', @chen_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Checking'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'CHAS'),
 'Business Checking Account', 285000.00, 0.0150, '2018-01-10', 'Active'),

('chen-invest-001', @chen_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Brokerage'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'SCHW'),
 'Corporate Investment Account', 3200000.00, 0.0000, '2018-01-10', 'Active');

-- Wilson Retirement Accounts
INSERT INTO Accounts (AccountCode, HouseholdID, AccountTypeID, InstitutionID, Name, Balance, APY, OpenDate, Status) VALUES
('wilson-checking-001', @wilson_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Checking'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'WFC'),
 'Retirement Checking Account', 45000.00, 0.0125, '2021-09-05', 'Active'),

('wilson-savings-001', @wilson_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Savings'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'WFC'),
 'Emergency Fund', 125000.00, 0.0400, '2021-09-05', 'Active'),

('wilson-ira-001', @wilson_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Traditional IRA'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'FID'),
 'Retirement Portfolio', 850000.00, 0.0000, '2021-09-05', 'Active');

-- Garcia Foundation Accounts  
INSERT INTO Accounts (AccountCode, HouseholdID, AccountTypeID, InstitutionID, Name, Balance, APY, OpenDate, Status) VALUES
('garcia-checking-001', @garcia_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Checking'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'BOA'),
 'Foundation Operating Account', 195000.00, 0.0175, '2017-11-30', 'Active'),

('garcia-invest-001', @garcia_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Brokerage'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'VG'),
 'Endowment Portfolio', 4500000.00, 0.0000, '2017-11-30', 'Active');

-- Thompson Individual Accounts
INSERT INTO Accounts (AccountCode, HouseholdID, AccountTypeID, InstitutionID, Name, Balance, APY, OpenDate, Status) VALUES
('thompson-checking-001', @thompson_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Checking'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'CHAS'),
 'Personal Checking Account', 75000.00, 0.0150, '2022-04-18', 'Active'),

('thompson-savings-001', @thompson_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Savings'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'CHAS'),
 'High-Yield Savings', 85000.00, 0.0450, '2022-04-18', 'Active'),

('thompson-invest-001', @thompson_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Brokerage'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'TD'),
 'Growth Portfolio', 1800000.00, 0.0000, '2022-04-18', 'Active');

-- Retired Educators Accounts
INSERT INTO Accounts (AccountCode, HouseholdID, AccountTypeID, InstitutionID, Name, Balance, APY, OpenDate, Status) VALUES
('retired-checking-001', @retired_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Checking'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'WFC'),
 'Joint Checking Account', 25000.00, 0.0100, '2020-02-14', 'Active'),

('retired-savings-001', @retired_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Savings'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'WFC'),
 'Emergency Fund', 65000.00, 0.0350, '2020-02-14', 'Active'),

('retired-cd-001', @retired_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'CD'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'WFC'),
 'Conservative CD Ladder', 450000.00, 0.0525, '2020-02-14', 'Active');

-- Startup Founder Accounts
INSERT INTO Accounts (AccountCode, HouseholdID, AccountTypeID, InstitutionID, Name, Balance, APY, OpenDate, Status) VALUES
('startup-checking-001', @startup_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Checking'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'SCHW'),
 'Business Checking Account', 185000.00, 0.0175, '2023-06-08', 'Active'),

('startup-invest-001', @startup_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Brokerage'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'SCHW'),
 'Equity Investment Portfolio', 5200000.00, 0.0000, '2023-06-08', 'Active');

-- Multigenerational Wealth Accounts  
INSERT INTO Accounts (AccountCode, HouseholdID, AccountTypeID, InstitutionID, Name, Balance, APY, OpenDate, Status) VALUES
('multi-checking-001', @multigenerational_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Checking'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'CHAS'),
 'Trust Operating Account', 425000.00, 0.0200, '2015-10-01', 'Active'),

('multi-invest-001', @multigenerational_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Trust Account'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'SCHW'),
 'Legacy Investment Portfolio', 15800000.00, 0.0000, '2015-10-01', 'Active');

-- Divorced Single Parent Accounts
INSERT INTO Accounts (AccountCode, HouseholdID, AccountTypeID, InstitutionID, Name, Balance, APY, OpenDate, Status) VALUES
('divorced-checking-001', @divorced_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Checking'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'BOA'),
 'Personal Checking Account', 32000.00, 0.0125, '2022-01-30', 'Active'),

('divorced-savings-001', @divorced_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Savings'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'BOA'),
 'Emergency Savings', 48000.00, 0.0400, '2022-01-30', 'Active'),

('divorced-529-001', @divorced_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = '529 Plan'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'VG'),
 'Children Education Fund', 125000.00, 0.0000, '2022-01-30', 'Active');

-- Real Estate Investors Accounts
INSERT INTO Accounts (AccountCode, HouseholdID, AccountTypeID, InstitutionID, Name, Balance, APY, OpenDate, Status) VALUES
('realestate-checking-001', @realestate_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Checking'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'WFC'),
 'Property Management Checking', 145000.00, 0.0150, '2019-08-12', 'Active'),

('realestate-invest-001', @realestate_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Brokerage'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'TD'),
 'Real Estate Investment Portfolio', 2800000.00, 0.0000, '2019-08-12', 'Active');

-- Young Inheritance Accounts
INSERT INTO Accounts (AccountCode, HouseholdID, AccountTypeID, InstitutionID, Name, Balance, APY, OpenDate, Status) VALUES
('inheritance-checking-001', @inheritance_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Checking'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'CHAS'),
 'Trust Distribution Account', 85000.00, 0.0150, '2024-03-01', 'Active'),

('inheritance-invest-001', @inheritance_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Trust Account'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'VG'),
 'Conservative Growth Portfolio', 1250000.00, 0.0000, '2024-03-01', 'Active');

-- Energy Executive Accounts
INSERT INTO Accounts (AccountCode, HouseholdID, AccountTypeID, InstitutionID, Name, Balance, APY, OpenDate, Status) VALUES
('energy-checking-001', @energy_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Checking'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'CHAS'),
 'Executive Checking Account', 235000.00, 0.0175, '2017-12-05', 'Active'),

('energy-mm-001', @energy_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Money Market'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'CHAS'),
 'Money Market Account', 325000.00, 0.0475, '2017-12-05', 'Active'),

('energy-invest-001', @energy_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Brokerage'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'SCHW'),
 'Energy Sector Portfolio', 4200000.00, 0.0000, '2017-12-05', 'Active');

-- Healthcare Professionals Accounts
INSERT INTO Accounts (AccountCode, HouseholdID, AccountTypeID, InstitutionID, Name, Balance, APY, OpenDate, Status) VALUES
('healthcare-checking-001', @healthcare_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Checking'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'BOA'),
 'Medical Practice Checking', 125000.00, 0.0150, '2019-03-22', 'Active'),

('healthcare-savings-001', @healthcare_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Savings'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'BOA'),
 'Emergency Fund', 95000.00, 0.0425, '2019-03-22', 'Active'),

('healthcare-invest-001', @healthcare_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Brokerage'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'FID'),
 'Healthcare Investment Portfolio', 1850000.00, 0.0000, '2019-03-22', 'Active');

-- Military Retirees Accounts  
INSERT INTO Accounts (AccountCode, HouseholdID, AccountTypeID, InstitutionID, Name, Balance, APY, OpenDate, Status) VALUES
('military-checking-001', @military_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Checking'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'WFC'),
 'Military Retirement Checking', 42000.00, 0.0125, '2021-06-01', 'Active'),

('military-savings-001', @military_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Savings'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'WFC'),
 'High-Yield Savings', 75000.00, 0.0400, '2021-06-01', 'Active'),

('military-tsp-001', @military_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = '401k'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'FID'),
 'TSP Rollover Account', 650000.00, 0.0000, '2021-06-01', 'Active');

-- Entertainment Industry Accounts
INSERT INTO Accounts (AccountCode, HouseholdID, AccountTypeID, InstitutionID, Name, Balance, APY, OpenDate, Status) VALUES
('entertainment-checking-001', @entertainment_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Checking'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'CHAS'),
 'Production Company Checking', 385000.00, 0.0175, '2020-11-18', 'Active'),

('entertainment-invest-001', @entertainment_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Brokerage'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'TD'),
 'Entertainment Portfolio', 7200000.00, 0.0000, '2020-11-18', 'Active');

-- Small Business Owners Accounts
INSERT INTO Accounts (AccountCode, HouseholdID, AccountTypeID, InstitutionID, Name, Balance, APY, OpenDate, Status) VALUES
('smallbiz-checking-001', @smallbiz_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Checking'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'WFC'),
 'Business Checking Account', 95000.00, 0.0150, '2018-09-30', 'Active'),

('smallbiz-savings-001', @smallbiz_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Savings'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'WFC'),
 'Business Emergency Fund', 85000.00, 0.0400, '2018-09-30', 'Active'),

('smallbiz-invest-001', @smallbiz_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Brokerage'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'SCHW'),
 'Business Investment Portfolio', 1200000.00, 0.0000, '2018-09-30', 'Active');

-- Legal Professionals Accounts
INSERT INTO Accounts (AccountCode, HouseholdID, AccountTypeID, InstitutionID, Name, Balance, APY, OpenDate, Status) VALUES
('legal-checking-001', @legal_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Checking'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'CHAS'),
 'Law Firm Operating Account', 165000.00, 0.0175, '2019-05-14', 'Active'),

('legal-mm-001', @legal_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Money Market'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'CHAS'),
 'Client Trust Money Market', 125000.00, 0.0450, '2019-05-14', 'Active'),

('legal-invest-001', @legal_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Brokerage'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'VG'),
 'Conservative Investment Portfolio', 2100000.00, 0.0000, '2019-05-14', 'Active');

-- Pharmaceutical Executives Accounts
INSERT INTO Accounts (AccountCode, HouseholdID, AccountTypeID, InstitutionID, Name, Balance, APY, OpenDate, Status) VALUES
('pharma-checking-001', @pharma_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Checking'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'SCHW'),
 'Executive Checking Account', 315000.00, 0.0200, '2016-08-25', 'Active'),

('pharma-mm-001', @pharma_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Money Market'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'SCHW'),
 'High-Yield Money Market', 485000.00, 0.0500, '2016-08-25', 'Active'),

('pharma-invest-001', @pharma_household,
 (SELECT AccountTypeID FROM AccountTypes WHERE TypeName = 'Brokerage'),
 (SELECT InstitutionID FROM Institutions WHERE InstitutionCode = 'FID'),
 'Pharma Executive Portfolio', 9500000.00, 0.0000, '2016-08-25', 'Active');

-- Add some positions for major investment accounts
DECLARE @chen_investment INT = (SELECT AccountID FROM Accounts WHERE AccountCode = 'chen-invest-001');
DECLARE @garcia_investment INT = (SELECT AccountID FROM Accounts WHERE AccountCode = 'garcia-invest-001');
DECLARE @thompson_investment INT = (SELECT AccountID FROM Accounts WHERE AccountCode = 'thompson-invest-001');
DECLARE @startup_investment INT = (SELECT AccountID FROM Accounts WHERE AccountCode = 'startup-invest-001');
DECLARE @multi_investment INT = (SELECT AccountID FROM Accounts WHERE AccountCode = 'multi-invest-001');
DECLARE @realestate_investment INT = (SELECT AccountID FROM Accounts WHERE AccountCode = 'realestate-invest-001');
DECLARE @energy_investment INT = (SELECT AccountID FROM Accounts WHERE AccountCode = 'energy-invest-001');
DECLARE @healthcare_investment INT = (SELECT AccountID FROM Accounts WHERE AccountCode = 'healthcare-invest-001');
DECLARE @entertainment_investment INT = (SELECT AccountID FROM Accounts WHERE AccountCode = 'entertainment-invest-001');
DECLARE @legal_investment INT = (SELECT AccountID FROM Accounts WHERE AccountCode = 'legal-invest-001');
DECLARE @pharma_investment INT = (SELECT AccountID FROM Accounts WHERE AccountCode = 'pharma-invest-001');

-- Chen Enterprises Portfolio (Conservative corporate)
INSERT INTO Positions (AccountID, SecurityID, Quantity, CostBasis, MarketValue, AsOfDate) VALUES
(@chen_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'SPY'), 2800.00, 1150000.00, 1247876.00, '2025-09-26'),
(@chen_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'AGG'), 18000.00, 1800000.00, 1844100.00, '2025-09-26'),
(@chen_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'VTI'), 450.00, 95000.00, 105700.05, '2025-09-26');

-- Garcia Foundation Portfolio (Endowment style)
INSERT INTO Positions (AccountID, SecurityID, Quantity, CostBasis, MarketValue, AsOfDate) VALUES
(@garcia_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'VTI'), 8500.00, 1850000.00, 1996556.50, '2025-09-26'),
(@garcia_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'VEA'), 35000.00, 1450000.00, 1583050.00, '2025-09-26'),
(@garcia_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'AGG'), 10000.00, 985000.00, 1024500.00, '2025-09-26');

-- Thompson Individual Portfolio (Aggressive growth)
INSERT INTO Positions (AccountID, SecurityID, Quantity, CostBasis, MarketValue, AsOfDate) VALUES
(@thompson_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'QQQ'), 2200.00, 780000.00, 856064.00, '2025-09-26'),
(@thompson_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'VUG'), 1850.00, 485000.00, 551929.00, '2025-09-26'),
(@thompson_investment, (SELECT SecurityID FROM Securities WHERE Symbol = 'NVDA'), 850.00, 325000.00, 388263.00, '2025-09-26');

-- Add performance data for all households
DECLARE @current_date DATE = '2025-09-26';
DECLARE @i INT = 0;

-- Add performance data for each household (3 months of recent data)
WHILE @i < 3
BEGIN
    INSERT INTO PerformanceData (HouseholdID, AsOfDate, PortfolioValue, BenchmarkValue, TotalReturn, BenchmarkReturn) VALUES
    -- Chen Enterprises
    (@chen_household, DATEADD(MONTH, -@i, @current_date), 3485000 - (@i * 15000), 3450000 - (@i * 12000), 12.4 - (@i * 0.2), 11.8 - (@i * 0.15)),
    -- Wilson Retirement
    (@wilson_household, DATEADD(MONTH, -@i, @current_date), 1020000 - (@i * 8000), 995000 - (@i * 7500), 6.8 - (@i * 0.1), 6.2 - (@i * 0.08)),
    -- Garcia Foundation
    (@garcia_household, DATEADD(MONTH, -@i, @current_date), 4695000 - (@i * 25000), 4625000 - (@i * 22000), 9.5 - (@i * 0.15), 8.9 - (@i * 0.12)),
    -- Thompson Individual
    (@thompson_household, DATEADD(MONTH, -@i, @current_date), 1960000 - (@i * 12000), 1895000 - (@i * 10000), 22.3 - (@i * 0.3), 19.8 - (@i * 0.25)),
    -- Retired Educators
    (@retired_household, DATEADD(MONTH, -@i, @current_date), 540000 - (@i * 5000), 525000 - (@i * 4500), 4.2 - (@i * 0.05), 3.8 - (@i * 0.04)),
    -- Startup Founder
    (@startup_household, DATEADD(MONTH, -@i, @current_date), 5385000 - (@i * 35000), 5250000 - (@i * 32000), 28.5 - (@i * 0.4), 25.2 - (@i * 0.35)),
    -- Multigenerational Wealth
    (@multigenerational_household, DATEADD(MONTH, -@i, @current_date), 16225000 - (@i * 45000), 15950000 - (@i * 42000), 10.8 - (@i * 0.18), 10.2 - (@i * 0.15)),
    -- Divorced Single Parent
    (@divorced_household, DATEADD(MONTH, -@i, @current_date), 205000 - (@i * 2000), 198000 - (@i * 1800), 15.2 - (@i * 0.25), 13.8 - (@i * 0.22)),
    -- Real Estate Investors
    (@realestate_household, DATEADD(MONTH, -@i, @current_date), 2945000 - (@i * 18000), 2875000 - (@i * 16000), 11.5 - (@i * 0.2), 10.9 - (@i * 0.18)),
    -- Young Inheritance
    (@inheritance_household, DATEADD(MONTH, -@i, @current_date), 1335000 - (@i * 8000), 1295000 - (@i * 7500), 7.2 - (@i * 0.12), 6.8 - (@i * 0.1)),
    -- Energy Executive
    (@energy_household, DATEADD(MONTH, -@i, @current_date), 4760000 - (@i * 25000), 4650000 - (@i * 22000), 13.8 - (@i * 0.22), 12.9 - (@i * 0.19)),
    -- Healthcare Professionals
    (@healthcare_household, DATEADD(MONTH, -@i, @current_date), 2070000 - (@i * 12000), 2025000 - (@i * 11000), 8.9 - (@i * 0.15), 8.3 - (@i * 0.12)),
    -- Military Retirees
    (@military_household, DATEADD(MONTH, -@i, @current_date), 767000 - (@i * 6000), 745000 - (@i * 5500), 5.8 - (@i * 0.08), 5.4 - (@i * 0.07)),
    -- Entertainment Industry
    (@entertainment_household, DATEADD(MONTH, -@i, @current_date), 7585000 - (@i * 38000), 7350000 - (@i * 35000), 19.2 - (@i * 0.28), 17.5 - (@i * 0.25)),
    -- Small Business Owners
    (@smallbiz_household, DATEADD(MONTH, -@i, @current_date), 1380000 - (@i * 8000), 1345000 - (@i * 7500), 9.8 - (@i * 0.16), 9.2 - (@i * 0.14)),
    -- Legal Professionals
    (@legal_household, DATEADD(MONTH, -@i, @current_date), 2390000 - (@i * 15000), 2325000 - (@i * 14000), 7.5 - (@i * 0.12), 7.1 - (@i * 0.1)),
    -- Pharmaceutical Executives
    (@pharma_household, DATEADD(MONTH, -@i, @current_date), 10300000 - (@i * 45000), 10050000 - (@i * 42000), 16.8 - (@i * 0.25), 15.2 - (@i * 0.22));
    
    SET @i = @i + 1;
END;

-- Add cash trend data for major households
INSERT INTO CashTrendData (HouseholdID, AsOfDate, TotalCashBalance, CheckingBalance, SavingsBalance, MoneyMarketBalance, CDBalance) VALUES
-- Chen Enterprises
(@chen_household, '2025-09-26', 285000.00, 285000.00, 0.00, 0.00, 0.00),
(@chen_household, '2025-08-26', 275000.00, 275000.00, 0.00, 0.00, 0.00),
(@chen_household, '2025-07-26', 265000.00, 265000.00, 0.00, 0.00, 0.00),

-- Wilson Retirement  
(@wilson_household, '2025-09-26', 170000.00, 45000.00, 125000.00, 0.00, 0.00),
(@wilson_household, '2025-08-26', 165000.00, 42000.00, 123000.00, 0.00, 0.00),
(@wilson_household, '2025-07-26', 160000.00, 38000.00, 122000.00, 0.00, 0.00),

-- Garcia Foundation
(@garcia_household, '2025-09-26', 195000.00, 195000.00, 0.00, 0.00, 0.00),
(@garcia_household, '2025-08-26', 185000.00, 185000.00, 0.00, 0.00, 0.00),
(@garcia_household, '2025-07-26', 175000.00, 175000.00, 0.00, 0.00, 0.00),

-- Pharmaceutical Executives
(@pharma_household, '2025-09-26', 800000.00, 315000.00, 0.00, 485000.00, 0.00),
(@pharma_household, '2025-08-26', 785000.00, 305000.00, 0.00, 480000.00, 0.00),
(@pharma_household, '2025-07-26', 775000.00, 295000.00, 0.00, 480000.00, 0.00);

PRINT 'Additional household data added successfully!';
PRINT 'All 21 households now have complete account and performance data.';