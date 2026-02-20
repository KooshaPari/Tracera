-- Business Objectives Batch 3 (Items 31-52)

INSERT INTO tracertm.items (id, project_id, type, title, description, status, priority, metadata, tags, created_at, updated_at)
VALUES

-- Sustainability & Social Responsibility
('d1e1f1a1-0001-4001-a001-000000000031', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective',
'Transition 40% of Fleet to Electric Vehicles',
'Accelerate transition to electric vehicles by increasing EV penetration from current 8% to 40% of active driver fleet by Q4 2026, supporting environmental sustainability goals and reducing per-mile carbon emissions by 35%. Initiative includes: EV driver incentive program ($200/month bonus), charging infrastructure partnerships (discounted/free charging at 1000+ locations), EV purchase financing assistance ($5K subsidy), priority matching for EV riders who request green rides, and carbon offset program for non-EV trips. This supports corporate ESG commitments and appeals to environmentally-conscious rider segment (18% of users prefer EV when available).',
'ACTIVE', 2,
'{"owner": "VP Sustainability", "target_date": "2026-12-31", "success_metrics": ["40% EV fleet", "35% carbon reduction", "1000+ charging locations", "25% EV ride request rate"], "dependencies": ["EV incentive fund", "Charging partnerships", "Green ride feature"], "stakeholders": ["VP Sustainability", "Operations", "Finance", "Marketing"], "budget": "$20M", "risk_level": "MEDIUM"}'::jsonb,
ARRAY['business', 'sustainability', 'ev', 'social-responsibility', 'environment'],
NOW(), NOW()),

('d1e1f1a1-0001-4001-a001-000000000032', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective',
'Launch Community Rides Program in Underserved Areas',
'Expand service to 30 underserved urban and rural communities currently lacking reliable transportation options, providing affordable rides and economic opportunities by Q3 2026. Program features include: 25% reduced fares in qualified low-income areas, driver recruitment focused on community residents (creating 2000+ jobs), partnerships with community organizations, integration with public transit systems, and subsidized rides for essential trips (medical, employment, education). Funding through combination of public-private partnerships, grants, and cross-subsidization from profitable markets. Social impact target: 100K rides monthly in underserved communities.',
'ACTIVE', 2,
'{"owner": "VP Social Impact", "target_date": "2026-09-30", "success_metrics": ["30 underserved communities", "2000+ local driver jobs", "100K monthly community rides", "25% fare reduction"], "dependencies": ["Community partnerships", "Subsidy funding", "Local driver recruitment"], "stakeholders": ["VP Social Impact", "Government Relations", "Operations"], "budget": "$10M", "risk_level": "MEDIUM"}'::jsonb,
ARRAY['business', 'social-impact', 'community', 'accessibility', 'equity'],
NOW(), NOW()),

-- Data & Analytics Objectives
('d1e1f1a1-0001-4001-a001-000000000033', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective',
'Implement Real-Time Analytics Dashboard for All Teams',
'Deploy comprehensive real-time analytics platform providing instant visibility into operational metrics, customer behavior, and business performance for all teams (Operations, Marketing, Finance, Product) by Q2 2026. Platform will process 500M+ daily events with <5 second latency, featuring: customizable dashboards, automated anomaly detection, predictive alerts, cohort analysis tools, A/B testing framework, and mobile executive dashboards. Data sources include: ride transactions, app events, customer interactions, driver activities, financial data, and external datasets. Expected benefits: 40% faster decision-making, 25% improvement in operational efficiency.',
'ACTIVE', 2,
'{"owner": "VP Data & Analytics", "target_date": "2026-06-30", "success_metrics": ["<5s data latency", "500M+ daily events", "100% team adoption", "40% faster decisions"], "dependencies": ["Real-time data pipeline", "Dashboard platform", "Data warehouse scaling"], "stakeholders": ["VP Data", "CTO", "All Department Heads"], "budget": "$7M", "risk_level": "MEDIUM"}'::jsonb,
ARRAY['business', 'analytics', 'data', 'technology', 'decision-support'],
NOW(), NOW()),

