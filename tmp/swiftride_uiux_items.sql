-- SwiftRide UI/UX Items Generation
-- Generated: 2026-01-31T20:28:34.709713
-- Project ID: cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e
-- Total Items: 602

BEGIN;

-- ========================================
-- WIREFRAMES (100 items)
-- ========================================
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '72bc6d1e-500f-43cb-b22f-eca6760629fe',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Login Screen',
    'Authentication screen with email/phone and password fields, social login options',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd3e9229f-f831-4ebf-b4e6-564b41a18a67',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Registration Flow',
    'Multi-step registration with personal info, vehicle details, and document upload',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'fe4b641c-c67b-4e51-87e1-7e6e39ca0528',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Dashboard Home',
    'Main dashboard showing earnings, active status toggle, and quick stats',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ea80a241-bda0-45c1-bae1-6738542dbde6',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Profile Settings',
    'Profile management with photo, contact info, preferences, and documents',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '906e3461-f5a2-4ca6-8a3a-abd1ae43dcbc',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Ride Request Notification',
    'Full-screen incoming ride request with rider info and route preview',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '00751ad6-c74b-46cd-a983-ab3be9d33d51',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Ride Acceptance Screen',
    'Ride details with accept/decline buttons, ETA calculation, and earnings estimate',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'aa04e6c6-f2f7-4a3e-85fd-0056f8de7c6a',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Active Ride Navigation',
    'Turn-by-turn navigation with rider contact, trip details, and safety features',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ba368145-0d5d-4cf6-8d5c-244fb164fc68',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Pickup Confirmation Screen',
    'Confirm rider identity with photo, name, and trip code verification',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '0e76678f-d27c-4bfd-9d27-b345281f9c3c',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: In-Progress Ride View',
    'Active trip status with destination, estimated time, and emergency contact',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b6134e7e-65c2-477b-ac88-846be8680f37',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Drop-off Confirmation',
    'Trip completion screen with fare summary and rating prompt',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '081779ab-4790-4ca1-ac1b-0792c1292837',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Earnings Dashboard',
    'Detailed earnings breakdown with daily/weekly/monthly views and charts',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '8bd0c27e-27b4-4d41-83d4-55005baa92a6',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Earnings History',
    'Transaction list with filters, search, and export options',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'a5304725-8f92-4bc5-ae5b-513dc4b7b9ba',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Trip History List',
    'Past rides with details, maps, and earnings for each trip',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '23dff964-75ce-45b1-b63f-c30ea321cb3a',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Trip Detail View',
    'Individual trip information with route map, timeline, and earnings breakdown',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'f136ced0-0d9b-4bba-8fe7-7e097daaf8eb',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Schedule Planner',
    'Calendar view for setting availability and preferred driving hours',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'f7559866-f4c2-41d5-b896-3454cfb4c59d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Heat Map',
    'Real-time map showing high-demand areas and surge pricing zones',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '16bf445a-c0f5-4bf4-abbc-751e38d6b69c',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Messages Inbox',
    'In-app messaging for rider communication and support tickets',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '04383505-880f-4016-b5d2-d268b21085c3',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Notifications Center',
    'All notifications including ride requests, earnings, and system updates',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '94d5d38c-0774-4c33-9ff6-399492b8ea5c',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Support Chat',
    'Live chat interface for driver support with categorized help topics',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd443d4e7-6c41-4459-b971-1bc41c6d3573',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Documents Manager',
    'Upload and manage licenses, insurance, vehicle registration',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd49676c3-427b-4ade-9640-b175d93b0561',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Vehicle Management',
    'Add/edit vehicle details, photos, and switch between multiple vehicles',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd24fec99-3603-4757-bda9-dfb59ffd2c07',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Rating Details',
    'Overall rating with breakdown by categories and recent feedback',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e2da8855-a485-4e5b-89e5-59d4db8f077a',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Referral Program',
    'Referral code sharing, tracking, and reward status',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '7d5012d7-035f-4055-96d1-e167af4b2896',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Safety Center',
    'Emergency contacts, safety tips, and incident reporting',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '0e7273b8-4454-48c0-9d25-bc328a132562',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Offline Mode',
    'Screen shown when driver goes offline with earnings summary',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'c4cd68a4-958d-4c6a-94e7-93d8ec67f165',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Payout Setup',
    'Bank account configuration for earnings withdrawal',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '3f9e6b16-15a0-44b4-8e5a-5b56f38e2671',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Tax Information',
    'Tax forms, earnings reports, and 1099 information',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'dd454cf5-7d74-40b8-a888-03e91ed7dc4e',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Training Modules',
    'Onboarding videos and certification courses',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '761114ab-4ffe-4ed8-bc81-89d070780ea3',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Performance Metrics',
    'Acceptance rate, cancellation rate, and other KPIs',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '4c006b10-4995-4df4-9c1d-d3b86f8d493e',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Incentives Dashboard',
    'Active bonuses, challenges, and rewards tracking',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd0edb8c4-3907-4d5c-a05c-3aac0a6cfcc5',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Navigation Preferences',
    'Settings for preferred navigation app integration',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '7fd19439-34a5-41c1-87bc-9c2ce883e354',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Accessibility Settings',
    'Voice controls, text size, and other accessibility options',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'def44f18-c7ce-44ac-8ee9-472859e4e2d1',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Language Selection',
    'Multi-language support settings',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'dc8eaff1-44b0-4c06-9b0c-cb3f297d2f14',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Privacy Settings',
    'Data sharing, location tracking, and privacy controls',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'c76801dd-52b8-4a42-947b-f9294a39569b',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver App: Driver Beta Features',
    'Opt-in testing for new features and improvements',
    'wireframe',
    'open',
    '{"app": "driver", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2e816265-e30b-477b-aa99-813a4f28b341',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Login Screen',
    'Authentication with email/phone, social login, and quick guest access',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '1b7deaef-c5ea-4730-a9d9-81e298637ac4',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Signup Flow',
    'Simple registration with name, email, phone verification',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '164b30c8-dd1a-4d6f-8245-9085de0f9fc8',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Home Screen',
    'Map-based interface with pickup/destination inputs and ride type selector',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '47ff1b04-8219-4387-bae9-4575c32a33f7',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Location Picker',
    'Interactive map for selecting pickup and drop-off locations with search',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '8295ab8a-4633-45a4-95c1-ec70aa545eaf',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Destination Input',
    'Search bar with autocomplete, recent locations, and saved places',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b7f1a04b-01b9-4539-a1bb-79dcd77c0d56',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Ride Type Selection',
    'Choose between economy, premium, XL, and other ride categories',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '82e39dad-623a-4623-9a90-9f246728aae3',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Price Estimate Screen',
    'Fare breakdown showing base fare, distance, time, and surge pricing',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '90e77a7e-7416-44a8-a30c-490ef127180a',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Confirmation',
    'Final ride details review before booking with payment method',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '35ab53ad-cc44-434f-859b-7c1d82e3df8f',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Finding Driver Animation',
    'Real-time matching screen with estimated wait time',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '271a0857-53c1-4fc9-9f46-2b0ccb64b1d0',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Driver En Route Screen',
    'Live driver tracking with ETA, driver info, and contact options',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '7d52930f-d773-4bbf-8515-5cb99863263c',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Active Ride Tracking',
    'Real-time trip progress with route, ETA, and safety features',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '6a28e81e-fa03-4bd4-b7b9-bcc90228a7c4',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Safety Toolkit',
    'Emergency button, trip sharing, and trusted contacts',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '8a7843fe-169c-4875-aaf1-3ab806c4342d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Trip Completion Screen',
    'Ride summary with fare breakdown and receipt',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '8134f6c4-61a7-4628-a215-4600a77acff7',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Rating Screen',
    'Rate driver and provide feedback with optional tip',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '7d67ac22-d5a3-4595-a4af-423070f8410d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Profile Settings',
    'Account management with photo, contact info, and preferences',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2d8f2fff-1cc7-4b71-b8ea-65265dc5cca7',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Payment Methods',
    'Manage credit cards, PayPal, and other payment options',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'aa7c9493-ccdf-46e3-b330-8009f1e6dfda',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Trip History',
    'Past rides with receipts, maps, and option to rebook',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2c38ed13-0b44-4ff5-97c6-2b8080cfe745',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Favorites Management',
    'Saved locations like home, work, and frequent destinations',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '8f44e837-cfe1-4eab-970a-78cf13839960',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Scheduled Rides',
    'Book rides in advance with calendar integration',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'f58232d1-99b1-4fd0-a19e-3f25bbcacfe3',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Referral Program',
    'Invite friends and track referral credits',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ae2a573f-e512-47b8-9f83-0098c698b332',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Support Center',
    'Help articles, FAQs, and contact support options',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b61f77de-761b-4074-bf72-dfe12287196e',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Messages Inbox',
    'Communication with drivers and support team',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ee5653d4-26d2-4ce0-b739-600656e1e1f3',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Notifications',
    'Ride updates, promotions, and account notifications',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '9a21adb4-3edd-45e3-bc59-e6af3c23f84b',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Promo Codes',
    'Enter and manage promotional codes and discounts',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd9a77a7e-94c5-4857-bf3b-19fbd78990c3',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Accessibility Features',
    'Voice commands, screen reader support, and visual aids',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'f518572c-52aa-481d-a81d-28fbc8b0460c',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Family Profiles',
    'Manage multiple riders under one account',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'aaf41462-c1c5-47a1-a243-8118acaeba94',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Business Account',
    'Corporate account with expense reporting and billing',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '52726100-2919-4328-8aaf-52a20785c0d8',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Split Payment',
    'Share ride cost with other passengers',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2fb4e296-6159-456d-a8a5-4c5bebe66f79',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Lost Items',
    'Report and track lost items left in vehicles',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '69664622-7400-4142-9246-dc7791ce5ccc',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Ride Preferences',
    'Default ride types, quiet mode, and other preferences',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '1c7f5c7c-51c2-4ef4-8f1b-5a123e7ba77b',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Privacy Dashboard',
    'Location history, data sharing, and privacy controls',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '96ee99f3-8e45-472d-9eab-39ee3b365fb1',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Language Settings',
    'Multi-language interface options',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '0627b1df-e795-4e2c-8201-5ee3fe0472e1',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Receipt Details',
    'Detailed fare breakdown with map and trip timeline',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ec93d628-cc9f-4c41-a047-8de4f1d3c0a6',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Safety Report',
    'Incident reporting with photo/video upload',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '37bda5e0-dc80-4870-8d3f-a0d03b4c8c3d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider App: Rider Account Verification',
    'ID verification for enhanced security and features',
    'wireframe',
    'open',
    '{"app": "rider", "category": "screen", "platform": "mobile"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e49d59b6-eca1-4e80-a9a3-cbb46a848cfc',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Login Portal',
    'Secure authentication with 2FA and role-based access',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '866cfae2-42b4-4bf6-ac6f-13ebc6966925',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Main Dashboard',
    'Overview with key metrics, alerts, and quick actions',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '5dd7973d-5510-4c3e-b733-3f59bfc2ff89',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Analytics Dashboard',
    'Business intelligence with charts, graphs, and KPIs',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '4d077155-4017-4113-880e-a91f931133ad',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Driver Management',
    'List, search, and manage all driver accounts',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '6ab6ab9c-e155-4f72-a3c7-5ae6b4e11470',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Driver Details',
    'Individual driver profile with verification status and performance',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '02ce56c1-0ce8-47d7-9431-c8a92971d3bf',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Rider Management',
    'List, search, and manage all rider accounts',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '075499a6-50eb-4a77-a7f4-d6ddb2485e94',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Rider Details',
    'Individual rider profile with trip history and payment info',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ad63f0af-bc87-4220-be01-85b5c97739ad',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Trip Monitoring',
    'Real-time view of all active trips on map',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd25763b5-04af-4e55-81d5-2f21d537f469',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Trip Details',
    'Individual trip information with timeline and GPS tracking',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '4573c10b-13f2-4964-a1a0-184cd2a0f948',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Financial Dashboard',
    'Revenue, payouts, and financial metrics',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'bf55eb04-ba4b-40bd-8038-63ba4f271670',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Payout Management',
    'Process driver payments and view payout history',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b4a902f8-2cd5-40a4-954b-0cb325959e25',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Surge Pricing Control',
    'Configure and monitor dynamic pricing zones',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'aa354d23-eda4-4c3c-83c6-24112d61f42a',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Geofence Manager',
    'Define service areas and restricted zones',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '71caae9a-a101-425c-bb4a-6c5798df3a69',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Promotion Manager',
    'Create and manage promotional campaigns',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '0c21be6d-d86b-4a66-9da3-c306ad5c307e',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Support Ticket System',
    'Handle customer and driver support requests',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd2f1bfe0-f90e-4a97-b0e0-55082dadaf51',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin User Verification',
    'Review and approve driver/rider verification documents',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ed66a4e4-1872-4840-b742-118ef9197779',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Safety Incident Reports',
    'Track and manage safety-related incidents',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2aff29de-13f5-48cd-8884-7e268cdcdbc6',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Fraud Detection',
    'Monitor suspicious activities and patterns',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'c7248105-2f62-4195-8d63-513906cb9bf4',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Rating Disputes',
    'Review and resolve rating-related conflicts',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2f88caee-c21f-4ffe-857e-58b0deced27f',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin System Configuration',
    'Configure platform settings and parameters',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '4c354ad4-dcf7-4f93-858c-2d582a36c6c6',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Role Management',
    'Assign permissions to admin users',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '6bb5dad3-133d-4bd1-bb26-0cf61630f64a',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Notification Center',
    'Send push notifications and announcements',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ea4fa268-3908-4698-aa6c-2231c3bf9e74',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Report Builder',
    'Custom report generation with filters and exports',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '66deef26-8a7d-4bd3-8b49-42790a58d304',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Audit Log',
    'Track all admin actions and system changes',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2e1d0890-3f07-46ad-9b00-054615a891c6',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Vehicle Approval',
    'Review and approve vehicle registration',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'abecd1a0-dc4a-40f7-ba23-deb3b0fa6ee4',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Driver Incentives',
    'Configure bonuses, challenges, and rewards',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '8199a11c-a067-4bc2-be6c-b5f568b25b92',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Heat Map Analytics',
    'Demand patterns and geographic insights',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'eda95ece-ea0b-43dd-a8d0-5e88365b695e',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Performance Metrics',
    'System health, uptime, and performance monitoring',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '4e05fe04-aeec-4ea8-8b93-dcbdf30a47bd',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin API Integration',
    'Manage third-party integrations and webhooks',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '96ce0805-e0a6-4cd0-ad87-30074adfd1c4',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin Portal: Admin Compliance Dashboard',
    'Regulatory compliance tracking and reporting',
    'wireframe',
    'open',
    '{"app": "admin", "category": "screen", "platform": "web"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'wireframe'],
    1,
    NOW(),
    NOW()
);

