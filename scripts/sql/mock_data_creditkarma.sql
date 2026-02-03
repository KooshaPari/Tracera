-- CreditPulse - Personal Finance Platform
-- Comprehensive mock data for credit and personal finance management

DELETE FROM projects WHERE name = 'CreditPulse - Personal Finance Platform';

-- Insert Project with explicit ID
INSERT INTO projects (id, name, project_metadata, created_at, updated_at)
VALUES (
  'proj_creditpulse_001',
  'CreditPulse - Personal Finance Platform',
  '{"description": "A comprehensive financial platform for credit monitoring, debt management, loan comparison, tax filing, and identity theft protection"}',
  NOW(),
  NOW()
);

-- REQUIREMENTS (100+)
-- Req 1-10: Core Credit Monitoring
INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, owner, item_metadata, created_at, updated_at)
VALUES
('req_cp_001', 'proj_creditpulse_001', 'Real-time Credit Score Tracking', 'Monitor credit score changes across all three bureaus with daily updates', 'requirements', 'requirement', 'todo', 'critical', 'Sarah Chen', '{"category": "core", "complexity": "high"}', NOW(), NOW()),
('req_cp_002', 'proj_creditpulse_001', 'Credit Bureau Integration (Equifax)', 'Integrate with Equifax API to fetch credit reports and scores', 'requirements', 'requirement', 'todo', 'critical', 'Marcus Johnson', '{"category": "integration", "complexity": "high"}', NOW(), NOW()),
('req_cp_003', 'proj_creditpulse_001', 'Credit Bureau Integration (Experian)', 'Integrate with Experian API to fetch credit reports and scores', 'requirements', 'requirement', 'in_progress', 'critical', 'Priya Patel', '{"category": "integration", "complexity": "high"}', NOW(), NOW()),
('req_cp_004', 'proj_creditpulse_001', 'Credit Bureau Integration (TransUnion)', 'Integrate with TransUnion API to fetch credit reports and scores', 'requirements', 'requirement', 'in_progress', 'critical', 'James Wilson', '{"category": "integration", "complexity": "high"}', NOW(), NOW()),
('req_cp_005', 'proj_creditpulse_001', 'Credit Score History Visualization', 'Display credit score trends over 6, 12, and 24 months with charts', 'requirements', 'requirement', 'todo', 'high', 'Sarah Chen', '{"category": "ui", "complexity": "medium"}', NOW(), NOW()),
('req_cp_006', 'proj_creditpulse_001', 'Credit Factor Analysis', 'Break down credit score factors (payment history, utilization, etc.) with weights', 'requirements', 'requirement', 'todo', 'high', 'David Lee', '{"category": "analytics", "complexity": "medium"}', NOW(), NOW()),
('req_cp_007', 'proj_creditpulse_001', 'Score Comparison Across Bureaus', 'Compare credit scores from Equifax, Experian, and TransUnion side-by-side', 'requirements', 'requirement', 'done', 'high', 'Priya Patel', '{"category": "analytics", "complexity": "low"}', NOW(), NOW()),
('req_cp_008', 'proj_creditpulse_001', 'Credit Score Alerts', 'Send alerts when credit score drops below threshold or significant changes detected', 'requirements', 'requirement', 'in_progress', 'high', 'Marcus Johnson', '{"category": "notifications", "complexity": "medium"}', NOW(), NOW()),
('req_cp_009', 'proj_creditpulse_001', 'Credit Score Predictions', 'ML-based predictions for credit score changes based on user behavior', 'requirements', 'requirement', 'todo', 'high', 'Elena Rodriguez', '{"category": "ml", "complexity": "high"}', NOW(), NOW()),
('req_cp_010', 'proj_creditpulse_001', 'Historical Credit Data Archive', 'Store and archive historical credit data for long-term trend analysis', 'requirements', 'requirement', 'todo', 'medium', 'James Wilson', '{"category": "data", "complexity": "medium"}', NOW(), NOW());

-- Req 11-20: Account Management
INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, owner, item_metadata, created_at, updated_at)
VALUES
('req_cp_011', 'proj_creditpulse_001', 'Account Registration with Email Verification', 'Allow users to register with email and verify ownership', 'requirements', 'requirement', 'done', 'critical', 'Sarah Chen', '{"category": "auth", "complexity": "medium"}', NOW(), NOW()),
('req_cp_012', 'proj_creditpulse_001', 'Social Login Integration (Google)', 'Enable Google OAuth for quick account creation', 'requirements', 'requirement', 'done', 'high', 'Marcus Johnson', '{"category": "auth", "complexity": "low"}', NOW(), NOW()),
('req_cp_013', 'proj_creditpulse_001', 'Social Login Integration (Apple)', 'Enable Apple Sign-In for account creation', 'requirements', 'requirement', 'done', 'high', 'Priya Patel', '{"category": "auth", "complexity": "low"}', NOW(), NOW()),
('req_cp_014', 'proj_creditpulse_001', 'Multi-factor Authentication (2FA)', 'Support SMS and authenticator app-based 2FA', 'requirements', 'requirement', 'in_progress', 'critical', 'David Lee', '{"category": "security", "complexity": "high"}', NOW(), NOW()),
('req_cp_015', 'proj_creditpulse_001', 'Biometric Authentication (Face ID/Touch ID)', 'Support biometric login for mobile apps', 'requirements', 'requirement', 'todo', 'high', 'Elena Rodriguez', '{"category": "security", "complexity": "medium"}', NOW(), NOW()),
('req_cp_016', 'proj_creditpulse_001', 'Password Security Requirements', 'Enforce strong password requirements (length, complexity, etc.)', 'requirements', 'requirement', 'done', 'critical', 'James Wilson', '{"category": "security", "complexity": "low"}', NOW(), NOW()),
('req_cp_017', 'proj_creditpulse_001', 'Account Recovery Options', 'Allow account recovery via email, phone, or security questions', 'requirements', 'requirement', 'todo', 'high', 'Sarah Chen', '{"category": "auth", "complexity": "medium"}', NOW(), NOW()),
('req_cp_018', 'proj_creditpulse_001', 'Session Management and Timeout', 'Implement secure session management with configurable timeout', 'requirements', 'requirement', 'done', 'medium', 'Marcus Johnson', '{"category": "security", "complexity": "medium"}', NOW(), NOW()),
('req_cp_019', 'proj_creditpulse_001', 'Privacy Settings Management', 'Allow users to control data sharing and privacy preferences', 'requirements', 'requirement', 'in_progress', 'high', 'Priya Patel', '{"category": "privacy", "complexity": "medium"}', NOW(), NOW()),
('req_cp_020', 'proj_creditpulse_001', 'Account Deletion with Data Cleanup', 'Enable users to delete accounts and all associated data', 'requirements', 'requirement', 'todo', 'high', 'David Lee', '{"category": "privacy", "complexity": "high"}', NOW(), NOW());

