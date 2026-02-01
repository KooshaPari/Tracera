-- Market Segments Batch (Items 11-50) - 40 additional segments

INSERT INTO tracertm.items (id, project_id, type, title, description, status, priority, metadata, tags, created_at, updated_at)
VALUES

-- Geographic Segments
('f1f1f1a1-0003-4003-a003-000000000011', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'market_segment',
'Dense Urban Core Residents',
'Individuals living in high-density urban cores of major metropolitan areas (NYC, SF, Chicago, Boston, etc.) with population density >15,000 people per square mile. Segment size: 8.5M potential riders in top 25 metros. Characteristics: No car ownership (68%), public transit users (85%), high smartphone penetration (98%), above-average income ($75K+ median). Transportation needs: Daily commuting (42% of rides), evening social (28%), airport (15%), errands (15%). Pain points: Subway delays, parking scarcity, vehicle ownership costs ($8K+/year). Preferences: Fastest ETA priority, willingness to pay premium for reliability, eco-conscious (prefer EV options). Current penetration: 32% have used SwiftRide in last 90 days. Growth strategy: Corporate commuter programs, transit integration, late-night service reliability.',
'ACTIVE', 1,
'{"size_millions": 8.5, "markets": ["NYC", "SF", "Chicago", "Boston", "DC", "Seattle"], "demographics": {"median_income": 75000, "car_ownership": 32, "transit_users": 85}, "ride_purposes": {"commute": 42, "social": 28, "airport": 15, "errands": 15}, "pain_points": ["Transit delays", "Parking scarcity", "Vehicle costs"], "preferences": ["Fast ETA", "Reliability", "EV options"], "penetration_rate": 32, "growth_rate_yoy": 18}'::jsonb,
ARRAY['market-segment', 'geographic', 'urban', 'high-density', 'transit'],
NOW(), NOW()),

('f1f1f1a1-0003-4003-a003-000000000012', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'market_segment',
'Suburban Commuters',
'Suburban residents who commute to urban centers for work, living 10-30 miles from city core. Segment size: 22M potential riders across all markets. Characteristics: High car ownership (92%), dual-income households (68%), family-oriented (55% have children), median income $95K. Transportation patterns: Peak hour commuting (75% of rides 7-9am, 5-7pm), occasional leisure trips to city, airport runs. Pain points: Traffic congestion (avg 45min commute), parking costs ($200-400/month), vehicle wear and tear, desire to be productive during commute. Use cases: Park-and-ride from transit stations, door-to-door commuting, carpooling alternatives. Current penetration: 12%. Growth opportunity: Commuter subscriptions, employer partnerships, guaranteed pricing.',
'ACTIVE', 2,
'{"size_millions": 22.0, "distance_from_core": "10-30 miles", "demographics": {"car_ownership": 92, "dual_income": 68, "with_children": 55, "median_income": 95000}, "commute_patterns": {"peak_morning": "7-9am 40%", "peak_evening": "5-7pm 35%"}, "pain_points": ["Traffic congestion", "Parking costs $200-400/mo", "Vehicle maintenance"], "use_cases": ["Park-and-ride", "Door-to-door commute", "Carpool alternative"], "penetration_rate": 12, "growth_potential": "HIGH"}'::jsonb,
ARRAY['market-segment', 'geographic', 'suburban', 'commuter', 'family'],
NOW(), NOW()),

('f1f1f1a1-0003-4003-a003-000000000013', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'market_segment',
'College Town Students',
'University students in college towns and campus-adjacent areas. Segment size: 15M students across 500+ college markets. Demographics: 18-24 years (75%), limited vehicle access (60% no car on campus), price-sensitive, tech-native, social riders. Ride patterns: Weekend nights (Friday/Saturday 8pm-2am = 45% of rides), spring break/holiday travel, off-campus errands, occasional airport trips. Pain points: Limited late-night transit, campus parking restrictions, DUI concerns, group coordination. Preferences: Ride-sharing/pooling for cost savings, student discounts, safety features (share trip), flexible pickup/dropoff points. Current penetration: 28% in top 50 college markets. Seasonality: High during school year, 60% drop during summer.',
'ACTIVE', 2,
'{"size_millions": 15.0, "college_markets": 500, "demographics": {"age_range": "18-24", "no_car": 60, "price_sensitive": true, "tech_native": true}, "ride_patterns": {"weekend_nights": 45, "spring_break": 15, "errands": 25, "airport": 15}, "pain_points": ["Late-night transit", "Campus parking", "DUI risk", "Group coordination"], "preferences": ["Ride sharing", "Student discounts", "Safety features"], "penetration_rate": 28, "seasonality": "60% summer drop"}'::jsonb,
ARRAY['market-segment', 'demographic', 'students', 'college', 'young-adults'],
NOW(), NOW()),