-- ========================================
-- COMPONENTS (120 items)
-- ========================================
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '4d5191d0-47e8-4133-bf41-794e0decc5e7',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'MapView',
    'Interactive map component with real-time driver/rider positions',
    'component',
    'open',
    '{"category": "map", "complexity": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '5f53ccc8-0393-4254-9685-a293eb37fad2',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'LocationPicker',
    'Autocomplete search with map pin for location selection',
    'component',
    'open',
    '{"category": "map", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ec6e0191-0be0-43b3-825b-e967837115cd',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'RoutePolyline',
    'Animated route visualization on map',
    'component',
    'open',
    '{"category": "map", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '1108407c-5cc9-49d5-9847-5b8e9e05b97f',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'GeoFenceOverlay',
    'Display service area boundaries on map',
    'component',
    'open',
    '{"category": "map", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '37737114-bda5-4d42-90c0-577ec01d84a2',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'HeatMapLayer',
    'Demand density visualization',
    'component',
    'open',
    '{"category": "map", "complexity": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'c6a722ec-2f43-459c-9521-d52938234dd4',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'DriverMarker',
    'Animated driver icon with directional indicator',
    'component',
    'open',
    '{"category": "map", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ff8cbcc8-7a20-4c09-a545-45cea4e9c6c0',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'PickupDropoffMarkers',
    'Origin and destination pins with labels',
    'component',
    'open',
    '{"category": "map", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'c95aafdf-dc61-4140-8dc5-a62e55482c04',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'ETAOverlay',
    'Estimated time overlay on route',
    'component',
    'open',
    '{"category": "map", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'fb18449c-3a9a-4c1d-b3e6-39b5e50225f5',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'TrafficLayer',
    'Real-time traffic conditions',
    'component',
    'open',
    '{"category": "map", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2b33e506-e5a5-4417-b0e8-7333342afefa',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'MapControls',
    'Zoom, center, and map type controls',
    'component',
    'open',
    '{"category": "map", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '4b330918-2bdc-4995-a8ff-18fb206038fd',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'GeocodeSearch',
    'Address to coordinates conversion',
    'component',
    'open',
    '{"category": "map", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'fccc2560-c234-43af-946c-9c404cfd25df',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'ReverseGeocode',
    'Coordinates to address conversion',
    'component',
    'open',
    '{"category": "map", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '8d8e3c59-8d36-4d50-bcb8-cfff66300ec8',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'MapLoadingState',
    'Skeleton loader for map initialization',
    'component',
    'open',
    '{"category": "map", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '60655eac-02ff-4b8a-812a-c0628dae9770',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'CurrentLocationButton',
    'Get user''s current GPS position',
    'component',
    'open',
    '{"category": "map", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '9dd58c28-fac3-48d6-bfaa-1eb02142766a',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'SavedPlacesMap',
    'Display saved locations on map',
    'component',
    'open',
    '{"category": "map", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ba2e1c77-5f7f-453d-a072-430adf3f16da',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'RideRequestCard',
    'Display incoming ride request details',
    'component',
    'open',
    '{"category": "ride", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '9a579a45-6da0-43b4-ac9d-e00fb8a93b60',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'RideStatusBanner',
    'Current ride status indicator',
    'component',
    'open',
    '{"category": "ride", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '382d0d19-5b41-447a-ab51-b005a3603887',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'TripTimeline',
    'Visual timeline of trip stages',
    'component',
    'open',
    '{"category": "ride", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '18adb8b7-d99e-4c01-9c9a-2d13b32047fa',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'FareEstimator',
    'Calculate and display fare estimate',
    'component',
    'open',
    '{"category": "ride", "complexity": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '785f668f-b62c-4293-910f-0710dda833c5',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'RideTypeSelector',
    'Choose between ride categories',
    'component',
    'open',
    '{"category": "ride", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '42685d04-71b8-4c0b-843e-158c60044fe5',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'DriverCard',
    'Driver profile with photo, rating, vehicle',
    'component',
    'open',
    '{"category": "ride", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'c218e1f0-0862-4137-b4f0-7e1aceb87b80',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'RiderCard',
    'Rider profile for driver view',
    'component',
    'open',
    '{"category": "ride", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'a70d204e-77f6-4198-98f3-bd4447754a13',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'TripCodeDisplay',
    '4-digit verification code',
    'component',
    'open',
    '{"category": "ride", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ad0598db-1d6a-4b04-af67-8936ff8a77b5',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'EmergencyButton',
    'SOS button with emergency contacts',
    'component',
    'open',
    '{"category": "ride", "complexity": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2bfd7c87-9d97-440d-b9b6-2f49b99c6930',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'ShareTripButton',
    'Share live trip with contacts',
    'component',
    'open',
    '{"category": "ride", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'f5260b16-dca8-4b3c-b883-9ce03e838cb1',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'CancelRideModal',
    'Cancel ride with reason selection',
    'component',
    'open',
    '{"category": "ride", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b9d9e5cf-19dd-4f13-8715-efb3ce56e7dc',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'RideHistoryCard',
    'Past ride summary card',
    'component',
    'open',
    '{"category": "ride", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '0936414b-d521-4d64-a5a3-2badd51a88d7',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'RideReceiptModal',
    'Detailed fare breakdown',
    'component',
    'open',
    '{"category": "ride", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '4a3d79df-9829-46c6-9e2e-9c51eea61c98',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'ScheduleRideForm',
    'Book ride for future time',
    'component',
    'open',
    '{"category": "ride", "complexity": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '26badce5-d32b-4ea0-8850-89dc18ba9e97',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'MultiStopEditor',
    'Add/remove multiple stops',
    'component',
    'open',
    '{"category": "ride", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '4c2356fd-c79f-4733-a184-9952402d3e9b',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'RideOptionsPanel',
    'Accessibility, preferences, notes',
    'component',
    'open',
    '{"category": "ride", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'f59eaf1c-3d92-44f2-91ce-99680142450d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'WaitTimeIndicator',
    'Estimated driver arrival time',
    'component',
    'open',
    '{"category": "ride", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e5d9a687-f1bf-4972-bcf1-9a78c230afe8',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'DestinationInput',
    'Smart destination search',
    'component',
    'open',
    '{"category": "ride", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '5d3e3280-64a7-4831-91a3-92c1e675035e',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'FavoriteDestinations',
    'Quick access saved places',
    'component',
    'open',
    '{"category": "ride", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'fd266555-a391-4abc-9198-4e7abbf6a4b3',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'RideSummaryCard',
    'Trip completion summary',
    'component',
    'open',
    '{"category": "ride", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd4a36bf3-4066-43dd-97bb-fcb584be72b1',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'PaymentMethodSelector',
    'Choose payment method',
    'component',
    'open',
    '{"category": "payment", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '1d655847-39fa-423b-aa33-1225819c4856',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'AddPaymentMethodForm',
    'Add credit card or PayPal',
    'component',
    'open',
    '{"category": "payment", "complexity": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '8d1947fb-a16b-4f54-a9a8-c0cc20a44025',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'FareBreakdown',
    'Itemized fare calculation',
    'component',
    'open',
    '{"category": "payment", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '8e88f1d9-083b-4f26-b716-5f9ece96f585',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'TipSelector',
    'Custom or preset tip amounts',
    'component',
    'open',
    '{"category": "payment", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '8f94d8ba-7c55-4852-8fda-b2d424c66e74',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'PromoCodeInput',
    'Apply discount code',
    'component',
    'open',
    '{"category": "payment", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '749ca8f1-002c-4190-a062-76c4a32b6456',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'SplitPaymentModal',
    'Divide fare between riders',
    'component',
    'open',
    '{"category": "payment", "complexity": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2b8aee77-3ec0-4829-a952-d4c10098e543',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'PaymentHistoryList',
    'Transaction history',
    'component',
    'open',
    '{"category": "payment", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '95fd1cff-c38f-4bf4-a15e-3ab55c47e762',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'InvoiceGenerator',
    'Generate PDF receipts',
    'component',
    'open',
    '{"category": "payment", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '06d42004-c569-425b-9b1c-60b043644998',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'RefundRequestForm',
    'Submit refund request',
    'component',
    'open',
    '{"category": "payment", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'adcc674e-a821-4b31-8c07-8c6caec9848f',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'PayoutSchedule',
    'Driver earnings payout calendar',
    'component',
    'open',
    '{"category": "payment", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '66d6a674-c3ab-40f5-9fc4-8394f7cb47e1',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'BankAccountForm',
    'Link bank for payouts',
    'component',
    'open',
    '{"category": "payment", "complexity": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '55d6cbf1-3624-48c3-8ff2-a2b01d73e517',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'PaymentSecurityBadge',
    'PCI compliance indicator',
    'component',
    'open',
    '{"category": "payment", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b1a0c308-5e0c-4129-8a30-c713674169a6',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'RatingStars',
    '5-star rating component',
    'component',
    'open',
    '{"category": "rating", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '9c570450-1148-480b-8a73-0b1eef9ccc56',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'RatingDetails',
    'Category-based rating breakdown',
    'component',
    'open',
    '{"category": "rating", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd6773ecb-394a-4ce8-b8f3-ca85c72e6edc',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'FeedbackForm',
    'Text feedback with predefined options',
    'component',
    'open',
    '{"category": "rating", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e77d8ca0-ef3e-48bd-a722-5f5966c18c3f',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'DriverRatingHistory',
    'Historical rating trends',
    'component',
    'open',
    '{"category": "rating", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '70c7fc5d-f5d2-4ea8-8e26-ed2f95d74f08',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'ComplimentBadges',
    'Positive feedback badges',
    'component',
    'open',
    '{"category": "rating", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '4a52d7c7-2cde-46a3-b87f-c913dbbd1668',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'ReportIssueForm',
    'Report problem with categories',
    'component',
    'open',
    '{"category": "rating", "complexity": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2b638b00-cb51-4a7a-9254-40ad94ea290b',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'RatingPrompt',
    'Post-ride rating request',
    'component',
    'open',
    '{"category": "rating", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'df67040a-fb76-42a1-a349-80a7524f7e03',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'AverageRatingDisplay',
    'Overall rating with count',
    'component',
    'open',
    '{"category": "rating", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd96b301a-2e43-4251-8685-33d4f3656cb6',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'RecentReviews',
    'Latest rider/driver feedback',
    'component',
    'open',
    '{"category": "rating", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd808ee59-73ed-4756-9229-de04bbcfae81',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'RatingFilterTabs',
    'Filter reviews by rating',
    'component',
    'open',
    '{"category": "rating", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd82499bc-719b-4e6c-9a58-cd96c5c040ce',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'NavigationBar',
    'Main app navigation',
    'component',
    'open',
    '{"category": "navigation", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '75e037cc-7e63-44bb-9c58-ad1fb1f674a4',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'TabBar',
    'Bottom tab navigation',
    'component',
    'open',
    '{"category": "navigation", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'bf78c0e3-1285-4f73-b969-b2373313f0d0',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'SideMenu',
    'Drawer menu with options',
    'component',
    'open',
    '{"category": "navigation", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e9c2f157-c776-4b52-9240-41f98286ed39',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Breadcrumbs',
    'Navigation breadcrumb trail',
    'component',
    'open',
    '{"category": "navigation", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ad53f32e-2f19-437b-b267-287c0cf6ff0e',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'BackButton',
    'Contextual back navigation',
    'component',
    'open',
    '{"category": "navigation", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'a39c2455-a128-4572-9a97-21bfa9cebf46',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'QuickActions',
    'Floating action buttons',
    'component',
    'open',
    '{"category": "navigation", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'cf7c9c10-2ee8-41fb-b8a5-35fc6c7aeec6',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'SearchBar',
    'Global search component',
    'component',
    'open',
    '{"category": "navigation", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '52e4b245-b8b3-464f-b479-576dac1ff5fe',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'MenuIcon',
    'Hamburger menu toggle',
    'component',
    'open',
    '{"category": "navigation", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'aaf8c536-9192-4306-b644-f799a4a6c4ed',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'ProfileHeader',
    'User profile banner',
    'component',
    'open',
    '{"category": "profile", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '92a0e5ef-b470-4463-9022-25f3a53df6e3',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'ProfilePhotoUpload',
    'Avatar upload with crop',
    'component',
    'open',
    '{"category": "profile", "complexity": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b19099ec-3ccf-4b9b-a0c0-a66fcef77450',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'EditProfileForm',
    'Update user information',
    'component',
    'open',
    '{"category": "profile", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '064d9932-0233-4967-b168-086ea5f1b89f',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'VerificationBadge',
    'ID verified indicator',
    'component',
    'open',
    '{"category": "profile", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '30506752-8fbe-44b8-b395-aec24677d66c',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'DocumentUploader',
    'Upload licenses, insurance',
    'component',
    'open',
    '{"category": "profile", "complexity": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2b2ec5e6-a29b-40c6-855b-99a9dc3d2ded',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'PreferencesPanel',
    'User settings and preferences',
    'component',
    'open',
    '{"category": "profile", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'f03da615-02a4-402c-806d-dd46296a1ff7',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'LanguageSelector',
    'Multi-language dropdown',
    'component',
    'open',
    '{"category": "profile", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ce7b6ef9-50b1-4157-97a7-0d3e7bfc0ab5',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'NotificationSettings',
    'Configure notification preferences',
    'component',
    'open',
    '{"category": "profile", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e979fa85-6bd2-497c-aa63-f9f1c0c50a3d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'PrivacyControls',
    'Data sharing and privacy',
    'component',
    'open',
    '{"category": "profile", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '36ee566e-ca54-49e9-a767-864067387f14',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'AccountDeletionModal',
    'Delete account confirmation',
    'component',
    'open',
    '{"category": "profile", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'a29bee86-d915-4cb6-b985-8808325f08fb',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'EarningsChart',
    'Line chart for daily/weekly earnings',
    'component',
    'open',
    '{"category": "analytics", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b6bc8b2f-c855-406c-b64c-05fbbea7efe4',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'TripStatistics',
    'Pie chart of trip categories',
    'component',
    'open',
    '{"category": "analytics", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '9ab21f91-eb12-4585-8df2-4a0044f47e64',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'PerformanceGauge',
    'Radial gauge for metrics',
    'component',
    'open',
    '{"category": "analytics", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '8d99410e-55a0-495c-b620-2a2641a11ace',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'ActivityHeatmap',
    'Calendar heatmap of activity',
    'component',
    'open',
    '{"category": "analytics", "complexity": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ae287230-3d9e-4dc2-8297-defef3d0cb41',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'RevenueBreakdown',
    'Stacked bar chart',
    'component',
    'open',
    '{"category": "analytics", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'a8c4a229-eabc-4353-bf35-61af5e3f7ad2',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'TrendIndicator',
    'Up/down trend arrows',
    'component',
    'open',
    '{"category": "analytics", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '6a6c50ed-0dcb-4cfb-b83c-7e128c0629ff',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'KPICard',
    'Key performance indicator card',
    'component',
    'open',
    '{"category": "analytics", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2739cddd-cb0b-4d99-ab3a-4eaf8882a05b',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'ComparisonChart',
    'Period-over-period comparison',
    'component',
    'open',
    '{"category": "analytics", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '287ff662-3aa5-49f4-9396-01249a4c86b1',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'GoalProgressBar',
    'Progress toward target',
    'component',
    'open',
    '{"category": "analytics", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '31cd6eb9-f618-4650-9a71-1a09df15c72d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'LiveActivityFeed',
    'Real-time activity stream',
    'component',
    'open',
    '{"category": "analytics", "complexity": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '99197830-a21a-4354-8435-f846ee58731d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'ChatBubble',
    'Individual message bubble',
    'component',
    'open',
    '{"category": "messaging", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '5b3aadaa-e416-48c6-ab02-1b3d415342fd',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'ChatThread',
    'Conversation thread view',
    'component',
    'open',
    '{"category": "messaging", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '5fdef43a-4139-4820-9594-3fa684a18ba4',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'MessageInput',
    'Text input with send button',
    'component',
    'open',
    '{"category": "messaging", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '4bca2beb-4425-4bf7-8b02-9c0804cb9e74',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'QuickReplies',
    'Predefined message buttons',
    'component',
    'open',
    '{"category": "messaging", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2c00fec9-6503-4edb-b3ed-81b81d816022',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'NotificationCard',
    'In-app notification item',
    'component',
    'open',
    '{"category": "messaging", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2c90752b-44ad-474e-bec2-9c72e2860b05',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'NotificationBadge',
    'Unread count indicator',
    'component',
    'open',
    '{"category": "messaging", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'f2b8b258-10e2-450d-b775-41c78fd46bc6',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'PushNotificationPreview',
    'Preview notification appearance',
    'component',
    'open',
    '{"category": "messaging", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'a223f63b-9d81-43f7-887a-6a66611cb2ff',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'InboxList',
    'Message threads list',
    'component',
    'open',
    '{"category": "messaging", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '72a62218-aa43-4040-b537-536ceb6a061d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'VoiceCallButton',
    'Initiate phone call',
    'component',
    'open',
    '{"category": "messaging", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b4f73fed-702f-48b5-9854-6be1159f7733',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'TypingIndicator',
    'Show when other user is typing',
    'component',
    'open',
    '{"category": "messaging", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '9df582f3-65f6-4e23-b698-3b679890d9f2',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'LoadingSpinner',
    'Activity indicator',
    'component',
    'open',
    '{"category": "ui", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '5eb569f5-575c-4680-9fa9-1a77a9355cbb',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'SkeletonLoader',
    'Content placeholder',
    'component',
    'open',
    '{"category": "ui", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'c82cb694-d4a8-4240-9f16-5cf8c9629243',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'ErrorAlert',
    'Error message display',
    'component',
    'open',
    '{"category": "ui", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'a3db4dc5-55d2-4325-8b8f-978874ea9071',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'SuccessToast',
    'Success notification',
    'component',
    'open',
    '{"category": "ui", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ff599278-94da-45c7-869a-1e7545ccd08f',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'ConfirmationModal',
    'Action confirmation dialog',
    'component',
    'open',
    '{"category": "ui", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b9d289ed-4cb1-4c23-a9a4-d0cfe676581d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'PullToRefresh',
    'Swipe to refresh content',
    'component',
    'open',
    '{"category": "ui", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'f7c64037-b083-49df-a841-cdd8905df966',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'InfiniteScroll',
    'Load more on scroll',
    'component',
    'open',
    '{"category": "ui", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '1a549e10-236f-4437-8934-e0784dd03913',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Accordion',
    'Expandable content sections',
    'component',
    'open',
    '{"category": "ui", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2145fb90-e9ee-4381-a1aa-4084db737d0d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Toggle',
    'On/off switch',
    'component',
    'open',
    '{"category": "ui", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '75d5b5ee-380e-4dc3-be56-eec7179c7f77',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Slider',
    'Range selector',
    'component',
    'open',
    '{"category": "ui", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ea68b6c8-e9a0-428b-8354-d6c095d1d268',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'DateTimePicker',
    'Date and time selection',
    'component',
    'open',
    '{"category": "ui", "complexity": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '408202fc-634f-4c5f-9730-ae12e730a039',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Checkbox',
    'Single checkbox component',
    'component',
    'open',
    '{"category": "ui", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '42167955-b5ec-4505-adfc-1c5f70fce1ef',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'RadioGroup',
    'Radio button group',
    'component',
    'open',
    '{"category": "ui", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ac133424-d6ed-4c52-923b-ce0cddf57a1f',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Dropdown',
    'Select dropdown menu',
    'component',
    'open',
    '{"category": "ui", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd837e8a5-e314-4766-a078-f14293e76c5a',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'ProgressIndicator',
    'Step-by-step progress',
    'component',
    'open',
    '{"category": "ui", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '66fe71b7-ea75-41ac-9e00-f41e47d7366a',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'SafetyShieldIcon',
    'Security indicator',
    'component',
    'open',
    '{"category": "safety", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '4cfa3c3b-99e6-44b6-8755-9759490de45c',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'TrustedContactsList',
    'Emergency contact management',
    'component',
    'open',
    '{"category": "safety", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '5d0ed354-96e6-4e40-8e25-22510f868fba',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'TripSharingPanel',
    'Share trip with contacts',
    'component',
    'open',
    '{"category": "safety", "complexity": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'fb9dbd74-9d59-407a-aa0a-bc69b8dd6da7',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'IncidentReportForm',
    'Report safety incident',
    'component',
    'open',
    '{"category": "safety", "complexity": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '9e246b3b-b0c7-4eea-a3a3-591a0abfe19f',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'TwoFactorAuth',
    '2FA setup and verification',
    'component',
    'open',
    '{"category": "safety", "complexity": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'f2177ca8-51ea-4d9d-8161-173bafa504f7',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'SecuritySettings',
    'Account security options',
    'component',
    'open',
    '{"category": "safety", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'f710dda8-22df-4dbc-a5e4-c912cc7f1057',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'IDVerificationFlow',
    'Identity verification steps',
    'component',
    'open',
    '{"category": "safety", "complexity": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '3286d8e4-934e-498b-82eb-222c11458f38',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'SafetyTipsCard',
    'Safety guidelines display',
    'component',
    'open',
    '{"category": "safety", "complexity": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '0f70fbcb-9993-4510-a06a-3d86b647aadc',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'EmergencyContactsForm',
    'Manage emergency contacts',
    'component',
    'open',
    '{"category": "safety", "complexity": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '7cec6ef6-ecad-41f7-8bbc-f6f7e6f3c417',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'LiveLocationSharing',
    'Real-time location sharing',
    'component',
    'open',
    '{"category": "safety", "complexity": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'component'],
    1,
    NOW(),
    NOW()
);