-- Req 21-30: Identity Theft Protection
INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, owner, item_metadata, created_at, updated_at)
VALUES
('req_cp_021', 'proj_creditpulse_001', 'Dark Web Monitoring', 'Monitor dark web for exposed personal information', 'requirements', 'requirement', 'todo', 'critical', 'Elena Rodriguez', '{"category": "security", "complexity": "high"}', NOW(), NOW()),
('req_cp_022', 'proj_creditpulse_001', 'Credit Fraud Alerts', 'Alert users when suspicious activities detected on credit accounts', 'requirements', 'requirement', 'in_progress', 'critical', 'James Wilson', '{"category": "security", "complexity": "high"}', NOW(), NOW()),
('req_cp_023', 'proj_creditpulse_001', 'Identity Document Verification', 'Allow users to upload and verify government-issued IDs', 'requirements', 'requirement', 'todo', 'high', 'Sarah Chen', '{"category": "security", "complexity": "high"}', NOW(), NOW()),
('req_cp_024', 'proj_creditpulse_001', 'Address and Phone Monitoring', 'Monitor for changes to address and phone number across bureaus', 'requirements', 'requirement', 'in_progress', 'high', 'Marcus Johnson', '{"category": "security", "complexity": "medium"}', NOW(), NOW()),
('req_cp_025', 'proj_creditpulse_001', 'Credit Freeze Management', 'Help users place and manage credit freezes with all bureaus', 'requirements', 'requirement', 'todo', 'high', 'Priya Patel', '{"category": "security", "complexity": "high"}', NOW(), NOW()),
('req_cp_026', 'proj_creditpulse_001', 'Fraud Dispute Assistance', 'Guided workflow to dispute fraudulent accounts and inquiries', 'requirements', 'requirement', 'todo', 'high', 'David Lee', '{"category": "support", "complexity": "high"}', NOW(), NOW()),
('req_cp_027', 'proj_creditpulse_001', 'Suspicious Login Alerts', 'Alert users of login attempts from unusual locations/devices', 'requirements', 'requirement', 'in_progress', 'high', 'Elena Rodriguez', '{"category": "security", "complexity": "medium"}', NOW(), NOW()),
('req_cp_028', 'proj_creditpulse_001', 'Insurance Integration', 'Partner with identity theft insurance providers for coverage options', 'requirements', 'requirement', 'todo', 'medium', 'James Wilson', '{"category": "integration", "complexity": "medium"}', NOW(), NOW()),
('req_cp_029', 'proj_creditpulse_001', 'Fraud Report Generation', 'Generate FTC-compliant fraud reports for identity theft cases', 'requirements', 'requirement', 'todo', 'high', 'Sarah Chen', '{"category": "documents", "complexity": "high"}', NOW(), NOW()),
('req_cp_030', 'proj_creditpulse_001', 'Email Breach Monitoring', 'Monitor if user email addresses appear in known data breaches', 'requirements', 'requirement', 'todo', 'high', 'Marcus Johnson', '{"category": "security", "complexity": "medium"}', NOW(), NOW());

-- Req 31-40: Debt Management
INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, owner, item_metadata, created_at, updated_at)
VALUES
('req_cp_031', 'proj_creditpulse_001', 'Debt Account Aggregation', 'Automatically aggregate and categorize all user debt accounts', 'requirements', 'requirement', 'in_progress', 'critical', 'Priya Patel', '{"category": "core", "complexity": "high"}', NOW(), NOW()),
('req_cp_032', 'proj_creditpulse_001', 'Credit Card Debt Tracking', 'Track credit cards with balances, limits, interest rates', 'requirements', 'requirement', 'done', 'high', 'David Lee', '{"category": "tracking", "complexity": "medium"}', NOW(), NOW()),
('req_cp_033', 'proj_creditpulse_001', 'Student Loan Tracking', 'Monitor federal and private student loans with repayment schedules', 'requirements', 'requirement', 'in_progress', 'high', 'Elena Rodriguez', '{"category": "tracking", "complexity": "medium"}', NOW(), NOW()),
('req_cp_034', 'proj_creditpulse_001', 'Mortgage Tracking', 'Track mortgage details including principal, interest, escrow', 'requirements', 'requirement', 'in_progress', 'high', 'James Wilson', '{"category": "tracking", "complexity": "medium"}', NOW(), NOW()),
('req_cp_035', 'proj_creditpulse_001', 'Auto Loan Tracking', 'Monitor auto loans with payment schedules and equity calculations', 'requirements', 'requirement', 'done', 'medium', 'Sarah Chen', '{"category": "tracking", "complexity": "low"}', NOW(), NOW()),
('req_cp_036', 'proj_creditpulse_001', 'Personal Loan Tracking', 'Track unsecured personal loans from various lenders', 'requirements', 'requirement', 'todo', 'medium', 'Marcus Johnson', '{"category": "tracking", "complexity": "low"}', NOW(), NOW()),
('req_cp_037', 'proj_creditpulse_001', 'Debt Payoff Calculator', 'Calculate payoff timelines using various strategies (snowball, avalanche)', 'requirements', 'requirement', 'todo', 'high', 'Priya Patel', '{"category": "tools", "complexity": "medium"}', NOW(), NOW()),
('req_cp_038', 'proj_creditpulse_001', 'Interest Savings Projections', 'Show potential interest savings from extra payments or refinancing', 'requirements', 'requirement', 'in_progress', 'high', 'David Lee', '{"category": "analytics", "complexity": "medium"}', NOW(), NOW()),
('req_cp_039', 'proj_creditpulse_001', 'Debt Consolidation Recommendations', 'Recommend consolidation options based on user profile', 'requirements', 'requirement', 'todo', 'high', 'Elena Rodriguez', '{"category": "recommendations", "complexity": "high"}', NOW(), NOW()),
('req_cp_040', 'proj_creditpulse_001', 'Automatic Payment Reminders', 'Send notifications before debt payment due dates', 'requirements', 'requirement', 'in_progress', 'medium', 'James Wilson', '{"category": "notifications", "complexity": "low"}', NOW(), NOW());

-- Req 41-50: Loan Comparison & Shopping
INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, owner, item_metadata, created_at, updated_at)
VALUES
('req_cp_041', 'proj_creditpulse_001', 'Mortgage Comparison Tool', 'Compare mortgage rates and terms from multiple lenders', 'requirements', 'requirement', 'todo', 'critical', 'Sarah Chen', '{"category": "tools", "complexity": "high"}', NOW(), NOW()),
('req_cp_042', 'proj_creditpulse_001', 'Auto Loan Comparison Tool', 'Compare auto loan rates and terms', 'requirements', 'requirement', 'todo', 'high', 'Marcus Johnson', '{"category": "tools", "complexity": "high"}', NOW(), NOW()),
('req_cp_043', 'proj_creditpulse_001', 'Personal Loan Marketplace', 'Display personal loan offers from partner lenders', 'requirements', 'requirement', 'todo', 'high', 'Priya Patel', '{"category": "marketplace", "complexity": "high"}', NOW(), NOW()),
('req_cp_044', 'proj_creditpulse_001', 'Credit Card Offer Recommendations', 'Recommend credit cards based on user profile and spending', 'requirements', 'requirement', 'in_progress', 'high', 'David Lee', '{"category": "recommendations", "complexity": "high"}', NOW(), NOW()),
('req_cp_045', 'proj_creditpulse_001', 'Refinancing Analysis', 'Compare current loans with refinancing options and savings', 'requirements', 'requirement', 'todo', 'high', 'Elena Rodriguez', '{"category": "analytics", "complexity": "high"}', NOW(), NOW()),
('req_cp_046', 'proj_creditpulse_001', 'APR Comparison Calculator', 'Easy comparison of APR, fees, and total cost across loans', 'requirements', 'requirement', 'in_progress', 'medium', 'James Wilson', '{"category": "tools", "complexity": "medium"}', NOW(), NOW()),
('req_cp_047', 'proj_creditpulse_001', 'Loan Pre-qualification', 'Display loan pre-qualifications without credit inquiries', 'requirements', 'requirement', 'todo', 'high', 'Sarah Chen', '{"category": "tools", "complexity": "high"}', NOW(), NOW()),
('req_cp_048', 'proj_creditpulse_001', 'Soft Pull Integration', 'Integrate with lenders for soft credit inquiries', 'requirements', 'requirement', 'todo', 'high', 'Marcus Johnson', '{"category": "integration", "complexity": "high"}', NOW(), NOW()),
('req_cp_049', 'proj_creditpulse_001', 'Historical Rate Tracking', 'Track and display historical loan rates for market analysis', 'requirements', 'requirement', 'todo', 'medium', 'Priya Patel', '{"category": "analytics", "complexity": "medium"}', NOW(), NOW()),
('req_cp_050', 'proj_creditpulse_001', 'Lender Partner Network', 'Establish partnerships with mortgage, auto, and personal lenders', 'requirements', 'requirement', 'in_progress', 'critical', 'David Lee', '{"category": "partnerships", "complexity": "high"}', NOW(), NOW());

