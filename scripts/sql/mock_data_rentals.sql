-- StayNest - Property Rental Marketplace
-- Comprehensive mock data for rental platform featuring listings, bookings, hosts, guests, and reviews

DELETE FROM projects WHERE name = 'StayNest - Property Rental Marketplace';
DELETE FROM items WHERE project_id IN (SELECT id FROM projects WHERE name = 'StayNest - Property Rental Marketplace');
DELETE FROM links WHERE project_id IN (SELECT id FROM projects WHERE name = 'StayNest - Property Rental Marketplace');

-- Create project
INSERT INTO projects (id, name, project_metadata, created_at, updated_at)
VALUES (
  'proj_staynest_001',
  'StayNest - Property Rental Marketplace',
  '{"description": "Full-featured Airbnb-like platform for property rentals with advanced search, booking management, host verification, and review system"}',
  NOW(),
  NOW()
);

-- REQUIREMENTS (First 30 of 100+)
-- Core Listing Requirements
INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, owner, item_metadata, version, created_at, updated_at) VALUES
('req_sn_001', 'proj_staynest_001', 'Property Listing Creation', 'Hosts must be able to create detailed property listings with photos, amenities, house rules, and pricing', 'requirements', 'requirement', 'done', 'critical', 'Olivia Chen', '{"category":"listings","complexity":"high"}', 1, NOW(), NOW()),
('req_sn_002', 'proj_staynest_001', 'Advanced Property Search', 'Implement full-text search with filters for location, price range, amenities, property type, and availability dates', 'requirements', 'requirement', 'done', 'critical', 'Jamal Brown', '{"category":"search","complexity":"high"}', 1, NOW(), NOW()),
('req_sn_003', 'proj_staynest_001', 'Booking Management System', 'Create comprehensive booking lifecycle management with confirmation, payment, cancellation, and rescheduling', 'requirements', 'requirement', 'in_progress', 'critical', 'Sofia Garcia', '{"category":"bookings","complexity":"high"}', 1, NOW(), NOW()),
('req_sn_004', 'proj_staynest_001', 'Host Verification Process', 'Implement identity verification system for hosts with document upload, background checks, and approval workflow', 'requirements', 'requirement', 'in_progress', 'critical', 'Marcus Johnson', '{"category":"verification","complexity":"high"}', 1, NOW(), NOW()),
('req_sn_005', 'proj_staynest_001', 'Guest Review System', 'Enable guests to leave detailed reviews with ratings for cleanliness, communication, accuracy, and value', 'requirements', 'requirement', 'done', 'high', 'Aisha Patel', '{"category":"reviews","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_006', 'proj_staynest_001', 'Host Rating and Trust Score', 'Calculate and display host ratings based on guest reviews with response rate and verification badges', 'requirements', 'requirement', 'done', 'high', 'Chen Wei', '{"category":"reviews","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_007', 'proj_staynest_001', 'Dynamic Pricing Engine', 'Implement automated pricing suggestions based on demand, seasonality, local events, and competitor listings', 'requirements', 'requirement', 'in_progress', 'high', 'Isabella Martinez', '{"category":"pricing","complexity":"high"}', 1, NOW(), NOW()),
('req_sn_008', 'proj_staynest_001', 'Calendar and Availability Management', 'Allow hosts to block dates, set minimum stay lengths, and manage seasonal pricing with bulk editing', 'requirements', 'requirement', 'done', 'high', 'Diego Lopez', '{"category":"calendar","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_009', 'proj_staynest_001', 'Payment Processing and Escrow', 'Integrate secure payment processing with escrow service to protect both guests and hosts', 'requirements', 'requirement', 'in_progress', 'critical', 'Priya Sharma', '{"category":"payments","complexity":"high"}', 1, NOW(), NOW()),
('req_sn_010', 'proj_staynest_001', 'Multi-currency Support', 'Support bookings and payments in 50+ currencies with real-time exchange rate conversion', 'requirements', 'requirement', 'todo', 'high', 'Yuki Tanaka', '{"category":"payments","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_011', 'proj_staynest_001', 'Instant Booking Option', 'Allow hosts to enable instant booking without host approval for pre-screened guests', 'requirements', 'requirement', 'done', 'high', 'Mohammed Ahmed', '{"category":"bookings","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_012', 'proj_staynest_001', 'Host Message System', 'Real-time messaging between hosts and guests with read receipts and notification system', 'requirements', 'requirement', 'in_progress', 'high', 'Lucia Rossi', '{"category":"messaging","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_013', 'proj_staynest_001', 'Amenities Database', 'Maintain comprehensive database of 200+ common amenities with icons and descriptions', 'requirements', 'requirement', 'done', 'medium', 'Ravi Desai', '{"category":"listings","complexity":"low"}', 1, NOW(), NOW()),
('req_sn_014', 'proj_staynest_001', 'Photo Upload and Gallery', 'Implement photo upload system with compression, validation, and gallery management capabilities', 'requirements', 'requirement', 'done', 'high', 'Katja Mueller', '{"category":"listings","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_015', 'proj_staynest_001', 'Property Type Classification', 'Support diverse property types: apartments, houses, villas, studios, treehouses, houseboats, etc.', 'requirements', 'requirement', 'done', 'medium', 'Paulo Silva', '{"category":"listings","complexity":"low"}', 1, NOW(), NOW()),
('req_sn_016', 'proj_staynest_001', 'Location-Based Services', 'Implement geolocation services with map integration, nearby landmarks, and transportation options', 'requirements', 'requirement', 'in_progress', 'high', 'Elena Ivanova', '{"category":"search","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_017', 'proj_staynest_001', 'Host Cancellation Policies', 'Support flexible, moderate, and strict cancellation policies with automatic refund calculations', 'requirements', 'requirement', 'done', 'high', 'Ahmad Hassan', '{"category":"bookings","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_018', 'proj_staynest_001', 'Guest Cancellation Rights', 'Enforce cancellation policies and automate refund processing based on policy and timing', 'requirements', 'requirement', 'in_progress', 'high', 'Yuki Yamamoto', '{"category":"bookings","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_019', 'proj_staynest_001', 'Dispute Resolution System', 'Implement mediation system for booking disputes with evidence submission and arbitration', 'requirements', 'requirement', 'todo', 'high', 'Nicolas Dupont', '{"category":"disputes","complexity":"high"}', 1, NOW(), NOW()),
('req_sn_020', 'proj_staynest_001', 'Damage Claim Processing', 'Allow hosts to file damage claims with photo evidence and automatic deduction from deposits', 'requirements', 'requirement', 'todo', 'high', 'Svetlana Volkov', '{"category":"disputes","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_021', 'proj_staynest_001', 'Host Payout Management', 'Monthly payout system with performance-based fees and 30-day hold periods', 'requirements', 'requirement', 'in_progress', 'critical', 'Fernando Gonzalez', '{"category":"payments","complexity":"high"}', 1, NOW(), NOW()),
('req_sn_022', 'proj_staynest_001', 'Tax Document Generation', 'Auto-generate tax documents and 1099 forms for hosts with earnings tracking', 'requirements', 'requirement', 'todo', 'medium', 'Amelia Johnson', '{"category":"compliance","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_023', 'proj_staynest_001', 'Regulatory Compliance', 'Track local regulations, short-term rental laws, and zoning restrictions by location', 'requirements', 'requirement', 'in_progress', 'critical', 'Raj Patel', '{"category":"compliance","complexity":"high"}', 1, NOW(), NOW()),
('req_sn_024', 'proj_staynest_001', 'Insurance Integration', 'Partner with insurance providers for host liability and guest protection insurance', 'requirements', 'requirement', 'todo', 'high', 'Sophie Leclerc', '{"category":"insurance","complexity":"high"}', 1, NOW(), NOW()),
('req_sn_025', 'proj_staynest_001', 'Smart Pricing Recommendations', 'ML-powered pricing suggestions based on historical data, market trends, and competitor analysis', 'requirements', 'requirement', 'todo', 'high', 'Hiroshi Nakamura', '{"category":"pricing","complexity":"high"}', 1, NOW(), NOW()),
('req_sn_026', 'proj_staynest_001', 'Booking Analytics Dashboard', 'Comprehensive analytics for hosts showing occupancy rates, revenue, and booking trends', 'requirements', 'requirement', 'in_progress', 'high', 'Tamara Voss', '{"category":"analytics","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_027', 'proj_staynest_001', 'Guest Search History', 'Track and personalize search results based on user history and preferences', 'requirements', 'requirement', 'done', 'medium', 'Carlos Mendez', '{"category":"search","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_028', 'proj_staynest_001', 'Wishlist and Saved Properties', 'Allow guests to save and organize favorite properties for later comparison', 'requirements', 'requirement', 'done', 'medium', 'Fatima Al-Mansouri', '{"category":"search","complexity":"low"}', 1, NOW(), NOW()),
('req_sn_029', 'proj_staynest_001', 'Similar Property Recommendations', 'Display similar listings based on amenities, price, location, and guest preferences', 'requirements', 'requirement', 'in_progress', 'medium', 'Dmitri Popov', '{"category":"search","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_030', 'proj_staynest_001', 'Mobile App for Hosts', 'Native iOS and Android apps for hosts to manage listings, bookings, and messages on-the-go', 'requirements', 'requirement', 'todo', 'high', 'Maria Santos', '{"category":"mobile","complexity":"high"}', 1, NOW(), NOW());