-- ========================================
-- USER FLOWS (80 items)
-- ========================================
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '5c45302b-aade-41b0-af1d-861711b6a6a3',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: First-time Signup and Onboarding',
    'New user downloads app → Signs up → Verifies phone → Adds payment → Takes tutorial → Books first ride',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "high", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '6a8ebaa0-2477-49e3-955b-dae3f9e8cb6a',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Request Immediate Ride',
    'Opens app → Sets pickup location → Sets destination → Reviews fare → Selects ride type → Confirms booking → Waits for match',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "medium", "steps": 7}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'c1a0317c-eb40-4fb9-b34e-d29550f44181',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Schedule Future Ride',
    'Opens app → Selects schedule option → Sets date/time → Sets locations → Reviews fare → Confirms booking → Receives confirmation',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "medium", "steps": 7}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '966696de-e8d7-43e3-baea-a86bd1373287',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Track Active Ride',
    'Receives driver match → Views driver info → Tracks driver arrival → Confirms pickup → Tracks trip progress → Arrives at destination',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'a34c0056-e330-497e-a4c4-230e37f3a0d6',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Cancel Ride Before Pickup',
    'Views active booking → Clicks cancel → Selects reason → Reviews cancellation fee → Confirms cancellation → Receives confirmation',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'cc23c9d3-3058-482a-8c51-1d2b4105adc7',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Complete Payment After Ride',
    'Trip ends → Reviews fare → Adds tip → Confirms payment → Receives receipt → Returns to home',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '497b5303-4f45-4e69-807b-c1d22f034cb5',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Rate Driver and Provide Feedback',
    'Trip completes → Sees rating prompt → Selects star rating → Adds comments → Selects badges → Submits feedback',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '9b54357a-5fdd-4c3d-8a4b-208f3a104047',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Add Payment Method',
    'Opens settings → Selects payments → Clicks add method → Enters card details → Verifies card → Sets as default',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2fcaf586-85b1-474b-9193-76dd1526a3d3',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Apply Promo Code',
    'Views ride estimate → Clicks promo field → Enters code → Validates code → Sees discount → Confirms booking',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '397e5f47-a638-4116-a2ca-541102de458f',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Save Favorite Location',
    'Enters destination → Sees save option → Names location → Selects icon → Saves location → Appears in favorites',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '4e6c6d5e-2eda-491d-bbd9-66997cce3822',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Contact Driver During Trip',
    'Views active trip → Opens driver contact → Chooses call/message → Communicates → Closes contact → Returns to trip view',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '1f07dc8f-4d3b-4bfe-83d5-6db375a6f4bb',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Share Trip with Contacts',
    'Active trip → Opens safety menu → Selects share trip → Chooses contacts → Sends share → Contact receives link',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '08f3d480-7f91-40c1-962a-b1c1a3f7bbf1',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Report Lost Item',
    'Opens trip history → Selects trip → Clicks lost item → Describes item → Submits report → Receives ticket',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'bec1847b-1230-41a9-b2bd-be76746fa17b',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Request Refund',
    'Opens trip history → Selects trip → Clicks issue → Selects refund → Explains reason → Submits request',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'f58ae199-8dca-4d3b-8ef6-dc64a3b6277f',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Update Profile Information',
    'Opens settings → Selects profile → Edits fields → Uploads photo → Saves changes → Sees confirmation',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '6d4337f6-d530-40bd-8cd3-56dc828fbd98',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Enable Push Notifications',
    'Opens settings → Selects notifications → Toggles categories → Grants permissions → Tests notification → Saves preferences',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd8076926-eb86-4e0d-88fa-e19c50b47f3f',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Invite Friend with Referral',
    'Opens referral screen → Copies code → Shares via app → Friend signs up → Friend takes ride → Both receive credit',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'f82fcc5d-129a-46a3-8e06-b984f779feae',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Split Fare with Friend',
    'During booking → Enables split → Enters friend''s contact → Friend accepts → Both charged → Trip proceeds',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "high", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'c98c1ef7-f49e-495c-b518-da619c65ec38',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Add Multiple Stops',
    'Sets pickup → Clicks add stop → Enters stop 1 → Adds stop 2 → Sets final destination → Reviews total fare',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '02ba3558-8bca-475b-a351-adf1c2e75567',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Change Destination Mid-Trip',
    'Active trip → Requests change → Enters new destination → Driver accepts → Fare updates → Trip continues',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '178f1b79-3e9f-4143-8dce-1b6453d8718d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Enable Accessibility Features',
    'Opens settings → Selects accessibility → Enables voice commands → Adjusts text size → Enables screen reader → Tests features',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'f44b3580-61d8-4300-95ce-4fe766f50f90',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: View Trip History and Receipts',
    'Opens menu → Selects history → Filters trips → Selects trip → Views receipt → Downloads PDF',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '71dac908-2054-4412-89c9-e919e255c864',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Contact Customer Support',
    'Opens help → Searches issue → No match found → Clicks contact → Describes problem → Receives ticket',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '9c04ca0f-914f-4683-aea5-be3a02e9f8d9',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Report Safety Incident',
    'During/after trip → Opens safety → Reports incident → Provides details → Uploads evidence → Emergency contacted',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "high", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'a36bef42-da2f-42b6-8056-1931997a06dd',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Switch Languages',
    'Opens settings → Selects language → Chooses from list → Confirms change → App reloads → New language applied',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '63ac1006-6a99-4d1a-aff5-c9318ea0f153',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Verify Identity for Premium Features',
    'Prompted for verification → Uploads ID → Takes selfie → AI validates → Manual review → Account verified',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "high", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '1d9f5ba1-d465-40d1-9ad1-f1fb96e2ea10',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Enable Quiet Mode',
    'During booking → Enables quiet mode → Driver notified → Trip proceeds quietly → Trip completes → Normal mode restored',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd77e904b-fb37-4c95-878b-e6192100c00c',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Book Ride for Someone Else',
    'Opens app → Selects ride for others → Enters their details → Sets pickup → Books ride → Other rider notified',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '49f9c2ef-50f9-46d7-a954-dc319d38185b',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Set Default Ride Preferences',
    'Opens settings → Selects preferences → Sets default ride type → Sets music preference → Sets AC preference → Saves defaults',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e5355385-f897-4f62-be42-fe87d8c12f4e',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rider: Logout and Delete Account',
    'Opens settings → Selects account → Requests deletion → Confirms action → Provides feedback → Account deleted',
    'user_flow',
    'open',
    '{"user_type": "rider", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'cf4f5bd5-76a0-4623-bce3-9ac74eaa29c2',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Complete Onboarding',
    'Downloads app → Signs up → Uploads documents → Vehicle inspection → Background check → Training modules → Account activated',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "high", "steps": 7}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'cc3a4f12-59d1-45fa-a595-5e2f4d51248c',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Go Online and Accept First Ride',
    'Opens app → Toggles online → Receives request → Reviews details → Accepts ride → Navigates to pickup',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd967a4d8-fcae-41b9-93c0-38207093ffd2',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Navigate to Pickup Location',
    'Accepts ride → Gets directions → Follows navigation → Contacts rider → Arrives at pickup → Confirms arrival',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '67d97a78-3036-488e-8663-d77736c3ff83',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Verify and Pickup Rider',
    'Arrives at pickup → Confirms trip code → Verifies rider identity → Starts trip → Begins navigation → Trip active',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'a059ef8c-a5dd-4aa1-821c-7b49720b9c0c',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Complete Trip and Get Paid',
    'Arrives at destination → Ends trip → Fare calculated → Rider pays → Earnings credited → Ready for next ride',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '3b5f59e4-8e01-4349-a4b3-847fec8cc719',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Rate Rider',
    'Trip completes → Rating prompt → Selects stars → Adds comment → Submits rating → Returns to availability',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'de488d0b-86f1-47de-ab79-6a73d784260c',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Decline Ride Request',
    'Receives request → Reviews details → Decides to decline → Selects reason → Confirms decline → Remains online',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '982d3870-0752-425e-9208-3157022f468a',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Cancel Accepted Ride',
    'Has active booking → Clicks cancel → Selects reason → Reviews penalty → Confirms cancellation → Returns to available',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '6dfbdc07-efe7-4609-ac57-77e3fa1defd4',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: View Daily Earnings',
    'Opens earnings → Selects today → Views breakdown → Checks trips → Reviews deductions → Exports summary',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '58c2e09a-d612-4b42-8306-2ac112d46730',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Cash Out Earnings',
    'Opens earnings → Selects payout → Enters amount → Confirms bank → Initiates transfer → Receives confirmation',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '7189ca44-5bef-42ce-b4fd-c09c8bc98e19',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Set Availability Schedule',
    'Opens schedule → Selects days → Sets time blocks → Sets recurring → Saves schedule → Receives reminders',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2fc6dfd0-610a-4c93-9c9e-933303db1633',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: View Heat Map for High Demand',
    'Opens map → Enables heat layer → Identifies hotspots → Drives to area → Goes online → Receives requests',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '4b327f70-380b-4bc8-9cab-6ee9df775b7a',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Upload New Vehicle Documents',
    'Opens documents → Selects vehicle → Clicks update → Takes photos → Uploads files → Awaits approval',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '3d63db10-a466-402e-bb47-7b22bca47d71',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Switch Between Vehicles',
    'Opens settings → Selects vehicles → Chooses vehicle → Confirms switch → Vehicle updated → Ready to drive',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'adbc9cb1-c6a7-44b2-af33-d3342c233892',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Contact Rider Before Pickup',
    'Has active booking → Opens rider contact → Calls or texts → Coordinates meeting → Confirms location → Navigates',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e030952b-3a1b-4008-93e8-5e5c1ea5d6a0',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Report Rider Issue',
    'During/after trip → Opens report → Selects issue type → Provides details → Submits report → Support notified',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '6f356a7e-dfff-4365-9be4-53d1dd798c7c',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: View Performance Metrics',
    'Opens performance → Views acceptance rate → Checks cancellations → Reviews ratings → Sees streaks → Sets goals',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '5328f2d0-600b-4b67-a35f-fd93655413a0',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Participate in Incentive Program',
    'Views incentives → Selects challenge → Accepts terms → Tracks progress → Completes challenge → Receives bonus',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '76c0b150-ce9d-4580-ab95-9be62d1e7ac0',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Refer New Driver',
    'Opens referral → Shares code → Friend signs up → Friend completes rides → Bonus unlocked → Both earn reward',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '96e68bf4-703f-4365-a50f-2628acf90920',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Take Training Course',
    'Opens training → Selects course → Watches videos → Takes quiz → Passes test → Earns certificate',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '8856804d-f0a2-4a57-99c1-2efca5966898',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Update Bank Account',
    'Opens payouts → Selects bank → Enters routing → Enters account → Verifies details → Saves changes',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'f9528522-cbb3-4775-a783-d665657b8f8d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Download Tax Documents',
    'Opens documents → Selects tax year → Generates 1099 → Reviews summary → Downloads PDF → Files taxes',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '491ab602-7b56-4346-8ebf-d946e7c140df',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Enable Navigation App Integration',
    'Opens settings → Selects navigation → Chooses app → Grants permissions → Tests integration → Sets default',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'aba1de58-2da1-4cda-9729-8fd6076fc2bf',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Go Offline and View Summary',
    'Completes last trip → Toggles offline → Views session summary → Checks earnings → Reviews stats → Closes app',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'abcfa497-7a3e-4f42-bf79-09d4db42626e',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Contact Support for Issue',
    'Encounters problem → Opens support → Searches FAQ → No solution → Starts chat → Issue resolved',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'fbcbe8f6-ed90-465d-9397-51978e1b27dd',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Report Safety Concern',
    'Safety issue → Opens safety center → Reports incident → Provides evidence → Submits report → Support responds',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "high", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '7010d251-394f-447c-ae3e-b176a716d050',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Update Profile Photo',
    'Opens profile → Selects photo → Takes/uploads image → Crops image → Submits for review → Photo approved',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '040bc181-6f09-4f37-bbf2-ae6e274fea96',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Check Rating Breakdown',
    'Opens ratings → Views overall → Sees category breakdown → Reads comments → Identifies improvements → Sets action plan',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '6a4438ed-6a5a-48e5-99ec-6e2887dc0625',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Opt into Beta Features',
    'Opens settings → Selects beta → Reviews features → Accepts terms → Features enabled → Provides feedback',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'a2304875-442e-4818-b229-e8016f1d0c28',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Driver: Deactivate Account',
    'Opens settings → Selects account → Requests deactivation → Confirms decision → Provides reason → Account deactivated',
    'user_flow',
    'open',
    '{"user_type": "driver", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '9d7d1e68-234d-48c5-bd25-d36bd32e2a93',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin: Review and Approve Driver Application',
    'Views pending → Opens application → Reviews documents → Runs background check → Makes decision → Notifies applicant',
    'user_flow',
    'open',
    '{"user_type": "admin", "complexity": "high", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '27da0dcf-a37e-45d9-bb19-8b9f79bbba9e',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin: Investigate Fraud Alert',
    'Receives alert → Opens case → Reviews transactions → Checks patterns → Takes action → Closes case',
    'user_flow',
    'open',
    '{"user_type": "admin", "complexity": "high", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ec37fe2d-87d0-4b26-bab4-89f22e160035',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin: Resolve Customer Support Ticket',
    'Views queue → Opens ticket → Reads issue → Takes corrective action → Responds to user → Closes ticket',
    'user_flow',
    'open',
    '{"user_type": "admin", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '4d529f9f-9cd8-4852-ad52-553e59970bd5',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin: Configure Surge Pricing Zone',
    'Opens pricing → Creates zone → Sets boundaries → Defines multiplier → Sets triggers → Activates surge',
    'user_flow',
    'open',
    '{"user_type": "admin", "complexity": "high", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '51495f5e-a005-4f0a-a8d1-793b9bbcf427',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin: Generate Financial Report',
    'Opens reports → Selects parameters → Chooses date range → Runs report → Reviews data → Exports to Excel',
    'user_flow',
    'open',
    '{"user_type": "admin", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '1f2a5363-0728-4a45-8ec7-3d9fbaf32c86',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin: Process Driver Payout',
    'Views pending → Reviews amounts → Verifies bank details → Initiates transfer → Updates status → Notifies drivers',
    'user_flow',
    'open',
    '{"user_type": "admin", "complexity": "high", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '50dc66e7-4eaa-4178-87b9-97753d5b5eb6',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin: Create Promotional Campaign',
    'Opens promotions → Creates campaign → Sets criteria → Defines discount → Sets duration → Launches promo',
    'user_flow',
    'open',
    '{"user_type": "admin", "complexity": "high", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e792577f-ac98-4eba-af09-6c768fc3ca4e',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin: Monitor Active Trips',
    'Opens monitoring → Views map → Checks trip statuses → Identifies issues → Intervenes if needed → Logs activity',
    'user_flow',
    'open',
    '{"user_type": "admin", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '5c1b4912-d479-442d-a731-818878959441',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin: Suspend Driver Account',
    'Reviews violation → Opens driver profile → Logs reason → Suspends account → Notifies driver → Updates records',
    'user_flow',
    'open',
    '{"user_type": "admin", "complexity": "high", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '63e16da6-095f-4e63-84f3-2fa934fb413e',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin: Approve Vehicle Registration',
    'Views pending vehicles → Opens submission → Verifies photos → Checks insurance → Makes decision → Notifies driver',
    'user_flow',
    'open',
    '{"user_type": "admin", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'acba8618-063e-4cf6-ade0-76a8197e200b',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin: Handle Safety Incident',
    'Receives incident → Opens case → Contacts parties → Gathers evidence → Takes action → Closes investigation',
    'user_flow',
    'open',
    '{"user_type": "admin", "complexity": "high", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2a7d6323-2b32-4288-b874-c2dfa8fdc9d6',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin: Update Platform Pricing',
    'Opens config → Sets base fare → Defines per-mile rate → Sets per-minute rate → Reviews impact → Deploys changes',
    'user_flow',
    'open',
    '{"user_type": "admin", "complexity": "high", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '3c0d7b63-fb95-48e4-b2ca-f37a2ea46e11',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin: Review Rating Dispute',
    'Opens dispute → Reviews rating → Checks trip details → Contacts parties → Makes ruling → Updates rating',
    'user_flow',
    'open',
    '{"user_type": "admin", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'a669a427-366c-4ee3-9926-38eaed2e1ad8',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin: Configure Service Area',
    'Opens geofences → Creates polygon → Sets boundaries → Defines restrictions → Tests area → Activates zone',
    'user_flow',
    'open',
    '{"user_type": "admin", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '8078a415-39fb-458d-a223-20cd436e7239',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin: Send Push Notification',
    'Opens notifications → Composes message → Selects audience → Sets timing → Previews → Sends notification',
    'user_flow',
    'open',
    '{"user_type": "admin", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '505d2a63-ab83-4a30-a08d-2bbb0cea33f4',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin: Analyze Demand Patterns',
    'Opens analytics → Selects metrics → Chooses timeframe → Generates charts → Identifies trends → Exports insights',
    'user_flow',
    'open',
    '{"user_type": "admin", "complexity": "medium", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '73970603-9e9b-45ec-aa3f-1208b4b3a16c',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin: Manage Admin User Permissions',
    'Opens users → Selects admin → Views permissions → Updates roles → Saves changes → Notifies admin',
    'user_flow',
    'open',
    '{"user_type": "admin", "complexity": "high", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd837a4fc-88a3-4312-b6de-c5c05595483b',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin: Review Audit Logs',
    'Opens audit → Filters by date → Searches actions → Reviews changes → Identifies issues → Takes corrective action',
    'user_flow',
    'open',
    '{"user_type": "admin", "complexity": "low", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b9fedff1-e2d3-475e-965e-68e387f20052',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin: Configure Third-Party Integration',
    'Opens integrations → Selects service → Enters API keys → Tests connection → Configures settings → Activates integration',
    'user_flow',
    'open',
    '{"user_type": "admin", "complexity": "high", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'dabccf46-1e8e-4f59-9dd0-eba5239ea727',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Admin: Generate Compliance Report',
    'Opens compliance → Selects regulations → Chooses period → Runs audit → Reviews violations → Exports report',
    'user_flow',
    'open',
    '{"user_type": "admin", "complexity": "high", "steps": 6}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'user_flow'],
    1,
    NOW(),
    NOW()
);

