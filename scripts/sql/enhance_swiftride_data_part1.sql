-- ==============================================================================
-- SwiftRide Project Data Enhancement Script - Part 1
-- Business & Product Layers
-- ==============================================================================
-- Project ID: cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e
-- ==============================================================================

BEGIN;

-- Disable triggers for faster bulk insert
SET session_replication_role = replica;

-- ==============================================================================
-- BUSINESS LAYER: Business Objectives, KPIs, Market Segments, Personas
-- ==============================================================================

-- Business Objectives (20 items)
INSERT INTO items (id, project_id, type, title, description, status, priority, metadata, tags) VALUES
('10000001-0001-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective', 'Achieve 40% Market Share in Top 50 Cities', 'Become the leading ride-sharing platform with dominant market position', 'in_progress', 1, '{"target_date": "2027-12-31", "kpi": "market_share", "target": 40, "current": 12}', ARRAY['strategic', 'growth']),
('10000001-0002-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective', 'Scale to $5B Annual Recurring Revenue', 'Drive revenue growth through user acquisition and service expansion', 'in_progress', 1, '{"target_date": "2027-12-31", "kpi": "arr", "target": 5000000000}', ARRAY['strategic', 'revenue']),
('10000001-0003-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective', 'Driver Satisfaction Above 4.5 Stars', 'Maintain high driver satisfaction through fair compensation and support', 'in_progress', 2, '{"target_date": "2026-12-31", "kpi": "driver_satisfaction", "target": 4.5, "current": 4.2}', ARRAY['drivers', 'satisfaction']),
('10000001-0004-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective', 'Carbon Neutral Operations by 2028', 'Achieve 100% carbon neutrality through EV adoption and offsets', 'planned', 2, '{"target_date": "2028-12-31", "kpi": "carbon_neutral", "target": 100}', ARRAY['sustainability', 'esg']),
('10000001-0005-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective', 'Zero Safety Fatalities', 'Eliminate all fatal accidents through technology and training', 'in_progress', 1, '{"target_date": "2027-12-31", "kpi": "fatality_rate", "target": 0}', ARRAY['safety', 'critical']);