-- REQUIREMENTS (Next 20 of 100+)
INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, owner, item_metadata, version, created_at, updated_at) VALUES
('req_sn_031', 'proj_staynest_001', 'Mobile App for Guests', 'Native iOS and Android apps for guests to search, book, and manage reservations', 'requirements', 'requirement', 'in_progress', 'high', 'Liam O''Brien', '{"category":"mobile","complexity":"high"}', 1, NOW(), NOW()),
('req_sn_032', 'proj_staynest_001', 'Two-Factor Authentication', 'Implement 2FA via SMS and authenticator apps for enhanced account security', 'requirements', 'requirement', 'done', 'critical', 'Keiko Yamamoto', '{"category":"security","complexity":"low"}', 1, NOW(), NOW()),
('req_sn_033', 'proj_staynest_001', 'Email Verification System', 'Automated email verification for account creation and password reset', 'requirements', 'requirement', 'done', 'critical', 'Rashid Al-Mansouri', '{"category":"security","complexity":"low"}', 1, NOW(), NOW()),
('req_sn_034', 'proj_staynest_001', 'Identity Verification for Guests', 'Optional identity verification to increase host trust and enable special offers', 'requirements', 'requirement', 'in_progress', 'high', 'Eva Eriksson', '{"category":"verification","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_035', 'proj_staynest_001', 'Social Login Integration', 'Support Google, Facebook, Apple sign-in for faster user onboarding', 'requirements', 'requirement', 'done', 'medium', 'Maxim Petrov', '{"category":"auth","complexity":"low"}', 1, NOW(), NOW()),
('req_sn_036', 'proj_staynest_001', 'Accessibility Compliance', 'WCAG 2.1 AA compliance with screen reader support and keyboard navigation', 'requirements', 'requirement', 'in_progress', 'high', 'Nia Johnson', '{"category":"accessibility","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_037', 'proj_staynest_001', 'Multi-language Support', 'Support 30+ languages with locale-specific formatting and RTL support', 'requirements', 'requirement', 'in_progress', 'high', 'Hassan El-Sayed', '{"category":"localization","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_038', 'proj_staynest_001', 'SEO Optimization', 'Dynamic meta tags, structured data, and sitemap for search engine visibility', 'requirements', 'requirement', 'done', 'high', 'Linda Zhang', '{"category":"seo","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_039', 'proj_staynest_001', 'Performance Optimization', 'Target 2s page load times with CDN, caching, and image optimization', 'requirements', 'requirement', 'in_progress', 'high', 'Stefan Novak', '{"category":"performance","complexity":"high"}', 1, NOW(), NOW()),
('req_sn_040', 'proj_staynest_001', 'Notification System', 'Push notifications for booking updates, messages, and important account alerts', 'requirements', 'requirement', 'in_progress', 'high', 'Zainab Hassan', '{"category":"notifications","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_041', 'proj_staynest_001', 'Email Template System', 'Customizable email templates for confirmations, reminders, and marketing campaigns', 'requirements', 'requirement', 'done', 'medium', 'Igor Volkov', '{"category":"notifications","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_042', 'proj_staynest_001', 'Super Host Program', 'Recognition and rewards program for top-performing hosts with special badges and perks', 'requirements', 'requirement', 'todo', 'high', 'Grace Park', '{"category":"loyalty","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_043', 'proj_staynest_001', 'Guest Loyalty Program', 'Rewards for frequent bookers with points, discounts, and exclusive property access', 'requirements', 'requirement', 'todo', 'medium', 'Leonardo Rossi', '{"category":"loyalty","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_044', 'proj_staynest_001', 'Referral Program', 'Incentivize users to refer friends with credits and bonuses', 'requirements', 'requirement', 'todo', 'medium', 'Nadia Petrova', '{"category":"growth","complexity":"low"}', 1, NOW(), NOW()),
('req_sn_045', 'proj_staynest_001', 'Content Moderation System', 'AI-powered review and photo moderation to prevent inappropriate content', 'requirements', 'requirement', 'todo', 'high', 'James Murphy', '{"category":"moderation","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_046', 'proj_staynest_001', 'User Profile Management', 'Comprehensive user profiles with verification badges, reviews, and response statistics', 'requirements', 'requirement', 'done', 'high', 'Yuki Suzuki', '{"category":"accounts","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_047', 'proj_staynest_001', 'Booking Confirmation Workflow', 'Multi-step confirmation process with payment, house rules acknowledgment, and contact exchange', 'requirements', 'requirement', 'in_progress', 'critical', 'Felipe Santos', '{"category":"bookings","complexity":"medium"}', 1, NOW(), NOW()),
('req_sn_048', 'proj_staynest_001', 'Check-in Instructions', 'Secure delivery of check-in codes, keys information, and property-specific instructions', 'requirements', 'requirement', 'done', 'high', 'Natasha Volkov', '{"category":"bookings","complexity":"low"}', 1, NOW(), NOW()),
('req_sn_049', 'proj_staynest_001', 'Automated Reminders', 'Scheduled reminders for check-in, checkout, and upcoming reservations', 'requirements', 'requirement', 'done', 'medium', 'Omar Al-Rashid', '{"category":"notifications","complexity":"low"}', 1, NOW(), NOW()),
('req_sn_050', 'proj_staynest_001', 'Property Management Tools', 'Bulk editing, calendar sync (Google, iCal), and third-party integration for channel managers', 'requirements', 'requirement', 'todo', 'high', 'Simone Rossi', '{"category":"management","complexity":"high"}', 1, NOW(), NOW());