-- ========================================
-- INTERACTIONS (90 items)
-- ========================================
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '316d546a-f0bd-49d0-96c3-39f1e7467df5',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Tap to Select Location on Map',
    'Single tap on map to set pickup/dropoff location',
    'interaction',
    'open',
    '{"gesture": "tap", "component": "map"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b3ac353e-9d7a-46bb-9e1f-29fa8fdc653d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Long Press to Pin Location',
    'Press and hold map to drop pin at precise location',
    'interaction',
    'open',
    '{"gesture": "long_press", "component": "map"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '05775fd5-e3ff-46c2-90ad-a39548ef5350',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Pinch to Zoom Map',
    'Pinch gesture to zoom in/out on map view',
    'interaction',
    'open',
    '{"gesture": "pinch", "component": "map"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'f3fc20e0-337c-4f34-a18a-70f4d6396f99',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Swipe to Dismiss Modal',
    'Swipe down to close bottom sheet or modal',
    'interaction',
    'open',
    '{"gesture": "swipe", "component": "modal"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd31478bd-411e-47e7-86ed-758bae0f6c8e',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Swipe Card to Delete Payment Method',
    'Swipe left on card to reveal delete action',
    'interaction',
    'open',
    '{"gesture": "swipe", "component": "list"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'efcf3ba9-0995-41d6-b883-eb71e1b17492',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Pull Down to Refresh Trip History',
    'Pull-to-refresh gesture to update trip list',
    'interaction',
    'open',
    '{"gesture": "pull", "component": "list"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '666ab18a-ec88-4149-8bb1-da419c383efb',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Drag to Reorder Favorite Locations',
    'Long press and drag to reorder saved places',
    'interaction',
    'open',
    '{"gesture": "drag", "component": "list"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '695fb40e-8cb9-47ca-9e39-602fae16d8bd',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Double Tap to Zoom on Driver Photo',
    'Double tap driver photo to view full size',
    'interaction',
    'open',
    '{"gesture": "double_tap", "component": "image"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '30c64df5-87d5-4c3f-8575-8df0d19d2d0f',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Swipe Up for Ride Options',
    'Swipe up bottom sheet to see all ride types',
    'interaction',
    'open',
    '{"gesture": "swipe", "component": "sheet"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '4bf1e925-6c62-4224-b403-459891137f64',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Tap Outside to Close Dropdown',
    'Tap anywhere outside to dismiss dropdown menu',
    'interaction',
    'open',
    '{"gesture": "tap", "component": "dropdown"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '1acf6a15-e152-49f6-b332-1e18d0efc075',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Slide to Accept Ride Request',
    'Slide button from left to right to accept',
    'interaction',
    'open',
    '{"gesture": "slide", "component": "button"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e683efe1-cac8-4606-99ae-4f8948484990',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Shake Device to Report Problem',
    'Shake phone to quickly access report form',
    'interaction',
    'open',
    '{"gesture": "shake", "component": "global"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '07a1cdf0-f221-43cb-ac61-0dc9083f73fd',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rotate Device for Landscape Map',
    'Auto-rotate to landscape for fuller map view',
    'interaction',
    'open',
    '{"gesture": "rotate", "component": "map"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e72226be-be59-4085-86d5-6749d10c4255',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Swipe Between Tabs',
    'Swipe left/right to navigate between tab views',
    'interaction',
    'open',
    '{"gesture": "swipe", "component": "tabs"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'c32545cd-7a57-4b3f-b9b6-92c574e211b0',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Tap and Hold for Quick Actions',
    'Long press on trip card for quick menu',
    'interaction',
    'open',
    '{"gesture": "long_press", "component": "card"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e4e65488-478f-4ae3-b706-0554382d89b4',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Flick to Scroll Quickly',
    'Fast swipe to scroll rapidly through list',
    'interaction',
    'open',
    '{"gesture": "flick", "component": "list"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '20b27ba1-479d-44cc-8b26-f6e2e5fdc216',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Tap Status Bar to Scroll to Top',
    'Tap status bar to quickly scroll to top',
    'interaction',
    'open',
    '{"gesture": "tap", "component": "scroll"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '1f1e462e-3d79-4d6d-88ba-4c0d2d5c0048',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Two-Finger Rotate Map',
    'Two-finger rotation gesture to rotate map bearing',
    'interaction',
    'open',
    '{"gesture": "rotate", "component": "map"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '3a9c2f28-5c99-460f-a4f9-be2c8f6a431d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Edge Swipe for Side Menu',
    'Swipe from left edge to open navigation drawer',
    'interaction',
    'open',
    '{"gesture": "edge_swipe", "component": "menu"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'afddfa97-c990-4944-a045-10ac2eb3f072',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    '3D Touch for Quick Preview',
    'Force touch on trip for quick preview',
    'interaction',
    'open',
    '{"gesture": "force_touch", "component": "list"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '8176d9bb-083a-471f-849d-0d42a358540a',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Click to Toggle Driver Online Status',
    'Tap switch to go online/offline',
    'interaction',
    'open',
    '{"type": "toggle", "component": "switch"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '827fdedf-1122-4e2b-9f08-bd661f565108',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Click to Confirm Ride Booking',
    'Tap ''Confirm'' button to book ride',
    'interaction',
    'open',
    '{"type": "submit", "component": "button"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '5726d1b6-16c9-4d18-9040-dbc0464f555c',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Click to Open Navigation App',
    'Tap ''Navigate'' to launch external navigation',
    'interaction',
    'open',
    '{"type": "action", "component": "button"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '0072a84a-8c47-44ff-8db0-ff62b8de6b24',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Click to Call Driver/Rider',
    'Tap phone icon to initiate call',
    'interaction',
    'open',
    '{"type": "action", "component": "icon"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'f1eb4677-a6ea-4289-a6a6-29231db23b22',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Click to Send Message',
    'Tap message icon to open chat',
    'interaction',
    'open',
    '{"type": "action", "component": "icon"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '784c0184-4107-4431-9562-4b0dba9bc587',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Click to Expand Trip Details',
    'Tap chevron to expand/collapse details',
    'interaction',
    'open',
    '{"type": "expand", "component": "accordion"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '08f72380-84d5-4fc9-a114-c9f62e613fa0',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Click to Share Trip',
    'Tap share icon to send trip link',
    'interaction',
    'open',
    '{"type": "action", "component": "icon"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e879d79d-1d89-420b-b4f1-8192aa94ee9d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Click Emergency Button',
    'Tap SOS button to trigger emergency protocol',
    'interaction',
    'open',
    '{"type": "critical", "component": "button"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '67af6bf6-9d6b-4a26-a9da-e5bcbfa151ce',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Click to Apply Filter',
    'Tap filter chip to activate filter',
    'interaction',
    'open',
    '{"type": "toggle", "component": "chip"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '1644895f-d07d-4cab-a319-3d5ddbd9afda',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Click to Sort List',
    'Tap column header to sort by that field',
    'interaction',
    'open',
    '{"type": "sort", "component": "table"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '8800274c-ee98-48db-8644-c6ebdc4eaf4f',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Click to Download Receipt',
    'Tap PDF icon to download receipt',
    'interaction',
    'open',
    '{"type": "download", "component": "icon"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'f50e7056-bf75-4e55-82bb-ed8cad00aa53',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Click to Copy Referral Code',
    'Tap code to copy to clipboard',
    'interaction',
    'open',
    '{"type": "copy", "component": "text"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '13b5bed7-d388-45c5-90af-759e92a1eb49',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Click to Upload Document',
    'Tap upload area to select file',
    'interaction',
    'open',
    '{"type": "upload", "component": "dropzone"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '5cd6d83d-ac58-4599-915e-fb7843e527e3',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Click to Play Training Video',
    'Tap play button on video thumbnail',
    'interaction',
    'open',
    '{"type": "media", "component": "video"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'f1bf59a9-1bf9-4c01-a631-9e0f222fa219',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Click to Expand Notification',
    'Tap notification banner to see full message',
    'interaction',
    'open',
    '{"type": "expand", "component": "banner"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '30b16e2f-24bd-4383-9dd6-78b0ab361e54',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Type in Location Search',
    'Enter address in search field with autocomplete',
    'interaction',
    'open',
    '{"type": "text_input", "component": "search"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '1b7c695e-3174-401c-b3cb-a7461009ef69',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Select from Dropdown Menu',
    'Click dropdown to select payment method',
    'interaction',
    'open',
    '{"type": "select", "component": "dropdown"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2dfaba04-9dc7-49f1-acdf-f4b078c39e0f',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Adjust Slider for Tip Amount',
    'Drag slider to set custom tip percentage',
    'interaction',
    'open',
    '{"type": "slide", "component": "slider"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '88154660-61d5-4d6b-b9cb-03c97becc5be',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Select Date and Time',
    'Open date picker to schedule future ride',
    'interaction',
    'open',
    '{"type": "date_select", "component": "picker"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '9449fcae-f419-4dff-b06f-7ede512c08d0',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Toggle Checkbox for Terms',
    'Check box to accept terms and conditions',
    'interaction',
    'open',
    '{"type": "checkbox", "component": "checkbox"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '91e29dd4-0c7f-40b6-990c-3fd4a37307c0',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Select Radio Button for Ride Type',
    'Choose one option from ride type list',
    'interaction',
    'open',
    '{"type": "radio", "component": "radio"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b3ec29e9-cf8d-444b-bf8f-49826442fae1',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Upload Photo for Profile',
    'Click avatar to upload profile picture',
    'interaction',
    'open',
    '{"type": "upload", "component": "image"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e4fb46cb-3183-46a2-bb23-d8bb15c349ca',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Enter Credit Card Details',
    'Type card number with auto-formatting',
    'interaction',
    'open',
    '{"type": "text_input", "component": "form"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '1090533b-d38f-4d4d-b87c-b412c42964b9',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Select Star Rating',
    'Tap stars to select 1-5 rating',
    'interaction',
    'open',
    '{"type": "rating", "component": "stars"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '0b123f8e-7687-4286-9427-6ee95d5d6754',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Type Message in Chat',
    'Enter text in chat input field',
    'interaction',
    'open',
    '{"type": "text_input", "component": "chat"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '9bfe0587-0593-4d62-a401-1bdea58857f0',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Select Multi-Stop Destinations',
    'Add multiple addresses for route',
    'interaction',
    'open',
    '{"type": "multi_select", "component": "list"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'cff46609-2abd-47ce-8aec-87232834c92e',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Adjust Volume Slider',
    'Drag slider for navigation volume',
    'interaction',
    'open',
    '{"type": "slide", "component": "slider"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ae532d8d-1d75-4a88-91a3-1b78c563532d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Toggle Switch for Notifications',
    'Enable/disable notification categories',
    'interaction',
    'open',
    '{"type": "toggle", "component": "switch"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '64d04a83-9919-4163-b8cb-ebaf8108b308',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Enter Promo Code',
    'Type promotional code in dedicated field',
    'interaction',
    'open',
    '{"type": "text_input", "component": "input"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '29f886bb-8dd5-4661-9daa-e312cc06d843',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Select Language from List',
    'Choose preferred language from dropdown',
    'interaction',
    'open',
    '{"type": "select", "component": "dropdown"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '87cdb474-3a42-4cf7-8bb9-8eb0cb6c0d0b',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Loading Spinner While Finding Driver',
    'Animated spinner during driver matching',
    'interaction',
    'open',
    '{"type": "loading", "feedback": "visual"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '00a7a73a-43ca-4398-8e09-d25135a437e3',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Success Checkmark on Payment',
    'Green checkmark animation on successful payment',
    'interaction',
    'open',
    '{"type": "success", "feedback": "visual"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e1525e14-9987-4b92-9f84-4bbd7dc3972e',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Error Shake on Invalid Input',
    'Input field shakes when validation fails',
    'interaction',
    'open',
    '{"type": "error", "feedback": "visual"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '09225cb5-89b7-4102-be81-e97f3d7200c4',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Haptic Feedback on Ride Accept',
    'Vibration when driver accepts ride',
    'interaction',
    'open',
    '{"type": "success", "feedback": "haptic"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '7751dba7-c5b8-430f-84fa-a57372de9a63',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Sound Effect on New Request',
    'Audio alert for incoming ride request',
    'interaction',
    'open',
    '{"type": "notification", "feedback": "audio"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '98fab3b2-5a82-478b-89f0-a6ed7726b077',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Progress Bar During Upload',
    'Animated bar showing document upload progress',
    'interaction',
    'open',
    '{"type": "progress", "feedback": "visual"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '22bf5c02-70ca-46c4-ba66-0d90971566f4',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Pulse Animation on Emergency Button',
    'Pulsing red glow on SOS button',
    'interaction',
    'open',
    '{"type": "attention", "feedback": "visual"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '125dd661-68b9-4252-ad02-801c865c5a89',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Skeleton Screen While Loading',
    'Placeholder animation during data fetch',
    'interaction',
    'open',
    '{"type": "loading", "feedback": "visual"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd8d12d07-f8d8-46dc-bb6c-cfe8c00be4ae',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Toast Notification on Save',
    'Brief message confirming data saved',
    'interaction',
    'open',
    '{"type": "success", "feedback": "visual"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '321ae14f-a64c-4cd3-ba4b-63113bb64c88',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Bounce Animation on Button Press',
    'Button bounces on tap for feedback',
    'interaction',
    'open',
    '{"type": "interaction", "feedback": "visual"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b6d75683-92e0-4fe9-ba35-90d3a7180842',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Fade In/Out Transition',
    'Smooth fade between screen transitions',
    'interaction',
    'open',
    '{"type": "transition", "feedback": "visual"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b5be74ef-0ac7-4f2c-a198-10dd8a9a3f1e',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Car Icon Animation on Route',
    'Animated car moving along route polyline',
    'interaction',
    'open',
    '{"type": "tracking", "feedback": "visual"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e6afb8e8-499c-4e7d-a0f0-3079df13d16f',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Ripple Effect on Tap',
    'Material ripple spreading from tap point',
    'interaction',
    'open',
    '{"type": "interaction", "feedback": "visual"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'aac9302d-bdf3-4c5a-ae37-56f4f3519582',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Count-Up Animation for Earnings',
    'Numbers animate counting up to total',
    'interaction',
    'open',
    '{"type": "data", "feedback": "visual"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'bdb3079a-d51f-4ef6-b06f-c40cdb9cb139',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Badge Bounce on New Notification',
    'Notification badge bounces when new item',
    'interaction',
    'open',
    '{"type": "notification", "feedback": "visual"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '1512df08-89e0-4071-9674-093132af10c7',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Navigate to Trip Details Screen',
    'Transition from list to detail view',
    'interaction',
    'open',
    '{"type": "navigation", "pattern": "drill_down"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '01ea6ff2-0aa6-489e-bd8a-9db66a7ac641',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Return to Previous Screen',
    'Back button or gesture to go back',
    'interaction',
    'open',
    '{"type": "navigation", "pattern": "back"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '853e1674-f59e-4163-9ea9-a85f14b02320',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Tab Switch to Different Section',
    'Navigate between main app sections',
    'interaction',
    'open',
    '{"type": "navigation", "pattern": "tab"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '3eda5b09-3f0d-4f6a-a09e-f24efee0e2ff',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Modal Opens for Quick Action',
    'Bottom sheet slides up for action',
    'interaction',
    'open',
    '{"type": "navigation", "pattern": "modal"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2ec00792-3488-4f3e-bbe0-8eb09d7e347b',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Deep Link to Specific Screen',
    'URL opens app to specific view',
    'interaction',
    'open',
    '{"type": "navigation", "pattern": "deep_link"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '36fac937-c8a0-4846-b6f9-9f524d72a059',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Breadcrumb Navigation in Admin',
    'Click breadcrumb to navigate up hierarchy',
    'interaction',
    'open',
    '{"type": "navigation", "pattern": "breadcrumb"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '220fcccc-d975-4d6d-b259-ca6a7a4ca7f3',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Wizard Steps for Onboarding',
    'Multi-step flow with next/previous',
    'interaction',
    'open',
    '{"type": "navigation", "pattern": "wizard"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b4078b3e-1514-4aa1-a76b-fad32bd200ee',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Drawer Opens for Menu',
    'Side menu slides in from edge',
    'interaction',
    'open',
    '{"type": "navigation", "pattern": "drawer"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '3d905d6a-c08d-4f1f-a3c3-3eddc0a642cd',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Popup for Confirmation',
    'Alert dialog requires user decision',
    'interaction',
    'open',
    '{"type": "navigation", "pattern": "dialog"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'f79ca252-709b-45dc-9ef0-a56d58c6a06d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Redirect After Successful Action',
    'Auto-navigate after completing task',
    'interaction',
    'open',
    '{"type": "navigation", "pattern": "redirect"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '73d9e7ea-d311-4420-85bb-78c0deb77196',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Context Menu on Long Press',
    'Menu appears at touch point',
    'interaction',
    'open',
    '{"type": "navigation", "pattern": "context_menu"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ea546cc7-ab30-4186-82b3-97f6b40b138c',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Stepper Shows Progress',
    'Visual indicator of current step',
    'interaction',
    'open',
    '{"type": "navigation", "pattern": "stepper"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'a3d339c5-c066-4e02-b509-8e50bba0a02e',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Carousel for Feature Tour',
    'Swipe through onboarding slides',
    'interaction',
    'open',
    '{"type": "navigation", "pattern": "carousel"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '061a0754-71ae-4b69-b188-811f09ad7bda',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Accordion Expand/Collapse',
    'Click header to reveal content',
    'interaction',
    'open',
    '{"type": "navigation", "pattern": "accordion"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '1ff600aa-0b20-4e40-9f61-2ee30b28bc9c',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Infinite Scroll Pagination',
    'Auto-load more items at bottom',
    'interaction',
    'open',
    '{"type": "navigation", "pattern": "infinite_scroll"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '1dbfb1ab-ae39-4cc3-8ba9-c51dbf392674',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Live Driver Location Updates',
    'Driver marker animates in real-time on map',
    'interaction',
    'open',
    '{"type": "realtime", "technology": "websocket"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b97ff9d9-15fb-45b1-b07c-32528cbad3e6',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'ETA Updates Every 30 Seconds',
    'Arrival time recalculates dynamically',
    'interaction',
    'open',
    '{"type": "realtime", "technology": "polling"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'fdd6cd6b-18ad-4fb8-9827-5b15888f3b4e',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Ride Status Changes',
    'UI updates when ride status changes',
    'interaction',
    'open',
    '{"type": "realtime", "technology": "websocket"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '60af0032-b178-4c32-8843-e2781152d2d1',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'New Message Notification',
    'Chat updates when new message arrives',
    'interaction',
    'open',
    '{"type": "realtime", "technology": "websocket"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd453ec28-bef0-44be-adfe-a60237fffc6b',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Earnings Counter Increments',
    'Total earnings updates after each trip',
    'interaction',
    'open',
    '{"type": "realtime", "technology": "event"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'a61dd2d5-24c8-40aa-a9a0-397f7fc29159',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Surge Pricing Banner Appears',
    'Alert shows when surge becomes active',
    'interaction',
    'open',
    '{"type": "realtime", "technology": "push"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '282ea03e-7bbf-43ba-b3fe-591c9b3bd8f8',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Online Driver Count Updates',
    'Admin dashboard shows live driver count',
    'interaction',
    'open',
    '{"type": "realtime", "technology": "websocket"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '96fd044b-ac81-4fcb-a997-26ac2ea0f819',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Trip Request Countdown',
    'Timer counts down before request expires',
    'interaction',
    'open',
    '{"type": "realtime", "technology": "timer"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '614837f0-b257-4a13-9807-dac27c9bc676',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Live Activity Feed',
    'Admin sees real-time activity stream',
    'interaction',
    'open',
    '{"type": "realtime", "technology": "websocket"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'a6918508-8edd-4ab7-a661-0177e37167e6',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Notification Badge Updates',
    'Unread count increases instantly',
    'interaction',
    'open',
    '{"type": "realtime", "technology": "push"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'interaction'],
    1,
    NOW(),
    NOW()
);