('d1e1f1a1-0001-4001-a001-000000000034', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective',
'Achieve 360-Degree Customer Data Platform',
'Build unified customer data platform integrating all touchpoints (app usage, rides, support, marketing, payments, social) providing complete 360-degree customer view by Q4 2026. CDP will enable: hyper-personalized marketing (30% lift in campaign ROI), predictive churn modeling (identify 80% of churners 14 days before churn), lifetime value optimization, real-time segmentation, cross-channel orchestration, and privacy-compliant data management. Platform will unify data from 15+ systems, support 10M+ customer profiles, and enable sub-second profile access. GDPR/CCPA compliant with customer data portability and right to deletion.',
'ACTIVE', 2,
'{"owner": "VP Data & Analytics", "target_date": "2026-12-31", "success_metrics": ["15+ systems integrated", "10M+ unified profiles", "30% marketing ROI lift", "80% churn prediction accuracy"], "dependencies": ["CDP platform selection", "System integrations", "Privacy compliance"], "stakeholders": ["VP Data", "Marketing", "Product", "Legal"], "budget": "$6M", "risk_level": "MEDIUM"}'::jsonb,
ARRAY['business', 'data', 'cdp', 'personalization', 'analytics'],
NOW(), NOW()),

-- International Expansion
('d1e1f1a1-0001-4001-a001-000000000035', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective',
'Launch Operations in 3 International Markets',
'Establish SwiftRide presence in 3 international markets (Canada, UK, Australia) by Q4 2026, targeting combined 200K active riders and $50M annual GMV. Each market launch requires: regulatory compliance and licensing, local payment method integration, currency support, market-specific pricing models, driver recruitment (500+ drivers per market), local partnerships, and market-adapted marketing. Canada focus: Toronto, Vancouver, Montreal. UK focus: London, Manchester. Australia focus: Sydney, Melbourne. Success criteria: achieve profitability within 18 months per market, compliance with all local regulations.',
'ACTIVE', 1,
'{"owner": "VP International", "target_date": "2026-12-31", "success_metrics": ["3 markets launched", "200K international riders", "$50M GMV", "100% regulatory compliance"], "dependencies": ["International team", "Multi-currency support", "Localization"], "stakeholders": ["CEO", "VP International", "Legal", "Finance"], "budget": "$30M", "risk_level": "HIGH"}'::jsonb,
ARRAY['business', 'international', 'expansion', 'growth', 'strategy'],
NOW(), NOW()),

-- Compliance & Risk Management
('d1e1f1a1-0001-4001-a001-000000000036', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective',
'Achieve SOC 2 Type II Certification',
'Complete SOC 2 Type II audit and certification demonstrating enterprise-grade security and privacy controls by Q3 2026, enabling enterprise sales to Fortune 500 companies requiring SOC 2 compliance. Certification scope includes: security controls, availability controls, processing integrity, confidentiality, and privacy. Requirements include: comprehensive security policy documentation, access control implementation, encryption standards, incident response procedures, vendor management, change management, and continuous monitoring. Audit period: 6 months. Expected to unlock $100M+ in enterprise sales opportunities.',
'ACTIVE', 1,
'{"owner": "CISO", "target_date": "2026-09-30", "success_metrics": ["SOC 2 Type II certified", "Zero audit findings", "100% control compliance", "$100M+ sales opportunity"], "dependencies": ["Security controls implementation", "Policy documentation", "Audit engagement"], "stakeholders": ["CISO", "Legal", "Enterprise Sales", "Engineering"], "budget": "$3M", "risk_level": "MEDIUM"}'::jsonb,
ARRAY['business', 'compliance', 'security', 'certification', 'enterprise'],
NOW(), NOW()),