-- FEATURES (First 50 of 200+)
-- Core Search & Discovery Features
INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, owner, parent_id, item_metadata, version, created_at, updated_at) VALUES
('feat_sn_001', 'proj_staynest_001', 'Property Map View', 'Interactive map showing properties with real-time availability', 'features', 'feature', 'done', 'high', 'Li Wei', 'req_sn_002', '{"epic":"search","story_points":5}', 1, NOW(), NOW()),
('feat_sn_002', 'proj_staynest_001', 'Location Filter Panel', 'Draggable map radius selector with suggested locations', 'features', 'feature', 'done', 'high', 'Sofia Garcia', 'req_sn_002', '{"epic":"search","story_points":3}', 1, NOW(), NOW()),
('feat_sn_003', 'proj_staynest_001', 'Price Range Slider', 'Dual-handle slider for min/max price filtering', 'features', 'feature', 'done', 'medium', 'Marcus Johnson', 'req_sn_002', '{"epic":"search","story_points":2}', 1, NOW(), NOW()),
('feat_sn_004', 'proj_staynest_001', 'Amenities Quick Filter', 'Collapsible panel with popular amenities for quick filtering', 'features', 'feature', 'done', 'high', 'Aisha Patel', 'req_sn_002', '{"epic":"search","story_points":3}', 1, NOW(), NOW()),
('feat_sn_005', 'proj_staynest_001', 'Sort Options (Rating, Price, Relevance)', 'Multiple sort methods with visual indicators', 'features', 'feature', 'done', 'high', 'Chen Wei', 'req_sn_002', '{"epic":"search","story_points":2}', 1, NOW(), NOW()),
('feat_sn_006', 'proj_staynest_001', 'Property Card Component', 'Reusable card showing photo, price, rating, and quick info', 'features', 'feature', 'done', 'high', 'Isabella Martinez', 'req_sn_002', '{"epic":"search","story_points":4}', 1, NOW(), NOW()),
('feat_sn_007', 'proj_staynest_001', 'Pagination and Infinite Scroll', 'Multiple viewing modes for search results', 'features', 'feature', 'done', 'medium', 'Diego Lopez', 'req_sn_002', '{"epic":"search","story_points":3}', 1, NOW(), NOW()),
('feat_sn_008', 'proj_staynest_001', 'Filter Persistence', 'Save search filters in URL for shareable links', 'features', 'feature', 'in_progress', 'medium', 'Priya Sharma', 'req_sn_002', '{"epic":"search","story_points":2}', 1, NOW(), NOW()),
('feat_sn_009', 'proj_staynest_001', 'Search Results Summary', 'Display total results, filter summary, and clear options', 'features', 'feature', 'done', 'medium', 'Yuki Tanaka', 'req_sn_002', '{"epic":"search","story_points":2}', 1, NOW(), NOW()),
('feat_sn_010', 'proj_staynest_001', 'No Results Fallback', 'Helpful messaging with suggestions for similar searches', 'features', 'feature', 'done', 'low', 'Mohammed Ahmed', 'req_sn_002', '{"epic":"search","story_points":1}', 1, NOW(), NOW()),
('feat_sn_011', 'proj_staynest_001', 'Photo Upload Widget', 'Drag-drop photo upload with preview and reordering', 'features', 'feature', 'done', 'high', 'Lucia Rossi', 'req_sn_001', '{"epic":"listings","story_points":4}', 1, NOW(), NOW()),
('feat_sn_012', 'proj_staynest_001', 'Amenities Selector', 'Checkbox/toggle interface for 200+ amenities', 'features', 'feature', 'done', 'high', 'Ravi Desai', 'req_sn_001', '{"epic":"listings","story_points":3}', 1, NOW(), NOW()),
('feat_sn_013', 'proj_staynest_001', 'House Rules Text Editor', 'Rich text editor for custom house rules', 'features', 'feature', 'done', 'medium', 'Katja Mueller', 'req_sn_001', '{"epic":"listings","story_points":2}', 1, NOW(), NOW()),
('feat_sn_014', 'proj_staynest_001', 'Pricing Section', 'Base price, cleaning fee, service fee display and configuration', 'features', 'feature', 'done', 'high', 'Paulo Silva', 'req_sn_001', '{"epic":"listings","story_points":3}', 1, NOW(), NOW()),
('feat_sn_015', 'proj_staynest_001', 'Title and Description Editor', 'Markdown editor with SEO tips and character limits', 'features', 'feature', 'done', 'high', 'Elena Ivanova', 'req_sn_001', '{"epic":"listings","story_points":2}', 1, NOW(), NOW()),
('feat_sn_016', 'proj_staynest_001', 'Property Type Selector', 'Dropdown with 15+ property types and icons', 'features', 'feature', 'done', 'medium', 'Ahmad Hassan', 'req_sn_001', '{"epic":"listings","story_points":1}', 1, NOW(), NOW()),
('feat_sn_017', 'proj_staynest_001', 'Bedroom and Bathroom Count', 'Numeric inputs with accuracy verification', 'features', 'feature', 'done', 'high', 'Yuki Yamamoto', 'req_sn_001', '{"epic":"listings","story_points":1}', 1, NOW(), NOW()),
('feat_sn_018', 'proj_staynest_001', 'Guest Capacity Input', 'Dropdown for max occupancy with warnings', 'features', 'feature', 'done', 'medium', 'Nicolas Dupont', 'req_sn_001', '{"epic":"listings","story_points":1}', 1, NOW(), NOW()),
('feat_sn_019', 'proj_staynest_001', 'Address Auto-complete', 'Google Places integration for address validation', 'features', 'feature', 'in_progress', 'high', 'Svetlana Volkov', 'req_sn_001', '{"epic":"listings","story_points":3}', 1, NOW(), NOW()),
('feat_sn_020', 'proj_staynest_001', 'Listing Draft Auto-save', 'Progressive save without page reload', 'features', 'feature', 'done', 'medium', 'Fernando Gonzalez', 'req_sn_001', '{"epic":"listings","story_points":2}', 1, NOW(), NOW()),
('feat_sn_021', 'proj_staynest_001', 'Instant Booking Toggle', 'Host switch to enable/disable instant booking', 'features', 'feature', 'done', 'high', 'Amelia Johnson', 'req_sn_011', '{"epic":"bookings","story_points":2}', 1, NOW(), NOW()),
('feat_sn_022', 'proj_staynest_001', 'Request to Book Workflow', 'Host approval step with confirmation email', 'features', 'feature', 'done', 'high', 'Raj Patel', 'req_sn_003', '{"epic":"bookings","story_points":4}', 1, NOW(), NOW()),
('feat_sn_023', 'proj_staynest_001', 'Booking Confirmation Email', 'Automated HTML email with reservation details', 'features', 'feature', 'done', 'medium', 'Sophie Leclerc', 'req_sn_003', '{"epic":"bookings","story_points":2}', 1, NOW(), NOW()),
('feat_sn_024', 'proj_staynest_001', 'Check-in Code Generation', 'Secure 6-digit code with expiration and multiple sends', 'features', 'feature', 'done', 'high', 'Hiroshi Nakamura', 'req_sn_048', '{"epic":"bookings","story_points":2}', 1, NOW(), NOW()),
('feat_sn_025', 'proj_staynest_001', 'Pre-arrival Message', 'Customizable host message sent 24 hours before check-in', 'features', 'feature', 'done', 'medium', 'Tamara Voss', 'req_sn_003', '{"epic":"bookings","story_points":2}', 1, NOW(), NOW()),
('feat_sn_026', 'proj_staynest_001', 'Cancellation Request Flow', 'Guest cancellation with refund calculator display', 'features', 'feature', 'in_progress', 'high', 'Carlos Mendez', 'req_sn_018', '{"epic":"bookings","story_points":3}', 1, NOW(), NOW()),
('feat_sn_027', 'proj_staynest_001', 'Refund Calculator Component', 'Real-time calculation of refund amounts', 'features', 'feature', 'done', 'high', 'Fatima Al-Mansouri', 'req_sn_018', '{"epic":"bookings","story_points":2}', 1, NOW(), NOW()),
('feat_sn_028', 'proj_staynest_001', 'Booking Timeline View', 'Visual timeline of booking status changes', 'features', 'feature', 'in_progress', 'medium', 'Dmitri Popov', 'req_sn_003', '{"epic":"bookings","story_points":3}', 1, NOW(), NOW()),
('feat_sn_029', 'proj_staynest_001', 'Guest Checklist Widget', 'Pre-arrival checklist for guests to prepare', 'features', 'feature', 'done', 'low', 'Maria Santos', 'req_sn_003', '{"epic":"bookings","story_points":2}', 1, NOW(), NOW()),
('feat_sn_030', 'proj_staynest_001', 'Booking Modification UI', 'Guest ability to request date/guest count changes', 'features', 'feature', 'todo', 'medium', 'Liam O''Brien', 'req_sn_003', '{"epic":"bookings","story_points":4}', 1, NOW(), NOW()),
('feat_sn_031', 'proj_staynest_001', 'Month View Calendar', 'Interactive calendar showing availability by date', 'features', 'feature', 'done', 'high', 'Keiko Yamamoto', 'req_sn_008', '{"epic":"calendar","story_points":5}', 1, NOW(), NOW()),
('feat_sn_032', 'proj_staynest_001', 'Minimum Stay Settings', 'Configure minimum nights for weekdays/weekends/seasons', 'features', 'feature', 'done', 'high', 'Rashid Al-Mansouri', 'req_sn_008', '{"epic":"calendar","story_points":2}', 1, NOW(), NOW()),
('feat_sn_033', 'proj_staynest_001', 'Bulk Date Blocking', 'Select range and block multiple dates at once', 'features', 'feature', 'in_progress', 'high', 'Eva Eriksson', 'req_sn_008', '{"epic":"calendar","story_points":3}', 1, NOW(), NOW()),
('feat_sn_034', 'proj_staynest_001', 'Seasonal Pricing Rules', 'Set date ranges with different pricing tiers', 'features', 'feature', 'done', 'high', 'Maxim Petrov', 'req_sn_007', '{"epic":"pricing","story_points":4}', 1, NOW(), NOW()),
('feat_sn_035', 'proj_staynest_001', 'Holiday Price Override', 'Special pricing for holiday periods', 'features', 'feature', 'done', 'medium', 'Nia Johnson', 'req_sn_007', '{"epic":"pricing","story_points":2}', 1, NOW(), NOW()),
('feat_sn_036', 'proj_staynest_001', 'Calendar Sync (iCal)', 'Export calendar to iCal format for integrations', 'features', 'feature', 'todo', 'high', 'Hassan El-Sayed', 'req_sn_050', '{"epic":"management","story_points":4}', 1, NOW(), NOW()),
('feat_sn_037', 'proj_staynest_001', 'Google Calendar Sync', 'Two-way sync with Google Calendar', 'features', 'feature', 'todo', 'high', 'Linda Zhang', 'req_sn_050', '{"epic":"management","story_points":5}', 1, NOW(), NOW()),
('feat_sn_038', 'proj_staynest_001', 'Chat Interface', 'Real-time messaging thread view', 'features', 'feature', 'in_progress', 'high', 'Stefan Novak', 'req_sn_012', '{"epic":"messaging","story_points":5}', 1, NOW(), NOW()),
('feat_sn_039', 'proj_staynest_001', 'Message Notifications', 'Email and push notifications for new messages', 'features', 'feature', 'done', 'high', 'Zainab Hassan', 'req_sn_012', '{"epic":"messaging","story_points":2}', 1, NOW(), NOW()),
('feat_sn_040', 'proj_staynest_001', 'Read Receipts', 'Show message read status with timestamps', 'features', 'feature', 'done', 'medium', 'Igor Volkov', 'req_sn_012', '{"epic":"messaging","story_points":1}', 1, NOW(), NOW()),
('feat_sn_041', 'proj_staynest_001', 'Quick Reply Templates', 'Pre-written responses for common messages', 'features', 'feature', 'done', 'medium', 'Grace Park', 'req_sn_050', '{"epic":"messaging","story_points":2}', 1, NOW(), NOW()),
('feat_sn_042', 'proj_staynest_001', 'Message Search', 'Full-text search within conversation threads', 'features', 'feature', 'todo', 'low', 'Leonardo Rossi', 'req_sn_012', '{"epic":"messaging","story_points":2}', 1, NOW(), NOW()),
('feat_sn_043', 'proj_staynest_001', 'Archived Conversations', 'Archive/unarchive conversations feature', 'features', 'feature', 'done', 'low', 'Nadia Petrova', 'req_sn_012', '{"epic":"messaging","story_points":1}', 1, NOW(), NOW()),
('feat_sn_044', 'proj_staynest_001', 'Review Submission Form', 'Star rating selector, category ratings, and text feedback', 'features', 'feature', 'done', 'high', 'James Murphy', 'req_sn_005', '{"epic":"reviews","story_points":3}', 1, NOW(), NOW()),
('feat_sn_045', 'proj_staynest_001', 'Photo Upload in Reviews', 'Allow guests to attach photos to reviews', 'features', 'feature', 'in_progress', 'medium', 'Yuki Suzuki', 'req_sn_005', '{"epic":"reviews","story_points":2}', 1, NOW(), NOW()),
('feat_sn_046', 'proj_staynest_001', 'Review Display Component', 'Star rating display with text content and guest avatar', 'features', 'feature', 'done', 'high', 'Felipe Santos', 'req_sn_005', '{"epic":"reviews","story_points":2}', 1, NOW(), NOW()),
('feat_sn_047', 'proj_staynest_001', 'Host Review Response', 'Hosts can reply to guest reviews', 'features', 'feature', 'done', 'medium', 'Natasha Volkov', 'req_sn_006', '{"epic":"reviews","story_points":2}', 1, NOW(), NOW()),
('feat_sn_048', 'proj_staynest_001', 'Review Filtering and Sorting', 'Filter reviews by rating and sort by date/helpful', 'features', 'feature', 'done', 'medium', 'Omar Al-Rashid', 'req_sn_005', '{"epic":"reviews","story_points":2}', 1, NOW(), NOW()),
('feat_sn_049', 'proj_staynest_001', 'Helpful Vote Feature', 'Guests vote on review helpfulness', 'features', 'feature', 'done', 'low', 'Simone Rossi', 'req_sn_005', '{"epic":"reviews","story_points":1}', 1, NOW(), NOW()),
('feat_sn_050', 'proj_staynest_001', 'Host Rating Badge', 'Display host rating with verified badge', 'features', 'feature', 'done', 'high', 'Kwame Osei', 'req_sn_006', '{"epic":"reviews","story_points":2}', 1, NOW(), NOW());

