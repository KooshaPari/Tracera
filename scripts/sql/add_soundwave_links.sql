-- SoundWave - Add Comprehensive Links (200+)
-- This script creates realistic connections between requirements, features, and tasks
-- Creating a densely connected graph for effective visualization

-- Clear existing links to prevent duplicates
DELETE FROM links WHERE project_id = 'proj_soundwave_001';

-- =============================
-- SECTION 1: Requirements → Features (implements)
-- =============================
-- req_sw_001 (Audio Playback Engine) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_001', 'req_sw_001', 'feat_sw_001', 'implements', '{}', NOW(), NOW()),
('link_sw_002', 'req_sw_001', 'feat_sw_002', 'implements', '{}', NOW(), NOW()),
('link_sw_003', 'req_sw_001', 'feat_sw_003', 'implements', '{}', NOW(), NOW());

-- req_sw_002 (User Authentication) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_004', 'req_sw_002', 'feat_sw_004', 'implements', '{}', NOW(), NOW()),
('link_sw_005', 'req_sw_002', 'feat_sw_005', 'implements', '{}', NOW(), NOW()),
('link_sw_006', 'req_sw_002', 'feat_sw_006', 'implements', '{}', NOW(), NOW());

-- req_sw_003 (Playlist Management) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_007', 'req_sw_003', 'feat_sw_007', 'implements', '{}', NOW(), NOW()),
('link_sw_008', 'req_sw_003', 'feat_sw_008', 'implements', '{}', NOW(), NOW()),
('link_sw_009', 'req_sw_003', 'feat_sw_009', 'implements', '{}', NOW(), NOW()),
('link_sw_010', 'req_sw_003', 'feat_sw_010', 'implements', '{}', NOW(), NOW());

-- req_sw_004 (Music Library Integration) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_011', 'req_sw_004', 'feat_sw_011', 'implements', '{}', NOW(), NOW()),
('link_sw_012', 'req_sw_004', 'feat_sw_012', 'implements', '{}', NOW(), NOW()),
('link_sw_013', 'req_sw_004', 'feat_sw_013', 'implements', '{}', NOW(), NOW());

-- req_sw_005 (Recommendation Engine) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_014', 'req_sw_005', 'feat_sw_014', 'implements', '{}', NOW(), NOW()),
('link_sw_015', 'req_sw_005', 'feat_sw_015', 'implements', '{}', NOW(), NOW()),
('link_sw_016', 'req_sw_005', 'feat_sw_016', 'implements', '{}', NOW(), NOW());

-- req_sw_006 (Offline Playback) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_017', 'req_sw_006', 'feat_sw_017', 'implements', '{}', NOW(), NOW()),
('link_sw_018', 'req_sw_006', 'feat_sw_018', 'implements', '{}', NOW(), NOW()),
('link_sw_019', 'req_sw_006', 'feat_sw_019', 'implements', '{}', NOW(), NOW());

-- req_sw_007 (Podcast Integration) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_020', 'req_sw_007', 'feat_sw_020', 'implements', '{}', NOW(), NOW()),
('link_sw_021', 'req_sw_007', 'feat_sw_021', 'implements', '{}', NOW(), NOW());

-- req_sw_008 (Social Features) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_022', 'req_sw_008', 'feat_sw_022', 'implements', '{}', NOW(), NOW()),
('link_sw_023', 'req_sw_008', 'feat_sw_023', 'implements', '{}', NOW(), NOW());

-- req_sw_009 (Lyrics Display) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_024', 'req_sw_009', 'feat_sw_024', 'implements', '{}', NOW(), NOW());

-- req_sw_010 (Queue Management) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_025', 'req_sw_010', 'feat_sw_025', 'implements', '{}', NOW(), NOW());

-- req_sw_011 (Search & Filtering) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_026', 'req_sw_011', 'feat_sw_026', 'implements', '{}', NOW(), NOW()),
('link_sw_027', 'req_sw_011', 'feat_sw_027', 'implements', '{}', NOW(), NOW());

-- req_sw_012 (Audio Quality Settings) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_028', 'req_sw_012', 'feat_sw_028', 'implements', '{}', NOW(), NOW());

-- req_sw_013 (Equalizer & Sound Effects) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_029', 'req_sw_013', 'feat_sw_029', 'implements', '{}', NOW(), NOW());

-- req_sw_014 (Sleep Timer) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_030', 'req_sw_014', 'feat_sw_030', 'implements', '{}', NOW(), NOW());

-- req_sw_015 (Loved Tracks System) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_031', 'req_sw_015', 'feat_sw_031', 'implements', '{}', NOW(), NOW());

-- req_sw_016 (Album Grouping) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_032', 'req_sw_016', 'feat_sw_032', 'implements', '{}', NOW(), NOW()),
('link_sw_033', 'req_sw_016', 'feat_sw_033', 'implements', '{}', NOW(), NOW());

-- req_sw_017 (Artist Pages) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_034', 'req_sw_017', 'feat_sw_034', 'implements', '{}', NOW(), NOW());

-- req_sw_018 (Genre-based Curation) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_035', 'req_sw_018', 'feat_sw_035', 'implements', '{}', NOW(), NOW());

-- req_sw_019 (Mood-based Playlists) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_036', 'req_sw_019', 'feat_sw_036', 'implements', '{}', NOW(), NOW()),
('link_sw_037', 'req_sw_019', 'feat_sw_037', 'implements', '{}', NOW(), NOW());

-- req_sw_020 (Time-based Playlists) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_038', 'req_sw_020', 'feat_sw_038', 'implements', '{}', NOW(), NOW());

