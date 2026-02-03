-- Realistic Mock Data Population Script
-- Creates authentic, complex project data representing an in-progress mobile banking app

-- Clean slate (only if tables exist and have data)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'projects') THEN
        IF EXISTS (SELECT 1 FROM projects WHERE name = 'Mobile Banking App' LIMIT 1) THEN
            DELETE FROM projects WHERE name = 'Mobile Banking App';
        END IF;
    END IF;
END $$;

-- Disable triggers temporarily
ALTER TABLE projects DISABLE TRIGGER ALL;
ALTER TABLE items DISABLE TRIGGER ALL;
ALTER TABLE links DISABLE TRIGGER ALL;

-- Create realistic project function
CREATE OR REPLACE FUNCTION create_realistic_mobile_banking_project()
RETURNS VARCHAR(255) AS $$
DECLARE
    v_project_id VARCHAR(255) := gen_random_uuid()::text;
    v_req_id VARCHAR(255);
    v_feat_id VARCHAR(255);
    v_test_id VARCHAR(255);
    v_api_id VARCHAR(255);
    v_db_id VARCHAR(255);
    v_comp_id VARCHAR(255);
    v_doc_id VARCHAR(255);
    v_sec_id VARCHAR(255);
    v_perf_id VARCHAR(255);
    v_deploy_id VARCHAR(255);
    i INTEGER;
    j INTEGER;
    v_feat_num INTEGER;
    v_status VARCHAR(50);
    v_priority VARCHAR(50);