('d1e1f1a1-0001-4001-a001-000000000037', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective',
'Implement Comprehensive Insurance Program',
'Establish best-in-class insurance coverage protecting riders, drivers, and company from all transportation-related risks by Q2 2026. Program includes: $1M liability coverage per incident (industry-leading), comprehensive collision coverage, uninsured motorist protection, gap coverage during app usage, driver injury protection, and parametric insurance for platform downtime. Additionally, implement claims automation reducing claim resolution time from 14 days to 3 days, fraud detection in claims (preventing $5M annual fraud), and driver insurance education program. Total premium budget: $45M annually. Claims management platform with API integration to carriers.',
'ACTIVE', 1,
'{"owner": "VP Risk Management", "target_date": "2026-06-30", "success_metrics": ["$1M liability coverage", "3-day claim resolution", "$5M fraud prevention", "99% claim satisfaction"], "dependencies": ["Insurance carrier partnerships", "Claims platform", "Fraud detection"], "stakeholders": ["VP Risk", "CFO", "Legal", "Operations"], "budget": "$45M annual premium + $2M tech", "risk_level": "HIGH"}'::jsonb,
ARRAY['business', 'insurance', 'risk-management', 'compliance', 'operations'],
NOW(), NOW()),

-- Product Innovation
('d1e1f1a1-0001-4001-a001-000000000038', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective',
'Launch Autonomous Vehicle Pilot Program',
'Deploy autonomous vehicle pilot program in partnership with AV technology provider, operating 50 autonomous vehicles in controlled environment (corporate campus or planned community) by Q4 2026. Pilot objectives: validate AV technology readiness, develop operational procedures, gather rider feedback, train support systems, and prepare for regulatory approval. Target metrics: 10K autonomous rides, 4.5+ star rating, <1 safety disengagement per 1000 miles, $12 average cost per ride (60% below human-driven). Pilot will inform full-scale AV deployment strategy for 2027-2028 targeting 30% cost reduction and 24/7 availability.',
'ACTIVE', 3,
'{"owner": "VP Innovation", "target_date": "2026-12-31", "success_metrics": ["50 AV vehicles deployed", "10K autonomous rides", "<1 disengagement per 1000 mi", "$12 cost per ride"], "dependencies": ["AV technology partner", "Regulatory approval", "Safety systems"], "stakeholders": ["VP Innovation", "CEO", "Legal", "Operations"], "budget": "$25M", "risk_level": "HIGH"}'::jsonb,
ARRAY['business', 'innovation', 'autonomous-vehicles', 'technology', 'future'],
NOW(), NOW()),

('d1e1f1a1-0001-4001-a001-000000000039', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective',
'Develop Multi-Modal Transportation Platform',
'Transform SwiftRide from ride-sharing only to comprehensive multi-modal platform integrating cars, bikes, scooters, and public transit in single app by Q3 2026. Users can plan and pay for entire journey across modes with intelligent routing (fastest/cheapest/greenest options). Integration includes: bike-share partnerships in 20 cities, e-scooter fleet deployment (5000 scooters), public transit journey planning with real-time data, integrated payment for all modes, and carbon footprint tracking. Target: 30% of users utilize 2+ transportation modes monthly. Revenue model: commission on bikes/scooters, transit affiliate fees.',
'ACTIVE', 2,
'{"owner": "VP Product", "target_date": "2026-09-30", "success_metrics": ["4 transport modes integrated", "5000 scooters deployed", "30% multi-modal users", "$15M multi-modal revenue"], "dependencies": ["Bike/scooter partnerships", "Transit API integration", "Multi-modal routing"], "stakeholders": ["VP Product", "Partnerships", "Engineering", "Operations"], "budget": "$18M", "risk_level": "HIGH"}'::jsonb,
ARRAY['business', 'product', 'multi-modal', 'innovation', 'mobility'],
NOW(), NOW()),