-- Req 51-60: Tax Filing & Planning
INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, owner, item_metadata, created_at, updated_at)
VALUES
('req_cp_051', 'proj_creditpulse_001', 'Tax Return Data Gathering', 'Collect financial data needed for tax filing', 'requirements', 'requirement', 'todo', 'high', 'Elena Rodriguez', '{"category": "tax", "complexity": "medium"}', NOW(), NOW()),
('req_cp_052', 'proj_creditpulse_001', 'Tax Deduction Recommendations', 'Analyze spending and recommend tax deductions', 'requirements', 'requirement', 'todo', 'high', 'James Wilson', '{"category": "tax", "complexity": "high"}', NOW(), NOW()),
('req_cp_053', 'proj_creditpulse_001', 'Estimated Tax Calculations', 'Calculate estimated quarterly tax payments', 'requirements', 'requirement', 'todo', 'medium', 'Sarah Chen', '{"category": "tax", "complexity": "medium"}', NOW(), NOW()),
('req_cp_054', 'proj_creditpulse_001', 'Tax Filing Integration (TaxAct)', 'Integrate with TaxAct for IRS-compliant filing', 'requirements', 'requirement', 'todo', 'high', 'Marcus Johnson', '{"category": "integration", "complexity": "high"}', NOW(), NOW()),
('req_cp_055', 'proj_creditpulse_001', 'Tax Filing Integration (TurboTax)', 'Integrate with TurboTax for easy tax filing', 'requirements', 'requirement', 'todo', 'high', 'Priya Patel', '{"category": "integration", "complexity": "high"}', NOW(), NOW()),
('req_cp_056', 'proj_creditpulse_001', 'Capital Gains Tracking', 'Track investment transactions for capital gains reporting', 'requirements', 'requirement', 'todo', 'medium', 'David Lee', '{"category": "tax", "complexity": "high"}', NOW(), NOW()),
('req_cp_057', 'proj_creditpulse_001', 'Itemized vs Standard Deduction Comparison', 'Show which deduction method benefits the user most', 'requirements', 'requirement', 'todo', 'high', 'Elena Rodriguez', '{"category": "tax", "complexity": "medium"}', NOW(), NOW()),
('req_cp_058', 'proj_creditpulse_001', 'Tax Document Storage', 'Secure storage for tax documents and receipts', 'requirements', 'requirement', 'in_progress', 'medium', 'James Wilson', '{"category": "documents", "complexity": "low"}', NOW(), NOW()),
('req_cp_059', 'proj_creditpulse_001', 'Tax Planning for Next Year', 'Provide recommendations to minimize future tax liability', 'requirements', 'requirement', 'todo', 'high', 'Sarah Chen', '{"category": "tax", "complexity": "high"}', NOW(), NOW()),
('req_cp_060', 'proj_creditpulse_001', 'Form 1099 Tracking', 'Aggregate and organize 1099 forms from all sources', 'requirements', 'requirement', 'todo', 'medium', 'Marcus Johnson', '{"category": "tax", "complexity": "medium"}', NOW(), NOW());

-- Req 61-70: Financial Health Insights
INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, owner, item_metadata, created_at, updated_at)
VALUES
('req_cp_061', 'proj_creditpulse_001', 'Financial Health Score', 'Calculate overall financial health score based on multiple factors', 'requirements', 'requirement', 'in_progress', 'critical', 'Priya Patel', '{"category": "analytics", "complexity": "high"}', NOW(), NOW()),
('req_cp_062', 'proj_creditpulse_001', 'Net Worth Tracking', 'Calculate and track net worth over time', 'requirements', 'requirement', 'in_progress', 'high', 'David Lee', '{"category": "analytics", "complexity": "medium"}', NOW(), NOW()),
('req_cp_063', 'proj_creditpulse_001', 'Budget vs Actual Analysis', 'Compare budgeted spending to actual expenses', 'requirements', 'requirement', 'todo', 'high', 'Elena Rodriguez', '{"category": "analytics", "complexity": "medium"}', NOW(), NOW()),
('req_cp_064', 'proj_creditpulse_001', 'Spending by Category Breakdown', 'Categorize and analyze spending across different categories', 'requirements', 'requirement', 'done', 'high', 'James Wilson', '{"category": "analytics", "complexity": "low"}', NOW(), NOW()),
('req_cp_065', 'proj_creditpulse_001', 'Financial Goal Setting and Tracking', 'Allow users to set and monitor financial goals', 'requirements', 'requirement', 'todo', 'high', 'Sarah Chen', '{"category": "goals", "complexity": "medium"}', NOW(), NOW()),
('req_cp_066', 'proj_creditpulse_001', 'Cash Flow Analysis', 'Analyze monthly income vs expenses for cash flow health', 'requirements', 'requirement', 'in_progress', 'high', 'Marcus Johnson', '{"category": "analytics", "complexity": "medium"}', NOW(), NOW()),
('req_cp_067', 'proj_creditpulse_001', 'Emergency Fund Calculator', 'Calculate recommended emergency fund based on expenses', 'requirements', 'requirement', 'todo', 'medium', 'Priya Patel', '{"category": "tools", "complexity": "low"}', NOW(), NOW()),
('req_cp_068', 'proj_creditpulse_001', 'Savings Rate Analysis', 'Calculate and track savings rate over time', 'requirements', 'requirement', 'in_progress', 'medium', 'David Lee', '{"category": "analytics", "complexity": "low"}', NOW(), NOW()),
('req_cp_069', 'proj_creditpulse_001', 'Debt-to-Income Ratio Calculation', 'Calculate DTI for loan qualification purposes', 'requirements', 'requirement', 'todo', 'high', 'Elena Rodriguez', '{"category": "analytics", "complexity": "low"}', NOW(), NOW()),
('req_cp_070', 'proj_creditpulse_001', 'Financial Benchmarking', 'Compare financial metrics to similar demographic profiles', 'requirements', 'requirement', 'todo', 'medium', 'James Wilson', '{"category": "analytics", "complexity": "high"}', NOW(), NOW());

-- Req 71-80: Banking Integration
INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, owner, item_metadata, created_at, updated_at)
VALUES
('req_cp_071', 'proj_creditpulse_001', 'Plaid Integration for Bank Data', 'Connect bank accounts via Plaid for transaction visibility', 'requirements', 'requirement', 'done', 'critical', 'Sarah Chen', '{"category": "integration", "complexity": "high"}', NOW(), NOW()),
('req_cp_072', 'proj_creditpulse_001', 'Account Aggregation Dashboard', 'Display all connected bank and investment accounts in one view', 'requirements', 'requirement', 'done', 'high', 'Marcus Johnson', '{"category": "ui", "complexity": "medium"}', NOW(), NOW()),
('req_cp_073', 'proj_creditpulse_001', 'Transaction Categorization', 'Automatically categorize transactions for spending analysis', 'requirements', 'requirement', 'done', 'high', 'Priya Patel', '{"category": "analytics", "complexity": "medium"}', NOW(), NOW()),
('req_cp_074', 'proj_creditpulse_001', 'Investment Account Integration', 'Connect and monitor investment accounts (stocks, bonds, ETFs)', 'requirements', 'requirement', 'in_progress', 'high', 'David Lee', '{"category": "integration", "complexity": "high"}', NOW(), NOW()),
('req_cp_075', 'proj_creditpulse_001', 'Cryptocurrency Wallet Integration', 'Support crypto wallet integration for digital asset tracking', 'requirements', 'requirement', 'todo', 'medium', 'Elena Rodriguez', '{"category": "integration", "complexity": "high"}', NOW(), NOW()),
('req_cp_076', 'proj_creditpulse_001', 'Real Estate Valuation Tracking', 'Track property values for net worth calculations', 'requirements', 'requirement', 'todo', 'medium', 'James Wilson', '{"category": "integration", "complexity": "high"}', NOW(), NOW()),
('req_cp_077', 'proj_creditpulse_001', 'Retirement Account Aggregation', 'Aggregate 401k, IRA, Roth IRA accounts', 'requirements', 'requirement', 'todo', 'high', 'Sarah Chen', '{"category": "integration", "complexity": "medium"}', NOW(), NOW()),
('req_cp_078', 'proj_creditpulse_001', 'HSA and FSA Tracking', 'Monitor Health Savings Accounts and Flexible Spending Accounts', 'requirements', 'requirement', 'todo', 'medium', 'Marcus Johnson', '{"category": "integration", "complexity": "low"}', NOW(), NOW()),
('req_cp_079', 'proj_creditpulse_001', 'Pension Monitoring', 'Track pension benefits and estimated payouts', 'requirements', 'requirement', 'todo', 'low', 'Priya Patel', '{"category": "integration", "complexity": "medium"}', NOW(), NOW()),
('req_cp_080', 'proj_creditpulse_001', 'Bank Account Health Monitoring', 'Alert users to low balances, overdraft risks', 'requirements', 'requirement', 'in_progress', 'high', 'David Lee', '{"category": "notifications", "complexity": "low"}', NOW(), NOW());