-- ========================================
-- DESIGN TOKENS (72 items)
-- ========================================
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'eb8fced1-81b1-4504-8bd0-363e8189a23d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Primary Brand Blue',
    '#0066FF - Main brand color for buttons and accents',
    'design_token',
    'open',
    '{"category": "color", "type": "primary", "value": "#0066FF"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '5d5623ab-123e-4a68-9916-851de02b1837',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Primary Hover Blue',
    '#0052CC - Hover state for primary color',
    'design_token',
    'open',
    '{"category": "color", "type": "primary", "value": "#0052CC"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '6799d019-b3cd-4932-8c28-c1ed84a56bdb',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Primary Pressed Blue',
    '#003D99 - Active/pressed state for primary',
    'design_token',
    'open',
    '{"category": "color", "type": "primary", "value": "#003D99"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '54ab02a6-6a14-4969-9ef4-c3bf2679642a',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Secondary Green',
    '#00B894 - Success, confirmations, earnings',
    'design_token',
    'open',
    '{"category": "color", "type": "secondary", "value": "#00B894"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'efb5c5ad-3a4c-4192-9817-c9832f6da531',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Error Red',
    '#FF3B30 - Errors, cancellations, critical actions',
    'design_token',
    'open',
    '{"category": "color", "type": "error", "value": "#FF3B30"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '8aa80134-08b6-49b4-9e96-a4fabe02f74c',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Warning Orange',
    '#FF9500 - Warnings and alerts',
    'design_token',
    'open',
    '{"category": "color", "type": "warning", "value": "#FF9500"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '91ae0baa-b012-4a89-b9ea-9994cd60e932',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Info Cyan',
    '#5AC8FA - Informational messages',
    'design_token',
    'open',
    '{"category": "color", "type": "info", "value": "#5AC8FA"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'a3ecc7b9-40ea-4fdd-ad29-b45445c08a89',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Background White',
    '#FFFFFF - Primary background color',
    'design_token',
    'open',
    '{"category": "color", "type": "background", "value": "#FFFFFF"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '4867099b-1dc6-4dfe-9f34-660c41da3aef',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Background Gray',
    '#F2F2F7 - Secondary background',
    'design_token',
    'open',
    '{"category": "color", "type": "background", "value": "#F2F2F7"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '413529a3-eadb-4bab-810f-4e5b666df19d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Surface White',
    '#FFFFFF - Card and surface color',
    'design_token',
    'open',
    '{"category": "color", "type": "surface", "value": "#FFFFFF"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '8460e662-59e8-4d21-ad51-bb7ba58cba83',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Text Primary Black',
    '#000000 - Primary text color',
    'design_token',
    'open',
    '{"category": "color", "type": "text", "value": "#000000"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'c077a979-40d6-4ef8-b076-58abd78d404a',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Text Secondary Gray',
    '#8E8E93 - Secondary text and labels',
    'design_token',
    'open',
    '{"category": "color", "type": "text", "value": "#8E8E93"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '31482245-f1ce-4a04-9fdc-80e62765eebd',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Text Disabled Gray',
    '#C7C7CC - Disabled text state',
    'design_token',
    'open',
    '{"category": "color", "type": "text", "value": "#C7C7CC"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '503eeead-cf91-4a86-9eb3-5953b2aaf140',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Border Light Gray',
    '#E5E5EA - Subtle borders and dividers',
    'design_token',
    'open',
    '{"category": "color", "type": "border", "value": "#E5E5EA"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '1724fa77-fac9-479a-bfda-a1dc3a245de0',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Border Medium Gray',
    '#C7C7CC - Standard borders',
    'design_token',
    'open',
    '{"category": "color", "type": "border", "value": "#C7C7CC"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '671c6c5f-a91e-48ae-a1e1-0f1db3847ff5',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Surge Red',
    '#D32F2F - Surge pricing indicator',
    'design_token',
    'open',
    '{"category": "color", "type": "functional", "value": "#D32F2F"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2021bdc3-2381-47ec-a73b-4b6a259f6a24',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rating Gold',
    '#FFB300 - Star ratings color',
    'design_token',
    'open',
    '{"category": "color", "type": "functional", "value": "#FFB300"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '6fb0ff3b-15dd-4756-92a8-2eb0d1d953fd',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Map Blue',
    '#4285F4 - Route and map accents',
    'design_token',
    'open',
    '{"category": "color", "type": "functional", "value": "#4285F4"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '3ebd35a6-0338-4920-92d4-b707f9588879',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Dark Mode Background',
    '#1C1C1E - Dark theme background',
    'design_token',
    'open',
    '{"category": "color", "type": "dark", "value": "#1C1C1E"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'db60b29e-7220-4d8f-b31f-fd9dd29f05fe',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Dark Mode Surface',
    '#2C2C2E - Dark theme surface',
    'design_token',
    'open',
    '{"category": "color", "type": "dark", "value": "#2C2C2E"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ae52da0b-b2d2-4404-9e2d-960bfe93dd83',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Font Family Primary',
    'SF Pro Text, -apple-system, system-ui',
    'design_token',
    'open',
    '{"category": "typography", "type": "family", "value": "SF Pro Text"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'abe56cab-817b-4c8c-a94f-35f4cd856572',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Font Family Display',
    'SF Pro Display for large headings',
    'design_token',
    'open',
    '{"category": "typography", "type": "family", "value": "SF Pro Display"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '85930c13-ae44-42ac-949f-6c9a52b7cc17',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Font Family Monospace',
    'SF Mono for codes and numbers',
    'design_token',
    'open',
    '{"category": "typography", "type": "family", "value": "SF Mono"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '024a2998-fe4d-4d93-b225-569e35c210ef',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Font Size XS',
    '12px - Small labels and captions',
    'design_token',
    'open',
    '{"category": "typography", "type": "size", "value": "12px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'a00785d0-f13f-4c60-a543-443ba61da050',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Font Size SM',
    '14px - Body text and descriptions',
    'design_token',
    'open',
    '{"category": "typography", "type": "size", "value": "14px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'a37a5ebb-278a-44b4-8f14-94b97c2d3d76',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Font Size MD',
    '16px - Default body size',
    'design_token',
    'open',
    '{"category": "typography", "type": "size", "value": "16px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd8a94714-78b8-4bcc-8462-81321cd4897e',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Font Size LG',
    '18px - Emphasized text',
    'design_token',
    'open',
    '{"category": "typography", "type": "size", "value": "18px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ca3c01d9-32c6-4d31-9689-454b2c8006e3',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Font Size XL',
    '24px - Section headings',
    'design_token',
    'open',
    '{"category": "typography", "type": "size", "value": "24px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '0cd25e7e-3257-4654-a400-18a36abd3533',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Font Size 2XL',
    '32px - Page titles',
    'design_token',
    'open',
    '{"category": "typography", "type": "size", "value": "32px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'a0cd9106-626d-4a71-b470-c3f5659838db',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Font Size 3XL',
    '48px - Large display text',
    'design_token',
    'open',
    '{"category": "typography", "type": "size", "value": "48px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '239e4bd5-f831-439f-891a-2364d120a404',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Font Weight Regular',
    '400 - Normal text weight',
    'design_token',
    'open',
    '{"category": "typography", "type": "weight", "value": "400"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '6dbeca5b-f097-47d5-bedd-4daf02d0d8b8',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Font Weight Medium',
    '500 - Emphasized text',
    'design_token',
    'open',
    '{"category": "typography", "type": "weight", "value": "500"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '7e6439ee-4b30-4cbc-a5dd-609cbdf7a23a',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Font Weight Semibold',
    '600 - Headings and labels',
    'design_token',
    'open',
    '{"category": "typography", "type": "weight", "value": "600"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e38df441-da9d-47d9-a537-c10018ea1732',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Font Weight Bold',
    '700 - Strong emphasis',
    'design_token',
    'open',
    '{"category": "typography", "type": "weight", "value": "700"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'fc7bef31-c330-46df-a62d-2f9d9b7c403e',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Line Height Tight',
    '1.2 - Headings and titles',
    'design_token',
    'open',
    '{"category": "typography", "type": "line_height", "value": "1.2"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e18ff182-652b-4666-bd4a-1e9a940e2a71',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Line Height Normal',
    '1.5 - Body text',
    'design_token',
    'open',
    '{"category": "typography", "type": "line_height", "value": "1.5"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '71f8819e-0771-4a96-a3cc-45c5ecf38e8a',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Line Height Relaxed',
    '1.75 - Comfortable reading',
    'design_token',
    'open',
    '{"category": "typography", "type": "line_height", "value": "1.75"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e49cd185-bf37-4169-b164-30560630d7f5',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Space XXS',
    '4px - Minimal spacing',
    'design_token',
    'open',
    '{"category": "spacing", "type": "padding", "value": "4px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '3a59fddf-1e6a-4a7f-8337-ec93dfc4d9e3',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Space XS',
    '8px - Compact spacing',
    'design_token',
    'open',
    '{"category": "spacing", "type": "padding", "value": "8px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '5e558a9c-3261-4d99-943d-cff84a596f55',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Space SM',
    '12px - Small spacing',
    'design_token',
    'open',
    '{"category": "spacing", "type": "padding", "value": "12px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'dd315995-2c95-4b50-8755-c15425d81c91',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Space MD',
    '16px - Standard spacing',
    'design_token',
    'open',
    '{"category": "spacing", "type": "padding", "value": "16px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd1531663-8d30-46ce-985d-a2cff0b41682',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Space LG',
    '24px - Large spacing',
    'design_token',
    'open',
    '{"category": "spacing", "type": "padding", "value": "24px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '5f15afac-dc3c-4503-a3f4-2e4b95d707a7',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Space XL',
    '32px - Extra large spacing',
    'design_token',
    'open',
    '{"category": "spacing", "type": "padding", "value": "32px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '7bf7909e-372f-48cd-b64f-3da389f290e8',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Space 2XL',
    '48px - Section spacing',
    'design_token',
    'open',
    '{"category": "spacing", "type": "padding", "value": "48px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'c8b4b688-3b21-4e44-bf86-97a5223c8ebe',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Space 3XL',
    '64px - Major section spacing',
    'design_token',
    'open',
    '{"category": "spacing", "type": "padding", "value": "64px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '6761f841-b7e9-40d2-9014-26e9ebe8de24',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Gap XS',
    '8px - Small element gap',
    'design_token',
    'open',
    '{"category": "spacing", "type": "gap", "value": "8px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '244523c4-1f44-4367-9b9f-20cff71ebef0',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Gap SM',
    '12px - Standard gap',
    'design_token',
    'open',
    '{"category": "spacing", "type": "gap", "value": "12px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '92f5e785-4d52-4edc-ade1-8ff70d4d91ea',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Gap MD',
    '16px - Medium gap',
    'design_token',
    'open',
    '{"category": "spacing", "type": "gap", "value": "16px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'af31665f-34de-4de4-9a3c-c8f528c9df50',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Gap LG',
    '24px - Large gap',
    'design_token',
    'open',
    '{"category": "spacing", "type": "gap", "value": "24px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '6de074e2-356d-4ff5-802b-8a9641037287',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Radius None',
    '0px - Sharp corners',
    'design_token',
    'open',
    '{"category": "radius", "type": "corner", "value": "0px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2d80428d-a728-4ba6-a7ee-d3ef015d5f0d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Radius SM',
    '4px - Subtle rounding',
    'design_token',
    'open',
    '{"category": "radius", "type": "corner", "value": "4px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '5c3ec657-466c-4b72-bc2a-efd418028bba',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Radius MD',
    '8px - Standard rounding',
    'design_token',
    'open',
    '{"category": "radius", "type": "corner", "value": "8px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'bebf3180-14d1-4aa6-8baf-543e85a8dbf5',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Radius LG',
    '12px - Pronounced rounding',
    'design_token',
    'open',
    '{"category": "radius", "type": "corner", "value": "12px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '3ece3b49-2e6a-4fb6-95a8-3ad5ab66ed74',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Radius XL',
    '16px - Large rounding',
    'design_token',
    'open',
    '{"category": "radius", "type": "corner", "value": "16px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '454ff06b-2a86-4f18-813a-53bc31f544bb',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Radius Full',
    '9999px - Pill shape',
    'design_token',
    'open',
    '{"category": "radius", "type": "corner", "value": "9999px"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '124d2427-2faa-4fb3-8f53-6c2d9fd7ef2a',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Shadow SM',
    '0 1px 2px rgba(0,0,0,0.05) - Subtle elevation',
    'design_token',
    'open',
    '{"category": "shadow", "type": "elevation", "value": "0 1px 2px rgba(0,0,0,0.05)"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '5511bbc3-bced-4c71-874e-14a4c1d15234',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Shadow MD',
    '0 4px 6px rgba(0,0,0,0.1) - Standard cards',
    'design_token',
    'open',
    '{"category": "shadow", "type": "elevation", "value": "0 4px 6px rgba(0,0,0,0.1)"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '4d12ae98-f826-4e99-8979-cf2e9c78b585',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Shadow LG',
    '0 10px 15px rgba(0,0,0,0.1) - Elevated modals',
    'design_token',
    'open',
    '{"category": "shadow", "type": "elevation", "value": "0 10px 15px rgba(0,0,0,0.1)"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '7d4fb5a6-8943-4230-999c-70bb15cf0c9e',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Shadow XL',
    '0 20px 25px rgba(0,0,0,0.15) - Floating elements',
    'design_token',
    'open',
    '{"category": "shadow", "type": "elevation", "value": "0 20px 25px rgba(0,0,0,0.15)"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '95453904-aca6-4029-8bf3-21689518ba6a',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Shadow Inner',
    'inset 0 2px 4px rgba(0,0,0,0.05) - Recessed',
    'design_token',
    'open',
    '{"category": "shadow", "type": "elevation", "value": "inset 0 2px 4px rgba(0,0,0,0.05)"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b2687344-f234-46da-9460-a447d4568f31',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Shadow None',
    'No shadow',
    'design_token',
    'open',
    '{"category": "shadow", "type": "elevation", "value": "none"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '8bf86bf3-1c45-4453-ae1c-8567e50f9c98',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Duration Fast',
    '150ms - Quick transitions',
    'design_token',
    'open',
    '{"category": "animation", "type": "duration", "value": "150ms"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'dd727e8f-c87a-4a00-8b02-8fbf71cb4067',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Duration Normal',
    '300ms - Standard animations',
    'design_token',
    'open',
    '{"category": "animation", "type": "duration", "value": "300ms"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '85c6d3eb-5b75-46f7-bd4d-94629298cec8',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Duration Slow',
    '500ms - Deliberate animations',
    'design_token',
    'open',
    '{"category": "animation", "type": "duration", "value": "500ms"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'c60a5d8d-495a-4892-8bb5-658b7781263d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Easing Standard',
    'cubic-bezier(0.4, 0.0, 0.2, 1)',
    'design_token',
    'open',
    '{"category": "animation", "type": "easing", "value": "cubic-bezier(0.4, 0.0, 0.2, 1)"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '33fe08c2-059c-496a-993a-1e7c862fce4b',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Easing Enter',
    'cubic-bezier(0.0, 0.0, 0.2, 1)',
    'design_token',
    'open',
    '{"category": "animation", "type": "easing", "value": "cubic-bezier(0.0, 0.0, 0.2, 1)"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '52c35d8a-a43a-4fbc-8a8a-7e8b840ef2e2',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Easing Exit',
    'cubic-bezier(0.4, 0.0, 1, 1)',
    'design_token',
    'open',
    '{"category": "animation", "type": "easing", "value": "cubic-bezier(0.4, 0.0, 1, 1)"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'f0774f0f-e98c-4397-80fe-d9cf67d1de16',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Easing Bounce',
    'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
    'design_token',
    'open',
    '{"category": "animation", "type": "easing", "value": "cubic-bezier(0.68, -0.55, 0.265, 1.55)"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd3da3866-470c-4937-8c92-eea4169cbb00',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Transition All',
    'all 300ms ease - General transition',
    'design_token',
    'open',
    '{"category": "animation", "type": "transition", "value": "all 300ms ease"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '0bce4f60-058d-4685-9c57-3d594204c425',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Transition Opacity',
    'opacity 150ms ease - Fade effect',
    'design_token',
    'open',
    '{"category": "animation", "type": "transition", "value": "opacity 150ms ease"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b2225f34-8e75-409a-82af-3616fe0b0a45',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Transition Transform',
    'transform 300ms cubic-bezier(0.4, 0.0, 0.2, 1)',
    'design_token',
    'open',
    '{"category": "animation", "type": "transition", "value": "transform 300ms"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '097cecc1-27e3-41a2-92ab-e9d1c3ded3b6',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Transition Color',
    'color 150ms ease - Color changes',
    'design_token',
    'open',
    '{"category": "animation", "type": "transition", "value": "color 150ms ease"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'design_token'],
    1,
    NOW(),
    NOW()
);