-- req_sw_021 (Radio Stations) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_039', 'req_sw_021', 'feat_sw_039', 'implements', '{}', NOW(), NOW()),
('link_sw_040', 'req_sw_021', 'feat_sw_040', 'implements', '{}', NOW(), NOW());

-- req_sw_022 (User Profiles) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_041', 'req_sw_022', 'feat_sw_041', 'implements', '{}', NOW(), NOW());

-- req_sw_023 (Listening Statistics) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_042', 'req_sw_023', 'feat_sw_042', 'implements', '{}', NOW(), NOW());

-- req_sw_024 (Year in Review) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_043', 'req_sw_024', 'feat_sw_043', 'implements', '{}', NOW(), NOW());

-- req_sw_025 (Notifications System) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_044', 'req_sw_025', 'feat_sw_044', 'implements', '{}', NOW(), NOW());

-- req_sw_026 (Premium Features) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_045', 'req_sw_026', 'feat_sw_045', 'implements', '{}', NOW(), NOW());

-- req_sw_027 (Payment Processing) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_046', 'req_sw_027', 'feat_sw_046', 'implements', '{}', NOW(), NOW());

-- req_sw_028 (Analytics Dashboard) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_047', 'req_sw_028', 'feat_sw_047', 'implements', '{}', NOW(), NOW());

-- req_sw_029 (Content Moderation) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_048', 'req_sw_029', 'feat_sw_048', 'implements', '{}', NOW(), NOW());

-- req_sw_030 (Multi-language Support) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_049', 'req_sw_030', 'feat_sw_049', 'implements', '{}', NOW(), NOW());

-- req_sw_031 (Cross-Device Sync) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_050', 'req_sw_031', 'feat_sw_050', 'implements', '{}', NOW(), NOW()),
('link_sw_051', 'req_sw_031', 'feat_sw_051', 'implements', '{}', NOW(), NOW());

-- req_sw_032 (Duplicate Track Detection) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_052', 'req_sw_032', 'feat_sw_052', 'implements', '{}', NOW(), NOW());

-- req_sw_033 (Collaborative Playlists) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_053', 'req_sw_033', 'feat_sw_053', 'implements', '{}', NOW(), NOW());

-- req_sw_034 (Artist Verification) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_054', 'req_sw_034', 'feat_sw_054', 'implements', '{}', NOW(), NOW());

-- req_sw_035 (Fan Engagement Tools) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_055', 'req_sw_035', 'feat_sw_055', 'implements', '{}', NOW(), NOW());

-- req_sw_036 (Merch Integration) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_056', 'req_sw_036', 'feat_sw_056', 'implements', '{}', NOW(), NOW());

-- req_sw_037 (Concert Ticketing) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_057', 'req_sw_037', 'feat_sw_057', 'implements', '{}', NOW(), NOW());

-- req_sw_038 (Video Content) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_058', 'req_sw_038', 'feat_sw_058', 'implements', '{}', NOW(), NOW());

-- req_sw_039 (Session Sharing) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_059', 'req_sw_039', 'feat_sw_059', 'implements', '{}', NOW(), NOW());

-- req_sw_040 (Parental Controls) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_060', 'req_sw_040', 'feat_sw_060', 'implements', '{}', NOW(), NOW());

-- req_sw_041 (Accessibility Features) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_061', 'req_sw_041', 'feat_sw_061', 'implements', '{}', NOW(), NOW());

-- req_sw_042 (Dark Mode) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_062', 'req_sw_042', 'feat_sw_062', 'implements', '{}', NOW(), NOW());

-- req_sw_043 (Performance Optimization) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_063', 'req_sw_043', 'feat_sw_063', 'implements', '{}', NOW(), NOW());

-- req_sw_044 (API Rate Limiting) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_064', 'req_sw_044', 'feat_sw_064', 'implements', '{}', NOW(), NOW());

-- req_sw_045 (Webhook System) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_065', 'req_sw_045', 'feat_sw_065', 'implements', '{}', NOW(), NOW());

-- req_sw_046 (GraphQL API) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_066', 'req_sw_046', 'feat_sw_066', 'implements', '{}', NOW(), NOW());

-- req_sw_047 (REST API) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_067', 'req_sw_047', 'feat_sw_067', 'implements', '{}', NOW(), NOW());

-- req_sw_048 (Data Export) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_068', 'req_sw_048', 'feat_sw_068', 'implements', '{}', NOW(), NOW());

-- req_sw_049 (Privacy Controls) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_069', 'req_sw_049', 'feat_sw_069', 'implements', '{}', NOW(), NOW());

-- req_sw_050 (Security Audit Logging) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_070', 'req_sw_050', 'feat_sw_070', 'implements', '{}', NOW(), NOW());

-- req_sw_051 (Two-Factor Authentication) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_071', 'req_sw_051', 'feat_sw_071', 'implements', '{}', NOW(), NOW());

-- req_sw_052 (Bot Detection) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_072', 'req_sw_052', 'feat_sw_072', 'implements', '{}', NOW(), NOW());

-- req_sw_053 (DDoS Protection) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_073', 'req_sw_053', 'feat_sw_073', 'implements', '{}', NOW(), NOW());

-- req_sw_054 (Data Encryption) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_074', 'req_sw_054', 'feat_sw_074', 'implements', '{}', NOW(), NOW());

-- req_sw_055 (Incident Response) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_075', 'req_sw_055', 'feat_sw_075', 'implements', '{}', NOW(), NOW());

-- req_sw_056 (Backup & Disaster Recovery) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_076', 'req_sw_056', 'feat_sw_076', 'implements', '{}', NOW(), NOW());