BEGIN
    -- Create Mobile Banking App project
    INSERT INTO projects (id, name, project_metadata, created_at, updated_at)
    VALUES (
        v_project_id,
        'Mobile Banking App',
        jsonb_build_object(
            'slug', 'mobile-banking-app',
            'domain', 'mobile',
            'status', 'active',
            'priority', 'high',
            'description', 'Secure mobile banking application with biometric auth, transfers, bill pay, and investment tracking',
            'tech_stack', jsonb_build_array('React Native', 'Node.js', 'PostgreSQL', 'Redis', 'AWS'),
            'team_size', 12,
            'sprint_length', 2,
            'start_date', '2025-11-01',
            'target_release', '2026-06-15'
        ),
        NOW() - INTERVAL '60 days',
        NOW()
    );

    -- Create 120 realistic requirements (epics) with varied progress
    FOR i IN 1..120 LOOP
        -- Vary status: ~25% done, ~30% in_progress, ~45% todo (realistic for large project)
        v_status := CASE 
            WHEN i <= 30 THEN 'done'
            WHEN i <= 66 THEN 'in_progress'
            ELSE 'todo'
        END;
        
        v_priority := CASE 
            WHEN i <= 40 THEN 'high'
            WHEN i <= 80 THEN 'medium'
            ELSE 'low'
        END;
        
        INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, created_at, updated_at, item_metadata)
        VALUES (
            gen_random_uuid()::text,
            v_project_id,
            'REQ-' || LPAD(i::text, 3, '0') || ': ' || CASE 
                WHEN i <= 12 THEN CASE i
                    WHEN 1 THEN 'User Authentication & Security'
                    WHEN 2 THEN 'Account Management & Profile'
                    WHEN 3 THEN 'Money Transfers & Payments'
                    WHEN 4 THEN 'Bill Payment System'
                    WHEN 5 THEN 'Investment Portfolio Management'
                    WHEN 6 THEN 'Transaction History & Statements'
                    WHEN 7 THEN 'Budgeting & Spending Analytics'
                    WHEN 8 THEN 'Push Notifications & Alerts'
                    WHEN 9 THEN 'Customer Support Integration'
                    WHEN 10 THEN 'Card Management & Controls'
                    WHEN 11 THEN 'Savings Goals & Round-ups'
                    ELSE 'Multi-Currency Support'
                END
                WHEN i <= 24 THEN CASE (i - 12)
                    WHEN 1 THEN 'Loan Application & Management'
                    WHEN 2 THEN 'Credit Score Monitoring'
                    WHEN 3 THEN 'Mortgage Calculator & Tools'
                    WHEN 4 THEN 'Insurance Product Integration'
                    WHEN 5 THEN 'Rewards Program Management'
                    WHEN 6 THEN 'Check Deposit via Mobile'
                    WHEN 7 THEN 'ATM & Branch Locator'
                    WHEN 8 THEN 'Account Opening Flow'
                    WHEN 9 THEN 'KYC & Identity Verification'
                    WHEN 10 THEN 'Document Management System'
                    WHEN 11 THEN 'Tax Document Aggregation'
                    ELSE 'Financial Planning Tools'
                END
                WHEN i <= 36 THEN CASE (i - 24)
                    WHEN 1 THEN 'Fraud Detection & Prevention'
                    WHEN 2 THEN 'Risk Assessment Engine'
                    WHEN 3 THEN 'Compliance Reporting'
                    WHEN 4 THEN 'Audit Trail & Logging'
                    WHEN 5 THEN 'Data Encryption & Security'
                    WHEN 6 THEN 'Access Control & Permissions'
                    WHEN 7 THEN 'Session Management'
                    WHEN 8 THEN 'API Security & Rate Limiting'
                    WHEN 9 THEN 'Data Backup & Recovery'
                    WHEN 10 THEN 'Disaster Recovery Planning'
                    WHEN 11 THEN 'Security Incident Response'
                    ELSE 'Vulnerability Management'
                END
                WHEN i <= 48 THEN CASE (i - 36)
                    WHEN 1 THEN 'Real-Time Payment Processing'
                    WHEN 2 THEN 'Payment Gateway Integration'
                    WHEN 3 THEN 'Recurring Payment Management'
                    WHEN 4 THEN 'Payment Dispute Resolution'
                    WHEN 5 THEN 'Payment Analytics & Reporting'
                    WHEN 6 THEN 'Merchant Payment Solutions'
                    WHEN 7 THEN 'QR Code Payment Support'
                    WHEN 8 THEN 'NFC & Contactless Payments'
                    WHEN 9 THEN 'Payment Scheduling & Automation'
                    WHEN 10 THEN 'Payment Limits & Controls'
                    WHEN 11 THEN 'Payment History & Reconciliation'
                    ELSE 'Payment Failure Handling'
                END
                WHEN i <= 60 THEN CASE (i - 48)
                    WHEN 1 THEN 'Account Aggregation Service'
                    WHEN 2 THEN 'Spending Pattern Analysis'
                    WHEN 3 THEN 'Financial Health Score'
                    WHEN 4 THEN 'Goal-Based Savings'
                    WHEN 5 THEN 'Expense Categorization AI'
                    WHEN 6 THEN 'Cash Flow Forecasting'
                    WHEN 7 THEN 'Debt Payoff Calculator'
                    WHEN 8 THEN 'Retirement Planning Tools'
                    WHEN 9 THEN 'Education Savings Planner'
                    WHEN 10 THEN 'Emergency Fund Tracker'
                    WHEN 11 THEN 'Net Worth Calculator'
                    ELSE 'Financial Wellness Dashboard'
                END
                WHEN i <= 72 THEN CASE (i - 60)
                    WHEN 1 THEN 'Investment Research & Analysis'
                    WHEN 2 THEN 'Portfolio Rebalancing'
                    WHEN 3 THEN 'Tax-Loss Harvesting'
                    WHEN 4 THEN 'Dividend Tracking'
                    WHEN 5 THEN 'Options Trading Support'
                    WHEN 6 THEN 'Cryptocurrency Integration'
                    WHEN 7 THEN 'ESG Investment Filtering'
                    WHEN 8 THEN 'Investment Alerts & Notifications'
                    WHEN 9 THEN 'Performance Benchmarking'
                    WHEN 10 THEN 'Tax Optimization Strategies'
                    WHEN 11 THEN 'Investment Goal Tracking'
                    ELSE 'Social Trading Features'
                END
                WHEN i <= 84 THEN CASE (i - 72)
                    WHEN 1 THEN 'Mobile App Performance Optimization'
                    WHEN 2 THEN 'Offline Mode Support'
                    WHEN 3 THEN 'Progressive Web App Features'
                    WHEN 4 THEN 'Dark Mode & Theming'
                    WHEN 5 THEN 'Accessibility Enhancements'
                    WHEN 6 THEN 'Multi-Language Support'
                    WHEN 7 THEN 'Voice Command Integration'
                    WHEN 8 THEN 'Biometric Quick Actions'
                    WHEN 9 THEN 'Widget & Shortcuts Support'
                    WHEN 10 THEN 'Apple Watch Integration'
                    WHEN 11 THEN 'Android Wear Integration'
                    ELSE 'Smart Home Device Integration'
                END
                WHEN i <= 96 THEN CASE (i - 84)
                    WHEN 1 THEN 'Marketing Campaign Management'
                    WHEN 2 THEN 'Personalized Offers Engine'
                    WHEN 3 THEN 'Referral Program System'
                    WHEN 4 THEN 'Loyalty Points Management'
                    WHEN 5 THEN 'Promotional Content Delivery'
                    WHEN 6 THEN 'A/B Testing Framework'
                    WHEN 7 THEN 'User Segmentation'
                    WHEN 8 THEN 'Behavioral Analytics'
                    WHEN 9 THEN 'Conversion Funnel Tracking'
                    WHEN 10 THEN 'Email Marketing Integration'
                    WHEN 11 THEN 'SMS Marketing Campaigns'
                    ELSE 'Push Notification Campaigns'
                END
                ELSE CASE (i - 96)
                    WHEN 1 THEN 'Data Analytics Platform'
                    WHEN 2 THEN 'Business Intelligence Dashboard'
                    WHEN 3 THEN 'Customer Journey Mapping'
                    WHEN 4 THEN 'Predictive Analytics Engine'
                    WHEN 5 THEN 'Machine Learning Models'
                    WHEN 6 THEN 'Real-Time Data Streaming'
                    WHEN 7 THEN 'Data Warehouse Integration'
                    WHEN 8 THEN 'ETL Pipeline Management'
                    WHEN 9 THEN 'Data Quality Assurance'
                    WHEN 10 THEN 'Regulatory Reporting Automation'
                    WHEN 11 THEN 'Custom Report Builder'
                    ELSE 'Data Visualization Tools'
                END
            END,
            CASE 
                WHEN i <= 12 THEN CASE i
                    WHEN 1 THEN 'Implement secure biometric authentication (Face ID, Touch ID, fingerprint), multi-factor authentication, session management, and fraud detection capabilities. Must comply with PCI DSS and banking regulations.'
                    WHEN 2 THEN 'Allow users to view and manage account details, update personal information, manage linked accounts, set account preferences, and configure privacy settings.'
                    WHEN 3 THEN 'Enable peer-to-peer transfers, ACH transfers, wire transfers, instant payments, and payment scheduling. Support for Zelle, Venmo integration, and international transfers.'
                    WHEN 4 THEN 'Enable users to pay bills, schedule recurring payments, manage payees, set up autopay, and receive payment reminders. Integration with major billers and utilities.'
                    WHEN 5 THEN 'Provide investment account access, portfolio tracking, market data, trading capabilities, robo-advisor integration, and investment performance analytics.'
                    WHEN 6 THEN 'Display comprehensive transaction history with search and filtering, generate statements, export data, categorize transactions, and provide spending insights.'
                    WHEN 7 THEN 'Offer budgeting tools, spending categorization, expense tracking, financial goal setting, and personalized financial insights and recommendations.'
                    WHEN 8 THEN 'Send real-time push notifications for transactions, account alerts, security events, bill reminders, and personalized financial tips.'
                    WHEN 9 THEN 'Integrate in-app chat support, FAQ system, video call support, ticket management, and knowledge base access.'
                    WHEN 10 THEN 'Allow users to view card details, freeze/unfreeze cards, set spending limits, manage card controls, and report lost/stolen cards.'
                    WHEN 11 THEN 'Enable users to set savings goals, enable round-up features, create savings buckets, and track progress toward financial goals.'
                    ELSE 'Support multiple currencies, currency conversion, international account management, and multi-currency transaction history.'
                END
                ELSE 'Comprehensive requirement covering ' || CASE (i % 12)
                    WHEN 0 THEN 'integration with third-party services, API development, data processing, user interface design, backend services, security implementation, performance optimization, testing framework, deployment pipeline, monitoring and alerting, documentation, and compliance requirements'
                    WHEN 1 THEN 'user experience enhancements, workflow optimization, error handling, data validation, caching strategies, database optimization, and scalability considerations'
                    WHEN 2 THEN 'real-time data synchronization, event-driven architecture, microservices integration, message queue implementation, and distributed system design'
                    WHEN 3 THEN 'mobile platform optimization, native feature integration, platform-specific UI/UX, performance tuning, and battery efficiency'
                    WHEN 4 THEN 'analytics and reporting capabilities, data visualization, business intelligence integration, and actionable insights generation'
                    WHEN 5 THEN 'security hardening, vulnerability assessment, penetration testing, compliance auditing, and security monitoring'
                    WHEN 6 THEN 'payment processing optimization, transaction routing, fee calculation, settlement processing, and reconciliation'
                    WHEN 7 THEN 'customer engagement features, personalization engine, recommendation system, and user retention strategies'
                    WHEN 8 THEN 'infrastructure automation, CI/CD pipeline, containerization, orchestration, and cloud resource management'
                    WHEN 9 THEN 'data governance, privacy controls, GDPR compliance, data retention policies, and consent management'
                    WHEN 10 THEN 'third-party integrations, partner API management, webhook handling, and external service orchestration'
                    ELSE 'advanced features including AI/ML capabilities, predictive analytics, automated decision-making, and intelligent automation'
                END || '. Includes comprehensive planning, design, implementation, testing, deployment, and maintenance considerations.'
            END,
            'REQUIREMENT',
            'requirement',
            v_status,
            v_priority,
            NOW() - INTERVAL '60 days' + (i || ' days')::interval,
            CASE WHEN v_status = 'done' THEN NOW() - INTERVAL '30 days' + (i || ' days')::interval ELSE NOW() END,
            jsonb_build_object(
                'epic_id', 'EPIC-' || LPAD(i::text, 3, '0'),
                'business_value', CASE WHEN i <= 4 THEN 'critical' WHEN i <= 8 THEN 'high' ELSE 'medium' END,
                'complexity', CASE WHEN i <= 3 THEN 'high' WHEN i <= 6 THEN 'medium' ELSE 'low' END,
                'dependencies', CASE WHEN i = 1 THEN jsonb_build_array() ELSE jsonb_build_array('REQ-001') END
            )
        )
        RETURNING id INTO v_req_id;
        
        -- Create 6-10 features per requirement (varies by complexity) - reduced to keep total manageable
        FOR j IN 1..(6 + (i % 5)) LOOP
            v_feat_num := (i - 1) * 10 + j;
            
            -- Vary feature status based on requirement status
            v_status := CASE 
                WHEN i <= 30 AND j <= 4 THEN 'done'
                WHEN i <= 30 AND j <= 7 THEN 'in_progress'
                WHEN i <= 66 AND j <= 2 THEN 'done'
                WHEN i <= 66 AND j <= 5 THEN 'in_progress'
                ELSE 'todo'
            END;
            
            v_priority := CASE 
                WHEN j <= 2 THEN 'high'
                WHEN j <= 5 THEN 'medium'
                ELSE 'low'
            END;
            
            INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, parent_id, created_at, updated_at, item_metadata)
            VALUES (
                gen_random_uuid()::text,
                v_project_id,
                'FEAT-' || LPAD(v_feat_num::text, 3, '0') || ': ' || CASE i
                    WHEN 1 THEN CASE j
                        WHEN 1 THEN 'Biometric Authentication Setup'
                        WHEN 2 THEN 'Multi-Factor Authentication Flow'
                        WHEN 3 THEN 'Session Management & Timeout'
                        WHEN 4 THEN 'Fraud Detection Engine Integration'
                        WHEN 5 THEN 'Password Reset Flow'
                        WHEN 6 THEN 'Security Question Management'
                        WHEN 7 THEN 'Device Trust Management'
                        WHEN 8 THEN 'Login Activity Monitoring'
                        ELSE 'Security Audit Logging'
                    END
                    WHEN 2 THEN CASE j
                        WHEN 1 THEN 'Account Overview Dashboard'
                        WHEN 2 THEN 'Profile Edit & Update'
                        WHEN 3 THEN 'Linked Account Management'
                        WHEN 4 THEN 'Account Settings & Preferences'
                        WHEN 5 THEN 'Privacy Controls'
                        WHEN 6 THEN 'Notification Preferences'
                        WHEN 7 THEN 'Account Verification'
                        ELSE 'Document Upload & Management'
                    END
                    WHEN 3 THEN CASE j
                        WHEN 1 THEN 'P2P Transfer Flow'
                        WHEN 2 THEN 'ACH Transfer Initiation'
                        WHEN 3 THEN 'Wire Transfer Processing'
                        WHEN 4 THEN 'Zelle Integration'
                        WHEN 5 THEN 'Transfer Scheduling'
                        WHEN 6 THEN 'Transfer Limits & Controls'
                        WHEN 7 THEN 'International Transfer Support'
                        ELSE 'Transfer History & Tracking'
                    END
                    WHEN 4 THEN CASE j
                        WHEN 1 THEN 'Bill Pay Dashboard'
                        WHEN 2 THEN 'Add Payee Flow'
                        WHEN 3 THEN 'One-Time Payment'
                        WHEN 4 THEN 'Recurring Payment Setup'
                        WHEN 5 THEN 'Payment Reminders'
                        WHEN 6 THEN 'Payment History'
                        WHEN 7 THEN 'Autopay Management'
                        ELSE 'Biller Directory Integration'
                    END
                    WHEN 5 THEN CASE j
                        WHEN 1 THEN 'Portfolio Overview'
                        WHEN 2 THEN 'Market Data Display'
                        WHEN 3 THEN 'Trade Execution'
                        WHEN 4 THEN 'Performance Analytics'
                        WHEN 5 THEN 'Robo-Advisor Integration'
                        WHEN 6 THEN 'Investment Alerts'
                        WHEN 7 THEN 'Tax Document Access'
                        ELSE 'Investment Research Tools'
                    END
                    WHEN 6 THEN CASE j
                        WHEN 1 THEN 'Transaction List View'
                        WHEN 2 THEN 'Transaction Search & Filter'
                        WHEN 3 THEN 'Statement Generation'
                        WHEN 4 THEN 'Transaction Export'
                        WHEN 5 THEN 'Transaction Categorization'
                        WHEN 6 THEN 'Spending Insights'
                        WHEN 7 THEN 'Transaction Details'
                        ELSE 'Recurring Transaction Detection'
                    END
                    WHEN 7 THEN CASE j
                        WHEN 1 THEN 'Budget Creation & Setup'
                        WHEN 2 THEN 'Spending Tracking'
                        WHEN 3 THEN 'Category Management'
                        WHEN 4 THEN 'Goal Setting Interface'
                        WHEN 5 THEN 'Financial Insights Dashboard'
                        WHEN 6 THEN 'Spending Alerts'
                        WHEN 7 THEN 'Trend Analysis'
                        ELSE 'Recommendation Engine'
                    END
                    WHEN 8 THEN CASE j
                        WHEN 1 THEN 'Transaction Notifications'
                        WHEN 2 THEN 'Account Alert Configuration'
                        WHEN 3 THEN 'Security Event Notifications'
                        WHEN 4 THEN 'Bill Reminder Notifications'
                        WHEN 5 THEN 'Push Notification Settings'
                        WHEN 6 THEN 'Email Notification Preferences'
                        WHEN 7 THEN 'SMS Notification Setup'
                        ELSE 'Notification History'
                    END
                    WHEN 9 THEN CASE j
                        WHEN 1 THEN 'In-App Chat Interface'
                        WHEN 2 THEN 'FAQ Search & Browse'
                        WHEN 3 THEN 'Video Call Support'
                        WHEN 4 THEN 'Ticket Creation & Tracking'
                        WHEN 5 THEN 'Knowledge Base Access'
                        WHEN 6 THEN 'Support History'
                        WHEN 7 THEN 'Feedback Collection'
                        ELSE 'Support Agent Rating'
                    END
                    WHEN 10 THEN CASE j
                        WHEN 1 THEN 'Card List & Details View'
                        WHEN 2 THEN 'Card Freeze/Unfreeze'
                        WHEN 3 THEN 'Spending Limit Controls'
                        WHEN 4 THEN 'Merchant Category Controls'
                        WHEN 5 THEN 'Geographic Controls'
                        WHEN 6 THEN 'Card Replacement Request'
                        WHEN 7 THEN 'Card Activation Flow'
                        ELSE 'Card Usage Analytics'
                    END
                    WHEN 11 THEN CASE j
                        WHEN 1 THEN 'Savings Goal Creation'
                        WHEN 2 THEN 'Round-Up Configuration'
                        WHEN 3 THEN 'Savings Buckets Management'
                        WHEN 4 THEN 'Progress Tracking Dashboard'
                        WHEN 5 THEN 'Goal Achievement Celebrations'
                        WHEN 6 THEN 'Automatic Transfer Rules'
                        WHEN 7 THEN 'Goal Sharing & Social'
                        ELSE 'Savings Insights & Tips'
                    END
                    ELSE CASE j
                        WHEN 1 THEN 'Multi-Currency Account Display'
                        WHEN 2 THEN 'Currency Conversion Calculator'
                        WHEN 3 THEN 'Exchange Rate Display'
                        WHEN 4 THEN 'International Transaction Support'
                        WHEN 5 THEN 'Multi-Currency History'
                        WHEN 6 THEN 'Currency Preferences'
                        WHEN 7 THEN 'FX Fee Transparency'
                        ELSE 'Currency Alerts & Notifications'
                    END
                END,
                'Detailed implementation for ' || CASE i
                    WHEN 1 THEN 'authentication and security feature'
                    WHEN 2 THEN 'account management capability'
                    WHEN 3 THEN 'money transfer functionality'
                    WHEN 4 THEN 'bill payment feature'
                    WHEN 5 THEN 'investment management tool'
                    WHEN 6 THEN 'transaction history feature'
                    WHEN 7 THEN 'budgeting capability'
                    WHEN 8 THEN 'notification system'
                    WHEN 9 THEN 'customer support feature'
                    WHEN 10 THEN 'card management functionality'
                    WHEN 11 THEN 'savings goal feature'
                    ELSE 'multi-currency support'
                END || '. Includes UI components, API integration, business logic, error handling, and user feedback mechanisms.',
                'FEATURE',
                'feature',
                v_status,
                v_priority,
                v_req_id,
                NOW() - INTERVAL '55 days' + ((i * 10 + j) || ' days')::interval,
                CASE WHEN v_status = 'done' THEN NOW() - INTERVAL '25 days' + ((i * 10 + j) || ' days')::interval ELSE NOW() END,
                jsonb_build_object(
                    'feature_id', 'FEAT-' || LPAD(v_feat_num::text, 3, '0'),
                    'story_points', CASE WHEN j <= 3 THEN 8 WHEN j <= 6 THEN 5 ELSE 3 END,
                    'assignee', CASE WHEN (i + j) % 4 = 0 THEN 'sarah.chen' WHEN (i + j) % 4 = 1 THEN 'mike.rodriguez' WHEN (i + j) % 4 = 2 THEN 'emily.johnson' ELSE 'david.kim' END,
                    'sprint', CASE WHEN i <= 3 THEN (j / 3)::int + 1 WHEN i <= 7 THEN (j / 2)::int + 4 ELSE (j / 2)::int + 8 END
                )
            )
            RETURNING id INTO v_feat_id;
            
            -- Create 2-3 tests per feature
            FOR k IN 1..(2 + (j % 2)) LOOP
                INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, parent_id, created_at, updated_at, item_metadata)
                VALUES (
                    gen_random_uuid()::text,
                    v_project_id,
                    'TEST-' || LPAD(((v_feat_num - 1) * 3 + k)::text, 4, '0') || ': ' || CASE k
                        WHEN 1 THEN 'Unit Tests'
                        WHEN 2 THEN 'Integration Tests'
                        ELSE 'E2E Tests'
                    END || ' for FEAT-' || LPAD(v_feat_num::text, 3, '0'),
                    CASE k
                        WHEN 1 THEN 'Comprehensive unit test coverage for business logic, utilities, and helper functions. Includes edge cases and error scenarios.'
                        WHEN 2 THEN 'Integration tests covering API endpoints, database interactions, external service integrations, and data flow validation.'
                        ELSE 'End-to-end tests simulating user workflows, UI interactions, cross-browser testing, and performance validation.'
                    END,
                    'TEST',
                    'test',
                    CASE WHEN v_status = 'done' AND k <= 2 THEN 'done' WHEN v_status = 'in_progress' AND k = 1 THEN 'done' ELSE 'todo' END,
                    'high',
                    v_feat_id,
                    NOW() - INTERVAL '50 days' + ((v_feat_num * 3 + k) || ' days')::interval,
                    NOW(),
                    jsonb_build_object(
                        'test_type', CASE k WHEN 1 THEN 'unit' WHEN 2 THEN 'integration' ELSE 'e2e' END,
                        'coverage_target', CASE k WHEN 1 THEN 90 WHEN 2 THEN 80 ELSE 70 END,
                        'framework', CASE k WHEN 1 THEN 'Jest' WHEN 2 THEN 'Jest + Supertest' ELSE 'Playwright' END
                    )
                );
            END LOOP;
            
            -- Create 1 API endpoint per feature
            INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, parent_id, created_at, updated_at, item_metadata)
            VALUES (
                gen_random_uuid()::text,
                v_project_id,
                'API-' || LPAD(v_feat_num::text, 3, '0') || ': REST Endpoint',
                'RESTful API endpoint implementation with request validation, authentication, authorization, error handling, rate limiting, and comprehensive documentation.',
                'API',
                'api',
                CASE WHEN v_status = 'done' THEN 'done' WHEN v_status = 'in_progress' THEN 'in_progress' ELSE 'todo' END,
                'medium',
                v_feat_id,
                NOW() - INTERVAL '48 days' + (v_feat_num || ' days')::interval,
                NOW(),
                jsonb_build_object(
                    'method', CASE WHEN j % 4 = 0 THEN 'POST' WHEN j % 4 = 1 THEN 'GET' WHEN j % 4 = 2 THEN 'PUT' ELSE 'DELETE' END,
                    'path', '/api/v1/' || CASE i
                        WHEN 1 THEN 'auth'
                        WHEN 2 THEN 'accounts'
                        WHEN 3 THEN 'transfers'
                        WHEN 4 THEN 'bills'
                        WHEN 5 THEN 'investments'
                        WHEN 6 THEN 'transactions'
                        WHEN 7 THEN 'budgets'
                        WHEN 8 THEN 'notifications'
                        WHEN 9 THEN 'support'
                        WHEN 10 THEN 'cards'
                        WHEN 11 THEN 'savings'
                        ELSE 'currency'
                    END || '/' || LPAD(j::text, 2, '0'),
                    'auth_required', true,
                    'rate_limit', (j * 100)::text || '/minute'
                )
            )
            RETURNING id INTO v_api_id;
        END LOOP;
        
        -- Create 4-6 database schemas per requirement
        FOR j IN 1..(4 + (i % 3)) LOOP
            INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, parent_id, created_at, updated_at, item_metadata)
            VALUES (
                gen_random_uuid()::text,
                v_project_id,
                'DB-' || LPAD(((i - 1) * 10 + j)::text, 3, '0') || ': ' || CASE j
                    WHEN 1 THEN 'User Schema'
                    WHEN 2 THEN 'Account Schema'
                    WHEN 3 THEN 'Transaction Schema'
                    WHEN 4 THEN 'Security Schema'
                    WHEN 5 THEN 'Audit Schema'
                    WHEN 6 THEN 'Configuration Schema'
                    WHEN 7 THEN 'Notification Schema'
                    WHEN 8 THEN 'Analytics Schema'
                    ELSE 'Integration Schema'
                END,
                'Database schema design with tables, indexes, constraints, foreign keys, and migration scripts. Includes performance optimization and data retention policies.',
                'DATABASE',
                'database',
                CASE WHEN i <= 3 AND j <= 5 THEN 'done' WHEN i <= 7 AND j <= 3 THEN 'done' ELSE 'todo' END,
                'medium',
                v_req_id,
                NOW() - INTERVAL '45 days' + ((i * 10 + j) || ' days')::interval,
                NOW(),
                jsonb_build_object(
                    'schema_name', 'req_' || LPAD(i::text, 2, '0') || '_' || LPAD(j::text, 2, '0'),
                    'tables_count', (j * 3),
                    'indexes_count', (j * 5),
                    'migration_version', '001_' || LPAD(i::text, 2, '0') || '_' || LPAD(j::text, 2, '0')
                )
            )
            RETURNING id INTO v_db_id;
        END LOOP;
        
        -- Create 3-5 UI components per requirement
        FOR j IN 1..(3 + (i % 3)) LOOP
            INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, parent_id, created_at, updated_at, item_metadata)
            VALUES (
                gen_random_uuid()::text,
                v_project_id,
                'COMP-' || LPAD(((i - 1) * 10 + j)::text, 3, '0') || ': ' || CASE j % 4
                    WHEN 0 THEN 'Form Component'
                    WHEN 1 THEN 'Display Component'
                    WHEN 2 THEN 'Interactive Component'
                    ELSE 'Navigation Component'
                END,
                'Reusable React Native component with TypeScript, accessibility support, responsive design, error handling, loading states, and comprehensive prop documentation.',
                'COMPONENT',
                'component',
                CASE WHEN i <= 4 AND j <= 4 THEN 'done' WHEN i <= 7 AND j <= 3 THEN 'in_progress' ELSE 'todo' END,
                'low',
                v_req_id,
                NOW() - INTERVAL '40 days' + ((i * 10 + j) || ' days')::interval,
                NOW(),
                jsonb_build_object(
                    'component_type', CASE j % 4 WHEN 0 THEN 'form' WHEN 1 THEN 'display' WHEN 2 THEN 'interactive' ELSE 'navigation' END,
                    'framework', 'React Native',
                    'accessibility_level', 'WCAG 2.1 AA',
                    'test_coverage', (70 + (j * 5))::text || '%'
                )
            )
            RETURNING id INTO v_comp_id;
        END LOOP;
        
        -- Create 3-5 documentation items per requirement
        FOR j IN 1..(3 + (i % 3)) LOOP
            INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, parent_id, created_at, updated_at, item_metadata)
            VALUES (
                gen_random_uuid()::text,
                v_project_id,
                'DOC-' || LPAD(((i - 1) * 10 + j)::text, 3, '0') || ': ' || CASE j % 4
                    WHEN 0 THEN 'Technical Specification'
                    WHEN 1 THEN 'API Documentation'
                    WHEN 2 THEN 'User Guide'
                    ELSE 'Developer Guide'
                END,
                CASE j % 4
                    WHEN 0 THEN 'Comprehensive technical specification document covering architecture, data models, algorithms, and implementation details.'
                    WHEN 1 THEN 'Complete API documentation with endpoints, request/response schemas, authentication, error codes, and code examples.'
                    WHEN 2 THEN 'User-facing documentation with step-by-step guides, screenshots, FAQs, and troubleshooting tips.'
                    ELSE 'Developer onboarding guide with setup instructions, coding standards, testing guidelines, and contribution workflow.'
                END,
                'DOCUMENTATION',
                'documentation',
                CASE WHEN i <= 5 AND j <= 5 THEN 'done' ELSE 'todo' END,
                'low',
                v_req_id,
                NOW() - INTERVAL '35 days' + ((i * 10 + j) || ' days')::interval,
                NOW(),
                jsonb_build_object(
                    'doc_type', CASE j % 4 WHEN 0 THEN 'technical_spec' WHEN 1 THEN 'api_docs' WHEN 2 THEN 'user_guide' ELSE 'dev_guide' END,
                    'format', 'Markdown',
                    'pages', (j * 5),
                    'last_reviewed', CASE WHEN j <= 5 THEN (NOW() - INTERVAL '10 days')::text ELSE NULL END
                )
            )
            RETURNING id INTO v_doc_id;
        END LOOP;
        
        -- Create 4-6 security items per requirement
        FOR j IN 1..(4 + (i % 3)) LOOP
            INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, parent_id, created_at, updated_at, item_metadata)
            VALUES (
                gen_random_uuid()::text,
                v_project_id,
                'SEC-' || LPAD(((i - 1) * 10 + j)::text, 3, '0') || ': ' || CASE j
                    WHEN 1 THEN 'Security Review'
                    WHEN 2 THEN 'Penetration Testing'
                    WHEN 3 THEN 'Vulnerability Assessment'
                    WHEN 4 THEN 'Compliance Audit'
                    WHEN 5 THEN 'Security Training'
                    ELSE 'Incident Response Plan'
                END,
                CASE j
                    WHEN 1 THEN 'Comprehensive security review covering authentication, authorization, data encryption, and secure coding practices.'
                    WHEN 2 THEN 'Penetration testing to identify vulnerabilities, attack vectors, and security weaknesses in the application.'
                    WHEN 3 THEN 'Automated vulnerability scanning and manual security assessment of code, infrastructure, and dependencies.'
                    WHEN 4 THEN 'Compliance audit to ensure adherence to PCI DSS, GDPR, and banking regulations.'
                    WHEN 5 THEN 'Security awareness training for development team covering OWASP Top 10 and secure development practices.'
                    ELSE 'Incident response procedures, escalation paths, and recovery plans for security breaches.'
                END,
                'SECURITY',
                'security',
                CASE WHEN i <= 3 AND j <= 3 THEN 'done' WHEN i <= 6 AND j <= 2 THEN 'in_progress' ELSE 'todo' END,
                'high',
                v_req_id,
                NOW() - INTERVAL '30 days' + ((i * 10 + j) || ' days')::interval,
                NOW(),
                jsonb_build_object(
                    'security_level', CASE WHEN j <= 2 THEN 'critical' WHEN j <= 4 THEN 'high' ELSE 'medium' END,
                    'compliance_standard', CASE WHEN j <= 3 THEN 'PCI DSS' WHEN j <= 5 THEN 'GDPR' ELSE 'SOC 2' END,
                    'risk_score', (j * 2)::text
                )
            )
            RETURNING id INTO v_sec_id;
        END LOOP;
        
        -- Create 4-6 performance items per requirement
        FOR j IN 1..(4 + (i % 3)) LOOP
            INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, parent_id, created_at, updated_at, item_metadata)
            VALUES (
                gen_random_uuid()::text,
                v_project_id,
                'PERF-' || LPAD(((i - 1) * 10 + j)::text, 3, '0') || ': ' || CASE j
                    WHEN 1 THEN 'Load Testing'
                    WHEN 2 THEN 'Performance Optimization'
                    WHEN 3 THEN 'Caching Strategy'
                    WHEN 4 THEN 'Database Query Optimization'
                    WHEN 5 THEN 'API Response Time Optimization'
                    ELSE 'Memory Leak Detection'
                END,
                CASE j
                    WHEN 1 THEN 'Load testing to validate system performance under expected and peak load conditions. Target: <2s response time for 95th percentile.'
                    WHEN 2 THEN 'Code profiling and optimization to improve rendering performance, reduce bundle size, and optimize asset loading.'
                    WHEN 3 THEN 'Implementation of caching strategies for API responses, database queries, and static assets to reduce latency.'
                    WHEN 4 THEN 'Database query optimization including index tuning, query rewriting, and connection pooling.'
                    WHEN 5 THEN 'API endpoint optimization focusing on response time, payload size reduction, and efficient data serialization.'
                    ELSE 'Memory profiling and leak detection to ensure stable long-term performance and prevent crashes.'
                END,
                'PERFORMANCE',
                'performance',
                CASE WHEN i <= 4 AND j <= 4 THEN 'done' WHEN i <= 7 AND j <= 2 THEN 'in_progress' ELSE 'todo' END,
                'medium',
                v_req_id,
                NOW() - INTERVAL '25 days' + ((i * 10 + j) || ' days')::interval,
                NOW(),
                jsonb_build_object(
                    'target_latency', (j * 50)::text || 'ms',
                    'target_throughput', (j * 1000)::text || ' req/s',
                    'optimization_area', CASE j WHEN 1 THEN 'load' WHEN 2 THEN 'code' WHEN 3 THEN 'caching' WHEN 4 THEN 'database' WHEN 5 THEN 'api' ELSE 'memory' END
                )
            )
            RETURNING id INTO v_perf_id;
        END LOOP;
        
        -- Create 5-7 deployment items per requirement
        FOR j IN 1..(5 + (i % 3)) LOOP
            INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, parent_id, created_at, updated_at, item_metadata)
            VALUES (
                gen_random_uuid()::text,
                v_project_id,
                'DEPLOY-' || LPAD(((i - 1) * 10 + j)::text, 3, '0') || ': ' || CASE j % 3
                    WHEN 0 THEN 'Production Deployment'
                    WHEN 1 THEN 'Staging Deployment'
                    ELSE 'Development Environment'
                END,
                CASE j % 3
                    WHEN 0 THEN 'Production deployment configuration with blue-green deployment, rollback procedures, monitoring, and alerting.'
                    WHEN 1 THEN 'Staging environment setup for QA testing, integration testing, and pre-production validation.'
                    ELSE 'Development environment configuration with local setup, Docker containers, and development tooling.'
                END,
                'DEPLOYMENT',
                'deployment',
                CASE WHEN i <= 5 AND j <= 5 THEN 'done' ELSE 'todo' END,
                'medium',
                v_req_id,
                NOW() - INTERVAL '20 days' + ((i * 10 + j) || ' days')::interval,
                NOW(),
                jsonb_build_object(
                    'environment', CASE j % 3 WHEN 0 THEN 'production' WHEN 1 THEN 'staging' ELSE 'development' END,
                    'infrastructure', 'AWS',
                    'deployment_method', CASE j % 3 WHEN 0 THEN 'blue-green' WHEN 1 THEN 'canary' ELSE 'direct' END,
                    'auto_scaling', CASE WHEN j % 3 = 0 THEN true ELSE false END
                )
            )
            RETURNING id INTO v_deploy_id;
        END LOOP;
    END LOOP;

    -- Create comprehensive traceability links
    -- Requirements -> Features
    INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, created_at, link_metadata)
    SELECT gen_random_uuid()::text, v_project_id, req.id, feat.id, 'implements', NOW(), jsonb_build_object('strength', 'strong')
    FROM items req JOIN items feat ON feat.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.item_type = 'requirement' AND feat.project_id = v_project_id AND feat.item_type = 'feature';

    -- Features -> Tests
    INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, created_at, link_metadata)
    SELECT gen_random_uuid()::text, v_project_id, feat.id, test.id, 'tested_by', NOW(), jsonb_build_object('coverage', 'comprehensive')
    FROM items feat JOIN items test ON test.parent_id = feat.id
    WHERE feat.project_id = v_project_id AND feat.item_type = 'feature' AND test.project_id = v_project_id AND test.item_type = 'test';

    -- Features -> APIs
    INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, created_at, link_metadata)
    SELECT gen_random_uuid()::text, v_project_id, feat.id, api.id, 'exposes', NOW(), jsonb_build_object('version', 'v1')
    FROM items feat JOIN items api ON api.parent_id = feat.id
    WHERE feat.project_id = v_project_id AND feat.item_type = 'feature' AND api.project_id = v_project_id AND api.item_type = 'api';

    -- Requirements -> Databases
    INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, created_at, link_metadata)
    SELECT gen_random_uuid()::text, v_project_id, req.id, db.id, 'requires', NOW(), jsonb_build_object('dependency_type', 'data')
    FROM items req JOIN items db ON db.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.item_type = 'requirement' AND db.project_id = v_project_id AND db.item_type = 'database';

    -- Requirements -> Components
    INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, created_at, link_metadata)
    SELECT gen_random_uuid()::text, v_project_id, req.id, comp.id, 'uses', NOW(), jsonb_build_object('usage', 'ui')
    FROM items req JOIN items comp ON comp.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.item_type = 'requirement' AND comp.project_id = v_project_id AND comp.item_type = 'component';

    -- Requirements -> Documentation
    INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, created_at, link_metadata)
    SELECT gen_random_uuid()::text, v_project_id, req.id, doc.id, 'documented_by', NOW(), jsonb_build_object('doc_type', 'technical')
    FROM items req JOIN items doc ON doc.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.item_type = 'requirement' AND doc.project_id = v_project_id AND doc.item_type = 'documentation';

    -- Requirements -> Security
    INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, created_at, link_metadata)
    SELECT gen_random_uuid()::text, v_project_id, req.id, sec.id, 'secured_by', NOW(), jsonb_build_object('security_level', 'high')
    FROM items req JOIN items sec ON sec.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.item_type = 'requirement' AND sec.project_id = v_project_id AND sec.item_type = 'security';

    -- Requirements -> Performance
    INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, created_at, link_metadata)
    SELECT gen_random_uuid()::text, v_project_id, req.id, perf.id, 'optimized_by', NOW(), jsonb_build_object('optimization_type', 'performance')
    FROM items req JOIN items perf ON perf.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.item_type = 'requirement' AND perf.project_id = v_project_id AND perf.item_type = 'performance';

    -- Requirements -> Deployment
    INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, created_at, link_metadata)
    SELECT gen_random_uuid()::text, v_project_id, req.id, deploy.id, 'deployed_by', NOW(), jsonb_build_object('environment', 'production')
    FROM items req JOIN items deploy ON deploy.parent_id = req.id
    WHERE req.project_id = v_project_id AND req.item_type = 'requirement' AND deploy.project_id = v_project_id AND deploy.item_type = 'deployment';

    -- Cross-feature dependencies (some features depend on others)
    -- Use row_number to create dependencies between features
    INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, created_at, link_metadata)
    SELECT gen_random_uuid()::text, v_project_id, f1.id, f2.id, 'depends_on', NOW(), jsonb_build_object('dependency_type', 'functional')
    FROM (
        SELECT id, parent_id, ROW_NUMBER() OVER (PARTITION BY parent_id ORDER BY created_at) as rn
        FROM items
        WHERE project_id = v_project_id AND item_type = 'feature'
    ) f1
    JOIN (
        SELECT id, parent_id, ROW_NUMBER() OVER (PARTITION BY parent_id ORDER BY created_at) as rn
        FROM items
        WHERE project_id = v_project_id AND item_type = 'feature'
    ) f2 ON f2.parent_id = f1.parent_id AND f2.rn < f1.rn AND f1.rn % 3 = 0;

    RETURN v_project_id;