-- ========================================
-- ACCESSIBILITY REQUIREMENTS (80 items)
-- ========================================
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'fe01f266-32a5-4f6a-8750-a09edd2ced56',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Text Alternatives for Images',
    'All images have descriptive alt text (WCAG 1.1.1)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "1.1.1", "category": "perceivable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e012f07e-609b-44ca-8fc2-ef5f23e128eb',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Captions for Audio Content',
    'Pre-recorded audio has synchronized captions (WCAG 1.2.2)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "1.2.2", "category": "perceivable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '6bde7276-c120-40ec-b0a1-61e00f94b323',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Audio Descriptions for Video',
    'Videos include audio descriptions of visual content (WCAG 1.2.3)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "1.2.3", "category": "perceivable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '0d21419b-1e6d-4350-a94f-4a71ba4fe6be',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Info and Relationships',
    'Information structure conveyed through markup (WCAG 1.3.1)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "1.3.1", "category": "perceivable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'a4b3589a-04f9-4986-a010-5ab87d58a38c',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Meaningful Sequence',
    'Content reading order is logical (WCAG 1.3.2)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "1.3.2", "category": "perceivable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '1bf3bf43-17c8-413f-a9f4-62b54b8f2b05',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Sensory Characteristics',
    'Instructions don''t rely solely on shape/color/location (WCAG 1.3.3)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "1.3.3", "category": "perceivable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '3c09e94b-0bf3-4ab7-98e9-e2e96deea198',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Use of Color',
    'Color not used as only visual means of conveying info (WCAG 1.4.1)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "1.4.1", "category": "perceivable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '3a40f6ec-744d-4988-92bd-ea14813cd4f3',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Audio Control',
    'Mechanism to pause/stop auto-playing audio (WCAG 1.4.2)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "1.4.2", "category": "perceivable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '9bbdd0fe-4476-4bfa-a645-d1eca8ebc0b9',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Keyboard Accessible',
    'All functionality available via keyboard (WCAG 2.1.1)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "2.1.1", "category": "operable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '758deda8-3826-4773-8e72-07f024152ac9',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'No Keyboard Trap',
    'Keyboard focus can move away from all components (WCAG 2.1.2)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "2.1.2", "category": "operable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '72de4bdc-4820-4bf3-b970-6dba5996febf',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Timing Adjustable',
    'Time limits can be adjusted, extended, or disabled (WCAG 2.2.1)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "2.2.1", "category": "operable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b25f9dce-0df1-4ad6-9be4-f5f85bb83e17',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Pause, Stop, Hide',
    'Moving content can be paused or hidden (WCAG 2.2.2)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "2.2.2", "category": "operable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '20bc9c47-a261-4080-bdfc-1420614ba633',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Three Flashes or Below',
    'Content doesn''t flash more than 3 times/second (WCAG 2.3.1)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "2.3.1", "category": "operable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'aca69729-256e-4b55-ac93-e5b6bd7dffbd',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Bypass Blocks',
    'Skip navigation mechanism provided (WCAG 2.4.1)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "2.4.1", "category": "operable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '05dee54f-1bdb-4ce8-b00c-0513e3e313ea',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Page Titled',
    'Each page has descriptive title (WCAG 2.4.2)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "2.4.2", "category": "operable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ccdf6128-dcae-46ff-8c7a-be0f59e5cad3',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Focus Order',
    'Focus order preserves meaning and operability (WCAG 2.4.3)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "2.4.3", "category": "operable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b898325c-3134-4285-8f0d-5605142f30cf',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Link Purpose in Context',
    'Purpose of each link clear from link text or context (WCAG 2.4.4)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "2.4.4", "category": "operable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '6fae93d6-55b7-4f5a-81ee-1bb20cc1b285',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Language of Page',
    'Default human language of page identified (WCAG 3.1.1)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "3.1.1", "category": "understandable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '7ec96c17-7a39-40cc-977e-a1bec379f221',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'On Focus',
    'Focus doesn''t trigger unexpected context change (WCAG 3.2.1)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "3.2.1", "category": "understandable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '9f15bc91-0bb7-4ca6-9cf3-6b56c8f1b4a5',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'On Input',
    'Changing setting doesn''t cause unexpected context change (WCAG 3.2.2)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "3.2.2", "category": "understandable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '37d5a5cb-33a1-4c71-8b32-7b6aa73df8ca',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Error Identification',
    'Input errors automatically detected and described (WCAG 3.3.1)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "3.3.1", "category": "understandable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd6198258-c4d2-4384-a18f-77d26a8cd384',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Labels or Instructions',
    'Labels provided for user input (WCAG 3.3.2)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "3.3.2", "category": "understandable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '5db53a28-60ca-4604-bbdc-fcc15130bce7',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Parsing',
    'Markup valid and no duplicate IDs (WCAG 4.1.1)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "4.1.1", "category": "robust"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd65679be-fe51-462a-9b73-84297d924a25',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Name, Role, Value',
    'Name and role determined programmatically (WCAG 4.1.2)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "4.1.2", "category": "robust"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'efc8caa5-31d9-49b4-b8ea-b5e87ab54c09',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Reflow',
    'Content reflows at 320px without horizontal scroll (WCAG 1.4.10)',
    'accessibility_requirement',
    'open',
    '{"level": "AA", "guideline": "1.4.10", "category": "perceivable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '0b79e6b8-25fd-4c47-827e-30d1d43476d5',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Contrast Ratio - Normal Text',
    '4.5:1 contrast for normal text (WCAG 1.4.3)',
    'accessibility_requirement',
    'open',
    '{"level": "AA", "guideline": "1.4.3", "category": "perceivable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '5c0aff42-6ea1-443e-87aa-8dd3b1ad8bfb',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Contrast Ratio - Large Text',
    '3:1 contrast for large text (WCAG 1.4.3)',
    'accessibility_requirement',
    'open',
    '{"level": "AA", "guideline": "1.4.3", "category": "perceivable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '103d0b31-06fc-4b4e-8dbc-cc6aaf49f878',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Resize Text',
    'Text can be resized to 200% without loss of content (WCAG 1.4.4)',
    'accessibility_requirement',
    'open',
    '{"level": "AA", "guideline": "1.4.4", "category": "perceivable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '5c8bb957-0d26-48df-8a8d-39f8a56dde9f',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Images of Text',
    'Use real text instead of images of text (WCAG 1.4.5)',
    'accessibility_requirement',
    'open',
    '{"level": "AA", "guideline": "1.4.5", "category": "perceivable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '740d67bf-ee1e-4759-baf4-f8e746f28c62',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Orientation',
    'Content works in both portrait and landscape (WCAG 1.3.4)',
    'accessibility_requirement',
    'open',
    '{"level": "AA", "guideline": "1.3.4", "category": "perceivable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '53ecf0f9-1973-4783-b9d9-5bab0b7b0e67',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Identify Input Purpose',
    'Input purpose can be programmatically determined (WCAG 1.3.5)',
    'accessibility_requirement',
    'open',
    '{"level": "AA", "guideline": "1.3.5", "category": "perceivable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ca600165-ed92-4383-8be1-820a8ce728b8',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Multiple Ways',
    'Multiple ways to locate pages (WCAG 2.4.5)',
    'accessibility_requirement',
    'open',
    '{"level": "AA", "guideline": "2.4.5", "category": "operable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'abd6bfe7-9371-4228-8ae4-6ab3ba3d14ca',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Headings and Labels',
    'Headings and labels describe topic or purpose (WCAG 2.4.6)',
    'accessibility_requirement',
    'open',
    '{"level": "AA", "guideline": "2.4.6", "category": "operable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '9d603df2-0ad8-4778-801b-a2e9a45b8bc7',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Focus Visible',
    'Keyboard focus indicator is visible (WCAG 2.4.7)',
    'accessibility_requirement',
    'open',
    '{"level": "AA", "guideline": "2.4.7", "category": "operable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '51b2dad5-e0d6-4d25-8562-d3664e8b3d84',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Language of Parts',
    'Language of passages identified (WCAG 3.1.2)',
    'accessibility_requirement',
    'open',
    '{"level": "AA", "guideline": "3.1.2", "category": "understandable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'dff0207e-8452-49c5-a6f4-ce48abf9ead4',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Consistent Navigation',
    'Navigation consistent across pages (WCAG 3.2.3)',
    'accessibility_requirement',
    'open',
    '{"level": "AA", "guideline": "3.2.3", "category": "understandable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd011b0d0-0d5d-4c68-97f6-4703607fbf82',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Consistent Identification',
    'Components with same function identified consistently (WCAG 3.2.4)',
    'accessibility_requirement',
    'open',
    '{"level": "AA", "guideline": "3.2.4", "category": "understandable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b0d035f2-8da0-421c-88e7-e7cb13eb9681',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Error Suggestion',
    'Suggestions provided for correcting errors (WCAG 3.3.3)',
    'accessibility_requirement',
    'open',
    '{"level": "AA", "guideline": "3.3.3", "category": "understandable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2c0e2578-43cb-4bd2-a0c1-d3fe8c72dabf',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Error Prevention - Legal/Financial',
    'Submissions are reversible, checked, or confirmed (WCAG 3.3.4)',
    'accessibility_requirement',
    'open',
    '{"level": "AA", "guideline": "3.3.4", "category": "understandable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '8e93e685-ecd9-4688-a8a6-31e8976f345b',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Status Messages',
    'Status messages communicated to screen readers (WCAG 4.1.3)',
    'accessibility_requirement',
    'open',
    '{"level": "AA", "guideline": "4.1.3", "category": "robust"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '15abfe6c-aee8-4327-9233-a568a3ef57dc',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Pointer Gestures',
    'All functionality works with single pointer (WCAG 2.5.1)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "2.5.1", "category": "operable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'fc5ffbfd-399c-49c4-82c9-7cd2b2f55ef0',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Pointer Cancellation',
    'Up-event used for activation or abort available (WCAG 2.5.2)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "2.5.2", "category": "operable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '00f3b2bb-48b5-4023-9796-e5c59ea6e2ef',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Label in Name',
    'Accessible name contains visible text label (WCAG 2.5.3)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "2.5.3", "category": "operable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '0ff19971-0352-4818-b7ed-7d41b6724880',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Motion Actuation',
    'Motion-triggered functions can be disabled (WCAG 2.5.4)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "2.5.4", "category": "operable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '440fdb72-7453-43af-9884-4016f3a869f7',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Target Size',
    'Touch targets are at least 44x44 CSS pixels (WCAG 2.5.5)',
    'accessibility_requirement',
    'open',
    '{"level": "AAA", "guideline": "2.5.5", "category": "operable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '23f6726d-c7e1-4c11-a885-940aa2e9b979',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Concurrent Input',
    'Content doesn''t restrict use of input modalities (WCAG 2.5.6)',
    'accessibility_requirement',
    'open',
    '{"level": "AAA", "guideline": "2.5.6", "category": "operable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '85b4028a-27e2-4ef0-8a36-bc25aba9a446',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Text Spacing',
    'Content adapts to text spacing adjustments (WCAG 1.4.12)',
    'accessibility_requirement',
    'open',
    '{"level": "AA", "guideline": "1.4.12", "category": "perceivable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '69a2d69b-f479-4845-8af0-c9a18b43ecf3',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Content on Hover or Focus',
    'Hoverable content can be dismissed without moving pointer (WCAG 1.4.13)',
    'accessibility_requirement',
    'open',
    '{"level": "AA", "guideline": "1.4.13", "category": "perceivable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '9f37ac05-9bd9-4cd2-94df-9ea5ff529f68',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Non-text Contrast',
    '3:1 contrast for UI components and graphics (WCAG 1.4.11)',
    'accessibility_requirement',
    'open',
    '{"level": "AA", "guideline": "1.4.11", "category": "perceivable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b9ce6675-4fe9-44f4-9f37-5638c20ba3b4',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Character Key Shortcuts',
    'Single-key shortcuts can be disabled or remapped (WCAG 2.1.4)',
    'accessibility_requirement',
    'open',
    '{"level": "A", "guideline": "2.1.4", "category": "operable"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '731796ab-e62e-4244-99c5-f26edff33d62',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'VoiceOver Support - iOS',
    'Full compatibility with iOS VoiceOver screen reader',
    'accessibility_requirement',
    'open',
    '{"level": "platform", "platform": "iOS", "category": "screen_reader"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '034a6596-ef17-464b-a1d6-62ad70772f70',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'TalkBack Support - Android',
    'Full compatibility with Android TalkBack',
    'accessibility_requirement',
    'open',
    '{"level": "platform", "platform": "Android", "category": "screen_reader"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '395e1d5c-6b97-4575-9419-f3c593ba3529',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'NVDA Support - Web',
    'Compatible with NVDA screen reader on Windows',
    'accessibility_requirement',
    'open',
    '{"level": "platform", "platform": "Web", "category": "screen_reader"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '0566e242-fcfe-4b29-b608-b8b5cf570c64',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'JAWS Support - Web',
    'Compatible with JAWS screen reader',
    'accessibility_requirement',
    'open',
    '{"level": "platform", "platform": "Web", "category": "screen_reader"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'a5eaeee1-f3fc-4fa6-abcd-96f99200c424',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Voice Control - iOS',
    'All interactive elements accessible via Voice Control',
    'accessibility_requirement',
    'open',
    '{"level": "platform", "platform": "iOS", "category": "voice"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '325688dc-2ebc-4a1c-91a0-3ecf6604638d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Switch Control - iOS',
    'Full support for iOS Switch Control',
    'accessibility_requirement',
    'open',
    '{"level": "platform", "platform": "iOS", "category": "motor"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '98fb97b6-7714-47c5-bd64-bce7b6cdaade',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Dynamic Type - iOS',
    'Respects iOS Dynamic Type text size settings',
    'accessibility_requirement',
    'open',
    '{"level": "platform", "platform": "iOS", "category": "vision"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '445f9dea-eb63-49cc-92d2-96859f48b42b',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Reduce Motion - iOS',
    'Respects iOS Reduce Motion accessibility setting',
    'accessibility_requirement',
    'open',
    '{"level": "platform", "platform": "iOS", "category": "vestibular"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b5cd52dd-ef5a-43fe-bf96-3860dfd597eb',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Bold Text - iOS',
    'Works with iOS Bold Text setting',
    'accessibility_requirement',
    'open',
    '{"level": "platform", "platform": "iOS", "category": "vision"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '5e3f62fb-b70c-4ca5-a1c6-3ea513b47eac',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Increase Contrast - iOS',
    'Respects iOS Increase Contrast setting',
    'accessibility_requirement',
    'open',
    '{"level": "platform", "platform": "iOS", "category": "vision"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '9888ce6e-7a3f-40ab-8ad6-d8fb61b80eb1',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Font Scaling - Android',
    'Respects Android system font size',
    'accessibility_requirement',
    'open',
    '{"level": "platform", "platform": "Android", "category": "vision"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '11a60bfa-e094-4a17-bd03-9ce978508431',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Remove Animations - Android',
    'Honors Android Remove Animations setting',
    'accessibility_requirement',
    'open',
    '{"level": "platform", "platform": "Android", "category": "vestibular"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '4877f7c3-9a42-4cbb-b217-003e4dd74458',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'High Contrast - Windows',
    'Supports Windows High Contrast mode',
    'accessibility_requirement',
    'open',
    '{"level": "platform", "platform": "Web", "category": "vision"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'cfbbc6e8-5875-45b0-bf37-0baaee31c742',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Magnification Support',
    'Content works with screen magnification tools',
    'accessibility_requirement',
    'open',
    '{"level": "platform", "platform": "All", "category": "vision"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'bbc4144e-c422-4775-acd3-005808f2f080',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Semantic HTML - Web',
    'Proper use of semantic HTML elements',
    'accessibility_requirement',
    'open',
    '{"level": "platform", "platform": "Web", "category": "structure"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ae45d531-64f0-46be-bdc5-353bbca73075',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Emergency Features Without Login',
    'SOS and safety features accessible without authentication',
    'accessibility_requirement',
    'open',
    '{"level": "ux", "category": "safety", "priority": "critical"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '743400dc-14ec-42d0-95a5-09a8bdea4286',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Simple Language',
    'Plain language used throughout interface',
    'accessibility_requirement',
    'open',
    '{"level": "ux", "category": "cognitive", "priority": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2c4b8b17-d0d8-40a4-9328-74a595f89d3d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Consistent UI Patterns',
    'Same patterns used for similar actions across app',
    'accessibility_requirement',
    'open',
    '{"level": "ux", "category": "cognitive", "priority": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'cfa1592a-4dfa-478e-aa63-e7b6ad540a22',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Clear Error Messages',
    'Error messages explain what went wrong and how to fix',
    'accessibility_requirement',
    'open',
    '{"level": "ux", "category": "feedback", "priority": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '1df9508b-4f81-491d-b9bc-43c07a2840d2',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Loading States',
    'Clear indicators when content is loading',
    'accessibility_requirement',
    'open',
    '{"level": "ux", "category": "feedback", "priority": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '3e73db2e-c91b-4724-b3c9-1f97d5a49146',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Success Confirmations',
    'Visual and auditory feedback for successful actions',
    'accessibility_requirement',
    'open',
    '{"level": "ux", "category": "feedback", "priority": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '40eb474e-ab03-42ad-8e23-0b90f3e398a1',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Undo Functionality',
    'Ability to undo critical actions',
    'accessibility_requirement',
    'open',
    '{"level": "ux", "category": "error_prevention", "priority": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '691401d8-b4ba-4340-81b2-392ad533f8b2',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Timeout Warnings',
    'Warning before session timeout with option to extend',
    'accessibility_requirement',
    'open',
    '{"level": "ux", "category": "time", "priority": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'cbda3b03-e7be-4a4e-893f-17f2ede62a25',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Autosave Progress',
    'Form data automatically saved to prevent loss',
    'accessibility_requirement',
    'open',
    '{"level": "ux", "category": "error_prevention", "priority": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '703a1f69-1bff-4956-9cd4-5812c2ba9bf9',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Customizable Notifications',
    'Fine-grained control over notification types',
    'accessibility_requirement',
    'open',
    '{"level": "ux", "category": "personalization", "priority": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '97ae3c08-25fe-425c-9578-f95ac2d1bdc4',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Offline Mode Indicators',
    'Clear indication of offline status and limitations',
    'accessibility_requirement',
    'open',
    '{"level": "ux", "category": "feedback", "priority": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '56b81338-9c10-4402-a09e-fd398c331a27',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Large Touch Targets on Mobile',
    'All interactive elements minimum 44x44dp',
    'accessibility_requirement',
    'open',
    '{"level": "ux", "category": "motor", "priority": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '7b25286f-641f-4f9b-a239-51995c18a101',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Sufficient Spacing',
    'Adequate spacing between interactive elements',
    'accessibility_requirement',
    'open',
    '{"level": "ux", "category": "motor", "priority": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '6f634b04-a6a3-4069-b587-3249f1ff0cfa',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'One-Handed Mode Support',
    'Key functions accessible with one hand',
    'accessibility_requirement',
    'open',
    '{"level": "ux", "category": "motor", "priority": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e5f13061-3686-4d91-8337-0f6e1062daf6',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Help Documentation',
    'Context-sensitive help available throughout',
    'accessibility_requirement',
    'open',
    '{"level": "ux", "category": "cognitive", "priority": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'accessibility_requirement'],
    1,
    NOW(),
    NOW()
);