-- req_sw_057 (Load Balancing) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_077', 'req_sw_057', 'feat_sw_077', 'implements', '{}', NOW(), NOW());

-- req_sw_058 (CDN Integration) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_078', 'req_sw_058', 'feat_sw_078', 'implements', '{}', NOW(), NOW());

-- req_sw_059 (Database Optimization) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_079', 'req_sw_059', 'feat_sw_079', 'implements', '{}', NOW(), NOW());

-- req_sw_060 (Monitoring & Alerting) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_080', 'req_sw_060', 'feat_sw_080', 'implements', '{}', NOW(), NOW());

-- req_sw_061 (Machine Learning Pipeline) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_081', 'req_sw_061', 'feat_sw_081', 'implements', '{}', NOW(), NOW()),
('link_sw_082', 'req_sw_061', 'feat_sw_082', 'implements', '{}', NOW(), NOW());

-- req_sw_062 (A/B Testing Framework) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_083', 'req_sw_062', 'feat_sw_083', 'implements', '{}', NOW(), NOW());

-- req_sw_063 (Feature Flags) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_084', 'req_sw_063', 'feat_sw_084', 'implements', '{}', NOW(), NOW());

-- req_sw_064 (Blue-Green Deployments) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_085', 'req_sw_064', 'feat_sw_085', 'implements', '{}', NOW(), NOW());

-- req_sw_065 (Container Orchestration) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_086', 'req_sw_065', 'feat_sw_086', 'implements', '{}', NOW(), NOW());

-- req_sw_066 (Logging System) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_087', 'req_sw_066', 'feat_sw_087', 'implements', '{}', NOW(), NOW());

-- req_sw_067 (Distributed Tracing) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_088', 'req_sw_067', 'feat_sw_088', 'implements', '{}', NOW(), NOW());

-- req_sw_068 (Message Queue System) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_089', 'req_sw_068', 'feat_sw_089', 'implements', '{}', NOW(), NOW());

-- req_sw_069 (Cache Layer) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_090', 'req_sw_069', 'feat_sw_090', 'implements', '{}', NOW(), NOW());

-- req_sw_070 (Search Infrastructure) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_091', 'req_sw_070', 'feat_sw_091', 'implements', '{}', NOW(), NOW());

-- req_sw_071 (Streaming Backend) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_092', 'req_sw_071', 'feat_sw_092', 'implements', '{}', NOW(), NOW());

-- req_sw_072 (License Management) → Features
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_093', 'req_sw_072', 'feat_sw_093', 'implements', '{}', NOW(), NOW());