-- USER STORIES (First 30 of 100+)
-- As a Host
INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, owner, parent_id, item_metadata, version, created_at, updated_at) VALUES
('story_sn_001', 'proj_staynest_001', 'As a host, I want to create a property listing quickly', 'Host should complete listing in under 10 minutes with multi-step form', 'stories', 'story', 'done', 'critical', 'Leah Goldman', 'req_sn_001', '{"epic":"listings","sprint":1}', 1, NOW(), NOW()),
('story_sn_002', 'proj_staynest_001', 'As a host, I want to manage my calendar and availability', 'Hosts need visual calendar with drag-drop blocking and pricing', 'stories', 'story', 'in_progress', 'critical', 'Maxim Petrov', 'req_sn_008', '{"epic":"calendar","sprint":1}', 1, NOW(), NOW()),
('story_sn_003', 'proj_staynest_001', 'As a host, I want to set different pricing for seasons', 'Support seasonal rates with bulk import from CSV', 'stories', 'story', 'in_progress', 'high', 'Nia Johnson', 'req_sn_007', '{"epic":"pricing","sprint":2}', 1, NOW(), NOW()),
('story_sn_004', 'proj_staynest_001', 'As a host, I want to receive booking requests and approve them', 'Multi-step approval with payment processing', 'stories', 'story', 'done', 'critical', 'Hassan El-Sayed', 'req_sn_003', '{"epic":"bookings","sprint":1}', 1, NOW(), NOW()),
('story_sn_005', 'proj_staynest_001', 'As a host, I want to communicate with guests securely', 'Message system with encryption and read receipts', 'stories', 'story', 'in_progress', 'high', 'Linda Zhang', 'req_sn_012', '{"epic":"messaging","sprint":2}', 1, NOW(), NOW()),
('story_sn_006', 'proj_staynest_001', 'As a host, I want to see my earnings and payouts', 'Dashboard showing revenue with payment history', 'stories', 'story', 'done', 'high', 'Stefan Novak', 'req_sn_021', '{"epic":"payments","sprint":2}', 1, NOW(), NOW()),
('story_sn_007', 'proj_staynest_001', 'As a host, I want to respond to guest reviews', 'Interface to reply to reviews with moderation', 'stories', 'story', 'done', 'medium', 'Zainab Hassan', 'req_sn_006', '{"epic":"reviews","sprint":2}', 1, NOW(), NOW()),
('story_sn_008', 'proj_staynest_001', 'As a host, I want to enable instant booking for trusted guests', 'Toggle for instant booking with screening criteria', 'stories', 'story', 'done', 'high', 'Igor Volkov', 'req_sn_011', '{"epic":"bookings","sprint":1}', 1, NOW(), NOW()),
('story_sn_009', 'proj_staynest_001', 'As a host, I want to track my property performance analytics', 'Detailed dashboard with occupancy and revenue trends', 'stories', 'story', 'in_progress', 'high', 'Grace Park', 'req_sn_026', '{"epic":"analytics","sprint":3}', 1, NOW(), NOW()),
('story_sn_010', 'proj_staynest_001', 'As a host, I want to get verified to increase bookings', 'Verification flow with document upload and automated checks', 'stories', 'story', 'in_progress', 'critical', 'Leonardo Rossi', 'req_sn_004', '{"epic":"verification","sprint":1}', 1, NOW(), NOW()),
('story_sn_011', 'proj_staynest_001', 'As a guest, I want to search for properties with filters', 'Advanced search with map, price, dates, and amenities', 'stories', 'story', 'done', 'critical', 'Nadia Petrova', 'req_sn_002', '{"epic":"search","sprint":1}', 1, NOW(), NOW()),
('story_sn_012', 'proj_staynest_001', 'As a guest, I want to see detailed property information', 'Photos, reviews, host info, house rules, amenities', 'stories', 'story', 'done', 'critical', 'James Murphy', 'req_sn_001', '{"epic":"listings","sprint":1}', 1, NOW(), NOW()),
('story_sn_013', 'proj_staynest_001', 'As a guest, I want to book a property instantly', 'Quick booking flow without host approval', 'stories', 'story', 'done', 'high', 'Yuki Suzuki', 'req_sn_003', '{"epic":"bookings","sprint":1}', 1, NOW(), NOW()),
('story_sn_014', 'proj_staynest_001', 'As a guest, I want to request to book and wait for approval', 'Request flow with host notification and timeout', 'stories', 'story', 'done', 'high', 'Felipe Santos', 'req_sn_003', '{"epic":"bookings","sprint":1}', 1, NOW(), NOW()),
('story_sn_015', 'proj_staynest_001', 'As a guest, I want to cancel my booking with clear refund info', 'Cancellation form with live refund calculator', 'stories', 'story', 'in_progress', 'high', 'Natasha Volkov', 'req_sn_018', '{"epic":"bookings","sprint":2}', 1, NOW(), NOW()),
('story_sn_016', 'proj_staynest_001', 'As a guest, I want to message the host before or during my stay', 'Real-time chat with notifications', 'stories', 'story', 'in_progress', 'high', 'Omar Al-Rashid', 'req_sn_012', '{"epic":"messaging","sprint":2}', 1, NOW(), NOW()),
('story_sn_017', 'proj_staynest_001', 'As a guest, I want to leave a detailed review', 'Rating form with photos and detailed feedback', 'stories', 'story', 'done', 'high', 'Simone Rossi', 'req_sn_005', '{"epic":"reviews","sprint":2}', 1, NOW(), NOW()),
('story_sn_018', 'proj_staynest_001', 'As a guest, I want to save favorite properties', 'Wishlist feature with sharing capabilities', 'stories', 'story', 'done', 'medium', 'Kwame Osei', 'req_sn_028', '{"epic":"search","sprint":1}', 1, NOW(), NOW()),
('story_sn_019', 'proj_staynest_001', 'As a guest, I want to verify my identity for better deals', 'Optional verification with photo ID upload', 'stories', 'story', 'in_progress', 'medium', 'Valentina Rossi', 'req_sn_034', '{"epic":"verification","sprint":2}', 1, NOW(), NOW()),
('story_sn_020', 'proj_staynest_001', 'As a guest, I want to view my booking history', 'Timeline of past bookings with receipts and reviews', 'stories', 'story', 'done', 'high', 'Soren Jensen', 'req_sn_003', '{"epic":"bookings","sprint":1}', 1, NOW(), NOW()),
('story_sn_021', 'proj_staynest_001', 'As admin, I want to moderate reviews and photos', 'Content review queue with approve/reject/hide options', 'stories', 'story', 'todo', 'high', 'Rajesh Kumar', 'req_sn_045', '{"epic":"moderation","sprint":4}', 1, NOW(), NOW()),
('story_sn_022', 'proj_staynest_001', 'As admin, I want to detect fraud and suspicious behavior', 'Dashboard showing flagged users and bookings', 'stories', 'story', 'todo', 'critical', 'Svetlana Kuznetsova', 'req_sn_023', '{"epic":"security","sprint":4}', 1, NOW(), NOW()),
('story_sn_023', 'proj_staynest_001', 'As admin, I want to handle disputes between hosts and guests', 'Ticket system with resolution tracking', 'stories', 'story', 'todo', 'high', 'Marcus Thompson', 'req_sn_019', '{"epic":"disputes","sprint":4}', 1, NOW(), NOW()),
('story_sn_024', 'proj_staynest_001', 'As admin, I want to generate compliance reports', 'Export data for regulatory requirements', 'stories', 'story', 'todo', 'high', 'Amanda Foster', 'req_sn_023', '{"epic":"compliance","sprint":4}', 1, NOW(), NOW()),
('story_sn_025', 'proj_staynest_001', 'As admin, I want to manage host payouts and refunds', 'Batch processing and failure recovery system', 'stories', 'story', 'todo', 'critical', 'Christophe Blanc', 'req_sn_021', '{"epic":"payments","sprint":4}', 1, NOW(), NOW()),
('story_sn_026', 'proj_staynest_001', 'As admin, I want to monitor system performance', 'Dashboards for uptime, latency, and error rates', 'stories', 'story', 'todo', 'high', 'Asha Patel', 'req_sn_039', '{"epic":"operations","sprint":4}', 1, NOW(), NOW()),
('story_sn_027', 'proj_staynest_001', 'As admin, I want to send targeted notifications to users', 'Campaign builder with segmentation', 'stories', 'story', 'todo', 'medium', 'Viktor Novikov', 'req_sn_040', '{"epic":"notifications","sprint":4}', 1, NOW(), NOW()),
('story_sn_028', 'proj_staynest_001', 'As admin, I want to manage user roles and permissions', 'Admin panel with granular access control', 'stories', 'story', 'todo', 'high', 'Monica Santoro', 'req_sn_046', '{"epic":"accounts","sprint":4}', 1, NOW(), NOW());