-- ========================================
-- UX PATTERNS (60 items)
-- ========================================
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'c92e5a5a-e86b-47eb-9a43-00487a9cf65e',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Bottom Tab Bar Navigation',
    'Primary navigation with 4-5 tabs at bottom of screen',
    'ux_pattern',
    'open',
    '{"category": "navigation", "platform": "mobile", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '115f62e8-0068-445e-b756-b39c4de13938',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Hamburger Side Menu',
    'Hidden navigation menu accessed via hamburger icon',
    'ux_pattern',
    'open',
    '{"category": "navigation", "platform": "all", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'cdddc537-e239-4820-840a-c4bea75dcdc6',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Floating Action Button',
    'Primary action button floating at bottom-right',
    'ux_pattern',
    'open',
    '{"category": "navigation", "platform": "mobile", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'a36f1b51-f997-4c25-953f-865012019a56',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Breadcrumb Trail',
    'Hierarchical navigation showing current location',
    'ux_pattern',
    'open',
    '{"category": "navigation", "platform": "web", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '080ccab6-eac1-442f-8191-e747188598b3',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Step Indicator',
    'Visual progress through multi-step process',
    'ux_pattern',
    'open',
    '{"category": "navigation", "platform": "all", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '0e083e28-fb1c-4fca-80cf-086b4d12f7c7',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Modal Bottom Sheet',
    'Slide-up panel for contextual actions',
    'ux_pattern',
    'open',
    '{"category": "navigation", "platform": "mobile", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'c6de6704-5327-4b1e-bc94-6184ceb83d91',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Full-Screen Overlay',
    'Immersive full-screen view for focused task',
    'ux_pattern',
    'open',
    '{"category": "navigation", "platform": "all", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '958129f0-4b8f-45b3-b73f-f442bc1b122b',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Nested Dropdown Menu',
    'Hierarchical menu with sub-items',
    'ux_pattern',
    'open',
    '{"category": "navigation", "platform": "web", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '53eac943-1d64-4932-bce6-e5c4f0fdb4d6',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Wizard Flow',
    'Sequential multi-step process with next/back',
    'ux_pattern',
    'open',
    '{"category": "navigation", "platform": "all", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '03fbfd6a-8fb2-4645-a5ae-036b12c4e6fb',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Contextual Back Button',
    'Smart back navigation based on user journey',
    'ux_pattern',
    'open',
    '{"category": "navigation", "platform": "all", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '7ac1fe5d-fd49-41d0-9076-6073456ab3fa',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Autocomplete Search',
    'Search field with real-time suggestions',
    'ux_pattern',
    'open',
    '{"category": "input", "complexity": "medium", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b2cf42b0-8af9-4a7b-b9fe-0a0785decd24',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Location Picker with Map',
    'Interactive map for selecting geographic location',
    'ux_pattern',
    'open',
    '{"category": "input", "complexity": "high", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '5b105ea5-1657-4a1d-a619-c212372fa8bf',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Incremental Slider',
    'Drag slider with visual feedback and value display',
    'ux_pattern',
    'open',
    '{"category": "input", "complexity": "low", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '626b5915-d5d0-4adf-b2a5-2083d19c5e91',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Multi-Select Chips',
    'Tag-style multi-select with removable chips',
    'ux_pattern',
    'open',
    '{"category": "input", "complexity": "medium", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '535b63a3-1bbe-4795-9e00-daac356bab13',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Date Range Picker',
    'Select start and end dates with calendar UI',
    'ux_pattern',
    'open',
    '{"category": "input", "complexity": "high", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '331bf50d-396d-4404-a1e1-eb90337fb4e3',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Star Rating Selector',
    'Tap stars to select 1-5 rating',
    'ux_pattern',
    'open',
    '{"category": "input", "complexity": "low", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b44a4c51-83d3-44e3-811e-afd5c3083ec5',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Credit Card Form with Validation',
    'Real-time validation and formatting for card entry',
    'ux_pattern',
    'open',
    '{"category": "input", "complexity": "high", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'c44d92b8-3e0c-4de7-b69a-2fcac199f0dd',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'OTP Input Fields',
    'Segmented input for one-time passwords',
    'ux_pattern',
    'open',
    '{"category": "input", "complexity": "medium", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '7e248075-5a0b-4e63-9353-dae0ce24ca28',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Rich Text Editor',
    'Formatted text input with toolbar',
    'ux_pattern',
    'open',
    '{"category": "input", "complexity": "high", "usage": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'b066f583-5d2e-42e0-a36e-28d2c0ed68c2',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Voice Input',
    'Speech-to-text input alternative',
    'ux_pattern',
    'open',
    '{"category": "input", "complexity": "high", "usage": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '54091114-1f6d-4cd0-8606-b4c9e2af52c8',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Toast Notification',
    'Brief auto-dismissing message at screen bottom',
    'ux_pattern',
    'open',
    '{"category": "feedback", "duration": "short", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '02b907cb-0d31-4221-af4e-6ba41723a0b1',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Progress Bar with Percentage',
    'Visual progress indicator with numeric percentage',
    'ux_pattern',
    'open',
    '{"category": "feedback", "duration": "medium", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '65a0f96c-a4e4-4418-bec2-875a81634ddd',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Skeleton Screen Loader',
    'Content placeholder showing layout structure',
    'ux_pattern',
    'open',
    '{"category": "feedback", "duration": "short", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '0e5615ba-edbc-433f-9bb1-3b6fe7c2b0e7',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Empty State with Action',
    'Illustration and CTA when no content exists',
    'ux_pattern',
    'open',
    '{"category": "feedback", "duration": "permanent", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '56bc15fc-0323-4445-943c-fb7032128a2a',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Error Alert with Retry',
    'Error message with option to retry action',
    'ux_pattern',
    'open',
    '{"category": "feedback", "duration": "permanent", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'd366fa4e-606f-4da3-abbc-825bd520eee2',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Success Animation',
    'Celebratory animation on task completion',
    'ux_pattern',
    'open',
    '{"category": "feedback", "duration": "short", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '062fe5ea-fab4-4b71-b992-9fc377fda7e2',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Pull-to-Refresh',
    'Drag down to refresh content',
    'ux_pattern',
    'open',
    '{"category": "feedback", "duration": "short", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'bc3756ad-88d3-4888-8f29-a88f463764f4',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Infinite Scroll Loading',
    'Auto-load more content as user scrolls',
    'ux_pattern',
    'open',
    '{"category": "feedback", "duration": "ongoing", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '985bc9de-9516-4ed7-aad5-5791c8f93ccb',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Optimistic UI Update',
    'Immediate UI update before server confirmation',
    'ux_pattern',
    'open',
    '{"category": "feedback", "duration": "instant", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e3ba4e32-c164-44b1-b577-54a88e93cac3',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Haptic Feedback on Action',
    'Vibration response to user interaction',
    'ux_pattern',
    'open',
    '{"category": "feedback", "duration": "instant", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e4d4bc4a-8d4c-40f5-986d-4e06cb32b354',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Card Grid Layout',
    'Responsive grid of content cards',
    'ux_pattern',
    'open',
    '{"category": "layout", "responsiveness": "high", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e4bb207e-19e1-4850-a8ba-8d97f86669bd',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'List with Avatar and Actions',
    'Items with thumbnail, text, and action buttons',
    'ux_pattern',
    'open',
    '{"category": "layout", "responsiveness": "medium", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '72c2b919-bf62-45b7-9038-dbf896953bcf',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Accordion Expandable Sections',
    'Collapsible content sections',
    'ux_pattern',
    'open',
    '{"category": "layout", "responsiveness": "medium", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '8697f85e-d0e5-4a35-9602-65c7918e39c2',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Image Carousel',
    'Swipeable image gallery',
    'ux_pattern',
    'open',
    '{"category": "layout", "responsiveness": "low", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '8aac008c-1941-4d4d-bd85-438afe27057e',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Data Table with Sorting',
    'Tabular data with sortable columns',
    'ux_pattern',
    'open',
    '{"category": "layout", "responsiveness": "low", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '60757366-988c-4121-93a8-4d1660574ba0',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Timeline Visualization',
    'Chronological event timeline',
    'ux_pattern',
    'open',
    '{"category": "layout", "responsiveness": "medium", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'dbea0988-e430-4d53-b6ca-68a9d7495676',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Kanban Board',
    'Drag-and-drop columns for workflow',
    'ux_pattern',
    'open',
    '{"category": "layout", "responsiveness": "low", "usage": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '9d2f9209-44aa-4dd4-83bc-c6e66525d642',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Dashboard with Widgets',
    'Customizable widget-based dashboard',
    'ux_pattern',
    'open',
    '{"category": "layout", "responsiveness": "high", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '45398d46-8e15-4d6c-b3cb-1421acf84fe9',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Split View Master-Detail',
    'Two-pane layout with list and detail',
    'ux_pattern',
    'open',
    '{"category": "layout", "responsiveness": "medium", "usage": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'f5b9bea2-bf02-443a-9528-545591f5baa5',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Sticky Header',
    'Fixed header that remains visible on scroll',
    'ux_pattern',
    'open',
    '{"category": "layout", "responsiveness": "high", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '1129bbaf-4852-496b-9e9a-a96796675e96',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Welcome Tutorial Carousel',
    'Swipeable intro slides explaining features',
    'ux_pattern',
    'open',
    '{"category": "onboarding", "complexity": "low", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '7f56bec7-34af-498c-b27a-67f8f1b99ec6',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Progressive Disclosure',
    'Gradually reveal features as user progresses',
    'ux_pattern',
    'open',
    '{"category": "onboarding", "complexity": "medium", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'dc89edef-84fa-453e-9f50-c81367560986',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Contextual Tooltips',
    'In-context help on first use',
    'ux_pattern',
    'open',
    '{"category": "onboarding", "complexity": "low", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '61cdecef-cd8f-491c-8344-0c9c41ffadae',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Guided First-Time Flow',
    'Step-by-step walkthrough of initial setup',
    'ux_pattern',
    'open',
    '{"category": "onboarding", "complexity": "high", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'c80decb3-ee85-41c9-afe6-c1839a36a641',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Sample Data Playground',
    'Pre-populated demo data to explore features',
    'ux_pattern',
    'open',
    '{"category": "onboarding", "complexity": "medium", "usage": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'a6e035eb-76e9-4157-9dd3-b508bd36da17',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Shopping Cart Summary',
    'Itemized list with quantity and total',
    'ux_pattern',
    'open',
    '{"category": "transaction", "complexity": "medium", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ee4dcb44-498c-45e4-a8cd-874866378db8',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'One-Click Checkout',
    'Streamlined single-step payment',
    'ux_pattern',
    'open',
    '{"category": "transaction", "complexity": "high", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '7b225180-4c1e-4dbc-ad78-93acb8988226',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Saved Payment Methods',
    'Manage and select from saved cards',
    'ux_pattern',
    'open',
    '{"category": "transaction", "complexity": "medium", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'ba2e4ea4-5946-4b0d-84af-42379bbcd791',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Price Comparison Table',
    'Side-by-side feature and price comparison',
    'ux_pattern',
    'open',
    '{"category": "transaction", "complexity": "medium", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '27f7fccd-5600-43c0-abfb-4d8fa7069c63',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Receipt with Download Option',
    'Digital receipt with PDF export',
    'ux_pattern',
    'open',
    '{"category": "transaction", "complexity": "low", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '044c06c2-2835-48bf-8525-de81d4b56343',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'User Profile Card',
    'Avatar, name, bio, and stats',
    'ux_pattern',
    'open',
    '{"category": "social", "complexity": "low", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e8db172a-ed94-408e-82d2-7305ece0d03c',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Activity Feed',
    'Chronological stream of updates',
    'ux_pattern',
    'open',
    '{"category": "social", "complexity": "medium", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '04607330-86db-4120-a173-9c3aa02b5401',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Like/Favorite Heart Animation',
    'Animated heart on tap to favorite',
    'ux_pattern',
    'open',
    '{"category": "social", "complexity": "low", "usage": "low"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '0cbd474b-8735-4dd8-a60b-fb63f28c71ba',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Share Sheet',
    'Native sharing to other apps',
    'ux_pattern',
    'open',
    '{"category": "social", "complexity": "low", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '2f66bbd5-7927-47ef-bbbe-d07a45a3f6b5',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Referral Code Copy Button',
    'One-tap copy referral code',
    'ux_pattern',
    'open',
    '{"category": "social", "complexity": "low", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'e7208059-e345-4ca8-b11f-a7394bb1fad0',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Grouped Settings List',
    'Categorized settings with sections',
    'ux_pattern',
    'open',
    '{"category": "settings", "complexity": "low", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '59e7c7bb-6e7b-43a8-9bc5-38401e6001bd',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Toggle Switch with Label',
    'Binary on/off setting',
    'ux_pattern',
    'open',
    '{"category": "settings", "complexity": "low", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '903c922b-632f-4c78-a1cc-62136db29c44',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Disclosure Indicator',
    'Arrow indicating deeper navigation',
    'ux_pattern',
    'open',
    '{"category": "settings", "complexity": "low", "usage": "high"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    '76bd7b05-09b4-40cc-bab1-0130a716ad8d',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Segmented Control',
    '2-4 mutually exclusive options',
    'ux_pattern',
    'open',
    '{"category": "settings", "complexity": "low", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);
INSERT INTO items (id, project_id, title, description, type, status, metadata, priority, tags, version, created_at, updated_at)
VALUES (
    'cb17a625-7189-4673-b43e-a1884da1dc55',
    'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e',
    'Destructive Action Confirmation',
    'Red button with confirmation dialog',
    'ux_pattern',
    'open',
    '{"category": "settings", "complexity": "medium", "usage": "medium"}'::jsonb,
    0,
    ARRAY['swiftride', 'ui-ux', 'ux_pattern'],
    1,
    NOW(),
    NOW()
);

COMMIT;

-- Verify counts
SELECT type, COUNT(*) FROM items WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e' AND type IN ('wireframe', 'component', 'user_flow', 'interaction', 'design_token', 'accessibility_requirement', 'ux_pattern') GROUP BY type ORDER BY type;