-- =============================
-- SECTION 2: Features → Tasks (depends_on)
-- Each feature depends on 1-2 tasks
-- =============================
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_094', 'feat_sw_001', 'task_sw_001', 'depends_on', '{}', NOW(), NOW()),
('link_sw_095', 'feat_sw_002', 'task_sw_001', 'depends_on', '{}', NOW(), NOW()),
('link_sw_096', 'feat_sw_003', 'task_sw_002', 'depends_on', '{}', NOW(), NOW()),
('link_sw_097', 'feat_sw_004', 'task_sw_002', 'depends_on', '{}', NOW(), NOW()),
('link_sw_098', 'feat_sw_005', 'task_sw_003', 'depends_on', '{}', NOW(), NOW()),
('link_sw_099', 'feat_sw_006', 'task_sw_003', 'depends_on', '{}', NOW(), NOW()),
('link_sw_100', 'feat_sw_007', 'task_sw_004', 'depends_on', '{}', NOW(), NOW()),
('link_sw_101', 'feat_sw_008', 'task_sw_004', 'depends_on', '{}', NOW(), NOW()),
('link_sw_102', 'feat_sw_009', 'task_sw_005', 'depends_on', '{}', NOW(), NOW()),
('link_sw_103', 'feat_sw_010', 'task_sw_005', 'depends_on', '{}', NOW(), NOW()),
('link_sw_104', 'feat_sw_011', 'task_sw_006', 'depends_on', '{}', NOW(), NOW()),
('link_sw_105', 'feat_sw_012', 'task_sw_006', 'depends_on', '{}', NOW(), NOW()),
('link_sw_106', 'feat_sw_013', 'task_sw_007', 'depends_on', '{}', NOW(), NOW()),
('link_sw_107', 'feat_sw_014', 'task_sw_007', 'depends_on', '{}', NOW(), NOW()),
('link_sw_108', 'feat_sw_015', 'task_sw_008', 'depends_on', '{}', NOW(), NOW()),
('link_sw_109', 'feat_sw_016', 'task_sw_008', 'depends_on', '{}', NOW(), NOW()),
('link_sw_110', 'feat_sw_017', 'task_sw_009', 'depends_on', '{}', NOW(), NOW()),
('link_sw_111', 'feat_sw_018', 'task_sw_009', 'depends_on', '{}', NOW(), NOW()),
('link_sw_112', 'feat_sw_019', 'task_sw_010', 'depends_on', '{}', NOW(), NOW()),
('link_sw_113', 'feat_sw_020', 'task_sw_010', 'depends_on', '{}', NOW(), NOW()),
('link_sw_114', 'feat_sw_021', 'task_sw_011', 'depends_on', '{}', NOW(), NOW()),
('link_sw_115', 'feat_sw_022', 'task_sw_011', 'depends_on', '{}', NOW(), NOW()),
('link_sw_116', 'feat_sw_023', 'task_sw_012', 'depends_on', '{}', NOW(), NOW()),
('link_sw_117', 'feat_sw_024', 'task_sw_012', 'depends_on', '{}', NOW(), NOW()),
('link_sw_118', 'feat_sw_025', 'task_sw_013', 'depends_on', '{}', NOW(), NOW()),
('link_sw_119', 'feat_sw_026', 'task_sw_013', 'depends_on', '{}', NOW(), NOW()),
('link_sw_120', 'feat_sw_027', 'task_sw_014', 'depends_on', '{}', NOW(), NOW()),
('link_sw_121', 'feat_sw_028', 'task_sw_014', 'depends_on', '{}', NOW(), NOW()),
('link_sw_122', 'feat_sw_029', 'task_sw_015', 'depends_on', '{}', NOW(), NOW()),
('link_sw_123', 'feat_sw_030', 'task_sw_015', 'depends_on', '{}', NOW(), NOW()),
('link_sw_124', 'feat_sw_031', 'task_sw_016', 'depends_on', '{}', NOW(), NOW()),
('link_sw_125', 'feat_sw_032', 'task_sw_016', 'depends_on', '{}', NOW(), NOW()),
('link_sw_126', 'feat_sw_033', 'task_sw_017', 'depends_on', '{}', NOW(), NOW()),
('link_sw_127', 'feat_sw_034', 'task_sw_017', 'depends_on', '{}', NOW(), NOW()),
('link_sw_128', 'feat_sw_035', 'task_sw_018', 'depends_on', '{}', NOW(), NOW()),
('link_sw_129', 'feat_sw_036', 'task_sw_018', 'depends_on', '{}', NOW(), NOW()),
('link_sw_130', 'feat_sw_037', 'task_sw_019', 'depends_on', '{}', NOW(), NOW()),
('link_sw_131', 'feat_sw_038', 'task_sw_019', 'depends_on', '{}', NOW(), NOW()),
('link_sw_132', 'feat_sw_039', 'task_sw_020', 'depends_on', '{}', NOW(), NOW()),
('link_sw_133', 'feat_sw_040', 'task_sw_020', 'depends_on', '{}', NOW(), NOW()),
('link_sw_134', 'feat_sw_041', 'task_sw_001', 'depends_on', '{}', NOW(), NOW()),
('link_sw_135', 'feat_sw_042', 'task_sw_002', 'depends_on', '{}', NOW(), NOW()),
('link_sw_136', 'feat_sw_043', 'task_sw_003', 'depends_on', '{}', NOW(), NOW()),
('link_sw_137', 'feat_sw_044', 'task_sw_004', 'depends_on', '{}', NOW(), NOW()),
('link_sw_138', 'feat_sw_045', 'task_sw_005', 'depends_on', '{}', NOW(), NOW()),
('link_sw_139', 'feat_sw_046', 'task_sw_006', 'depends_on', '{}', NOW(), NOW()),
('link_sw_140', 'feat_sw_047', 'task_sw_007', 'depends_on', '{}', NOW(), NOW()),
('link_sw_141', 'feat_sw_048', 'task_sw_008', 'depends_on', '{}', NOW(), NOW()),
('link_sw_142', 'feat_sw_049', 'task_sw_009', 'depends_on', '{}', NOW(), NOW()),
('link_sw_143', 'feat_sw_050', 'task_sw_010', 'depends_on', '{}', NOW(), NOW()),
('link_sw_144', 'feat_sw_051', 'task_sw_011', 'depends_on', '{}', NOW(), NOW()),
('link_sw_145', 'feat_sw_052', 'task_sw_012', 'depends_on', '{}', NOW(), NOW()),
('link_sw_146', 'feat_sw_053', 'task_sw_013', 'depends_on', '{}', NOW(), NOW()),
('link_sw_147', 'feat_sw_054', 'task_sw_014', 'depends_on', '{}', NOW(), NOW()),
('link_sw_148', 'feat_sw_055', 'task_sw_015', 'depends_on', '{}', NOW(), NOW()),
('link_sw_149', 'feat_sw_056', 'task_sw_016', 'depends_on', '{}', NOW(), NOW()),
('link_sw_150', 'feat_sw_057', 'task_sw_017', 'depends_on', '{}', NOW(), NOW()),
('link_sw_151', 'feat_sw_058', 'task_sw_018', 'depends_on', '{}', NOW(), NOW()),
('link_sw_152', 'feat_sw_059', 'task_sw_019', 'depends_on', '{}', NOW(), NOW()),
('link_sw_153', 'feat_sw_060', 'task_sw_020', 'depends_on', '{}', NOW(), NOW()),
('link_sw_154', 'feat_sw_061', 'task_sw_001', 'depends_on', '{}', NOW(), NOW()),
('link_sw_155', 'feat_sw_062', 'task_sw_002', 'depends_on', '{}', NOW(), NOW()),
('link_sw_156', 'feat_sw_063', 'task_sw_003', 'depends_on', '{}', NOW(), NOW()),
('link_sw_157', 'feat_sw_064', 'task_sw_004', 'depends_on', '{}', NOW(), NOW()),
('link_sw_158', 'feat_sw_065', 'task_sw_005', 'depends_on', '{}', NOW(), NOW()),
('link_sw_159', 'feat_sw_066', 'task_sw_006', 'depends_on', '{}', NOW(), NOW()),
('link_sw_160', 'feat_sw_067', 'task_sw_007', 'depends_on', '{}', NOW(), NOW()),
('link_sw_161', 'feat_sw_068', 'task_sw_008', 'depends_on', '{}', NOW(), NOW()),
('link_sw_162', 'feat_sw_069', 'task_sw_009', 'depends_on', '{}', NOW(), NOW()),
('link_sw_163', 'feat_sw_070', 'task_sw_010', 'depends_on', '{}', NOW(), NOW()),
('link_sw_164', 'feat_sw_071', 'task_sw_011', 'depends_on', '{}', NOW(), NOW()),
('link_sw_165', 'feat_sw_072', 'task_sw_012', 'depends_on', '{}', NOW(), NOW()),
('link_sw_166', 'feat_sw_073', 'task_sw_013', 'depends_on', '{}', NOW(), NOW()),
('link_sw_167', 'feat_sw_074', 'task_sw_014', 'depends_on', '{}', NOW(), NOW()),
('link_sw_168', 'feat_sw_075', 'task_sw_015', 'depends_on', '{}', NOW(), NOW()),
('link_sw_169', 'feat_sw_076', 'task_sw_016', 'depends_on', '{}', NOW(), NOW()),
('link_sw_170', 'feat_sw_077', 'task_sw_017', 'depends_on', '{}', NOW(), NOW()),
('link_sw_171', 'feat_sw_078', 'task_sw_018', 'depends_on', '{}', NOW(), NOW()),
('link_sw_172', 'feat_sw_079', 'task_sw_019', 'depends_on', '{}', NOW(), NOW()),
('link_sw_173', 'feat_sw_080', 'task_sw_020', 'depends_on', '{}', NOW(), NOW()),
('link_sw_174', 'feat_sw_081', 'task_sw_001', 'depends_on', '{}', NOW(), NOW()),
('link_sw_175', 'feat_sw_082', 'task_sw_002', 'depends_on', '{}', NOW(), NOW()),
('link_sw_176', 'feat_sw_083', 'task_sw_003', 'depends_on', '{}', NOW(), NOW()),
('link_sw_177', 'feat_sw_084', 'task_sw_004', 'depends_on', '{}', NOW(), NOW()),
('link_sw_178', 'feat_sw_085', 'task_sw_005', 'depends_on', '{}', NOW(), NOW()),
('link_sw_179', 'feat_sw_086', 'task_sw_006', 'depends_on', '{}', NOW(), NOW()),
('link_sw_180', 'feat_sw_087', 'task_sw_007', 'depends_on', '{}', NOW(), NOW()),
('link_sw_181', 'feat_sw_088', 'task_sw_008', 'depends_on', '{}', NOW(), NOW()),
('link_sw_182', 'feat_sw_089', 'task_sw_009', 'depends_on', '{}', NOW(), NOW()),
('link_sw_183', 'feat_sw_090', 'task_sw_010', 'depends_on', '{}', NOW(), NOW()),
('link_sw_184', 'feat_sw_091', 'task_sw_011', 'depends_on', '{}', NOW(), NOW()),
('link_sw_185', 'feat_sw_092', 'task_sw_012', 'depends_on', '{}', NOW(), NOW()),
('link_sw_186', 'feat_sw_093', 'task_sw_013', 'depends_on', '{}', NOW(), NOW()),
('link_sw_187', 'feat_sw_094', 'task_sw_014', 'depends_on', '{}', NOW(), NOW()),
('link_sw_188', 'feat_sw_095', 'task_sw_015', 'depends_on', '{}', NOW(), NOW()),
('link_sw_189', 'feat_sw_096', 'task_sw_016', 'depends_on', '{}', NOW(), NOW()),
('link_sw_190', 'feat_sw_097', 'task_sw_017', 'depends_on', '{}', NOW(), NOW()),
('link_sw_191', 'feat_sw_098', 'task_sw_018', 'depends_on', '{}', NOW(), NOW()),
('link_sw_192', 'feat_sw_099', 'task_sw_019', 'depends_on', '{}', NOW(), NOW()),
('link_sw_193', 'feat_sw_100', 'task_sw_020', 'depends_on', '{}', NOW(), NOW());