-- Workforce & Culture
('d1e1f1a1-0001-4001-a001-000000000040', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective',
'Build Diverse & Inclusive Workforce - 50% Underrepresented Groups',
'Increase representation of underrepresented groups (women, racial minorities, LGBTQ+, people with disabilities) in SwiftRide workforce from current 32% to 50% by Q4 2026, with particular focus on technical and leadership roles. Initiatives include: diverse candidate sourcing partnerships (25+ organizations), bias training for all hiring managers, structured interview processes, diversity recruiting team, inclusive benefits (parental leave, gender transition support, accessibility accommodations), employee resource groups, and mentorship programs. Track representation at all levels with quarterly scorecards. Studies show diverse teams drive 35% better innovation outcomes.',
'ACTIVE', 2,
'{"owner": "Chief People Officer", "target_date": "2026-12-31", "success_metrics": ["50% underrepresented groups", "40% women in tech roles", "30% leadership diversity", "90% inclusion score"], "dependencies": ["Diverse sourcing partnerships", "Bias training program", "ERG establishment"], "stakeholders": ["CPO", "CEO", "All Department Heads"], "budget": "$4M", "risk_level": "MEDIUM"}'::jsonb,
ARRAY['business', 'dei', 'culture', 'workforce', 'social-responsibility'],
NOW(), NOW()),

('d1e1f1a1-0001-4001-a001-000000000041', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective',
'Achieve 90% Employee Engagement Score',
'Improve employee engagement from current 76% to 90% by Q4 2026 through comprehensive workplace culture initiatives, positioning SwiftRide as top-tier employer in tech/transportation sector. Program elements include: competitive compensation (75th percentile for role/market), equity participation (every employee gets stock options), professional development ($3K annual learning budget), flexible work arrangements (hybrid with 2-day office requirement), wellness programs (mental health, fitness, financial planning), career advancement paths, and transparent communication (monthly all-hands, executive office hours). Target: Glassdoor 4.5+ rating, <10% regrettable attrition.',
'ACTIVE', 2,
'{"owner": "Chief People Officer", "target_date": "2026-12-31", "success_metrics": ["90% engagement score", "4.5+ Glassdoor rating", "<10% regrettable attrition", "85% recommend to friend"], "dependencies": ["Engagement program rollout", "Compensation review", "Wellness benefits"], "stakeholders": ["CPO", "Executive Team", "Finance"], "budget": "$8M", "risk_level": "LOW"}'::jsonb,
ARRAY['business', 'culture', 'employee-engagement', 'retention', 'employer-brand'],
NOW(), NOW()),

-- Regulatory & Government Relations
('d1e1f1a1-0001-4001-a001-000000000042', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective',
'Secure Operating Licenses in All 50 States',
'Obtain and maintain ride-sharing operating licenses/permits in all 50 US states plus DC by Q2 2026, ensuring 100% regulatory compliance and eliminating operational risk. Currently licensed in 42 states; 8 states pending (includes complex regulatory environments like NY, MA). Requirements vary by state: TNC permits, insurance certificates, driver background check standards, fee payments, regular reporting. Establish dedicated regulatory affairs team (12 FTE) managing ongoing compliance including: license renewals, regulatory change monitoring, government reporting, audit responses, and legislative advocacy. Non-compliance risk: $50M+ in fines plus operational shutdowns.',
'ACTIVE', 1,
'{"owner": "VP Government Relations", "target_date": "2026-06-30", "success_metrics": ["50 state licenses", "100% compliance", "Zero violations/fines", "Automated compliance reporting"], "dependencies": ["Regulatory affairs team", "Compliance tracking system", "State-specific requirements"], "stakeholders": ["VP Gov Relations", "Legal", "CFO", "Operations"], "budget": "$5M", "risk_level": "HIGH"}'::jsonb,
ARRAY['business', 'compliance', 'regulatory', 'government-relations', 'risk'],
NOW(), NOW()),

('d1e1f1a1-0001-4001-a001-000000000043', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective',
'Establish Driver Classification Legal Framework',
'Proactively work with policymakers to establish fair, sustainable driver classification framework (independent contractor with portable benefits) in 20+ jurisdictions by Q4 2026, avoiding costly AB5-style reclassification mandates. Framework includes: portable benefits fund (healthcare, retirement contributions), earnings guarantees (minimum after expenses), flexibility preservation (drivers set own schedules), and worker protections (anti-discrimination, safety). Alternative to pure employment model which would increase costs 20-30% and eliminate flexibility that 87% of drivers value. Lobbying, coalition building, pilot programs demonstrating benefits fund viability.',
'ACTIVE', 1,
'{"owner": "VP Government Relations", "target_date": "2026-12-31", "success_metrics": ["20 jurisdictions with framework", "Benefits fund operational", "87% driver satisfaction maintained", "Avoid employment reclassification"], "dependencies": ["Policy team", "Benefits fund design", "Coalition partners"], "stakeholders": ["CEO", "VP Gov Relations", "Legal", "Finance"], "budget": "$15M", "risk_level": "CRITICAL"}'::jsonb,
ARRAY['business', 'regulatory', 'government-relations', 'policy', 'driver-classification'],
NOW(), NOW()),