-- TASKS (First 30 of 100+)
INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, owner, parent_id, item_metadata, version, created_at, updated_at) VALUES
('task_sn_001', 'proj_staynest_001', 'Setup PostgreSQL schema for listings table', 'Create listings table with indexes and constraints', 'tasks', 'task', 'done', 'critical', 'Aleksei Sokolov', 'story_sn_001', '{"sprint":1,"hours":4}', 1, NOW(), NOW()),
('task_sn_002', 'proj_staynest_001', 'Create ListingController API endpoints', 'POST /listings, GET /listings/:id, PUT /listings/:id', 'tasks', 'task', 'done', 'critical', 'Patricia Moore', 'story_sn_001', '{"sprint":1,"hours":8}', 1, NOW(), NOW()),
('task_sn_003', 'proj_staynest_001', 'Build property listing form component', 'React component with validation and multi-step wizard', 'tasks', 'task', 'in_progress', 'high', 'Karim Hassan', 'story_sn_001', '{"sprint":1,"hours":12}', 1, NOW(), NOW()),
('task_sn_004', 'proj_staynest_001', 'Implement photo upload and compression', 'Sharp library for image optimization, S3 storage', 'tasks', 'task', 'done', 'high', 'Isabel Garcia', 'feat_sn_011', '{"sprint":1,"hours":8}', 1, NOW(), NOW()),
('task_sn_005', 'proj_staynest_001', 'Create amenities database and seed data', 'CSV import script for 200+ amenities', 'tasks', 'task', 'done', 'medium', 'Johannes Mueller', 'req_sn_013', '{"sprint":1,"hours":6}', 1, NOW(), NOW()),
('task_sn_006', 'proj_staynest_001', 'Design and implement Calendar component', 'React calendar with availability visualization', 'tasks', 'task', 'in_progress', 'high', 'Priya Desai', 'feat_sn_031', '{"sprint":2,"hours":16}', 1, NOW(), NOW()),
('task_sn_007', 'proj_staynest_001', 'Implement Stripe payment integration', 'Webhook handlers and charge processing', 'tasks', 'task', 'done', 'critical', 'Thomas Mueller', 'feat_sn_014', '{"sprint":1,"hours":12}', 1, NOW(), NOW()),
('task_sn_008', 'proj_staynest_001', 'Setup real-time messaging with WebSockets', 'Socket.IO implementation for chat', 'tasks', 'task', 'in_progress', 'high', 'Yuki Nakamura', 'feat_sn_038', '{"sprint":2,"hours":14}', 1, NOW(), NOW()),
('task_sn_009', 'proj_staynest_001', 'Create booking state machine and workflows', 'State transitions and validation logic', 'tasks', 'task', 'done', 'critical', 'Gabriel Rodriguez', 'req_sn_003', '{"sprint":1,"hours":10}', 1, NOW(), NOW()),
('task_sn_010', 'proj_staynest_001', 'Implement review moderation queue UI', 'Admin interface for content review', 'tasks', 'task', 'todo', 'high', 'Leah Goldman', 'story_sn_021', '{"sprint":4,"hours":10}', 1, NOW(), NOW()),
('task_sn_011', 'proj_staynest_001', 'Build authentication with WorkOS AuthKit', 'OAuth flow and JWT token validation', 'tasks', 'task', 'done', 'critical', 'Maxim Petrov', 'req_sn_033', '{"sprint":1,"hours":8}', 1, NOW(), NOW()),
('task_sn_012', 'proj_staynest_001', 'Create user role and permission system', 'Database schema and service layer', 'tasks', 'task', 'todo', 'high', 'Nia Johnson', 'story_sn_028', '{"sprint":4,"hours":12}', 1, NOW(), NOW()),
('task_sn_013', 'proj_staynest_001', 'Implement two-factor authentication', 'SMS and authenticator app support', 'tasks', 'task', 'done', 'critical', 'Hassan El-Sayed', 'req_sn_032', '{"sprint":1,"hours":10}', 1, NOW(), NOW()),
('task_sn_014', 'proj_staynest_001', 'Build advanced search filters and faceting', 'Elasticsearch or SQL full-text search', 'tasks', 'task', 'in_progress', 'high', 'Linda Zhang', 'req_sn_002', '{"sprint":1,"hours":14}', 1, NOW(), NOW()),
('task_sn_015', 'proj_staynest_001', 'Create map integration component', 'Google Maps API with property pins', 'tasks', 'task', 'done', 'high', 'Stefan Novak', 'feat_sn_001', '{"sprint":1,"hours":8}', 1, NOW(), NOW()),
('task_sn_016', 'proj_staynest_001', 'Setup analytics event tracking', 'Segment or Mixpanel integration', 'tasks', 'task', 'todo', 'medium', 'Zainab Hassan', 'req_sn_026', '{"sprint":3,"hours":8}', 1, NOW(), NOW()),
('task_sn_017', 'proj_staynest_001', 'Build revenue dashboard with charts', 'Chart.js and revenue calculations', 'tasks', 'task', 'in_progress', 'high', 'Igor Volkov', 'story_sn_006', '{"sprint":2,"hours":10}', 1, NOW(), NOW()),
('task_sn_018', 'proj_staynest_001', 'Implement email template system', 'Handlebars templates with sendgrid', 'tasks', 'task', 'done', 'high', 'Grace Park', 'req_sn_041', '{"sprint":1,"hours":6}', 1, NOW(), NOW()),
('task_sn_019', 'proj_staynest_001', 'Create refund calculator service', 'Business logic for cancellation refunds', 'tasks', 'task', 'done', 'high', 'Leonardo Rossi', 'feat_sn_027', '{"sprint":2,"hours":6}', 1, NOW(), NOW()),
('task_sn_020', 'proj_staynest_001', 'Implement document verification API', 'OCR and document validation service', 'tasks', 'task', 'in_progress', 'critical', 'Nadia Petrova', 'req_sn_004', '{"sprint":1,"hours":16}', 1, NOW(), NOW()),
('task_sn_021', 'proj_staynest_001', 'Build fraud detection scoring engine', 'ML-based anomaly detection', 'tasks', 'task', 'todo', 'critical', 'James Murphy', 'story_sn_022', '{"sprint":4,"hours":20}', 1, NOW(), NOW()),
('task_sn_022', 'proj_staynest_001', 'Create tax calculation microservice', 'Support multiple jurisdictions', 'tasks', 'task', 'done', 'high', 'Yuki Suzuki', 'req_sn_009', '{"sprint":1,"hours":10}', 1, NOW(), NOW()),
('task_sn_023', 'proj_staynest_001', 'Setup Stripe Connect for host payouts', 'OAuth and transfer API', 'tasks', 'task', 'in_progress', 'critical', 'Felipe Santos', 'story_sn_006', '{"sprint":2,"hours":12}', 1, NOW(), NOW()),
('task_sn_024', 'proj_staynest_001', 'Build instant booking approval logic', 'Auto-approve for screened guests', 'tasks', 'task', 'done', 'high', 'Natasha Volkov', 'feat_sn_021', '{"sprint":1,"hours":6}', 1, NOW(), NOW()),
('task_sn_025', 'proj_staynest_001', 'Create host response email notification', 'WebSocket event for instant updates', 'tasks', 'task', 'done', 'medium', 'Omar Al-Rashid', 'feat_sn_022', '{"sprint":1,"hours":4}', 1, NOW(), NOW()),
('task_sn_026', 'proj_staynest_001', 'Implement calendar sync with iCal', 'iCalendar format export', 'tasks', 'task', 'todo', 'high', 'Simone Rossi', 'feat_sn_036', '{"sprint":3,"hours":10}', 1, NOW(), NOW()),
('task_sn_027', 'proj_staynest_001', 'Setup Google Calendar API integration', 'Two-way sync with Google Calendar', 'tasks', 'task', 'todo', 'high', 'Kwame Osei', 'feat_sn_037', '{"sprint":3,"hours":14}', 1, NOW(), NOW()),
('task_sn_028', 'proj_staynest_001', 'Create automated reminder system', 'Scheduled emails and push notifications', 'tasks', 'task', 'done', 'high', 'Valentina Rossi', 'req_sn_049', '{"sprint":1,"hours":8}', 1, NOW(), NOW()),
('task_sn_029', 'proj_staynest_001', 'Build dispute ticket management system', 'Queue, assignment, and resolution tracking', 'tasks', 'task', 'todo', 'high', 'Soren Jensen', 'story_sn_023', '{"sprint":4,"hours":16}', 1, NOW(), NOW()),
('task_sn_030', 'proj_staynest_001', 'Implement rate limiting and API throttling', 'Redis-based request tracking', 'tasks', 'task', 'done', 'high', 'Rajesh Kumar', 'req_sn_039', '{"sprint":2,"hours":6}', 1, NOW(), NOW());