-- =============================
-- SECTION 3: Tasks → Tests (tests)
-- Each task has at least one test
-- =============================
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_194', 'task_sw_001', 'test_sw_001', 'tests', '{}', NOW(), NOW()),
('link_sw_195', 'task_sw_002', 'test_sw_001', 'tests', '{}', NOW(), NOW()),
('link_sw_196', 'task_sw_003', 'test_sw_002', 'tests', '{}', NOW(), NOW()),
('link_sw_197', 'task_sw_004', 'test_sw_002', 'tests', '{}', NOW(), NOW()),
('link_sw_198', 'task_sw_005', 'test_sw_003', 'tests', '{}', NOW(), NOW()),
('link_sw_199', 'task_sw_006', 'test_sw_003', 'tests', '{}', NOW(), NOW()),
('link_sw_200', 'task_sw_007', 'test_sw_004', 'tests', '{}', NOW(), NOW()),
('link_sw_201', 'task_sw_008', 'test_sw_004', 'tests', '{}', NOW(), NOW()),
('link_sw_202', 'task_sw_009', 'test_sw_005', 'tests', '{}', NOW(), NOW()),
('link_sw_203', 'task_sw_010', 'test_sw_005', 'tests', '{}', NOW(), NOW()),
('link_sw_204', 'task_sw_011', 'test_sw_001', 'tests', '{}', NOW(), NOW()),
('link_sw_205', 'task_sw_012', 'test_sw_002', 'tests', '{}', NOW(), NOW()),
('link_sw_206', 'task_sw_013', 'test_sw_003', 'tests', '{}', NOW(), NOW()),
('link_sw_207', 'task_sw_014', 'test_sw_004', 'tests', '{}', NOW(), NOW()),
('link_sw_208', 'task_sw_015', 'test_sw_005', 'tests', '{}', NOW(), NOW()),
('link_sw_209', 'task_sw_016', 'test_sw_001', 'tests', '{}', NOW(), NOW()),
('link_sw_210', 'task_sw_017', 'test_sw_002', 'tests', '{}', NOW(), NOW()),
('link_sw_211', 'task_sw_018', 'test_sw_003', 'tests', '{}', NOW(), NOW()),
('link_sw_212', 'task_sw_019', 'test_sw_004', 'tests', '{}', NOW(), NOW()),
('link_sw_213', 'task_sw_020', 'test_sw_005', 'tests', '{}', NOW(), NOW());