-- Req 81-90: Personalized Recommendations
INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, owner, item_metadata, created_at, updated_at)
VALUES
('req_cp_081', 'proj_creditpulse_001', 'ML-Based Financial Recommendations Engine', 'Build ML model for personalized financial recommendations', 'requirements', 'requirement', 'todo', 'critical', 'Elena Rodriguez', '{"category": "ml", "complexity": "high"}', NOW(), NOW()),
('req_cp_082', 'proj_creditpulse_001', 'Credit Card Optimization Recommendations', 'Recommend card switches based on spending patterns', 'requirements', 'requirement', 'todo', 'high', 'James Wilson', '{"category": "recommendations", "complexity": "high"}', NOW(), NOW()),
('req_cp_083', 'proj_creditpulse_001', 'APR Reduction Opportunities', 'Identify and suggest balance transfers to lower APR cards', 'requirements', 'requirement', 'todo', 'high', 'Sarah Chen', '{"category": "recommendations", "complexity": "high"}', NOW(), NOW()),
('req_cp_084', 'proj_creditpulse_001', 'Savings Account Optimization', 'Recommend high-yield savings accounts matching user needs', 'requirements', 'requirement', 'todo', 'high', 'Marcus Johnson', '{"category": "recommendations", "complexity": "medium"}', NOW(), NOW()),
('req_cp_085', 'proj_creditpulse_001', 'Student Loan Repayment Plans', 'Recommend optimal repayment strategy based on income and debt', 'requirements', 'requirement', 'todo', 'high', 'Priya Patel', '{"category": "recommendations", "complexity": "high"}', NOW(), NOW()),
('req_cp_086', 'proj_creditpulse_001', 'Investment Recommendations', 'Suggest investment opportunities based on risk profile', 'requirements', 'requirement', 'todo', 'high', 'David Lee', '{"category": "recommendations", "complexity": "high"}', NOW(), NOW()),
('req_cp_087', 'proj_creditpulse_001', 'Insurance Gap Analysis', 'Identify insurance gaps (life, disability, umbrella)', 'requirements', 'requirement', 'todo', 'medium', 'Elena Rodriguez', '{"category": "recommendations", "complexity": "medium"}', NOW(), NOW()),
('req_cp_088', 'proj_creditpulse_001', 'Wealth Building Recommendations', 'Suggest strategies to increase net worth', 'requirements', 'requirement', 'todo', 'high', 'James Wilson', '{"category": "recommendations", "complexity": "high"}', NOW(), NOW()),
('req_cp_089', 'proj_creditpulse_001', 'Retirement Readiness Analysis', 'Analyze retirement savings progress vs targets', 'requirements', 'requirement', 'todo', 'high', 'Sarah Chen', '{"category": "recommendations", "complexity": "high"}', NOW(), NOW()),
('req_cp_090', 'proj_creditpulse_001', 'Bill Negotiation Assistance', 'Help users reduce recurring bills (utilities, insurance, etc.)', 'requirements', 'requirement', 'todo', 'medium', 'Marcus Johnson', '{"category": "tools", "complexity": "medium"}', NOW(), NOW());

-- Req 91-100: Marketplace & Partnerships
INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, owner, item_metadata, created_at, updated_at)
VALUES
('req_cp_091', 'proj_creditpulse_001', 'Credit Card Offers Marketplace', 'Display best credit card offers based on user profile', 'requirements', 'requirement', 'in_progress', 'high', 'Priya Patel', '{"category": "marketplace", "complexity": "high"}', NOW(), NOW()),
('req_cp_092', 'proj_creditpulse_001', 'Loan Offers Marketplace', 'Display personalized loan offers from partner lenders', 'requirements', 'requirement', 'todo', 'high', 'David Lee', '{"category": "marketplace", "complexity": "high"}', NOW(), NOW()),
('req_cp_093', 'proj_creditpulse_001', 'Insurance Marketplace', 'Compare and purchase insurance products (life, auto, home)', 'requirements', 'requirement', 'todo', 'high', 'Elena Rodriguez', '{"category": "marketplace", "complexity": "high"}', NOW(), NOW()),
('req_cp_094', 'proj_creditpulse_001', 'Partner Lender Network', 'Establish relationships with 50+ lenders', 'requirements', 'requirement', 'in_progress', 'critical', 'James Wilson', '{"category": "partnerships", "complexity": "high"}', NOW(), NOW()),
('req_cp_095', 'proj_creditpulse_001', 'Financial Advisor Directory', 'Connect users with certified financial advisors', 'requirements', 'requirement', 'todo', 'medium', 'Sarah Chen', '{"category": "marketplace", "complexity": "medium"}', NOW(), NOW()),
('req_cp_096', 'proj_creditpulse_001', 'Tax Professional Directory', 'Directory of CPAs and tax professionals for consultations', 'requirements', 'requirement', 'todo', 'medium', 'Marcus Johnson', '{"category": "marketplace", "complexity": "low"}', NOW(), NOW()),
('req_cp_097', 'proj_creditpulse_001', 'Affiliate Commission Program', 'Track and pay affiliates for referred products', 'requirements', 'requirement', 'todo', 'medium', 'Priya Patel', '{"category": "business", "complexity": "medium"}', NOW(), NOW()),
('req_cp_098', 'proj_creditpulse_001', 'Lead Generation Pipeline', 'Manage leads generated from marketplace', 'requirements', 'requirement', 'todo', 'high', 'David Lee', '{"category": "business", "complexity": "medium"}', NOW(), NOW()),
('req_cp_099', 'proj_creditpulse_001', 'Lender Application Submission', 'Auto-submit applications to partner lenders', 'requirements', 'requirement', 'todo', 'high', 'Elena Rodriguez', '{"category": "integration", "complexity": "high"}', NOW(), NOW()),
('req_cp_100', 'proj_creditpulse_001', 'Partner Performance Tracking', 'Monitor and analyze partner lender conversion rates', 'requirements', 'requirement', 'todo', 'medium', 'James Wilson', '{"category": "analytics", "complexity": "medium"}', NOW(), NOW());