-- TESTS (First 20 of 100+)
INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, owner, parent_id, item_metadata, version, created_at, updated_at) VALUES
('test_sn_001', 'proj_staynest_001', 'Unit test: validateListingInput', 'Test validation rules for listing creation form', 'tests', 'test', 'done', 'high', 'Svetlana Kuznetsova', 'task_sn_003', '{"type":"unit","coverage":95}', 1, NOW(), NOW()),
('test_sn_002', 'proj_staynest_001', 'Unit test: calculateRefund', 'Test refund calculation logic for different policies', 'tests', 'test', 'done', 'high', 'Marcus Thompson', 'task_sn_019', '{"type":"unit","coverage":98}', 1, NOW(), NOW()),
('test_sn_003', 'proj_staynest_001', 'Unit test: priceCalculation', 'Test pricing with taxes, fees, and discounts', 'tests', 'test', 'done', 'high', 'Amanda Foster', 'task_sn_022', '{"type":"unit","coverage":97}', 1, NOW(), NOW()),
('test_sn_004', 'proj_staynest_001', 'Integration test: createListing API', 'Test POST /api/listings with database persistence', 'tests', 'test', 'in_progress', 'high', 'Christophe Blanc', 'task_sn_002', '{"type":"integration","coverage":90}', 1, NOW(), NOW()),
('test_sn_005', 'proj_staynest_001', 'Integration test: searchListings API', 'Test search endpoint with filters and pagination', 'tests', 'test', 'in_progress', 'high', 'Asha Patel', 'task_sn_014', '{"type":"integration","coverage":88}', 1, NOW(), NOW()),
('test_sn_006', 'proj_staynest_001', 'Integration test: bookingWorkflow', 'Test complete booking request and approval flow', 'tests', 'test', 'done', 'critical', 'Viktor Novikov', 'task_sn_009', '{"type":"integration","coverage":94}', 1, NOW(), NOW()),
('test_sn_007', 'proj_staynest_001', 'Integration test: paymentProcessing', 'Test Stripe charge and refund handling', 'tests', 'test', 'done', 'critical', 'Monica Santoro', 'task_sn_007', '{"type":"integration","coverage":92}', 1, NOW(), NOW()),
('test_sn_008', 'proj_staynest_001', 'E2E test: hostListingFlow', 'Test complete listing creation workflow', 'tests', 'test', 'in_progress', 'high', 'Aleksei Sokolov', 'story_sn_001', '{"type":"e2e","coverage":85}', 1, NOW(), NOW()),
('test_sn_009', 'proj_staynest_001', 'E2E test: guestBookingFlow', 'Test search, view, and booking complete workflow', 'tests', 'test', 'in_progress', 'high', 'Patricia Moore', 'story_sn_011', '{"type":"e2e","coverage":86}', 1, NOW(), NOW()),
('test_sn_010', 'proj_staynest_001', 'E2E test: paymentCheckout', 'Test complete payment and confirmation flow', 'tests', 'test', 'done', 'critical', 'Karim Hassan', 'task_sn_007', '{"type":"e2e","coverage":91}', 1, NOW(), NOW()),
('test_sn_011', 'proj_staynest_001', 'Unit test: messageEncryption', 'Test encryption/decryption of chat messages', 'tests', 'test', 'done', 'high', 'Isabel Garcia', 'task_sn_008', '{"type":"unit","coverage":96}', 1, NOW(), NOW()),
('test_sn_012', 'proj_staynest_001', 'Integration test: messagingSystem', 'Test real-time message delivery and notifications', 'tests', 'test', 'in_progress', 'high', 'Johannes Mueller', 'feat_sn_038', '{"type":"integration","coverage":87}', 1, NOW(), NOW()),
('test_sn_013', 'proj_staynest_001', 'Unit test: reviewValidation', 'Test review rating and content validation', 'tests', 'test', 'done', 'medium', 'Priya Desai', 'feat_sn_044', '{"type":"unit","coverage":93}', 1, NOW(), NOW()),
('test_sn_014', 'proj_staynest_001', 'Integration test: reviewSystem', 'Test review submission and display workflow', 'tests', 'test', 'done', 'high', 'Thomas Mueller', 'story_sn_017', '{"type":"integration","coverage":89}', 1, NOW(), NOW()),
('test_sn_015', 'proj_staynest_001', 'Unit test: availabilityCalculation', 'Test calendar availability and conflicts', 'tests', 'test', 'done', 'high', 'Yuki Nakamura', 'feat_sn_031', '{"type":"unit","coverage":94}', 1, NOW(), NOW()),
('test_sn_016', 'proj_staynest_001', 'Integration test: calendarSync', 'Test iCal export and Google Calendar sync', 'tests', 'test', 'todo', 'high', 'Gabriel Rodriguez', 'task_sn_026', '{"type":"integration","coverage":80}', 1, NOW(), NOW()),
('test_sn_017', 'proj_staynest_001', 'Unit test: documentVerification', 'Test OCR and document validation logic', 'tests', 'test', 'in_progress', 'critical', 'Leah Goldman', 'task_sn_020', '{"type":"unit","coverage":91}', 1, NOW(), NOW()),
('test_sn_018', 'proj_staynest_001', 'Integration test: fraudDetection', 'Test fraud scoring and flagging system', 'tests', 'test', 'todo', 'critical', 'Maxim Petrov', 'task_sn_021', '{"type":"integration","coverage":75}', 1, NOW(), NOW()),
('test_sn_019', 'proj_staynest_001', 'Unit test: permissionChecks', 'Test role-based access control logic', 'tests', 'test', 'todo', 'high', 'Nia Johnson', 'task_sn_012', '{"type":"unit","coverage":96}', 1, NOW(), NOW()),
('test_sn_020', 'proj_staynest_001', 'E2E test: adminModeration', 'Test content review and moderation flow', 'tests', 'test', 'todo', 'high', 'Hassan El-Sayed', 'task_sn_010', '{"type":"e2e","coverage":82}', 1, NOW(), NOW());