-- =============================
-- SECTION 4: Requirements → Requirements (related_to)
-- Create relationships between logically related requirements
-- =============================
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_214', 'req_sw_001', 'req_sw_012', 'related_to', '{}', NOW(), NOW()),  -- Audio Playback → Audio Quality
('link_sw_215', 'req_sw_002', 'req_sw_051', 'related_to', '{}', NOW(), NOW()),  -- Auth → 2FA
('link_sw_216', 'req_sw_003', 'req_sw_033', 'related_to', '{}', NOW(), NOW()),  -- Playlists → Collaborative
('link_sw_217', 'req_sw_004', 'req_sw_032', 'related_to', '{}', NOW(), NOW()),  -- Library → Duplicates
('link_sw_218', 'req_sw_005', 'req_sw_061', 'related_to', '{}', NOW(), NOW()),  -- Recommendations → ML
('link_sw_219', 'req_sw_006', 'req_sw_069', 'related_to', '{}', NOW(), NOW()),  -- Offline → Cache
('link_sw_220', 'req_sw_007', 'req_sw_021', 'related_to', '{}', NOW(), NOW()),  -- Podcasts → Radio
('link_sw_221', 'req_sw_008', 'req_sw_035', 'related_to', '{}', NOW(), NOW()),  -- Social → Engagement
('link_sw_222', 'req_sw_009', 'req_sw_024', 'related_to', '{}', NOW(), NOW()),  -- Lyrics → Year Review
('link_sw_223', 'req_sw_010', 'req_sw_021', 'related_to', '{}', NOW(), NOW()),  -- Queue → Radio
('link_sw_224', 'req_sw_011', 'req_sw_070', 'related_to', '{}', NOW(), NOW()),  -- Search → Infrastructure
('link_sw_225', 'req_sw_013', 'req_sw_042', 'related_to', '{}', NOW(), NOW()),  -- Equalizer → Dark Mode
('link_sw_226', 'req_sw_014', 'req_sw_020', 'related_to', '{}', NOW(), NOW()),  -- Sleep Timer → Time Playlists
('link_sw_227', 'req_sw_015', 'req_sw_023', 'related_to', '{}', NOW(), NOW()),  -- Loved Tracks → Stats
('link_sw_228', 'req_sw_016', 'req_sw_017', 'related_to', '{}', NOW(), NOW()),  -- Album → Artist Pages
('link_sw_229', 'req_sw_018', 'req_sw_019', 'related_to', '{}', NOW(), NOW()),  -- Genre → Mood
('link_sw_230', 'req_sw_022', 'req_sw_023', 'related_to', '{}', NOW(), NOW()),  -- Profiles → Stats
('link_sw_231', 'req_sw_025', 'req_sw_029', 'related_to', '{}', NOW(), NOW()),  -- Notifications → Moderation
('link_sw_232', 'req_sw_026', 'req_sw_027', 'related_to', '{}', NOW(), NOW()),  -- Premium → Payment
('link_sw_233', 'req_sw_031', 'req_sw_064', 'related_to', '{}', NOW(), NOW()),  -- Sync → Deployments
('link_sw_234', 'req_sw_034', 'req_sw_041', 'related_to', '{}', NOW(), NOW()),  -- Verification → Accessibility
('link_sw_235', 'req_sw_036', 'req_sw_037', 'related_to', '{}', NOW(), NOW()),  -- Merch → Ticketing
('link_sw_236', 'req_sw_038', 'req_sw_058', 'related_to', '{}', NOW(), NOW()),  -- Video → CDN
('link_sw_237', 'req_sw_039', 'req_sw_031', 'related_to', '{}', NOW(), NOW()),  -- Session → Sync
('link_sw_238', 'req_sw_040', 'req_sw_049', 'related_to', '{}', NOW(), NOW()),  -- Parental → Privacy
('link_sw_239', 'req_sw_043', 'req_sw_059', 'related_to', '{}', NOW(), NOW()),  -- Performance → DB Optimization
('link_sw_240', 'req_sw_044', 'req_sw_053', 'related_to', '{}', NOW(), NOW()),  -- Rate Limiting → DDoS
('link_sw_241', 'req_sw_045', 'req_sw_046', 'related_to', '{}', NOW(), NOW()),  -- Webhooks → GraphQL
('link_sw_242', 'req_sw_047', 'req_sw_046', 'related_to', '{}', NOW(), NOW()),  -- REST → GraphQL
('link_sw_243', 'req_sw_048', 'req_sw_049', 'related_to', '{}', NOW(), NOW()),  -- Export → Privacy
('link_sw_244', 'req_sw_050', 'req_sw_066', 'related_to', '{}', NOW(), NOW()),  -- Audit → Logging
('link_sw_245', 'req_sw_052', 'req_sw_053', 'related_to', '{}', NOW(), NOW()),  -- Bot Detection → DDoS
('link_sw_246', 'req_sw_054', 'req_sw_057', 'related_to', '{}', NOW(), NOW()),  -- Encryption → Load Balancing
('link_sw_247', 'req_sw_055', 'req_sw_060', 'related_to', '{}', NOW(), NOW()),  -- Incident Response → Monitoring
('link_sw_248', 'req_sw_056', 'req_sw_057', 'related_to', '{}', NOW(), NOW()),  -- Backup → Load Balancing
('link_sw_249', 'req_sw_062', 'req_sw_063', 'related_to', '{}', NOW(), NOW()),  -- A/B Testing → Flags
('link_sw_250', 'req_sw_064', 'req_sw_065', 'related_to', '{}', NOW(), NOW()),  -- Blue-Green → Orchestration
('link_sw_251', 'req_sw_067', 'req_sw_066', 'related_to', '{}', NOW(), NOW()),  -- Tracing → Logging
('link_sw_252', 'req_sw_068', 'req_sw_089', 'related_to', '{}', NOW(), NOW()),  -- Message Queue → Cache
('link_sw_253', 'req_sw_072', 'req_sw_036', 'related_to', '{}', NOW(), NOW());  -- License → Merch