-- Demographic Segments
('f1f1f1a1-0003-4003-a003-000000000014', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'market_segment',
'Young Urban Professionals (25-35)',
'Career-focused individuals aged 25-35 living in urban areas, representing high-value rider segment. Size: 12M in target markets. Characteristics: High income ($80K-$150K), smartphone dependent, no children (75%), socially active, career-focused. Ride behavior: Frequent users (8-12 rides/month), morning commutes (6:30-9am), after-work social (6-11pm), weekend entertainment. Spending: $120-180/month on rides, willing to pay for premium service, low price sensitivity. Tech adoption: Early adopters, use multiple apps, expect seamless experience. LTV: $380 (vs $180 platform average). Growth: 25% YoY in segment. Strategy: Premium tier targeting, loyalty program focus, workplace partnerships, late-night reliability.',
'ACTIVE', 1,
'{"size_millions": 12.0, "age_range": "25-35", "demographics": {"income_range": "80K-150K", "no_children": 75, "urban": 100}, "rides_per_month": 10, "monthly_spend": 150, "ride_timing": {"morning_commute": 30, "after_work": 35, "weekend": 35}, "ltv": 380, "price_sensitivity": "LOW", "tech_adoption": "Early adopters", "growth_rate": 25, "strategy": ["Premium tier", "Loyalty", "Workplace partnerships"]}'::jsonb,
ARRAY['market-segment', 'demographic', 'young-professionals', 'high-value', 'urban'],
NOW(), NOW()),

('f1f1f1a1-0003-4003-a003-000000000015', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'market_segment',
'Senior Citizens (65+)',
'Older adults aged 65+ seeking independent mobility options. Size: 18M seniors in service areas, growing 3% annually. Characteristics: Fixed income majority (60%), health limitations (45%), no longer drive or limited driving (35%), family-reliant for transport. Transportation needs: Medical appointments (40% of rides), grocery/errands (30%), social visits (20%), other (10%). Pain points: Complex app interfaces, payment setup difficulties, driver communication challenges, safety concerns. Preferences: Simple booking (phone option), reliable on-time pickup, driver assistance, familiar drivers, accessible vehicles. Barriers: Technology adoption (only 40% comfortable with apps), cost sensitivity on fixed income. Opportunity: Healthcare partnerships (NEMT), senior centers, accessible fleet, simplified senior app version. Current penetration: 8%.',
'ACTIVE', 2,
'{"size_millions": 18.0, "age_range": "65+", "growth_rate": 3, "demographics": {"fixed_income": 60, "health_limitations": 45, "limited_driving": 35}, "ride_purposes": {"medical": 40, "errands": 30, "social": 20, "other": 10}, "pain_points": ["App complexity", "Payment setup", "Communication", "Safety"], "preferences": ["Phone booking", "Reliability", "Driver assistance", "Accessibility"], "tech_comfort": 40, "penetration_rate": 8, "opportunity": ["NEMT partnerships", "Accessible fleet"]}'::jsonb,
ARRAY['market-segment', 'demographic', 'seniors', 'accessibility', 'healthcare'],
NOW(), NOW()),

('f1f1f1a1-0003-4003-a003-000000000016', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'market_segment',
'Affluent Empty Nesters (50-65)',
'High-income couples/individuals aged 50-65 whose children have left home. Size: 8M in target demographics. Characteristics: Household income $150K+ (median $185K), high net worth, discretionary income, quality-focused, own multiple vehicles but choose rides for convenience. Usage: Dining/entertainment (35%), airport (25%), special events (20%), wine country/leisure (20%). Behavior: Premium service preference (60% use premium tier), high tips (average 25%), loyalty to preferred drivers, concierge expectations. Spend: $300+/month on average, price insensitive. LTV: $680 (platform highest). Preferences: Luxury vehicles, professional drivers, predictable pricing (no surge tolerance), airport services, wine tour packages. Strategy: Premium brand positioning, executive service tier, travel partnerships.',
'ACTIVE', 1,
'{"size_millions": 8.0, "age_range": "50-65", "demographics": {"median_income": 185000, "own_vehicles": 85, "discretionary_income": "HIGH"}, "ride_purposes": {"dining_entertainment": 35, "airport": 25, "events": 20, "leisure": 20}, "premium_usage": 60, "average_tip": 25, "monthly_spend": 300, "ltv": 680, "preferences": ["Luxury vehicles", "Professional drivers", "No surge", "Concierge"], "strategy": ["Premium brand", "Executive tier", "Travel partnerships"]}'::jsonb,
ARRAY['market-segment', 'demographic', 'affluent', 'premium', 'high-value'],
NOW(), NOW()),