-- APIs (First 20 of 50+)
INSERT INTO items (id, project_id, title, description, view, item_type, status, priority, owner, parent_id, item_metadata, version, created_at, updated_at) VALUES
('api_sn_001', 'proj_staynest_001', 'POST /api/listings - Create listing', 'Create new property listing with full details', 'apis', 'api', 'done', 'critical', 'Linda Zhang', 'task_sn_002', '{"method":"POST","auth":"required","rateLimit":10}', 1, NOW(), NOW()),
('api_sn_002', 'proj_staynest_001', 'GET /api/listings - Search listings', 'Advanced search with filters, sorting, pagination', 'apis', 'api', 'done', 'critical', 'Stefan Novak', 'task_sn_014', '{"method":"GET","auth":"optional","rateLimit":100}', 1, NOW(), NOW()),
('api_sn_003', 'proj_staynest_001', 'GET /api/listings/:id - Get listing details', 'Retrieve full listing with reviews and photos', 'apis', 'api', 'done', 'high', 'Zainab Hassan', 'task_sn_002', '{"method":"GET","auth":"optional","rateLimit":100}', 1, NOW(), NOW()),
('api_sn_004', 'proj_staynest_001', 'PUT /api/listings/:id - Update listing', 'Update listing details and photos', 'apis', 'api', 'in_progress', 'high', 'Igor Volkov', 'task_sn_002', '{"method":"PUT","auth":"required","rateLimit":20}', 1, NOW(), NOW()),
('api_sn_005', 'proj_staynest_001', 'DELETE /api/listings/:id - Deactivate listing', 'Soft delete listing while preserving data', 'apis', 'api', 'todo', 'medium', 'Grace Park', 'task_sn_002', '{"method":"DELETE","auth":"required","rateLimit":10}', 1, NOW(), NOW()),
('api_sn_006', 'proj_staynest_001', 'POST /api/bookings - Create booking', 'Submit booking request with payment', 'apis', 'api', 'done', 'critical', 'Leonardo Rossi', 'task_sn_009', '{"method":"POST","auth":"required","rateLimit":5}', 1, NOW(), NOW()),
('api_sn_007', 'proj_staynest_001', 'GET /api/bookings/:id - Get booking details', 'Retrieve booking with timeline and messages', 'apis', 'api', 'done', 'high', 'Nadia Petrova', 'task_sn_009', '{"method":"GET","auth":"required","rateLimit":50}', 1, NOW(), NOW()),
('api_sn_008', 'proj_staynest_001', 'POST /api/bookings/:id/cancel - Cancel booking', 'Process cancellation with refund', 'apis', 'api', 'in_progress', 'high', 'James Murphy', 'task_sn_019', '{"method":"POST","auth":"required","rateLimit":10}', 1, NOW(), NOW()),
('api_sn_009', 'proj_staynest_001', 'POST /api/reviews - Submit review', 'Create guest or host review with ratings', 'apis', 'api', 'done', 'high', 'Yuki Suzuki', 'feat_sn_044', '{"method":"POST","auth":"required","rateLimit":5}', 1, NOW(), NOW()),
('api_sn_010', 'proj_staynest_001', 'GET /api/reviews/:id - Get review details', 'Retrieve single review with responses', 'apis', 'api', 'done', 'medium', 'Felipe Santos', 'feat_sn_046', '{"method":"GET","auth":"optional","rateLimit":100}', 1, NOW(), NOW()),
('api_sn_011', 'proj_staynest_001', 'POST /api/payments/charge - Process payment', 'Charge guest card via Stripe', 'apis', 'api', 'done', 'critical', 'Natasha Volkov', 'task_sn_007', '{"method":"POST","auth":"required","rateLimit":10}', 1, NOW(), NOW()),
('api_sn_012', 'proj_staynest_001', 'GET /api/payments/invoice/:id - Get invoice', 'Download PDF invoice for booking', 'apis', 'api', 'done', 'medium', 'Omar Al-Rashid', 'task_sn_018', '{"method":"GET","auth":"required","rateLimit":50}', 1, NOW(), NOW()),
('api_sn_013', 'proj_staynest_001', 'GET /api/calendar/:listing_id - Get availability', 'Retrieve availability calendar for listing', 'apis', 'api', 'done', 'high', 'Simone Rossi', 'feat_sn_031', '{"method":"GET","auth":"optional","rateLimit":100}', 1, NOW(), NOW()),
('api_sn_014', 'proj_staynest_001', 'PUT /api/calendar/:listing_id - Update availability', 'Block/unblock dates and set pricing', 'apis', 'api', 'in_progress', 'high', 'Kwame Osei', 'feat_sn_033', '{"method":"PUT","auth":"required","rateLimit":20}', 1, NOW(), NOW()),
('api_sn_015', 'proj_staynest_001', 'POST /api/messages - Send message', 'Create new message between users', 'apis', 'api', 'in_progress', 'high', 'Valentina Rossi', 'feat_sn_038', '{"method":"POST","auth":"required","rateLimit":100}', 1, NOW(), NOW()),
('api_sn_016', 'proj_staynest_001', 'GET /api/messages/:conversation_id - Get thread', 'Retrieve message conversation history', 'apis', 'api', 'in_progress', 'high', 'Soren Jensen', 'feat_sn_038', '{"method":"GET","auth":"required","rateLimit":50}', 1, NOW(), NOW()),
('api_sn_017', 'proj_staynest_001', 'POST /api/verification/upload - Upload documents', 'Submit ID and verification documents', 'apis', 'api', 'done', 'critical', 'Rajesh Kumar', 'task_sn_020', '{"method":"POST","auth":"required","rateLimit":5}', 1, NOW(), NOW()),
('api_sn_018', 'proj_staynest_001', 'GET /api/analytics/host - Host dashboard metrics', 'Get revenue, occupancy, and performance data', 'apis', 'api', 'in_progress', 'high', 'Svetlana Kuznetsova', 'task_sn_017', '{"method":"GET","auth":"required","rateLimit":30}', 1, NOW(), NOW()),
('api_sn_019', 'proj_staynest_001', 'GET /api/payouts/schedule - Payout timeline', 'Retrieve payout schedule and status', 'apis', 'api', 'done', 'high', 'Marcus Thompson', 'story_sn_006', '{"method":"GET","auth":"required","rateLimit":20}', 1, NOW(), NOW()),
('api_sn_020', 'proj_staynest_001', 'POST /api/disputes - Create dispute ticket', 'Submit booking dispute for mediation', 'apis', 'api', 'todo', 'high', 'Amanda Foster', 'task_sn_029', '{"method":"POST","auth":"required","rateLimit":5}', 1, NOW(), NOW());

-- LINKS (200+ relations between items)
-- Requirements to Features Links
INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, link_metadata, created_at, updated_at) VALUES
('link_sn_001', 'proj_staynest_001', 'req_sn_002', 'feat_sn_001', 'implements', '{"order":1}', NOW(), NOW()),
('link_sn_002', 'proj_staynest_001', 'req_sn_002', 'feat_sn_002', 'implements', '{"order":2}', NOW(), NOW()),
('link_sn_003', 'proj_staynest_001', 'req_sn_002', 'feat_sn_003', 'implements', '{"order":3}', NOW(), NOW()),
('link_sn_004', 'proj_staynest_001', 'req_sn_002', 'feat_sn_004', 'implements', '{"order":4}', NOW(), NOW()),
('link_sn_005', 'proj_staynest_001', 'req_sn_002', 'feat_sn_005', 'implements', '{"order":5}', NOW(), NOW()),
('link_sn_006', 'proj_staynest_001', 'req_sn_001', 'feat_sn_011', 'implements', '{"order":1}', NOW(), NOW()),
('link_sn_007', 'proj_staynest_001', 'req_sn_001', 'feat_sn_012', 'implements', '{"order":2}', NOW(), NOW()),
('link_sn_008', 'proj_staynest_001', 'req_sn_001', 'feat_sn_013', 'implements', '{"order":3}', NOW(), NOW()),
('link_sn_009', 'proj_staynest_001', 'req_sn_001', 'feat_sn_014', 'implements', '{"order":4}', NOW(), NOW()),
('link_sn_010', 'proj_staynest_001', 'req_sn_001', 'feat_sn_015', 'implements', '{"order":5}', NOW(), NOW()),
('link_sn_011', 'proj_staynest_001', 'req_sn_003', 'feat_sn_022', 'implements', '{"order":1}', NOW(), NOW()),
('link_sn_012', 'proj_staynest_001', 'req_sn_003', 'feat_sn_023', 'implements', '{"order":2}', NOW(), NOW()),
('link_sn_013', 'proj_staynest_001', 'req_sn_003', 'feat_sn_028', 'implements', '{"order":3}', NOW(), NOW()),
('link_sn_014', 'proj_staynest_001', 'req_sn_003', 'feat_sn_029', 'implements', '{"order":4}', NOW(), NOW()),
('link_sn_015', 'proj_staynest_001', 'req_sn_008', 'feat_sn_031', 'implements', '{"order":1}', NOW(), NOW()),
('link_sn_016', 'proj_staynest_001', 'req_sn_008', 'feat_sn_032', 'implements', '{"order":2}', NOW(), NOW()),
('link_sn_017', 'proj_staynest_001', 'req_sn_008', 'feat_sn_033', 'implements', '{"order":3}', NOW(), NOW()),
('link_sn_018', 'proj_staynest_001', 'req_sn_007', 'feat_sn_034', 'implements', '{"order":1}', NOW(), NOW()),
('link_sn_019', 'proj_staynest_001', 'req_sn_007', 'feat_sn_035', 'implements', '{"order":2}', NOW(), NOW()),
('link_sn_020', 'proj_staynest_001', 'req_sn_012', 'feat_sn_038', 'implements', '{"order":1}', NOW(), NOW()),
('link_sn_021', 'proj_staynest_001', 'req_sn_012', 'feat_sn_039', 'implements', '{"order":2}', NOW(), NOW()),
('link_sn_022', 'proj_staynest_001', 'req_sn_012', 'feat_sn_040', 'implements', '{"order":3}', NOW(), NOW()),
('link_sn_023', 'proj_staynest_001', 'req_sn_012', 'feat_sn_043', 'implements', '{"order":4}', NOW(), NOW()),
('link_sn_024', 'proj_staynest_001', 'req_sn_005', 'feat_sn_044', 'implements', '{"order":1}', NOW(), NOW()),
('link_sn_025', 'proj_staynest_001', 'req_sn_005', 'feat_sn_045', 'implements', '{"order":2}', NOW(), NOW()),
('link_sn_026', 'proj_staynest_001', 'req_sn_005', 'feat_sn_046', 'implements', '{"order":3}', NOW(), NOW()),
('link_sn_027', 'proj_staynest_001', 'req_sn_006', 'feat_sn_047', 'implements', '{"order":1}', NOW(), NOW()),
('link_sn_028', 'proj_staynest_001', 'req_sn_006', 'feat_sn_050', 'implements', '{"order":2}', NOW(), NOW()),
('link_sn_029', 'proj_staynest_001', 'req_sn_009', 'api_sn_011', 'implements', '{"order":1}', NOW(), NOW()),
('link_sn_030', 'proj_staynest_001', 'req_sn_009', 'api_sn_012', 'implements', '{"order":2}', NOW(), NOW()),
('link_sn_031', 'proj_staynest_001', 'req_sn_009', 'task_sn_022', 'implements', '{"order":3}', NOW(), NOW()),
('link_sn_032', 'proj_staynest_001', 'req_sn_009', 'api_sn_018', 'implements', '{"order":4}', NOW(), NOW()),
('link_sn_033', 'proj_staynest_001', 'req_sn_009', 'api_sn_019', 'implements', '{"order":5}', NOW(), NOW());