-- KPIs (30 items)
INSERT INTO items (id, project_id, type, title, description, status, priority, metadata, tags) VALUES
('10000002-0001-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'kpi', 'Gross Booking Value (GBV)', 'Total dollar value of all rides booked through platform', 'active', 1, '{"unit": "USD", "frequency": "monthly", "target": 500000000, "current": 120000000}', ARRAY['revenue', 'financial']),
('10000002-0002-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'kpi', 'Take Rate Percentage', 'Commission percentage of GBV retained as revenue', 'active', 1, '{"unit": "percent", "frequency": "monthly", "target": 25, "current": 22.5}', ARRAY['revenue', 'unit-economics']),
('10000002-0003-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'kpi', 'Monthly Active Riders (MAR)', 'Unique riders completing at least one ride per month', 'active', 1, '{"unit": "count", "frequency": "monthly", "target": 15000000, "current": 3500000}', ARRAY['growth', 'engagement']),
('10000002-0004-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'kpi', 'Monthly Active Drivers (MAD)', 'Unique drivers completing at least one ride per month', 'active', 1, '{"unit": "count", "frequency": "monthly", "target": 500000, "current": 125000}', ARRAY['supply', 'drivers']),
('10000002-0005-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'kpi', 'Rides Per Day', 'Average completed rides daily', 'active', 2, '{"unit": "count", "frequency": "daily", "target": 5000000, "current": 1200000}', ARRAY['operations', 'volume']),
('10000002-0006-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'kpi', 'Average Wait Time', 'Time from request to driver arrival', 'active', 2, '{"unit": "seconds", "frequency": "hourly", "target": 240, "current": 320}', ARRAY['experience', 'efficiency']),
('10000002-0007-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'kpi', 'Rider Star Rating', 'Average star rating given by riders', 'active', 2, '{"unit": "stars", "frequency": "daily", "target": 4.8, "current": 4.6}', ARRAY['quality', 'satisfaction']),
('10000002-0008-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'kpi', 'Driver Star Rating', 'Average star rating given by drivers', 'active', 2, '{"unit": "stars", "frequency": "daily", "target": 4.5, "current": 4.2}', ARRAY['quality', 'drivers']),
('10000002-0009-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'kpi', 'Cancellation Rate', 'Percentage of rides canceled before pickup', 'active', 2, '{"unit": "percent", "frequency": "daily", "target": 5, "current": 8.2}', ARRAY['quality', 'experience']),
('10000002-0010-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'kpi', 'Driver Utilization Rate', 'Percentage of time drivers have passengers', 'active', 2, '{"unit": "percent", "frequency": "daily", "target": 60, "current": 45}', ARRAY['efficiency', 'operations']);

-- Market Segments (15 items)
INSERT INTO items (id, project_id, type, title, description, status, priority, metadata, tags) VALUES
('10000003-0001-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'market_segment', 'Daily Commuters', 'Professionals using ride-sharing for work commutes', 'active', 1, '{"size": 8000000, "growth_rate": 15, "avg_spend": 450}', ARRAY['b2c', 'commute']),
('10000003-0002-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'market_segment', 'Airport Travelers', 'Travelers needing airport transportation', 'active', 1, '{"size": 3000000, "growth_rate": 20, "avg_spend": 65}', ARRAY['b2c', 'travel']),
('10000003-0003-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'market_segment', 'Night Life & Entertainment', 'Users going to bars, restaurants, events', 'active', 2, '{"size": 5000000, "growth_rate": 10, "avg_spend": 35}', ARRAY['b2c', 'entertainment']),
('10000003-0004-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'market_segment', 'Corporate Accounts', 'Businesses providing ride credits to employees', 'active', 1, '{"size": 50000, "growth_rate": 25, "avg_spend": 25000}', ARRAY['b2b', 'enterprise']),
('10000003-0005-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'market_segment', 'Seniors & Accessibility', 'Elderly and disabled riders needing accessible transport', 'active', 2, '{"size": 2000000, "growth_rate": 30, "avg_spend": 200}', ARRAY['accessibility', 'social-impact']);

-- User Personas (20 items)
INSERT INTO items (id, project_id, type, title, description, status, priority, metadata, tags) VALUES
('10000004-0001-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'persona', 'Sarah - Daily Commuter', 'Marketing Manager, 32, uses SwiftRide twice daily for work', 'active', 1, '{"age": 32, "income": 85000, "tech_savvy": "high", "frequency": "daily"}', ARRAY['rider', 'commuter']),
('10000004-0002-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'persona', 'Marcus - Part-Time Driver', 'College student, 22, drives 20 hours/week for income', 'active', 1, '{"age": 22, "income": 25000, "hours_per_week": 20}', ARRAY['driver', 'part-time']),
('10000004-0003-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'persona', 'James - Full-Time Driver', 'Professional driver, 45, drives 50+ hours/week', 'active', 1, '{"age": 45, "income": 55000, "hours_per_week": 55}', ARRAY['driver', 'full-time']),
('10000004-0004-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'persona', 'Emily - Corporate Admin', 'HR Manager, 38, manages 500 employee ride accounts', 'active', 2, '{"age": 38, "employees_managed": 500}', ARRAY['b2b', 'decision-maker']),
('10000004-0005-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'persona', 'Robert - Senior Rider', 'Retired teacher, 72, uses for medical appointments', 'active', 2, '{"age": 72, "tech_savvy": "low", "frequency": "weekly"}', ARRAY['rider', 'senior']);

-- Business Rules (25 items)
INSERT INTO items (id, project_id, type, title, description, status, priority, metadata, tags) VALUES
('10000005-0001-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_rule', 'Surge Pricing Activation', 'Activate surge when demand exceeds supply by 30% in zone', 'active', 1, '{"threshold": 30, "unit": "percent", "metric": "demand_supply_ratio"}', ARRAY['pricing', 'operations']),
('10000005-0002-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_rule', 'Driver Background Check Renewal', 'Drivers must renew background check every 12 months', 'active', 1, '{"frequency": "12_months", "type": "background_check"}', ARRAY['compliance', 'safety']),
('10000005-0003-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_rule', 'Minimum Driver Rating', 'Drivers below 4.0 rating get warning; below 3.8 deactivated', 'active', 1, '{"warning_threshold": 4.0, "deactivation_threshold": 3.8}', ARRAY['quality', 'drivers']),
('10000005-0004-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_rule', 'Cancellation Fee Policy', 'Charge $5 if rider cancels after 2 minutes', 'active', 2, '{"fee": 5, "grace_period": 120, "currency": "USD"}', ARRAY['pricing', 'policy']),
('10000005-0005-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_rule', 'Maximum Ride Duration', 'Single rides cannot exceed 8 hours or 500 miles', 'active', 2, '{"max_duration": 28800, "max_distance": 500}', ARRAY['operations', 'safety']);

-- Compliance Requirements (20 items)
INSERT INTO items (id, project_id, type, title, description, status, priority, metadata, tags) VALUES
('10000006-0001-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'compliance', 'CCPA Data Privacy Compliance', 'California Consumer Privacy Act - user data rights', 'active', 1, '{"regulation": "CCPA", "jurisdiction": "California"}', ARRAY['legal', 'privacy']),
('10000006-0002-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'compliance', 'ADA Accessibility Requirements', 'Americans with Disabilities Act compliance', 'active', 1, '{"regulation": "ADA", "jurisdiction": "Federal"}', ARRAY['legal', 'accessibility']),
('10000006-0003-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'compliance', 'PCI-DSS Payment Security', 'Payment Card Industry Data Security Standard', 'active', 1, '{"regulation": "PCI-DSS", "level": "1"}', ARRAY['security', 'payments']),
('10000006-0004-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'compliance', 'City Transportation Permits', 'Municipal operating permits for each city', 'active', 1, '{"renewal": "annual", "cities_count": 50}', ARRAY['legal', 'municipal']),
('10000006-0005-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'compliance', 'GDPR EU Data Protection', 'General Data Protection Regulation compliance', 'active', 1, '{"regulation": "GDPR", "jurisdiction": "EU"}', ARRAY['legal', 'privacy']);

-- Revenue Models (10 items)
INSERT INTO items (id, project_id, type, title, description, status, priority, metadata, tags) VALUES
('10000007-0001-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'revenue_model', 'Per-Ride Commission', 'Standard 25% commission on completed rides', 'active', 1, '{"commission_rate": 25, "unit": "percent"}', ARRAY['revenue', 'primary']),
('10000007-0002-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'revenue_model', 'Subscription Plans', 'Monthly plans for discounted rides and benefits', 'active', 2, '{"plans": ["basic_9.99", "premium_24.99"]}', ARRAY['revenue', 'subscription']),
('10000007-0003-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'revenue_model', 'Cancellation Fees', 'Fees charged for late cancellations', 'active', 3, '{"fee_amount": 5, "monthly_volume": 500000}', ARRAY['revenue', 'fees']),
('10000007-0004-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'revenue_model', 'Advertising Revenue', 'In-app advertising and sponsored locations', 'planned', 3, '{"projected_revenue": 50000000}', ARRAY['revenue', 'advertising']),
('10000007-0005-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'revenue_model', 'Data Analytics Products', 'Anonymized mobility data sales', 'planned', 3, '{"projected_revenue": 25000000}', ARRAY['revenue', 'data']);

-- Pricing Strategies (15 items)
INSERT INTO items (id, project_id, type, title, description, status, priority, metadata, tags) VALUES
('10000008-0001-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'pricing_strategy', 'Dynamic Surge Pricing', 'Real-time pricing with 1.1x to 3.0x multipliers', 'active', 1, '{"min_multiplier": 1.1, "max_multiplier": 3.0}', ARRAY['pricing', 'dynamic']),
('10000008-0002-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'pricing_strategy', 'Time-of-Day Pricing', 'Lower prices during off-peak hours', 'active', 2, '{"off_peak_discount": 15}', ARRAY['pricing', 'temporal']),
('10000008-0003-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'pricing_strategy', 'Distance-Based Pricing', 'Base fare + per-mile + per-minute structure', 'active', 1, '{"base_fare": 2.5, "per_mile": 1.5, "per_minute": 0.25}', ARRAY['pricing', 'distance']),
('10000008-0004-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'pricing_strategy', 'Promotional Discounts', 'New user and referral discounts', 'active', 2, '{"new_user_discount": 10, "referral_credit": 15}', ARRAY['pricing', 'marketing']),
('10000008-0005-0000-0000-000000000000', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'pricing_strategy', 'Corporate Flat Rate', 'Fixed pricing for corporate accounts', 'active', 2, '{"discount_tiers": [10, 15, 20]}', ARRAY['pricing', 'b2b']);

COMMIT;