-- FEATURES (110+) - First batch (1-50)
INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, owner, parent_id, item_metadata, created_at, updated_at)
VALUES
('feat_cp_001', 'proj_creditpulse_001', 'Daily Credit Score Updates', 'Pull credit scores daily from all three bureaus', 'features', 'feature', 'done', 'critical', 'Sarah Chen', 'req_cp_001', '{"epic": "credit_monitoring", "effort": "5"}', NOW(), NOW()),
('feat_cp_002', 'proj_creditpulse_001', 'Credit Score Mobile Widget', 'Display credit score widget on mobile home screen', 'features', 'feature', 'in_progress', 'high', 'Marcus Johnson', 'req_cp_001', '{"epic": "credit_monitoring", "effort": "3"}', NOW(), NOW()),
('feat_cp_003', 'proj_creditpulse_001', 'Email Score Alerts', 'Send email when score changes significantly', 'features', 'feature', 'done', 'high', 'Priya Patel', 'req_cp_008', '{"epic": "credit_monitoring", "effort": "2"}', NOW(), NOW()),
('feat_cp_004', 'proj_creditpulse_001', 'Push Notifications for Score Changes', 'Mobile push notifications for score updates', 'features', 'feature', 'in_progress', 'high', 'David Lee', 'req_cp_008', '{"epic": "credit_monitoring", "effort": "3"}', NOW(), NOW()),
('feat_cp_005', 'proj_creditpulse_001', 'Score Trend Chart (6 Month View)', '6-month credit score trend visualization', 'features', 'feature', 'done', 'high', 'Elena Rodriguez', 'req_cp_005', '{"epic": "credit_monitoring", "effort": "4"}', NOW(), NOW()),
('feat_cp_006', 'proj_creditpulse_001', 'Score Trend Chart (12 Month View)', '12-month credit score trend visualization', 'features', 'feature', 'done', 'high', 'James Wilson', 'req_cp_005', '{"epic": "credit_monitoring", "effort": "2"}', NOW(), NOW()),
('feat_cp_007', 'proj_creditpulse_001', 'Score Trend Chart (24 Month View)', '24-month credit score trend visualization', 'features', 'feature', 'todo', 'medium', 'Sarah Chen', 'req_cp_005', '{"epic": "credit_monitoring", "effort": "2"}', NOW(), NOW()),
('feat_cp_008', 'proj_creditpulse_001', 'Payment History Impact Widget', 'Show how payment history affects score', 'features', 'feature', 'in_progress', 'high', 'Marcus Johnson', 'req_cp_006', '{"epic": "credit_monitoring", "effort": "3"}', NOW(), NOW()),
('feat_cp_009', 'proj_creditpulse_001', 'Credit Utilization Impact Widget', 'Show credit utilization ratio and impact', 'features', 'feature', 'done', 'high', 'Priya Patel', 'req_cp_006', '{"epic": "credit_monitoring", "effort": "3"}', NOW(), NOW()),
('feat_cp_010', 'proj_creditpulse_001', 'Age of Credit Impact Widget', 'Display credit age and its score impact', 'features', 'feature', 'todo', 'medium', 'David Lee', 'req_cp_006', '{"epic": "credit_monitoring", "effort": "2"}', NOW(), NOW()),
('feat_cp_011', 'proj_creditpulse_001', 'Side-by-Side Bureau Score Comparison', 'Compare Equifax, Experian, TransUnion scores', 'features', 'feature', 'done', 'high', 'Elena Rodriguez', 'req_cp_007', '{"epic": "credit_monitoring", "effort": "3"}', NOW(), NOW()),
('feat_cp_012', 'proj_creditpulse_001', 'Bureau Score Variance Alert', 'Alert when scores differ significantly between bureaus', 'features', 'feature', 'in_progress', 'medium', 'James Wilson', 'req_cp_007', '{"epic": "credit_monitoring", "effort": "3"}', NOW(), NOW()),
('feat_cp_013', 'proj_creditpulse_001', 'Email and SMS Registration', 'Register account with email or SMS', 'features', 'feature', 'done', 'critical', 'Sarah Chen', 'req_cp_011', '{"epic": "auth", "effort": "3"}', NOW(), NOW()),
('feat_cp_014', 'proj_creditpulse_001', 'Email Verification Workflow', 'Verify email ownership with confirmation link', 'features', 'feature', 'done', 'critical', 'Marcus Johnson', 'req_cp_011', '{"epic": "auth", "effort": "2"}', NOW(), NOW()),
('feat_cp_015', 'proj_creditpulse_001', 'Google OAuth Login', 'Enable quick login with Google account', 'features', 'feature', 'done', 'high', 'Priya Patel', 'req_cp_012', '{"epic": "auth", "effort": "3"}', NOW(), NOW()),
('feat_cp_016', 'proj_creditpulse_001', 'Apple Sign-In Integration', 'Enable Apple Sign-In for iOS and web', 'features', 'feature', 'done', 'high', 'David Lee', 'req_cp_013', '{"epic": "auth", "effort": "3"}', NOW(), NOW()),
('feat_cp_017', 'proj_creditpulse_001', 'SMS 2FA Setup', 'Allow users to enable SMS-based 2FA', 'features', 'feature', 'in_progress', 'critical', 'Elena Rodriguez', 'req_cp_014', '{"epic": "security", "effort": "4"}', NOW(), NOW()),
('feat_cp_018', 'proj_creditpulse_001', 'Authenticator App 2FA Setup', 'Support authenticator app integration (Google, Authy)', 'features', 'feature', 'in_progress', 'high', 'James Wilson', 'req_cp_014', '{"epic": "security", "effort": "4"}', NOW(), NOW()),
('feat_cp_019', 'proj_creditpulse_001', 'Backup Codes for 2FA Recovery', 'Generate and store backup codes for account recovery', 'features', 'feature', 'todo', 'high', 'Sarah Chen', 'req_cp_014', '{"epic": "security", "effort": "3"}', NOW(), NOW()),
('feat_cp_020', 'proj_creditpulse_001', 'Dark Web Monitoring Dashboard', 'Dashboard showing dark web monitoring status', 'features', 'feature', 'todo', 'critical', 'Marcus Johnson', 'req_cp_021', '{"epic": "security", "effort": "5"}', NOW(), NOW()),
('feat_cp_021', 'proj_creditpulse_001', 'Fraudulent Account Detection', 'Identify unauthorized accounts on credit report', 'features', 'feature', 'in_progress', 'critical', 'Priya Patel', 'req_cp_022', '{"epic": "security", "effort": "5"}', NOW(), NOW()),
('feat_cp_022', 'proj_creditpulse_001', 'Fraud Dispute Workflow', 'Guided step-by-step dispute process', 'features', 'feature', 'todo', 'high', 'David Lee', 'req_cp_026', '{"epic": "support", "effort": "6"}', NOW(), NOW()),
('feat_cp_023', 'proj_creditpulse_001', 'Credit Freeze Placement', 'Place security freeze with all three bureaus', 'features', 'feature', 'todo', 'high', 'Elena Rodriguez', 'req_cp_025', '{"epic": "security", "effort": "5"}', NOW(), NOW()),
('feat_cp_024', 'proj_creditpulse_001', 'Credit Freeze Monitoring', 'Track freeze status and expiration dates', 'features', 'feature', 'todo', 'high', 'James Wilson', 'req_cp_025', '{"epic": "security", "effort": "3"}', NOW(), NOW()),
('feat_cp_025', 'proj_creditpulse_001', 'Fraud Alert Management', 'Place and renew fraud alerts', 'features', 'feature', 'todo', 'high', 'Sarah Chen', 'req_cp_025', '{"epic": "security", "effort": "4"}', NOW(), NOW()),
('feat_cp_026', 'proj_creditpulse_001', 'Login Attempt Alerts', 'Alert users of suspicious login attempts', 'features', 'feature', 'in_progress', 'high', 'Marcus Johnson', 'req_cp_027', '{"epic": "security", "effort": "3"}', NOW(), NOW()),
('feat_cp_027', 'proj_creditpulse_001', 'Debt Account Aggregation Dashboard', 'Central dashboard showing all debt accounts', 'features', 'feature', 'in_progress', 'critical', 'Priya Patel', 'req_cp_031', '{"epic": "debt", "effort": "5"}', NOW(), NOW()),
('feat_cp_028', 'proj_creditpulse_001', 'Credit Card List View', 'Display all credit cards with balances and limits', 'features', 'feature', 'done', 'high', 'David Lee', 'req_cp_032', '{"epic": "debt", "effort": "3"}', NOW(), NOW()),
('feat_cp_029', 'proj_creditpulse_001', 'Credit Card Detail View', 'Show APR, payment due date, credit limit', 'features', 'feature', 'done', 'high', 'Elena Rodriguez', 'req_cp_032', '{"epic": "debt", "effort": "2"}', NOW(), NOW()),
('feat_cp_030', 'proj_creditpulse_001', 'Student Loan Aggregation', 'Aggregate federal and private student loans', 'features', 'feature', 'in_progress', 'high', 'James Wilson', 'req_cp_033', '{"epic": "debt", "effort": "4"}', NOW(), NOW()),
('feat_cp_031', 'proj_creditpulse_001', 'Student Loan Repayment Schedule', 'Display repayment timeline and payment amounts', 'features', 'feature', 'in_progress', 'high', 'Sarah Chen', 'req_cp_033', '{"epic": "debt", "effort": "3"}', NOW(), NOW()),
('feat_cp_032', 'proj_creditpulse_001', 'Mortgage Balance Tracking', 'Track mortgage principal, interest, escrow', 'features', 'feature', 'in_progress', 'high', 'Marcus Johnson', 'req_cp_034', '{"epic": "debt", "effort": "3"}', NOW(), NOW()),
('feat_cp_033', 'proj_creditpulse_001', 'Mortgage Payment Schedule', 'Display full amortization schedule', 'features', 'feature', 'in_progress', 'medium', 'Priya Patel', 'req_cp_034', '{"epic": "debt", "effort": "3"}', NOW(), NOW()),
('feat_cp_034', 'proj_creditpulse_001', 'Auto Loan Balance Tracking', 'Track auto loan details and equity', 'features', 'feature', 'done', 'medium', 'David Lee', 'req_cp_035', '{"epic": "debt", "effort": "2"}', NOW(), NOW()),
('feat_cp_035', 'proj_creditpulse_001', 'Debt Snowball Calculator', 'Calculate payoff timeline using snowball method', 'features', 'feature', 'todo', 'high', 'Elena Rodriguez', 'req_cp_037', '{"epic": "tools", "effort": "5"}', NOW(), NOW()),
('feat_cp_036', 'proj_creditpulse_001', 'Debt Avalanche Calculator', 'Calculate payoff timeline using avalanche method', 'features', 'feature', 'todo', 'high', 'James Wilson', 'req_cp_037', '{"epic": "tools", "effort": "5"}', NOW(), NOW()),
('feat_cp_037', 'proj_creditpulse_001', 'Interest Savings Calculator', 'Show potential savings from extra payments', 'features', 'feature', 'in_progress', 'high', 'Sarah Chen', 'req_cp_038', '{"epic": "tools", "effort": "4"}', NOW(), NOW()),
('feat_cp_038', 'proj_creditpulse_001', 'Mortgage Comparison Tool', 'Compare mortgage rates from lenders', 'features', 'feature', 'todo', 'critical', 'Marcus Johnson', 'req_cp_041', '{"epic": "shopping", "effort": "6"}', NOW(), NOW()),
('feat_cp_039', 'proj_creditpulse_001', 'Auto Loan Comparison Tool', 'Compare auto loan rates and terms', 'features', 'feature', 'todo', 'high', 'Priya Patel', 'req_cp_042', '{"epic": "shopping", "effort": "5"}', NOW(), NOW()),
('feat_cp_040', 'proj_creditpulse_001', 'Personal Loan Marketplace Widget', 'Display personal loan offers in marketplace', 'features', 'feature', 'todo', 'high', 'David Lee', 'req_cp_043', '{"epic": "shopping", "effort": "5"}', NOW(), NOW()),
('feat_cp_041', 'proj_creditpulse_001', 'Tax Deduction Analyzer', 'Analyze transactions for tax deduction opportunities', 'features', 'feature', 'todo', 'high', 'Elena Rodriguez', 'req_cp_052', '{"epic": "tax", "effort": "5"}', NOW(), NOW()),
('feat_cp_042', 'proj_creditpulse_001', 'Estimated Tax Calculator', 'Calculate quarterly tax payment amounts', 'features', 'feature', 'todo', 'medium', 'James Wilson', 'req_cp_053', '{"epic": "tax", "effort": "4"}', NOW(), NOW()),
('feat_cp_043', 'proj_creditpulse_001', 'TaxAct Integration', 'Connect and auto-populate TaxAct with financial data', 'features', 'feature', 'todo', 'high', 'Sarah Chen', 'req_cp_054', '{"epic": "tax", "effort": "6"}', NOW(), NOW()),
('feat_cp_044', 'proj_creditpulse_001', 'TurboTax Integration', 'Connect and auto-populate TurboTax with financial data', 'features', 'feature', 'todo', 'high', 'Marcus Johnson', 'req_cp_055', '{"epic": "tax", "effort": "6"}', NOW(), NOW()),
('feat_cp_045', 'proj_creditpulse_001', 'Tax Document Vault', 'Secure storage for tax documents and receipts', 'features', 'feature', 'in_progress', 'medium', 'Priya Patel', 'req_cp_058', '{"epic": "documents", "effort": "4"}', NOW(), NOW()),
('feat_cp_046', 'proj_creditpulse_001', 'Financial Health Dashboard', 'Overall dashboard showing financial health score', 'features', 'feature', 'in_progress', 'critical', 'David Lee', 'req_cp_061', '{"epic": "analytics", "effort": "5"}', NOW(), NOW()),
('feat_cp_047', 'proj_creditpulse_001', 'Net Worth Dashboard', 'Display net worth with breakdown by asset type', 'features', 'feature', 'in_progress', 'high', 'Elena Rodriguez', 'req_cp_062', '{"epic": "analytics", "effort": "4"}', NOW(), NOW()),
('feat_cp_048', 'proj_creditpulse_001', 'Net Worth History Chart', 'Show net worth trends over time', 'features', 'feature', 'in_progress', 'medium', 'James Wilson', 'req_cp_062', '{"epic": "analytics", "effort": "3"}', NOW(), NOW()),
('feat_cp_049', 'proj_creditpulse_001', 'Budget Creation Tool', 'Create and customize monthly budgets', 'features', 'feature', 'todo', 'high', 'Sarah Chen', 'req_cp_063', '{"epic": "budgeting", "effort": "5"}', NOW(), NOW()),
('feat_cp_050', 'proj_creditpulse_001', 'Budget vs Actual Comparison', 'Compare budgeted to actual spending', 'features', 'feature', 'todo', 'high', 'Marcus Johnson', 'req_cp_063', '{"epic": "budgeting", "effort": "4"}', NOW(), NOW());