-- Behavioral Segments
('f1f1f1a1-0003-4003-a003-000000000017', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'market_segment',
'Frequent Business Travelers',
'Regular business travelers using rides for work-related transportation. Size: 5M active business travelers. Characteristics: Expense account usage (75%), multiple cities, time-sensitive, efficiency-focused. Trip types: Airport transfers (45%), client meetings (30%), hotel-to-office (15%), business dinners (10%). Booking patterns: Advanced scheduling (50%), same-day on-demand (50%), often through corporate accounts. Spend: $400+/month, company-paid. Preferences: Receipt automation, expense integration (Concur/Expensify), reliable ETAs, premium vehicles, business-appropriate drivers, Wi-Fi connectivity. Pain points: Expenseport complexity, varying service quality across cities, last-minute reliability. Opportunity: National corporate accounts, travel management integration, airport priority programs, business traveler tier. LTV: $820.',
'ACTIVE', 1,
'{"size_millions": 5.0, "demographics": {"expense_account": 75, "multi_city": true, "time_sensitive": true}, "trip_types": {"airport": 45, "client_meetings": 30, "hotel_office": 15, "dining": 10}, "booking_patterns": {"scheduled": 50, "on_demand": 50}, "monthly_spend": 400, "preferences": ["Receipt automation", "Expense integration", "Reliability", "Premium vehicles", "WiFi"], "pain_points": ["Expense reporting", "Quality variance", "Reliability"], "ltv": 820, "opportunity": ["Corporate accounts", "TMC integration", "Airport programs"]}'::jsonb,
ARRAY['market-segment', 'behavioral', 'business-travel', 'corporate', 'high-value'],
NOW(), NOW()),

('f1f1f1a1-0003-4003-a003-000000000018', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'market_segment',
'Late Night / Weekend Party-Goers',
'Social riders using service primarily for nightlife and weekend entertainment. Size: 10M occasional users. Demographics: 21-35 age (70%), urban/suburban mix, social lifestyle, safety-conscious (DUI avoidance). Usage patterns: Friday/Saturday 9pm-3am (65% of rides), Thursday night (20%), occasional weekday evenings (15%). Ride purposes: Bar/restaurant transport (50%), nightclub/events (30%), party/friend visits (20%). Behavior: Group rides common (2.5 avg passengers), surge pricing acceptance for safety, tips correlated with driver patience/music/route. Spend: $80/month average, highly variable. Preferences: Reliable late-night availability, group-friendly vehicles, tolerance for pickup delays, safety features. Challenge: Surge pricing resentment, driver availability at peak times. Opportunity: Ride sharing optimization, entertainment venue partnerships, designated driver campaigns.',
'ACTIVE', 2,
'{"size_millions": 10.0, "demographics": {"age_range": "21-35", "urban_suburban_mix": true, "safety_conscious": true}, "usage_patterns": {"fri_sat_night": 65, "thursday": 20, "other_weekdays": 15}, "ride_purposes": {"bars_restaurants": 50, "clubs_events": 30, "parties": 20}, "avg_passengers": 2.5, "monthly_spend": 80, "surge_acceptance": "HIGH for safety", "preferences": ["Late-night availability", "Group vehicles", "Safety features"], "challenges": ["Surge resentment", "Peak availability"], "opportunity": ["Ride sharing", "Venue partnerships"]}'::jsonb,
ARRAY['market-segment', 'behavioral', 'nightlife', 'social', 'late-night'],
NOW(), NOW()),