END;
$$ LANGUAGE plpgsql;

-- Create the Mobile Banking App project
SELECT create_realistic_mobile_banking_project();

-- Re-enable triggers
ALTER TABLE projects ENABLE TRIGGER ALL;
ALTER TABLE items ENABLE TRIGGER ALL;
ALTER TABLE links ENABLE TRIGGER ALL;

-- Summary query
SELECT 
    p.name,
    COUNT(DISTINCT i.id) as total_items,
    COUNT(DISTINCT CASE WHEN i.item_type = 'requirement' THEN i.id END) as requirements,
    COUNT(DISTINCT CASE WHEN i.item_type = 'feature' THEN i.id END) as features,
    COUNT(DISTINCT CASE WHEN i.item_type = 'test' THEN i.id END) as tests,
    COUNT(DISTINCT CASE WHEN i.item_type = 'api' THEN i.id END) as apis,
    COUNT(DISTINCT CASE WHEN i.item_type = 'database' THEN i.id END) as databases,
    COUNT(DISTINCT CASE WHEN i.item_type = 'component' THEN i.id END) as components,
    COUNT(DISTINCT CASE WHEN i.item_type = 'documentation' THEN i.id END) as documentation,
    COUNT(DISTINCT CASE WHEN i.item_type = 'security' THEN i.id END) as security,
    COUNT(DISTINCT CASE WHEN i.item_type = 'performance' THEN i.id END) as performance,
    COUNT(DISTINCT CASE WHEN i.item_type = 'deployment' THEN i.id END) as deployment,
    COUNT(DISTINCT CASE WHEN i.status = 'done' THEN i.id END) as completed,
    COUNT(DISTINCT CASE WHEN i.status = 'in_progress' THEN i.id END) as in_progress,
    COUNT(DISTINCT l.id) as total_links
FROM projects p
LEFT JOIN items i ON i.project_id = p.id AND i.deleted_at IS NULL
LEFT JOIN links l ON (l.source_item_id = i.id OR l.target_item_id = i.id)
WHERE p.name = 'Mobile Banking App'
GROUP BY p.id, p.name;