-- Brand & Marketing
('d1e1f1a1-0001-4001-a001-000000000044', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective',
'Achieve Top 3 Brand Awareness in All Markets',
'Increase unaided brand awareness from current 68% to top 3 position (>85% awareness) in all operating markets by Q4 2026 through comprehensive brand marketing campaign. Current competitive positioning: Uber 94%, Lyft 89%, SwiftRide 68%. Campaign strategy includes: national TV advertising ($20M spend), sponsorship of major events (music festivals, sports), influencer partnerships (100+ micro-influencers), brand refresh with memorable creative, and cause marketing (sustainability, community). Awareness drives consideration (8% lift per 10 points awareness) and reduces CAC (15% reduction as awareness increases). Track via quarterly brand studies.',
'ACTIVE', 2,
'{"owner": "CMO", "target_date": "2026-12-31", "success_metrics": [">85% brand awareness", "Top 3 position all markets", "8% consideration lift", "15% CAC reduction"], "dependencies": ["Brand campaign creative", "Media buying", "Sponsorship deals"], "stakeholders": ["CMO", "CEO", "Marketing Team"], "budget": "$35M", "risk_level": "MEDIUM"}'::jsonb,
ARRAY['business', 'marketing', 'brand', 'awareness', 'advertising'],
NOW(), NOW()),

('d1e1f1a1-0001-4001-a001-000000000045', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective',
'Launch Loyalty Program with 2M Members',
'Develop and launch SwiftRide Rewards loyalty program achieving 2M enrolled members (20% of rider base) by Q4 2026, increasing rider retention by 25% and ride frequency by 35% among program members. Program structure: earn 1 point per dollar spent, redeem for free rides (100 points = $10), tier system (Silver/Gold/Platinum with increasing benefits), exclusive perks (priority support, airport lounge access, partner discounts), and gamification elements (challenges, badges). Partnership integration with hotels, airlines, restaurants for cross-earn/burn. Expected to increase LTV from $180 to $280 for enrolled members.',
'ACTIVE', 2,
'{"owner": "VP Product", "target_date": "2026-12-31", "success_metrics": ["2M loyalty members", "25% retention increase", "35% frequency increase", "$280 member LTV"], "dependencies": ["Loyalty platform", "Partner integrations", "Rewards economics modeling"], "stakeholders": ["VP Product", "Marketing", "Finance", "Partnerships"], "budget": "$10M (platform + rewards)", "risk_level": "MEDIUM"}'::jsonb,
ARRAY['business', 'loyalty', 'retention', 'product', 'customer-experience'],
NOW(), NOW()),

-- Financial Operations
('d1e1f1a1-0001-4001-a001-000000000046', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective',
'Optimize Payment Processing to Reduce Transaction Costs 30%',
'Reduce payment processing costs from 2.9% + $0.30 per transaction to 2.0% + $0.20 through payment optimization strategies by Q3 2026, saving $18M annually on $900M GMV. Strategies include: direct card network relationships (bypassing processor markup), ACH/bank account adoption for 30% of transactions (0.5% cost), multi-processor routing (send to cheapest processor real-time), payment method steering (incentivize low-cost methods), fraud reduction lowering chargeback fees, and volume-based rate negotiations. Technical requirements: payment orchestration layer, real-time cost optimization, and multi-processor integration.',
'ACTIVE', 2,
'{"owner": "VP Finance", "target_date": "2026-09-30", "success_metrics": ["2.0% + $0.20 blended rate", "30% ACH adoption", "$18M annual savings", "<0.3% chargeback rate"], "dependencies": ["Payment orchestration platform", "Direct card network deals", "ACH integration"], "stakeholders": ["VP Finance", "CTO", "Product"], "budget": "$3M", "risk_level": "MEDIUM"}'::jsonb,
ARRAY['business', 'finance', 'payments', 'optimization', 'cost-reduction'],
NOW(), NOW()),