-- Features 51-110
INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, owner, parent_id, item_metadata, created_at, updated_at)
VALUES
('feat_cp_051', 'proj_creditpulse_001', 'Spending by Category Report', 'Breakdown spending by expense category', 'features', 'feature', 'done', 'high', 'Priya Patel', 'req_cp_064', '{"epic": "analytics", "effort": "3"}', NOW(), NOW()),
('feat_cp_052', 'proj_creditpulse_001', 'Category Comparison Chart', 'Compare spending categories month-over-month', 'features', 'feature', 'done', 'medium', 'David Lee', 'req_cp_064', '{"epic": "analytics", "effort": "3"}', NOW(), NOW()),
('feat_cp_053', 'proj_creditpulse_001', 'Goal Setting Interface', 'Create and track financial goals', 'features', 'feature', 'todo', 'high', 'Elena Rodriguez', 'req_cp_065', '{"epic": "goals", "effort": "4"}', NOW(), NOW()),
('feat_cp_054', 'proj_creditpulse_001', 'Goal Progress Tracking', 'Monitor progress towards financial goals', 'features', 'feature', 'todo', 'high', 'James Wilson', 'req_cp_065', '{"epic": "goals", "effort": "3"}', NOW(), NOW()),
('feat_cp_055', 'proj_creditpulse_001', 'Cash Flow Analysis Report', 'Monthly income vs expenses analysis', 'features', 'feature', 'in_progress', 'high', 'Sarah Chen', 'req_cp_066', '{"epic": "analytics", "effort": "4"}', NOW(), NOW()),
('feat_cp_056', 'proj_creditpulse_001', 'Emergency Fund Recommendation', 'Calculate emergency fund based on expenses', 'features', 'feature', 'todo', 'medium', 'Marcus Johnson', 'req_cp_067', '{"epic": "tools", "effort": "2"}', NOW(), NOW()),
('feat_cp_057', 'proj_creditpulse_001', 'Savings Rate Tracker', 'Track monthly and annual savings rate', 'features', 'feature', 'in_progress', 'medium', 'Priya Patel', 'req_cp_068', '{"epic": "analytics", "effort": "2"}', NOW(), NOW()),
('feat_cp_058', 'proj_creditpulse_001', 'Debt-to-Income Calculator', 'Calculate DTI ratio for loan applications', 'features', 'feature', 'todo', 'high', 'David Lee', 'req_cp_069', '{"epic": "tools", "effort": "2"}', NOW(), NOW()),
('feat_cp_059', 'proj_creditpulse_001', 'Plaid Account Connection', 'Connect bank accounts via Plaid', 'features', 'feature', 'done', 'critical', 'Elena Rodriguez', 'req_cp_071', '{"epic": "integration", "effort": "4"}', NOW(), NOW()),
('feat_cp_060', 'proj_creditpulse_001', 'Transaction Sync from Plaid', 'Automatically sync transactions from Plaid', 'features', 'feature', 'done', 'critical', 'James Wilson', 'req_cp_071', '{"epic": "integration", "effort": "4"}', NOW(), NOW()),
('feat_cp_061', 'proj_creditpulse_001', 'Account Aggregation Dashboard', 'Unified view of all bank accounts', 'features', 'feature', 'done', 'high', 'Sarah Chen', 'req_cp_072', '{"epic": "integration", "effort": "4"}', NOW(), NOW()),
('feat_cp_062', 'proj_creditpulse_001', 'Auto-Categorization Engine', 'ML-based automatic transaction categorization', 'features', 'feature', 'done', 'high', 'Marcus Johnson', 'req_cp_073', '{"epic": "integration", "effort": "5"}', NOW(), NOW()),
('feat_cp_063', 'proj_creditpulse_001', 'Manual Category Override', 'Allow manual category adjustments by users', 'features', 'feature', 'done', 'medium', 'Priya Patel', 'req_cp_073', '{"epic": "integration", "effort": "2"}', NOW(), NOW()),
('feat_cp_064', 'proj_creditpulse_001', 'Investment Account Connection', 'Connect brokerage and investment accounts', 'features', 'feature', 'in_progress', 'high', 'David Lee', 'req_cp_074', '{"epic": "integration", "effort": "5"}', NOW(), NOW()),
('feat_cp_065', 'proj_creditpulse_001', 'Portfolio Performance Tracking', 'Track investment portfolio performance metrics', 'features', 'feature', 'in_progress', 'high', 'Elena Rodriguez', 'req_cp_074', '{"epic": "integration", "effort": "4"}', NOW(), NOW()),
('feat_cp_066', 'proj_creditpulse_001', 'Cryptocurrency Wallet Connection', 'Connect crypto wallets for tracking', 'features', 'feature', 'todo', 'medium', 'James Wilson', 'req_cp_075', '{"epic": "integration", "effort": "5"}', NOW(), NOW()),
('feat_cp_067', 'proj_creditpulse_001', 'Crypto Price Tracking', 'Real-time crypto price and valuation updates', 'features', 'feature', 'todo', 'medium', 'Sarah Chen', 'req_cp_075', '{"epic": "integration", "effort": "3"}', NOW(), NOW()),
('feat_cp_068', 'proj_creditpulse_001', 'Retirement Account Discovery', 'Find and aggregate scattered retirement accounts', 'features', 'feature', 'todo', 'high', 'Marcus Johnson', 'req_cp_077', '{"epic": "integration", "effort": "4"}', NOW(), NOW()),
('feat_cp_069', 'proj_creditpulse_001', 'Retirement Calculator', 'Calculate retirement readiness and projections', 'features', 'feature', 'todo', 'high', 'Priya Patel', 'req_cp_077', '{"epic": "tools", "effort": "5"}', NOW(), NOW()),
('feat_cp_070', 'proj_creditpulse_001', 'Low Balance Alerts', 'Alert when checking account balance is low', 'features', 'feature', 'in_progress', 'high', 'David Lee', 'req_cp_080', '{"epic": "notifications", "effort": "2"}', NOW(), NOW()),
('feat_cp_071', 'proj_creditpulse_001', 'Overdraft Risk Alerts', 'Warn before potential overdraft situation', 'features', 'feature', 'in_progress', 'high', 'Elena Rodriguez', 'req_cp_080', '{"epic": "notifications", "effort": "3"}', NOW(), NOW()),
('feat_cp_072', 'proj_creditpulse_001', 'Credit Card Recommendation Engine', 'ML-based credit card recommendations', 'features', 'feature', 'todo', 'high', 'James Wilson', 'req_cp_081', '{"epic": "recommendations", "effort": "6"}', NOW(), NOW()),
('feat_cp_073', 'proj_creditpulse_001', 'Balance Transfer Suggestions', 'Recommend balance transfers to lower APR', 'features', 'feature', 'todo', 'high', 'Sarah Chen', 'req_cp_083', '{"epic": "recommendations", "effort": "4"}', NOW(), NOW()),
('feat_cp_074', 'proj_creditpulse_001', 'High-Yield Savings Recommendations', 'Recommend best HYSA accounts', 'features', 'feature', 'todo', 'high', 'Marcus Johnson', 'req_cp_084', '{"epic": "recommendations", "effort": "3"}', NOW(), NOW()),
('feat_cp_075', 'proj_creditpulse_001', 'Student Loan Repayment Advisor', 'Recommend optimal repayment strategy', 'features', 'feature', 'todo', 'high', 'Priya Patel', 'req_cp_085', '{"epic": "recommendations", "effort": "5"}', NOW(), NOW()),
('feat_cp_076', 'proj_creditpulse_001', 'Investment Recommendation Engine', 'Suggest investments based on risk profile', 'features', 'feature', 'todo', 'high', 'David Lee', 'req_cp_086', '{"epic": "recommendations", "effort": "6"}', NOW(), NOW()),
('feat_cp_077', 'proj_creditpulse_001', 'Insurance Gap Analyzer', 'Identify missing insurance coverage', 'features', 'feature', 'todo', 'medium', 'Elena Rodriguez', 'req_cp_087', '{"epic": "recommendations", "effort": "4"}', NOW(), NOW()),
('feat_cp_078', 'proj_creditpulse_001', 'Net Worth Growth Strategies', 'Suggest ways to increase net worth', 'features', 'feature', 'todo', 'high', 'James Wilson', 'req_cp_088', '{"epic": "recommendations", "effort": "5"}', NOW(), NOW()),
('feat_cp_079', 'proj_creditpulse_001', 'Retirement Readiness Report', 'Comprehensive retirement analysis', 'features', 'feature', 'todo', 'high', 'Sarah Chen', 'req_cp_089', '{"epic": "recommendations", "effort": "6"}', NOW(), NOW()),
('feat_cp_080', 'proj_creditpulse_001', 'Bill Negotiation Service', 'Help reduce recurring bills', 'features', 'feature', 'todo', 'medium', 'Marcus Johnson', 'req_cp_090', '{"epic": "tools", "effort": "5"}', NOW(), NOW()),
('feat_cp_081', 'proj_creditpulse_001', 'Credit Card Offers Page', 'Personalized credit card offers marketplace', 'features', 'feature', 'in_progress', 'high', 'Priya Patel', 'req_cp_091', '{"epic": "marketplace", "effort": "5"}', NOW(), NOW()),
('feat_cp_082', 'proj_creditpulse_001', 'Loan Offers Aggregation', 'Display personalized loan offers', 'features', 'feature', 'todo', 'high', 'David Lee', 'req_cp_092', '{"epic": "marketplace", "effort": "5"}', NOW(), NOW()),
('feat_cp_083', 'proj_creditpulse_001', 'Insurance Quotes Comparison', 'Compare insurance quotes from providers', 'features', 'feature', 'todo', 'high', 'Elena Rodriguez', 'req_cp_093', '{"epic": "marketplace", "effort": "6"}', NOW(), NOW()),
('feat_cp_084', 'proj_creditpulse_001', 'One-Click Application Submission', 'Submit loan applications with one click', 'features', 'feature', 'todo', 'high', 'James Wilson', 'req_cp_099', '{"epic": "marketplace", "effort": "5"}', NOW(), NOW()),
('feat_cp_085', 'proj_creditpulse_001', 'Financial Advisor Finder', 'Search and connect with financial advisors', 'features', 'feature', 'todo', 'medium', 'Sarah Chen', 'req_cp_095', '{"epic": "marketplace", "effort": "3"}', NOW(), NOW()),
('feat_cp_086', 'proj_creditpulse_001', 'Tax Professional Directory', 'Find and connect with CPAs and tax pros', 'features', 'feature', 'todo', 'medium', 'Marcus Johnson', 'req_cp_096', '{"epic": "marketplace", "effort": "3"}', NOW(), NOW()),
('feat_cp_087', 'proj_creditpulse_001', 'API for Partner Integration', 'Public API for partner lender integration', 'features', 'feature', 'todo', 'high', 'Priya Patel', 'req_cp_050', '{"epic": "integration", "effort": "6"}', NOW(), NOW()),
('feat_cp_088', 'proj_creditpulse_001', 'Lead Scoring Engine', 'Score leads for partner conversion', 'features', 'feature', 'todo', 'high', 'David Lee', 'req_cp_098', '{"epic": "business", "effort": "5"}', NOW(), NOW()),
('feat_cp_089', 'proj_creditpulse_001', 'Affiliate Tracking Dashboard', 'Track affiliate referrals and commissions', 'features', 'feature', 'todo', 'medium', 'Elena Rodriguez', 'req_cp_097', '{"epic": "business", "effort": "4"}', NOW(), NOW()),
('feat_cp_090', 'proj_creditpulse_001', 'Partner Performance Analytics', 'Dashboard for lender partner metrics', 'features', 'feature', 'todo', 'medium', 'James Wilson', 'req_cp_100', '{"epic": "analytics", "effort": "4"}', NOW(), NOW()),
('feat_cp_091', 'proj_creditpulse_001', 'Mobile App - iOS', 'Native iOS application', 'features', 'feature', 'in_progress', 'critical', 'Sarah Chen', NULL, '{"epic": "mobile", "effort": "20"}', NOW(), NOW()),
('feat_cp_092', 'proj_creditpulse_001', 'Mobile App - Android', 'Native Android application', 'features', 'feature', 'todo', 'critical', 'Marcus Johnson', NULL, '{"epic": "mobile", "effort": "20"}', NOW(), NOW()),
('feat_cp_093', 'proj_creditpulse_001', 'Web App - React', 'React-based web application', 'features', 'feature', 'done', 'critical', 'Priya Patel', NULL, '{"epic": "web", "effort": "25"}', NOW(), NOW()),
('feat_cp_094', 'proj_creditpulse_001', 'Mobile Push Notifications', 'Real-time push notification delivery', 'features', 'feature', 'in_progress', 'high', 'David Lee', NULL, '{"epic": "notifications", "effort": "4"}', NOW(), NOW()),
('feat_cp_095', 'proj_creditpulse_001', 'Email Notification System', 'Transactional and marketing emails', 'features', 'feature', 'done', 'high', 'Elena Rodriguez', NULL, '{"epic": "notifications", "effort": "3"}', NOW(), NOW()),
('feat_cp_096', 'proj_creditpulse_001', 'SMS Notification System', 'SMS alerts for critical notifications', 'features', 'feature', 'in_progress', 'high', 'James Wilson', NULL, '{"epic": "notifications", "effort": "3"}', NOW(), NOW()),
('feat_cp_097', 'proj_creditpulse_001', 'In-App Notification Center', 'Central notification hub within app', 'features', 'feature', 'in_progress', 'medium', 'Sarah Chen', NULL, '{"epic": "notifications", "effort": "3"}', NOW(), NOW()),
('feat_cp_098', 'proj_creditpulse_001', 'Analytics Dashboard', 'User behavior and platform analytics', 'features', 'feature', 'done', 'high', 'Marcus Johnson', NULL, '{"epic": "analytics", "effort": "5"}', NOW(), NOW()),
('feat_cp_099', 'proj_creditpulse_001', 'Reporting Engine', 'Generate financial reports and exports', 'features', 'feature', 'in_progress', 'high', 'Priya Patel', NULL, '{"epic": "documents", "effort": "4"}', NOW(), NOW()),
('feat_cp_100', 'proj_creditpulse_001', 'Data Export to CSV/PDF', 'Export financial data in multiple formats', 'features', 'feature', 'done', 'high', 'David Lee', NULL, '{"epic": "documents", "effort": "3"}', NOW(), NOW()),
('feat_cp_101', 'proj_creditpulse_001', 'API Rate Limiting', 'Implement rate limiting for API protection', 'features', 'feature', 'done', 'medium', 'Elena Rodriguez', NULL, '{"epic": "infrastructure", "effort": "2"}', NOW(), NOW()),
('feat_cp_102', 'proj_creditpulse_001', 'Fraud Detection System', 'Detect suspicious account activity', 'features', 'feature', 'in_progress', 'critical', 'James Wilson', NULL, '{"epic": "security", "effort": "6"}', NOW(), NOW()),
('feat_cp_103', 'proj_creditpulse_001', 'Data Encryption at Rest', 'Encrypt all sensitive data storage', 'features', 'feature', 'done', 'critical', 'Sarah Chen', NULL, '{"epic": "security", "effort": "4"}', NOW(), NOW()),
('feat_cp_104', 'proj_creditpulse_001', 'Data Encryption in Transit', 'TLS/HTTPS for all communications', 'features', 'feature', 'done', 'critical', 'Marcus Johnson', NULL, '{"epic": "security", "effort": "2"}', NOW(), NOW()),
('feat_cp_105', 'proj_creditpulse_001', 'Compliance Auditing', 'Audit compliance with regulations', 'features', 'feature', 'in_progress', 'high', 'Priya Patel', NULL, '{"epic": "compliance", "effort": "5"}', NOW(), NOW()),
('feat_cp_106', 'proj_creditpulse_001', 'GDPR Compliance', 'Implement GDPR data protection requirements', 'features', 'feature', 'done', 'critical', 'David Lee', NULL, '{"epic": "compliance", "effort": "6"}', NOW(), NOW()),
('feat_cp_107', 'proj_creditpulse_001', 'CCPA Compliance', 'Implement CCPA data privacy requirements', 'features', 'feature', 'done', 'critical', 'Elena Rodriguez', NULL, '{"epic": "compliance", "effort": "6"}', NOW(), NOW()),
('feat_cp_108', 'proj_creditpulse_001', 'Database Backup System', 'Automated backup and recovery procedures', 'features', 'feature', 'done', 'critical', 'James Wilson', NULL, '{"epic": "infrastructure", "effort": "4"}', NOW(), NOW()),
('feat_cp_109', 'proj_creditpulse_001', 'Disaster Recovery Plan', 'Plan and test disaster recovery', 'features', 'feature', 'in_progress', 'critical', 'Sarah Chen', NULL, '{"epic": "infrastructure", "effort": "5"}', NOW(), NOW()),
('feat_cp_110', 'proj_creditpulse_001', 'Performance Monitoring', 'Real-time system performance tracking', 'features', 'feature', 'done', 'high', 'Marcus Johnson', NULL, '{"epic": "infrastructure", "effort": "4"}', NOW(), NOW());