('f1f1f1a1-0003-4003-a003-000000000019', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'market_segment',
'Price-Conscious Occasional Users',
'Infrequent riders who use service only when absolutely necessary or with discounts. Size: 35M light users. Characteristics: Price-sensitive, own vehicles (85%), ride-sharing for specific situations only. Usage: 1-3 rides/month, prompted by discounts/promos (60%), airport when parking expensive (25%), special events (10%), other (5%). Decision factors: Price comparison across platforms, promo code availability, comparison to parking/taxi alternatives. Spend: $25/month average. Demographics: Wide range, skews lower-middle income. Preferences: Transparency in pricing, advance fare estimates, discount notifications, shared rides for lower cost. Challenges: Low engagement, high CAC relative to LTV ($42 CAC, $85 LTV), promo dependency. Strategy: Convert to frequency through habit formation, subscription trials, reduce discount dependency.',
'ACTIVE', 3,
'{"size_millions": 35.0, "demographics": {"car_ownership": 85, "income": "lower-middle", "diverse_age": true}, "usage": {"rides_per_month": 2, "promo_driven": 60, "airport": 25, "events": 10, "other": 5}, "monthly_spend": 25, "decision_factors": ["Price comparison", "Promo codes", "vs parking/taxi"], "preferences": ["Price transparency", "Fare estimates", "Discounts", "Shared rides"], "cac": 42, "ltv": 85, "challenge": "Low engagement", "strategy": ["Habit formation", "Subscription trial", "Reduce promo dependency"]}'::jsonb,
ARRAY['market-segment', 'behavioral', 'price-sensitive', 'occasional', 'low-frequency'],
NOW(), NOW()),

('f1f1f1a1-0003-4003-a003-000000000020', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'market_segment',
'Daily Commuter Subscribers',
'Riders who use service for regular commuting, high subscription program candidates. Size: 3M potential (current 200K actual subscribers). Characteristics: Predictable schedules, M-F commuters, value convenience over vehicle ownership. Commute patterns: 5-10 rides/week same routes, morning (6-9am) + evening (4-7pm), 95% work-related. Current behavior: Spend $200-300/month on rides, high platform loyalty once established. Subscription appeal: Predictable costs, priority matching, no surge pricing, convenience. Demographics: Urban professionals, $60K-$120K income, 25-50 age, 60% do not own cars. Pain points: Cost variability with surge, priority during rush hour, monthly budgeting. Opportunity: Subscription conversion (only 7% of eligible riders currently subscribe), employer subsidies, guaranteed pricing. LTV with subscription: $450 vs $180 standard.',
'ACTIVE', 1,
'{"size_millions": 3.0, "current_subscribers": 200000, "demographics": {"income_range": "60K-120K", "age_range": "25-50", "no_car": 60}, "commute_frequency": "5-10 rides/week", "timing": {"morning": "6-9am", "evening": "4-7pm"}, "monthly_spend": 250, "subscription_rate": 7, "subscription_ltv": 450, "standard_ltv": 180, "pain_points": ["Cost variability", "Rush hour priority", "Budgeting"], "opportunity": ["Subscription conversion", "Employer subsidies", "Guaranteed pricing"]}'::jsonb,
ARRAY['market-segment', 'behavioral', 'commuters', 'subscription', 'high-frequency'],
NOW(), NOW()),

-- Psychographic Segments
('f1f1f1a1-0003-4003-a003-000000000021', 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e', 'market_segment',
'Eco-Conscious Sustainability Advocates',
'Environmentally-focused riders who prioritize green transportation options. Size: 6M with strong environmental values. Demographics: Higher education (75% college+), urban (80%), median income $70K, 25-45 age skew. Values: Carbon footprint reduction, support for electric vehicles, opposition to single-occupancy vehicles, climate action. Behavior: Actively select EV rides when available (+18% willing to wait), use ride-sharing/pooling (65% of rides), track personal carbon footprint. WTP premium: 10-15% for guaranteed EV rides. Ride purposes: Varied, but avoid when public transit feasible. Pain points: Limited EV availability (only 8% of fleet), can''t verify eco-claims, lack of carbon tracking. Preferences: EV filter, carbon footprint dashboard, offset programs, sustainability partnerships. Opportunity: Green tier subscription, EV expansion, environmental marketing, B-Corp partnerships. Brand affinity: High loyalty to eco-aligned brands.',
'ACTIVE', 2,
'{"size_millions": 6.0, "demographics": {"higher_ed": 75, "urban": 80, "median_income": 70000, "age_range": "25-45"}, "values": ["Carbon reduction", "EV support", "Climate action"], "behavior": {"ev_preference": true, "wait_for_ev": 18, "ride_sharing": 65}, "willingness_to_pay_premium": 12.5, "pain_points": ["Limited EV availability 8%", "Eco verification", "Carbon tracking"], "preferences": ["EV filter", "Carbon dashboard", "Offset programs"], "opportunity": ["Green subscription", "EV expansion", "Eco marketing"], "brand_loyalty": "HIGH for aligned values"}'::jsonb,
ARRAY['market-segment', 'psychographic', 'eco-conscious', 'sustainability', 'values-driven'],
NOW(), NOW());