-- =============================
-- SECTION 5: Features → Features (depends_on)
-- Create dependencies between features
-- =============================
INSERT INTO links (id, source_id, target_id, type, metadata, created_at, updated_at) VALUES
('link_sw_254', 'feat_sw_004', 'feat_sw_001', 'depends_on', '{}', NOW(), NOW()),  -- Auth depends on Playback
('link_sw_255', 'feat_sw_007', 'feat_sw_001', 'depends_on', '{}', NOW(), NOW()),  -- Playlists depends on Playback
('link_sw_256', 'feat_sw_011', 'feat_sw_007', 'depends_on', '{}', NOW(), NOW()),  -- Library depends on Playlists
('link_sw_257', 'feat_sw_014', 'feat_sw_001', 'depends_on', '{}', NOW(), NOW()),  -- Recommendations depends on Playback
('link_sw_258', 'feat_sw_017', 'feat_sw_001', 'depends_on', '{}', NOW(), NOW()),  -- Offline depends on Playback
('link_sw_259', 'feat_sw_020', 'feat_sw_001', 'depends_on', '{}', NOW(), NOW()),  -- Podcasts depends on Playback
('link_sw_260', 'feat_sw_022', 'feat_sw_004', 'depends_on', '{}', NOW(), NOW()),  -- Social depends on Auth
('link_sw_261', 'feat_sw_024', 'feat_sw_001', 'depends_on', '{}', NOW(), NOW()),  -- Lyrics depends on Playback
('link_sw_262', 'feat_sw_025', 'feat_sw_001', 'depends_on', '{}', NOW(), NOW()),  -- Queue depends on Playback
('link_sw_263', 'feat_sw_026', 'feat_sw_001', 'depends_on', '{}', NOW(), NOW()),  -- Search depends on Playback
('link_sw_264', 'feat_sw_028', 'feat_sw_001', 'depends_on', '{}', NOW(), NOW()),  -- Quality Settings depends on Playback
('link_sw_265', 'feat_sw_031', 'feat_sw_007', 'depends_on', '{}', NOW(), NOW()),  -- Loved Tracks depends on Playlists
('link_sw_266', 'feat_sw_032', 'feat_sw_011', 'depends_on', '{}', NOW(), NOW()),  -- Album Grouping depends on Library
('link_sw_267', 'feat_sw_034', 'feat_sw_011', 'depends_on', '{}', NOW(), NOW()),  -- Artist Pages depends on Library
('link_sw_268', 'feat_sw_035', 'feat_sw_032', 'depends_on', '{}', NOW(), NOW()),  -- Genre Curation depends on Albums
('link_sw_269', 'feat_sw_036', 'feat_sw_001', 'depends_on', '{}', NOW(), NOW()),  -- Mood Playlists depends on Playback
('link_sw_270', 'feat_sw_039', 'feat_sw_001', 'depends_on', '{}', NOW(), NOW()),  -- Radio depends on Playback
('link_sw_271', 'feat_sw_041', 'feat_sw_004', 'depends_on', '{}', NOW(), NOW()),  -- Profiles depends on Auth
('link_sw_272', 'feat_sw_042', 'feat_sw_041', 'depends_on', '{}', NOW(), NOW()),  -- Stats depends on Profiles
('link_sw_273', 'feat_sw_043', 'feat_sw_042', 'depends_on', '{}', NOW(), NOW()),  -- Year Review depends on Stats
('link_sw_274', 'feat_sw_044', 'feat_sw_022', 'depends_on', '{}', NOW(), NOW()),  -- Notifications depends on Social
('link_sw_275', 'feat_sw_045', 'feat_sw_004', 'depends_on', '{}', NOW(), NOW()),  -- Premium depends on Auth
('link_sw_276', 'feat_sw_046', 'feat_sw_045', 'depends_on', '{}', NOW(), NOW()),  -- Payment depends on Premium
('link_sw_277', 'feat_sw_050', 'feat_sw_001', 'depends_on', '{}', NOW(), NOW()),  -- Cross-Device Sync depends on Playback
('link_sw_278', 'feat_sw_052', 'feat_sw_011', 'depends_on', '{}', NOW(), NOW()),  -- Duplicate Detection depends on Library
('link_sw_279', 'feat_sw_053', 'feat_sw_007', 'depends_on', '{}', NOW(), NOW()),  -- Collaborative depends on Playlists
('link_sw_280', 'feat_sw_054', 'feat_sw_034', 'depends_on', '{}', NOW(), NOW()),  -- Verification depends on Artist Pages
('link_sw_281', 'feat_sw_055', 'feat_sw_054', 'depends_on', '{}', NOW(), NOW()),  -- Engagement depends on Verification
('link_sw_282', 'feat_sw_056', 'feat_sw_055', 'depends_on', '{}', NOW(), NOW()),  -- Merch depends on Engagement
('link_sw_283', 'feat_sw_057', 'feat_sw_034', 'depends_on', '{}', NOW(), NOW()),  -- Ticketing depends on Artist Pages
('link_sw_284', 'feat_sw_058', 'feat_sw_001', 'depends_on', '{}', NOW(), NOW()),  -- Video depends on Playback
('link_sw_285', 'feat_sw_059', 'feat_sw_050', 'depends_on', '{}', NOW(), NOW()),  -- Session Sharing depends on Sync
('link_sw_286', 'feat_sw_060', 'feat_sw_045', 'depends_on', '{}', NOW(), NOW()),  -- Parental Controls depends on Premium
('link_sw_287', 'feat_sw_062', 'feat_sw_041', 'depends_on', '{}', NOW(), NOW()),  -- Dark Mode depends on Profiles
('link_sw_288', 'feat_sw_063', 'feat_sw_001', 'depends_on', '{}', NOW(), NOW()),  -- Perf Optimization depends on Playback
('link_sw_289', 'feat_sw_064', 'feat_sw_067', 'depends_on', '{}', NOW(), NOW()),  -- Rate Limiting depends on API
('link_sw_290', 'feat_sw_065', 'feat_sw_064', 'depends_on', '{}', NOW(), NOW()),  -- Webhooks depends on Rate Limiting
('link_sw_291', 'feat_sw_066', 'feat_sw_067', 'depends_on', '{}', NOW(), NOW()),  -- GraphQL depends on API
('link_sw_292', 'feat_sw_069', 'feat_sw_045', 'depends_on', '{}', NOW(), NOW()),  -- Privacy depends on Premium
('link_sw_293', 'feat_sw_070', 'feat_sw_050', 'depends_on', '{}', NOW(), NOW()),  -- Audit Logging depends on Sync
('link_sw_294', 'feat_sw_071', 'feat_sw_004', 'depends_on', '{}', NOW(), NOW()),  -- 2FA depends on Auth
('link_sw_295', 'feat_sw_072', 'feat_sw_026', 'depends_on', '{}', NOW(), NOW()),  -- Bot Detection depends on Search
('link_sw_296', 'feat_sw_073', 'feat_sw_001', 'depends_on', '{}', NOW(), NOW()),  -- DDoS depends on Playback
('link_sw_297', 'feat_sw_074', 'feat_sw_045', 'depends_on', '{}', NOW(), NOW()),  -- Encryption depends on Premium
('link_sw_298', 'feat_sw_075', 'feat_sw_070', 'depends_on', '{}', NOW(), NOW()),  -- Incident Response depends on Audit
('link_sw_299', 'feat_sw_076', 'feat_sw_050', 'depends_on', '{}', NOW(), NOW()),  -- Backup depends on Sync
('link_sw_300', 'feat_sw_077', 'feat_sw_001', 'depends_on', '{}', NOW(), NOW()),  -- Load Balancing depends on Playback
('link_sw_301', 'feat_sw_078', 'feat_sw_001', 'depends_on', '{}', NOW(), NOW()),  -- CDN depends on Playback
('link_sw_302', 'feat_sw_079', 'feat_sw_026', 'depends_on', '{}', NOW(), NOW()),  -- DB Optimization depends on Search
('link_sw_303', 'feat_sw_080', 'feat_sw_070', 'depends_on', '{}', NOW(), NOW()),  -- Monitoring depends on Audit
('link_sw_304', 'feat_sw_081', 'feat_sw_014', 'depends_on', '{}', NOW(), NOW()),  -- ML Pipeline depends on Recommendations
('link_sw_305', 'feat_sw_082', 'feat_sw_081', 'depends_on', '{}', NOW(), NOW()),  -- A/B Testing depends on ML
('link_sw_306', 'feat_sw_083', 'feat_sw_082', 'depends_on', '{}', NOW(), NOW()),  -- Flags depends on A/B Testing
('link_sw_307', 'feat_sw_084', 'feat_sw_077', 'depends_on', '{}', NOW(), NOW()),  -- Blue-Green depends on Load Balancing
('link_sw_308', 'feat_sw_085', 'feat_sw_084', 'depends_on', '{}', NOW(), NOW()),  -- Orchestration depends on Blue-Green
('link_sw_309', 'feat_sw_086', 'feat_sw_070', 'depends_on', '{}', NOW(), NOW()),  -- Logging depends on Audit
('link_sw_310', 'feat_sw_087', 'feat_sw_086', 'depends_on', '{}', NOW(), NOW()),  -- Tracing depends on Logging
('link_sw_311', 'feat_sw_088', 'feat_sw_044', 'depends_on', '{}', NOW(), NOW()),  -- Message Queue depends on Notifications
('link_sw_312', 'feat_sw_089', 'feat_sw_063', 'depends_on', '{}', NOW(), NOW()),  -- Cache depends on Performance
('link_sw_313', 'feat_sw_090', 'feat_sw_026', 'depends_on', '{}', NOW(), NOW()),  -- Search depends on Search API
('link_sw_314', 'feat_sw_091', 'feat_sw_001', 'depends_on', '{}', NOW(), NOW()),  -- Streaming depends on Playback
('link_sw_315', 'feat_sw_092', 'feat_sw_046', 'depends_on', '{}', NOW(), NOW());  -- License depends on Payment

-- Summary: Total links created = 315+ providing comprehensive connectivity
-- Distribution:
-- Req → Features: 93 links
-- Features → Tasks: 100 links
-- Tasks → Tests: 20 links
-- Req → Req: 40 links
-- Feature → Features: 62 links
-- Total: 315 links (exceeds 200+ requirement)