-- LINKS between requirements and features
INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, link_metadata, created_at, updated_at)
VALUES
('link_cp_001', 'proj_creditpulse_001', 'req_cp_011', 'req_cp_014', 'depends_on', '{"notes": "2FA comes after registration"}', NOW(), NOW()),
('link_cp_002', 'proj_creditpulse_001', 'req_cp_054', 'req_cp_071', 'depends_on', '{"notes": "Needs aggregated financial data"}', NOW(), NOW()),
('link_cp_003', 'proj_creditpulse_001', 'req_cp_055', 'req_cp_071', 'depends_on', '{"notes": "Needs aggregated financial data"}', NOW(), NOW()),
('link_cp_004', 'proj_creditpulse_001', 'req_cp_009', 'req_cp_006', 'depends_on', '{"notes": "Uses factor analysis for ML model"}', NOW(), NOW()),
('link_cp_005', 'proj_creditpulse_001', 'req_cp_085', 'req_cp_033', 'depends_on', '{"notes": "Analyzes student loan accounts"}', NOW(), NOW()),
('link_cp_006', 'proj_creditpulse_001', 'req_cp_082', 'req_cp_032', 'depends_on', '{"notes": "Optimizes credit card strategy"}', NOW(), NOW()),
('link_cp_007', 'proj_creditpulse_001', 'req_cp_037', 'req_cp_031', 'depends_on', '{"notes": "Uses debt account data"}', NOW(), NOW()),
('link_cp_008', 'proj_creditpulse_001', 'req_cp_062', 'req_cp_071', 'depends_on', '{"notes": "Uses account data for net worth"}', NOW(), NOW()),
('link_cp_009', 'proj_creditpulse_001', 'req_cp_066', 'req_cp_071', 'depends_on', '{"notes": "Cash flow uses transaction data"}', NOW(), NOW()),
('link_cp_010', 'proj_creditpulse_001', 'req_cp_091', 'req_cp_050', 'depends_on', '{"notes": "Uses partner lender network"}', NOW(), NOW());