-- Stories to Features Links
INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, link_metadata, created_at, updated_at) VALUES
('link_sn_034', 'proj_staynest_001', 'story_sn_001', 'feat_sn_011', 'requires', '{"priority":"high"}', NOW(), NOW()),
('link_sn_035', 'proj_staynest_001', 'story_sn_001', 'feat_sn_012', 'requires', '{"priority":"high"}', NOW(), NOW()),
('link_sn_036', 'proj_staynest_001', 'story_sn_002', 'feat_sn_031', 'requires', '{"priority":"critical"}', NOW(), NOW()),
('link_sn_037', 'proj_staynest_001', 'story_sn_002', 'feat_sn_033', 'requires', '{"priority":"high"}', NOW(), NOW()),
('link_sn_038', 'proj_staynest_001', 'story_sn_011', 'feat_sn_001', 'requires', '{"priority":"high"}', NOW(), NOW()),
('link_sn_039', 'proj_staynest_001', 'story_sn_011', 'feat_sn_002', 'requires', '{"priority":"high"}', NOW(), NOW()),
('link_sn_040', 'proj_staynest_001', 'story_sn_013', 'api_sn_011', 'requires', '{"priority":"critical"}', NOW(), NOW()),
('link_sn_041', 'proj_staynest_001', 'story_sn_013', 'feat_sn_023', 'requires', '{"priority":"high"}', NOW(), NOW()),
('link_sn_042', 'proj_staynest_001', 'story_sn_015', 'feat_sn_027', 'requires', '{"priority":"critical"}', NOW(), NOW()),
('link_sn_043', 'proj_staynest_001', 'story_sn_016', 'feat_sn_038', 'requires', '{"priority":"high"}', NOW(), NOW()),
('link_sn_044', 'proj_staynest_001', 'story_sn_017', 'feat_sn_044', 'requires', '{"priority":"high"}', NOW(), NOW());

-- Tasks to Stories Links
INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, link_metadata, created_at, updated_at) VALUES
('link_sn_045', 'proj_staynest_001', 'task_sn_001', 'story_sn_001', 'implements', '{"dependency":"blocking"}', NOW(), NOW()),
('link_sn_046', 'proj_staynest_001', 'task_sn_002', 'story_sn_001', 'implements', '{"dependency":"blocking"}', NOW(), NOW()),
('link_sn_047', 'proj_staynest_001', 'task_sn_007', 'story_sn_013', 'implements', '{"dependency":"blocking"}', NOW(), NOW()),
('link_sn_048', 'proj_staynest_001', 'task_sn_008', 'story_sn_016', 'implements', '{"dependency":"blocking"}', NOW(), NOW()),
('link_sn_049', 'proj_staynest_001', 'task_sn_006', 'story_sn_002', 'implements', '{"dependency":"blocking"}', NOW(), NOW()),
('link_sn_050', 'proj_staynest_001', 'task_sn_009', 'story_sn_014', 'implements', '{"dependency":"blocking"}', NOW(), NOW());

-- Tests to Features/Tasks Links
INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, link_metadata, created_at, updated_at) VALUES
('link_sn_051', 'proj_staynest_001', 'test_sn_001', 'task_sn_003', 'validates', '{"coverage":"95%"}', NOW(), NOW()),
('link_sn_052', 'proj_staynest_001', 'test_sn_002', 'task_sn_019', 'validates', '{"coverage":"98%"}', NOW(), NOW()),
('link_sn_053', 'proj_staynest_001', 'test_sn_003', 'task_sn_022', 'validates', '{"coverage":"97%"}', NOW(), NOW()),
('link_sn_054', 'proj_staynest_001', 'test_sn_004', 'task_sn_002', 'validates', '{"coverage":"90%"}', NOW(), NOW()),
('link_sn_055', 'proj_staynest_001', 'test_sn_006', 'task_sn_009', 'validates', '{"coverage":"94%"}', NOW(), NOW()),
('link_sn_056', 'proj_staynest_001', 'test_sn_008', 'story_sn_001', 'validates', '{"coverage":"85%"}', NOW(), NOW()),
('link_sn_057', 'proj_staynest_001', 'test_sn_009', 'story_sn_011', 'validates', '{"coverage":"86%"}', NOW(), NOW());

-- APIs to Tasks Links
INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, link_metadata, created_at, updated_at) VALUES
('link_sn_058', 'proj_staynest_001', 'api_sn_001', 'task_sn_002', 'provides', '{"status":"done"}', NOW(), NOW()),
('link_sn_059', 'proj_staynest_001', 'api_sn_002', 'task_sn_014', 'provides', '{"status":"done"}', NOW(), NOW()),
('link_sn_060', 'proj_staynest_001', 'api_sn_006', 'task_sn_009', 'provides', '{"status":"done"}', NOW(), NOW()),
('link_sn_061', 'proj_staynest_001', 'api_sn_011', 'task_sn_007', 'provides', '{"status":"done"}', NOW(), NOW()),
('link_sn_062', 'proj_staynest_001', 'api_sn_015', 'task_sn_008', 'provides', '{"status":"in_progress"}', NOW(), NOW()),
('link_sn_063', 'proj_staynest_001', 'api_sn_013', 'task_sn_006', 'provides', '{"status":"done"}', NOW(), NOW());

-- Cross-Feature Dependencies
INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, link_metadata, created_at, updated_at) VALUES
('link_sn_064', 'proj_staynest_001', 'feat_sn_031', 'feat_sn_034', 'blocks', '{"reason":"requires_calendar_data"}', NOW(), NOW()),
('link_sn_065', 'proj_staynest_001', 'api_sn_011', 'task_sn_022', 'requires', '{"order":"before"}', NOW(), NOW()),
('link_sn_066', 'proj_staynest_001', 'feat_sn_044', 'feat_sn_046', 'blocks', '{"reason":"display_depends_on_submission"}', NOW(), NOW()),
('link_sn_067', 'proj_staynest_001', 'feat_sn_038', 'feat_sn_039', 'requires', '{"order":"before"}', NOW(), NOW()),
('link_sn_068', 'proj_staynest_001', 'feat_sn_038', 'feat_sn_040', 'requires', '{"order":"before"}', NOW(), NOW()),
('link_sn_069', 'proj_staynest_001', 'req_sn_004', 'task_sn_020', 'requires', '{"order":"before"}', NOW(), NOW()),
('link_sn_070', 'proj_staynest_001', 'req_sn_032', 'req_sn_033', 'requires', '{"order":"after"}', NOW(), NOW());

-- Final summary and commit
SELECT COUNT(*) as total_items FROM items WHERE project_id = 'proj_staynest_001';
SELECT COUNT(*) as total_links FROM links WHERE project_id = 'proj_staynest_001';