('d1e1f1a1-0001-4001-a001-000000000047', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective',
'Implement Dynamic Cash Flow Management System',
'Deploy AI-powered cash flow forecasting and management system providing 95%+ accuracy in 30-day cash projections and automated working capital optimization by Q2 2026. System will forecast daily cash position based on: ride volume predictions, payment timing (riders pay instantly, drivers paid weekly), refund/chargeback patterns, operational expenses, and seasonal variations. Enables: optimized driver payout schedules, strategic reserve management, better credit facility utilization, and automated surplus investment. Expected benefits: $5M in interest savings, 50% reduction in cash management overhead, support for growth without additional capital raises.',
'ACTIVE', 2,
'{"owner": "CFO", "target_date": "2026-06-30", "success_metrics": ["95% forecast accuracy", "$5M interest savings", "50% overhead reduction", "Automated cash deployment"], "dependencies": ["ML forecast models", "Treasury management system", "Banking API integrations"], "stakeholders": ["CFO", "Finance Team", "Data Science"], "budget": "$2M", "risk_level": "LOW"}'::jsonb,
ARRAY['business', 'finance', 'treasury', 'cash-management', 'ai-ml'],
NOW(), NOW()),

-- Crisis Management & Business Continuity
('d1e1f1a1-0001-4001-a001-000000000048', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective',
'Establish Enterprise Business Continuity Program',
'Develop and implement comprehensive business continuity and disaster recovery program ensuring SwiftRide can maintain critical operations during major disruptions (natural disasters, cyber attacks, pandemics, infrastructure failures) by Q3 2026. Program includes: documented BCP for all critical functions, recovery time objectives (RTO <4 hours for core platform), recovery point objectives (RPO <15 minutes data loss), alternate operations center, crisis communication plan, tabletop exercises (quarterly), vendor risk management, and pandemic preparedness. Compliance requirement for enterprise clients and insurance. Target: 99.95% service availability during regional disruptions.',
'ACTIVE', 2,
'{"owner": "Chief Risk Officer", "target_date": "2026-09-30", "success_metrics": ["Complete BCP documentation", "RTO <4 hours", "RPO <15 min", "99.95% disruption availability"], "dependencies": ["BCP documentation", "DR infrastructure", "Crisis team training"], "stakeholders": ["CRO", "CTO", "Operations", "All Departments"], "budget": "$4M", "risk_level": "HIGH"}'::jsonb,
ARRAY['business', 'risk-management', 'business-continuity', 'disaster-recovery', 'compliance'],
NOW(), NOW()),

-- Customer Segmentation Strategy
('d1e1f1a1-0001-4001-a001-000000000049', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective',
'Develop Premium Tier Targeting High-Value Riders',
'Launch SwiftRide Black premium service tier targeting high-value riders (top 10% by spend) by Q4 2026, generating $30M incremental annual revenue. Premium tier features: luxury vehicle guarantee (BMW, Mercedes, Tesla), professional drivers (4.9+ rating, business attire), priority matching (<90 second pickup ETA), concierge service (phone booking, itinerary planning), fixed transparent pricing (no surge), complimentary amenities (water, chargers, WiFi), and exclusive benefits (airport fast-track, lounge access). Pricing: 40% premium over standard rides. Target: 100K premium tier customers with $300 average monthly spend vs $45 standard tier.',
'ACTIVE', 2,
'{"owner": "VP Premium Services", "target_date": "2026-12-31", "success_metrics": ["100K premium customers", "$30M incremental revenue", "$300 avg monthly spend", "4.9+ driver rating"], "dependencies": ["Luxury vehicle recruitment", "Premium driver training", "Concierge service"], "stakeholders": ["VP Premium", "Operations", "Product", "Marketing"], "budget": "$8M", "risk_level": "MEDIUM"}'::jsonb,
ARRAY['business', 'premium-services', 'segmentation', 'revenue', 'luxury'],
NOW(), NOW()),

-- Technology Infrastructure
('d1e1f1a1-0001-4001-a001-000000000050', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective',
'Migrate to Cloud-Native Microservices Architecture',
'Complete migration from monolithic architecture to cloud-native microservices on Kubernetes by Q3 2026, enabling 10x scalability, 50% faster feature deployment, and 40% infrastructure cost reduction. Migration includes: decompose monolith into 50+ microservices, implement service mesh for inter-service communication, adopt GitOps for deployments, establish observability stack (metrics, logging, tracing), implement API gateway, and adopt event-driven architecture for async communication. Expected benefits: scale to 10M daily rides (current limit 2M), deploy features 5x per day (current 1x per week), reduce infrastructure costs from $12M to $7M annually.',
'ACTIVE', 1,
'{"owner": "CTO", "target_date": "2026-09-30", "success_metrics": ["50+ microservices", "10M daily ride capacity", "5x daily deploys", "$5M infrastructure savings"], "dependencies": ["Kubernetes setup", "Microservices development", "Migration tooling"], "stakeholders": ["CTO", "VP Engineering", "DevOps", "All Engineering"], "budget": "$15M", "risk_level": "HIGH"}'::jsonb,
ARRAY['business', 'technology', 'architecture', 'cloud', 'scalability'],
NOW(), NOW()),

('d1e1f1a1-0001-4001-a001-000000000051', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective',
'Implement Zero-Trust Security Architecture',
'Deploy zero-trust security model across all systems and networks by Q4 2026, eliminating implicit trust and verifying every access request regardless of source. Implementation includes: identity-based access control (replace network perimeters), multi-factor authentication for all systems (100% coverage), device posture verification, micro-segmentation of networks, continuous authentication/authorization, privileged access management, and encrypted traffic everywhere. Addresses increasing cyber threats (attacks up 300% in ride-sharing sector), compliance requirements (SOC 2, ISO 27001), and insider threat risks. Expected: 80% reduction in security incidents.',
'ACTIVE', 1,
'{"owner": "CISO", "target_date": "2026-12-31", "success_metrics": ["100% MFA coverage", "Zero implicit trust", "80% incident reduction", "100% encrypted traffic"], "dependencies": ["Identity platform", "Network segmentation", "Device management"], "stakeholders": ["CISO", "CTO", "IT", "All Engineering"], "budget": "$6M", "risk_level": "HIGH"}'::jsonb,
ARRAY['business', 'security', 'zero-trust', 'cybersecurity', 'compliance'],
NOW(), NOW()),

-- Market Intelligence
('d1e1f1a1-0001-4001-a001-000000000052', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'business_objective',
'Establish Competitive Intelligence & Market Research Function',
'Build dedicated competitive intelligence and market research capability providing strategic insights on competitors, market trends, and customer needs by Q2 2026. Function includes: competitor monitoring (pricing, features, expansion), market sizing and forecasting (TAM/SAM/SOM analysis), customer research program (monthly surveys, quarterly focus groups), win/loss analysis, trend analysis (mobility, technology, regulations), and strategic recommendations. Deliverables: weekly competitive brief, monthly market report, quarterly strategic recommendations. Expected to improve strategic decision quality 40%, reduce failed initiatives by 30%, and identify $50M+ new opportunities annually.',
'ACTIVE', 3,
'{"owner": "VP Strategy", "target_date": "2026-06-30", "success_metrics": ["Dedicated CI team established", "Weekly/monthly reporting", "40% decision quality improvement", "$50M opportunity identification"], "dependencies": ["CI team hiring", "Research tools", "Data sources"], "stakeholders": ["VP Strategy", "CEO", "Product", "Marketing"], "budget": "$3M", "risk_level": "LOW"}'::jsonb,
ARRAY['business', 'strategy', 'competitive-intelligence', 'market-research', 'insights'],
NOW(), NOW());
