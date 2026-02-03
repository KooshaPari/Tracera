-- Add comprehensive links between TeamSync items
-- This SQL script adds 250+ links to create a complete graph view
-- Links connect requirements -> features -> stories -> tasks -> tests
-- Plus cross-cutting links for relationships and dependencies

INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, link_metadata, created_at, updated_at) VALUES

-- MESSAGING EPIC: Requirements -> Features (implements)
('link_msg_100', 'proj_teamsync_001', 'req_msg_001', 'feat_msg_001', 'implements', '{"status": "complete"}', NOW() - INTERVAL '90 days', NOW() - INTERVAL '25 days'),
('link_msg_101', 'proj_teamsync_001', 'req_msg_001', 'feat_msg_002', 'implements', '{"status": "complete"}', NOW() - INTERVAL '88 days', NOW() - INTERVAL '23 days'),
('link_msg_102', 'proj_teamsync_001', 'req_msg_002', 'feat_msg_003', 'implements', '{"status": "complete"}', NOW() - INTERVAL '86 days', NOW() - INTERVAL '21 days'),
('link_msg_103', 'proj_teamsync_001', 'req_msg_002', 'feat_msg_004', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '84 days', NOW() - INTERVAL '19 days'),
('link_msg_104', 'proj_teamsync_001', 'req_msg_003', 'feat_msg_005', 'implements', '{"status": "complete"}', NOW() - INTERVAL '82 days', NOW() - INTERVAL '17 days'),
('link_msg_105', 'proj_teamsync_001', 'req_msg_003', 'feat_msg_006', 'implements', '{"status": "complete"}', NOW() - INTERVAL '80 days', NOW() - INTERVAL '15 days'),
('link_msg_106', 'proj_teamsync_001', 'req_msg_004', 'feat_msg_007', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '78 days', NOW() - INTERVAL '13 days'),
('link_msg_107', 'proj_teamsync_001', 'req_msg_004', 'feat_msg_008', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '76 days', NOW() - INTERVAL '11 days'),
('link_msg_108', 'proj_teamsync_001', 'req_msg_005', 'feat_msg_009', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '74 days', NOW() - INTERVAL '9 days'),
('link_msg_109', 'proj_teamsync_001', 'req_msg_005', 'feat_msg_010', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '72 days', NOW() - INTERVAL '7 days'),
('link_msg_110', 'proj_teamsync_001', 'req_msg_006', 'feat_msg_011', 'implements', '{"status": "complete"}', NOW() - INTERVAL '70 days', NOW() - INTERVAL '5 days'),
('link_msg_111', 'proj_teamsync_001', 'req_msg_007', 'feat_msg_012', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '68 days', NOW() - INTERVAL '3 days'),

-- MESSAGING EPIC: Features -> User Stories (traces_to)
('link_msg_120', 'proj_teamsync_001', 'feat_msg_001', 'story_msg_001', 'traces_to', '{"priority": "critical"}', NOW() - INTERVAL '85 days', NOW() - INTERVAL '20 days'),
('link_msg_121', 'proj_teamsync_001', 'feat_msg_002', 'story_msg_002', 'traces_to', '{"priority": "high"}', NOW() - INTERVAL '83 days', NOW() - INTERVAL '18 days'),
('link_msg_122', 'proj_teamsync_001', 'feat_msg_003', 'story_msg_006', 'traces_to', '{"priority": "high"}', NOW() - INTERVAL '81 days', NOW() - INTERVAL '16 days'),
('link_msg_123', 'proj_teamsync_001', 'feat_msg_004', 'story_msg_006', 'traces_to', '{"priority": "high"}', NOW() - INTERVAL '79 days', NOW() - INTERVAL '14 days'),
('link_msg_124', 'proj_teamsync_001', 'feat_msg_005', 'story_msg_007', 'traces_to', '{"priority": "medium"}', NOW() - INTERVAL '77 days', NOW() - INTERVAL '12 days'),
('link_msg_125', 'proj_teamsync_001', 'feat_msg_006', 'story_msg_008', 'traces_to', '{"priority": "high"}', NOW() - INTERVAL '75 days', NOW() - INTERVAL '10 days'),
('link_msg_126', 'proj_teamsync_001', 'feat_msg_007', 'story_msg_003', 'traces_to', '{"priority": "high"}', NOW() - INTERVAL '73 days', NOW() - INTERVAL '8 days'),
('link_msg_127', 'proj_teamsync_001', 'feat_msg_008', 'story_msg_003', 'traces_to', '{"priority": "medium"}', NOW() - INTERVAL '71 days', NOW() - INTERVAL '6 days'),
('link_msg_128', 'proj_teamsync_001', 'feat_msg_009', 'story_msg_004', 'traces_to', '{"priority": "medium"}', NOW() - INTERVAL '69 days', NOW() - INTERVAL '4 days'),
('link_msg_129', 'proj_teamsync_001', 'feat_msg_010', 'story_msg_004', 'traces_to', '{"priority": "low"}', NOW() - INTERVAL '67 days', NOW() - INTERVAL '2 days'),
('link_msg_130', 'proj_teamsync_001', 'feat_msg_011', 'story_msg_001', 'traces_to', '{"priority": "medium"}', NOW() - INTERVAL '65 days', NOW() - INTERVAL '1 days'),
('link_msg_131', 'proj_teamsync_001', 'feat_msg_012', 'story_msg_005', 'traces_to', '{"priority": "medium"}', NOW() - INTERVAL '63 days', NOW() - INTERVAL '0 days'),

-- USER STORIES -> TASKS (depends_on)
('link_msg_140', 'proj_teamsync_001', 'story_msg_001', 'task_msg_001', 'depends_on', '{"order": 1}', NOW() - INTERVAL '80 days', NOW() - INTERVAL '15 days'),
('link_msg_141', 'proj_teamsync_001', 'story_msg_001', 'task_msg_002', 'depends_on', '{"order": 2}', NOW() - INTERVAL '79 days', NOW() - INTERVAL '14 days'),
('link_msg_142', 'proj_teamsync_001', 'story_msg_002', 'task_msg_002', 'depends_on', '{"order": 1}', NOW() - INTERVAL '78 days', NOW() - INTERVAL '13 days'),
('link_msg_143', 'proj_teamsync_001', 'story_msg_003', 'task_msg_004', 'depends_on', '{"order": 1}', NOW() - INTERVAL '77 days', NOW() - INTERVAL '12 days'),
('link_msg_144', 'proj_teamsync_001', 'story_msg_004', 'task_msg_005', 'depends_on', '{"order": 1}', NOW() - INTERVAL '76 days', NOW() - INTERVAL '11 days'),
('link_msg_145', 'proj_teamsync_001', 'story_msg_005', 'task_msg_008', 'depends_on', '{"order": 1}', NOW() - INTERVAL '75 days', NOW() - INTERVAL '10 days'),
('link_msg_146', 'proj_teamsync_001', 'story_msg_006', 'task_msg_003', 'depends_on', '{"order": 1}', NOW() - INTERVAL '74 days', NOW() - INTERVAL '9 days'),
('link_msg_147', 'proj_teamsync_001', 'story_msg_007', 'task_msg_003', 'depends_on', '{"order": 1}', NOW() - INTERVAL '73 days', NOW() - INTERVAL '8 days'),
('link_msg_148', 'proj_teamsync_001', 'story_msg_008', 'task_msg_001', 'depends_on', '{"order": 1}', NOW() - INTERVAL '72 days', NOW() - INTERVAL '7 days'),

-- TASKS -> TESTS (tests)
('link_msg_150', 'proj_teamsync_001', 'task_msg_001', 'test_msg_001', 'tests', '{"coverage": 95}', NOW() - INTERVAL '75 days', NOW() - INTERVAL '10 days'),
('link_msg_151', 'proj_teamsync_001', 'task_msg_001', 'test_msg_002', 'tests', '{"coverage": 88}', NOW() - INTERVAL '74 days', NOW() - INTERVAL '9 days'),
('link_msg_152', 'proj_teamsync_001', 'task_msg_001', 'test_msg_003', 'tests', '{"coverage": 85}', NOW() - INTERVAL '73 days', NOW() - INTERVAL '8 days'),
('link_msg_153', 'proj_teamsync_001', 'task_msg_002', 'test_msg_002', 'tests', '{"coverage": 88}', NOW() - INTERVAL '72 days', NOW() - INTERVAL '7 days'),
('link_msg_154', 'proj_teamsync_001', 'task_msg_003', 'test_msg_006', 'tests', '{"coverage": 90}', NOW() - INTERVAL '71 days', NOW() - INTERVAL '6 days'),
('link_msg_155', 'proj_teamsync_001', 'task_msg_004', 'test_msg_004', 'tests', '{"coverage": 92}', NOW() - INTERVAL '70 days', NOW() - INTERVAL '5 days'),
('link_msg_156', 'proj_teamsync_001', 'task_msg_005', 'test_msg_001', 'tests', '{"coverage": 85}', NOW() - INTERVAL '69 days', NOW() - INTERVAL '4 days'),
('link_msg_157', 'proj_teamsync_001', 'task_msg_006', 'test_msg_005', 'tests', '{"coverage": 80}', NOW() - INTERVAL '68 days', NOW() - INTERVAL '3 days'),
('link_msg_158', 'proj_teamsync_001', 'task_msg_007', 'test_msg_010', 'tests', '{"coverage": 85}', NOW() - INTERVAL '67 days', NOW() - INTERVAL '2 days'),
('link_msg_159', 'proj_teamsync_001', 'task_msg_008', 'test_msg_009', 'tests', '{"coverage": 82}', NOW() - INTERVAL '66 days', NOW() - INTERVAL '1 days'),
('link_msg_160', 'proj_teamsync_001', 'task_msg_009', 'test_msg_001', 'tests', '{"coverage": 90}', NOW() - INTERVAL '65 days', NOW() - INTERVAL '0 days'),
('link_msg_161', 'proj_teamsync_001', 'task_msg_010', 'test_msg_001', 'tests', '{"coverage": 88}', NOW() - INTERVAL '64 days', NOW() - INTERVAL '-1 days'),

-- FEATURES -> API ENDPOINTS (traces_to)
('link_msg_170', 'proj_teamsync_001', 'feat_msg_001', 'api_msg_001', 'traces_to', '{"endpoint_status": "live"}', NOW() - INTERVAL '75 days', NOW() - INTERVAL '10 days'),
('link_msg_171', 'proj_teamsync_001', 'feat_msg_001', 'api_msg_002', 'traces_to', '{"endpoint_status": "live"}', NOW() - INTERVAL '74 days', NOW() - INTERVAL '9 days'),
('link_msg_172', 'proj_teamsync_001', 'feat_msg_001', 'api_msg_008', 'traces_to', '{"endpoint_status": "live"}', NOW() - INTERVAL '73 days', NOW() - INTERVAL '8 days'),
('link_msg_173', 'proj_teamsync_001', 'feat_msg_005', 'api_msg_003', 'traces_to', '{"endpoint_status": "live"}', NOW() - INTERVAL '72 days', NOW() - INTERVAL '7 days'),
('link_msg_174', 'proj_teamsync_001', 'feat_msg_006', 'api_msg_004', 'traces_to', '{"endpoint_status": "live"}', NOW() - INTERVAL '71 days', NOW() - INTERVAL '6 days'),
('link_msg_175', 'proj_teamsync_001', 'feat_msg_004', 'api_msg_006', 'traces_to', '{"endpoint_status": "beta"}', NOW() - INTERVAL '70 days', NOW() - INTERVAL '5 days'),
('link_msg_176', 'proj_teamsync_001', 'feat_msg_012', 'api_msg_007', 'traces_to', '{"endpoint_status": "beta"}', NOW() - INTERVAL '69 days', NOW() - INTERVAL '4 days'),
('link_msg_177', 'proj_teamsync_001', 'feat_msg_010', 'api_msg_005', 'traces_to', '{"endpoint_status": "live"}', NOW() - INTERVAL '68 days', NOW() - INTERVAL '3 days'),

-- CHANNELS EPIC: Requirements -> Features (implements)
('link_chan_100', 'proj_teamsync_001', 'req_chan_001', 'feat_chan_001', 'implements', '{"status": "complete"}', NOW() - INTERVAL '85 days', NOW() - INTERVAL '20 days'),
('link_chan_101', 'proj_teamsync_001', 'req_chan_001', 'feat_chan_002', 'implements', '{"status": "complete"}', NOW() - INTERVAL '83 days', NOW() - INTERVAL '18 days'),
('link_chan_102', 'proj_teamsync_001', 'req_chan_002', 'feat_chan_003', 'implements', '{"status": "complete"}', NOW() - INTERVAL '81 days', NOW() - INTERVAL '16 days'),
('link_chan_103', 'proj_teamsync_001', 'req_chan_003', 'feat_chan_004', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '79 days', NOW() - INTERVAL '14 days'),
('link_chan_104', 'proj_teamsync_001', 'req_chan_004', 'feat_chan_005', 'implements', '{"status": "complete"}', NOW() - INTERVAL '77 days', NOW() - INTERVAL '12 days'),
('link_chan_105', 'proj_teamsync_001', 'req_chan_005', 'feat_chan_006', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '75 days', NOW() - INTERVAL '10 days'),
('link_chan_106', 'proj_teamsync_001', 'req_chan_006', 'feat_chan_007', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '73 days', NOW() - INTERVAL '8 days'),

-- CHANNELS EPIC: Features -> API Endpoints (traces_to)
('link_chan_120', 'proj_teamsync_001', 'feat_chan_001', 'api_chan_001', 'traces_to', '{"endpoint_status": "live"}', NOW() - INTERVAL '80 days', NOW() - INTERVAL '15 days'),
('link_chan_121', 'proj_teamsync_001', 'feat_chan_002', 'api_chan_002', 'traces_to', '{"endpoint_status": "live"}', NOW() - INTERVAL '78 days', NOW() - INTERVAL '13 days'),
('link_chan_122', 'proj_teamsync_001', 'feat_chan_003', 'api_chan_003', 'traces_to', '{"endpoint_status": "live"}', NOW() - INTERVAL '76 days', NOW() - INTERVAL '11 days'),
('link_chan_123', 'proj_teamsync_001', 'feat_chan_004', 'api_chan_004', 'traces_to', '{"endpoint_status": "beta"}', NOW() - INTERVAL '74 days', NOW() - INTERVAL '9 days'),
('link_chan_124', 'proj_teamsync_001', 'feat_chan_005', 'api_chan_005', 'traces_to', '{"endpoint_status": "live"}', NOW() - INTERVAL '72 days', NOW() - INTERVAL '7 days'),

-- DIRECT MESSAGES EPIC: Requirements -> Features (implements)
('link_dm_100', 'proj_teamsync_001', 'req_dm_001', 'feat_dm_001', 'implements', '{"status": "complete"}', NOW() - INTERVAL '88 days', NOW() - INTERVAL '23 days'),
('link_dm_101', 'proj_teamsync_001', 'req_dm_002', 'feat_dm_002', 'implements', '{"status": "complete"}', NOW() - INTERVAL '86 days', NOW() - INTERVAL '21 days'),
('link_dm_102', 'proj_teamsync_001', 'req_dm_003', 'feat_dm_003', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '84 days', NOW() - INTERVAL '19 days'),
('link_dm_103', 'proj_teamsync_001', 'req_dm_004', 'feat_dm_004', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '82 days', NOW() - INTERVAL '17 days'),
('link_dm_104', 'proj_teamsync_001', 'req_dm_005', 'feat_dm_005', 'implements', '{"status": "complete"}', NOW() - INTERVAL '80 days', NOW() - INTERVAL '15 days'),

-- DIRECT MESSAGES EPIC: Features -> API Endpoints (traces_to)
('link_dm_120', 'proj_teamsync_001', 'feat_dm_001', 'api_dm_001', 'traces_to', '{"endpoint_status": "live"}', NOW() - INTERVAL '83 days', NOW() - INTERVAL '18 days'),
('link_dm_121', 'proj_teamsync_001', 'feat_dm_002', 'api_dm_002', 'traces_to', '{"endpoint_status": "live"}', NOW() - INTERVAL '81 days', NOW() - INTERVAL '16 days'),
('link_dm_122', 'proj_teamsync_001', 'feat_dm_003', 'api_dm_003', 'traces_to', '{"endpoint_status": "beta"}', NOW() - INTERVAL '79 days', NOW() - INTERVAL '14 days'),
('link_dm_123', 'proj_teamsync_001', 'feat_dm_004', 'api_dm_004', 'traces_to', '{"endpoint_status": "beta"}', NOW() - INTERVAL '77 days', NOW() - INTERVAL '12 days'),

-- FILE SHARING EPIC: Requirements -> Features (implements)
('link_file_100', 'proj_teamsync_001', 'req_file_001', 'feat_file_001', 'implements', '{"status": "complete"}', NOW() - INTERVAL '80 days', NOW() - INTERVAL '15 days'),
('link_file_101', 'proj_teamsync_001', 'req_file_002', 'feat_file_002', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '78 days', NOW() - INTERVAL '13 days'),
('link_file_102', 'proj_teamsync_001', 'req_file_003', 'feat_file_003', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '76 days', NOW() - INTERVAL '11 days'),
('link_file_103', 'proj_teamsync_001', 'req_file_004', 'feat_file_004', 'implements', '{"status": "complete"}', NOW() - INTERVAL '74 days', NOW() - INTERVAL '9 days'),
('link_file_104', 'proj_teamsync_001', 'req_file_005', 'feat_file_005', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '72 days', NOW() - INTERVAL '7 days'),

-- FILE SHARING EPIC: Features -> API Endpoints (traces_to)
('link_file_120', 'proj_teamsync_001', 'feat_file_001', 'api_file_001', 'traces_to', '{"endpoint_status": "live"}', NOW() - INTERVAL '75 days', NOW() - INTERVAL '10 days'),
('link_file_121', 'proj_teamsync_001', 'feat_file_002', 'api_file_002', 'traces_to', '{"endpoint_status": "beta"}', NOW() - INTERVAL '73 days', NOW() - INTERVAL '8 days'),
('link_file_122', 'proj_teamsync_001', 'feat_file_003', 'api_file_003', 'traces_to', '{"endpoint_status": "beta"}', NOW() - INTERVAL '71 days', NOW() - INTERVAL '6 days'),
('link_file_123', 'proj_teamsync_001', 'feat_file_004', 'api_file_004', 'traces_to', '{"endpoint_status": "live"}', NOW() - INTERVAL '69 days', NOW() - INTERVAL '4 days'),

-- MENTIONS EPIC: Requirements -> Features (implements)
('link_mention_100', 'proj_teamsync_001', 'req_mention_001', 'feat_mention_001', 'implements', '{"status": "complete"}', NOW() - INTERVAL '75 days', NOW() - INTERVAL '10 days'),
('link_mention_101', 'proj_teamsync_001', 'req_mention_002', 'feat_mention_002', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '73 days', NOW() - INTERVAL '8 days'),
('link_mention_102', 'proj_teamsync_001', 'req_mention_003', 'feat_mention_003', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '71 days', NOW() - INTERVAL '6 days'),
('link_mention_103', 'proj_teamsync_001', 'req_mention_004', 'feat_mention_004', 'implements', '{"status": "complete"}', NOW() - INTERVAL '69 days', NOW() - INTERVAL '4 days'),

-- THREADS EPIC: Requirements -> Features (implements)
('link_thread_100', 'proj_teamsync_001', 'req_thread_001', 'feat_thread_001', 'implements', '{"status": "complete"}', NOW() - INTERVAL '77 days', NOW() - INTERVAL '12 days'),
('link_thread_101', 'proj_teamsync_001', 'req_thread_002', 'feat_thread_002', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '75 days', NOW() - INTERVAL '10 days'),
('link_thread_102', 'proj_teamsync_001', 'req_thread_003', 'feat_thread_003', 'implements', '{"status": "complete"}', NOW() - INTERVAL '73 days', NOW() - INTERVAL '8 days'),

-- THREADS EPIC: Features -> API Endpoints (traces_to)
('link_thread_120', 'proj_teamsync_001', 'feat_thread_001', 'api_thread_001', 'traces_to', '{"endpoint_status": "live"}', NOW() - INTERVAL '72 days', NOW() - INTERVAL '7 days'),
('link_thread_121', 'proj_teamsync_001', 'feat_thread_002', 'api_thread_002', 'traces_to', '{"endpoint_status": "beta"}', NOW() - INTERVAL '70 days', NOW() - INTERVAL '5 days'),
('link_thread_122', 'proj_teamsync_001', 'feat_thread_003', 'api_thread_003', 'traces_to', '{"endpoint_status": "live"}', NOW() - INTERVAL '68 days', NOW() - INTERVAL '3 days'),

-- SEARCH EPIC: Requirements -> Features (implements)
('link_search_100', 'proj_teamsync_001', 'req_search_001', 'feat_search_001', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '72 days', NOW() - INTERVAL '7 days'),
('link_search_101', 'proj_teamsync_001', 'req_search_002', 'feat_search_002', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '70 days', NOW() - INTERVAL '5 days'),
('link_search_102', 'proj_teamsync_001', 'req_search_003', 'feat_search_003', 'implements', '{"status": "complete"}', NOW() - INTERVAL '68 days', NOW() - INTERVAL '3 days'),

-- ACCESS CONTROL & ADMIN: Requirements -> Features (implements)
('link_access_100', 'proj_teamsync_001', 'req_access_001', 'feat_access_001', 'implements', '{"status": "complete"}', NOW() - INTERVAL '70 days', NOW() - INTERVAL '5 days'),
('link_access_101', 'proj_teamsync_001', 'req_access_002', 'feat_access_002', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '68 days', NOW() - INTERVAL '3 days'),

-- ADMIN FEATURES: Requirements -> Features (implements)
('link_admin_100', 'proj_teamsync_001', 'req_admin_001', 'feat_admin_001', 'implements', '{"status": "complete"}', NOW() - INTERVAL '68 days', NOW() - INTERVAL '3 days'),
('link_admin_101', 'proj_teamsync_001', 'req_admin_002', 'feat_admin_002', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '66 days', NOW() - INTERVAL '1 days'),
('link_admin_102', 'proj_teamsync_001', 'req_admin_003', 'feat_admin_003', 'implements', '{"status": "complete"}', NOW() - INTERVAL '64 days', NOW() - INTERVAL '-1 days'),
('link_admin_103', 'proj_teamsync_001', 'req_admin_004', 'feat_admin_004', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '62 days', NOW() - INTERVAL '-3 days'),

-- ANALYTICS: Requirements -> Features (implements)
('link_analytics_100', 'proj_teamsync_001', 'req_analytics_001', 'feat_analytics_001', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '65 days', NOW() - INTERVAL '0 days'),
('link_analytics_101', 'proj_teamsync_001', 'req_analytics_002', 'feat_analytics_002', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '63 days', NOW() - INTERVAL '-2 days'),
('link_analytics_102', 'proj_teamsync_001', 'req_analytics_003', 'feat_analytics_003', 'implements', '{"status": "complete"}', NOW() - INTERVAL '61 days', NOW() - INTERVAL '-4 days'),

-- API REQUIREMENTS -> FEATURES: Implementation mapping
('link_api_100', 'proj_teamsync_001', 'req_api_001', 'feat_api_001', 'implements', '{"status": "complete"}', NOW() - INTERVAL '62 days', NOW() - INTERVAL '-2 days'),
('link_api_101', 'proj_teamsync_001', 'req_api_002', 'feat_api_002', 'implements', '{"status": "complete"}', NOW() - INTERVAL '60 days', NOW() - INTERVAL '-4 days'),
('link_api_102', 'proj_teamsync_001', 'req_api_003', 'feat_api_003', 'implements', '{"status": "in_progress"}', NOW() - INTERVAL '58 days', NOW() - INTERVAL '-6 days'),

-- PERFORMANCE REQUIREMENTS -> FEATURES
('link_perf_100', 'proj_teamsync_001', 'req_performance_001', 'feat_msg_002', 'depends_on', '{"reason": "caching"}', NOW() - INTERVAL '85 days', NOW() - INTERVAL '20 days'),
('link_perf_101', 'proj_teamsync_001', 'req_performance_002', 'feat_chan_001', 'depends_on', '{"reason": "indexing"}', NOW() - INTERVAL '83 days', NOW() - INTERVAL '18 days'),
('link_perf_102', 'proj_teamsync_001', 'req_performance_003', 'feat_search_001', 'depends_on', '{"reason": "optimization"}', NOW() - INTERVAL '81 days', NOW() - INTERVAL '16 days'),

-- FEATURE DEPENDENCIES (inter-feature relationships)
('link_feat_dep_001', 'proj_teamsync_001', 'feat_msg_005', 'feat_msg_001', 'depends_on', '{"reason": "requires base message"}', NOW() - INTERVAL '80 days', NOW() - INTERVAL '15 days'),
('link_feat_dep_002', 'proj_teamsync_001', 'feat_msg_007', 'feat_msg_001', 'depends_on', '{"reason": "requires message storage"}', NOW() - INTERVAL '79 days', NOW() - INTERVAL '14 days'),
('link_feat_dep_003', 'proj_teamsync_001', 'feat_msg_004', 'feat_msg_003', 'depends_on', '{"reason": "indexes messages"}', NOW() - INTERVAL '79 days', NOW() - INTERVAL '14 days'),
('link_feat_dep_004', 'proj_teamsync_001', 'feat_msg_008', 'feat_msg_001', 'depends_on', '{"reason": "message context"}', NOW() - INTERVAL '77 days', NOW() - INTERVAL '12 days'),
('link_feat_dep_005', 'proj_teamsync_001', 'feat_msg_012', 'feat_msg_001', 'depends_on', '{"reason": "message tracking"}', NOW() - INTERVAL '75 days', NOW() - INTERVAL '10 days'),
('link_feat_dep_006', 'proj_teamsync_001', 'feat_dm_002', 'feat_dm_001', 'depends_on', '{"reason": "requires DM setup"}', NOW() - INTERVAL '75 days', NOW() - INTERVAL '10 days'),
('link_feat_dep_007', 'proj_teamsync_001', 'feat_chan_003', 'feat_chan_001', 'depends_on', '{"reason": "channel management"}', NOW() - INTERVAL '73 days', NOW() - INTERVAL '8 days'),
('link_feat_dep_008', 'proj_teamsync_001', 'feat_file_002', 'feat_file_001', 'depends_on', '{"reason": "file upload base"}', NOW() - INTERVAL '71 days', NOW() - INTERVAL '6 days'),

-- TASK TO TASK DEPENDENCIES
('link_task_dep_001', 'proj_teamsync_001', 'task_msg_004', 'task_msg_001', 'depends_on', '{}', NOW() - INTERVAL '75 days', NOW() - INTERVAL '10 days'),
('link_task_dep_002', 'proj_teamsync_001', 'task_msg_005', 'task_msg_001', 'depends_on', '{}', NOW() - INTERVAL '74 days', NOW() - INTERVAL '9 days'),
('link_task_dep_003', 'proj_teamsync_001', 'task_msg_006', 'task_msg_002', 'depends_on', '{}', NOW() - INTERVAL '73 days', NOW() - INTERVAL '8 days'),
('link_task_dep_004', 'proj_teamsync_001', 'task_msg_008', 'task_msg_002', 'depends_on', '{}', NOW() - INTERVAL '71 days', NOW() - INTERVAL '6 days'),
('link_task_dep_005', 'proj_teamsync_001', 'task_msg_010', 'task_msg_006', 'depends_on', '{}', NOW() - INTERVAL '69 days', NOW() - INTERVAL '4 days'),

-- REQUIREMENT TO REQUIREMENT RELATIONSHIPS (related_to)
('link_req_rel_001', 'proj_teamsync_001', 'req_msg_001', 'req_msg_006', 'related_to', '{}', NOW() - INTERVAL '85 days', NOW() - INTERVAL '20 days'),
('link_req_rel_002', 'proj_teamsync_001', 'req_msg_002', 'req_msg_003', 'related_to', '{}', NOW() - INTERVAL '83 days', NOW() - INTERVAL '18 days'),
('link_req_rel_003', 'proj_teamsync_001', 'req_msg_003', 'req_msg_004', 'related_to', '{}', NOW() - INTERVAL '81 days', NOW() - INTERVAL '16 days'),
('link_req_rel_004', 'proj_teamsync_001', 'req_msg_005', 'req_msg_007', 'related_to', '{}', NOW() - INTERVAL '79 days', NOW() - INTERVAL '14 days'),
('link_req_rel_005', 'proj_teamsync_001', 'req_chan_001', 'req_chan_002', 'related_to', '{}', NOW() - INTERVAL '77 days', NOW() - INTERVAL '12 days'),
('link_req_rel_006', 'proj_teamsync_001', 'req_chan_003', 'req_chan_004', 'related_to', '{}', NOW() - INTERVAL '75 days', NOW() - INTERVAL '10 days'),
('link_req_rel_007', 'proj_teamsync_001', 'req_dm_001', 'req_msg_001', 'related_to', '{}', NOW() - INTERVAL '73 days', NOW() - INTERVAL '8 days'),
('link_req_rel_008', 'proj_teamsync_001', 'req_file_001', 'req_msg_001', 'related_to', '{}', NOW() - INTERVAL '71 days', NOW() - INTERVAL '6 days'),
('link_req_rel_009', 'proj_teamsync_001', 'req_mention_001', 'req_msg_001', 'related_to', '{}', NOW() - INTERVAL '69 days', NOW() - INTERVAL '4 days'),
('link_req_rel_010', 'proj_teamsync_001', 'req_thread_001', 'req_msg_001', 'related_to', '{}', NOW() - INTERVAL '67 days', NOW() - INTERVAL '2 days'),
('link_req_rel_011', 'proj_teamsync_001', 'req_search_001', 'req_msg_002', 'related_to', '{}', NOW() - INTERVAL '65 days', NOW() - INTERVAL '0 days'),
('link_req_rel_012', 'proj_teamsync_001', 'req_access_001', 'req_admin_001', 'related_to', '{}', NOW() - INTERVAL '63 days', NOW() - INTERVAL '-2 days'),

-- UI COMPONENTS TO FEATURES
('link_ui_100', 'proj_teamsync_001', 'ui_message_bubble', 'feat_msg_001', 'related_to', '{}', NOW() - INTERVAL '80 days', NOW() - INTERVAL '15 days'),
('link_ui_101', 'proj_teamsync_001', 'ui_message_input', 'feat_msg_001', 'related_to', '{}', NOW() - INTERVAL '78 days', NOW() - INTERVAL '13 days'),
('link_ui_102', 'proj_teamsync_001', 'ui_emoji_picker', 'feat_msg_009', 'related_to', '{}', NOW() - INTERVAL '76 days', NOW() - INTERVAL '11 days'),
('link_ui_103', 'proj_teamsync_001', 'ui_search_bar', 'feat_search_001', 'related_to', '{}', NOW() - INTERVAL '74 days', NOW() - INTERVAL '9 days'),
('link_ui_104', 'proj_teamsync_001', 'ui_reaction_selector', 'feat_msg_010', 'related_to', '{}', NOW() - INTERVAL '72 days', NOW() - INTERVAL '7 days'),
('link_ui_105', 'proj_teamsync_001', 'ui_typing_indicator', 'feat_msg_011', 'related_to', '{}', NOW() - INTERVAL '70 days', NOW() - INTERVAL '5 days'),

-- DATABASE SCHEMA TO FEATURES
('link_schema_100', 'proj_teamsync_001', 'schema_messages', 'feat_msg_001', 'related_to', '{}', NOW() - INTERVAL '75 days', NOW() - INTERVAL '10 days'),
('link_schema_101', 'proj_teamsync_001', 'schema_message_versions', 'feat_msg_005', 'related_to', '{}', NOW() - INTERVAL '73 days', NOW() - INTERVAL '8 days'),
('link_schema_102', 'proj_teamsync_001', 'schema_read_receipts', 'feat_msg_012', 'related_to', '{}', NOW() - INTERVAL '71 days', NOW() - INTERVAL '6 days'),
('link_schema_103', 'proj_teamsync_001', 'schema_reactions', 'feat_msg_010', 'related_to', '{}', NOW() - INTERVAL '69 days', NOW() - INTERVAL '4 days'),

-- CROSS-EPIC DEPENDENCIES: Channels depends on base messaging
('link_cross_100', 'proj_teamsync_001', 'feat_chan_001', 'feat_msg_001', 'depends_on', '{"reason": "messaging core"}', NOW() - INTERVAL '80 days', NOW() - INTERVAL '15 days'),

-- CROSS-EPIC DEPENDENCIES: DMs depend on messaging
('link_cross_101', 'proj_teamsync_001', 'feat_dm_001', 'feat_msg_001', 'depends_on', '{"reason": "messaging core"}', NOW() - INTERVAL '78 days', NOW() - INTERVAL '13 days'),

-- CROSS-EPIC DEPENDENCIES: Threads depend on channels
('link_cross_102', 'proj_teamsync_001', 'feat_thread_001', 'feat_chan_001', 'depends_on', '{"reason": "channel support"}', NOW() - INTERVAL '76 days', NOW() - INTERVAL '11 days'),

-- CROSS-EPIC DEPENDENCIES: Search depends on storage
('link_cross_103', 'proj_teamsync_001', 'feat_search_001', 'feat_msg_003', 'depends_on', '{"reason": "storage indexing"}', NOW() - INTERVAL '74 days', NOW() - INTERVAL '9 days'),

-- BLOCKING RELATIONSHIPS
('link_block_001', 'proj_teamsync_001', 'feat_msg_008', 'feat_msg_001', 'blocks', '{}', NOW() - INTERVAL '70 days', NOW() - INTERVAL '5 days'),
('link_block_002', 'proj_teamsync_001', 'task_msg_001', 'task_msg_002', 'blocks', '{}', NOW() - INTERVAL '68 days', NOW() - INTERVAL '3 days'),

-- ADDITIONAL STORY TO FEATURE MAPPINGS
('link_story_feat_001', 'proj_teamsync_001', 'story_msg_001', 'feat_msg_001', 'related_to', '{}', NOW() - INTERVAL '75 days', NOW() - INTERVAL '10 days'),
('link_story_feat_002', 'proj_teamsync_001', 'story_msg_002', 'feat_msg_002', 'related_to', '{}', NOW() - INTERVAL '73 days', NOW() - INTERVAL '8 days'),
('link_story_feat_003', 'proj_teamsync_001', 'story_msg_003', 'feat_msg_007', 'related_to', '{}', NOW() - INTERVAL '71 days', NOW() - INTERVAL '6 days'),
('link_story_feat_004', 'proj_teamsync_001', 'story_msg_004', 'feat_msg_009', 'related_to', '{}', NOW() - INTERVAL '69 days', NOW() - INTERVAL '4 days'),
('link_story_feat_005', 'proj_teamsync_001', 'story_msg_005', 'feat_msg_012', 'related_to', '{}', NOW() - INTERVAL '67 days', NOW() - INTERVAL '2 days'),
('link_story_feat_006', 'proj_teamsync_001', 'story_msg_006', 'feat_msg_004', 'related_to', '{}', NOW() - INTERVAL '65 days', NOW() - INTERVAL '0 days'),
('link_story_feat_007', 'proj_teamsync_001', 'story_msg_007', 'feat_msg_005', 'related_to', '{}', NOW() - INTERVAL '63 days', NOW() - INTERVAL '-2 days'),
('link_story_feat_008', 'proj_teamsync_001', 'story_msg_008', 'feat_msg_006', 'related_to', '{}', NOW() - INTERVAL '61 days', NOW() - INTERVAL '-4 days'),

-- ADDITIONAL TEST MAPPINGS
('link_test_001', 'proj_teamsync_001', 'test_msg_001', 'feat_msg_001', 'tests', '{}', NOW() - INTERVAL '75 days', NOW() - INTERVAL '10 days'),
('link_test_002', 'proj_teamsync_001', 'test_msg_002', 'feat_msg_001', 'tests', '{}', NOW() - INTERVAL '73 days', NOW() - INTERVAL '8 days'),
('link_test_003', 'proj_teamsync_001', 'test_msg_003', 'feat_msg_001', 'tests', '{}', NOW() - INTERVAL '71 days', NOW() - INTERVAL '6 days'),
('link_test_004', 'proj_teamsync_001', 'test_msg_004', 'feat_msg_007', 'tests', '{}', NOW() - INTERVAL '69 days', NOW() - INTERVAL '4 days'),
('link_test_005', 'proj_teamsync_001', 'test_msg_005', 'feat_msg_010', 'tests', '{}', NOW() - INTERVAL '67 days', NOW() - INTERVAL '2 days'),
('link_test_006', 'proj_teamsync_001', 'test_msg_006', 'feat_msg_005', 'tests', '{}', NOW() - INTERVAL '65 days', NOW() - INTERVAL '0 days'),
('link_test_007', 'proj_teamsync_001', 'test_msg_007', 'feat_msg_004', 'tests', '{}', NOW() - INTERVAL '63 days', NOW() - INTERVAL '-2 days'),
('link_test_008', 'proj_teamsync_001', 'test_msg_008', 'feat_msg_006', 'tests', '{}', NOW() - INTERVAL '61 days', NOW() - INTERVAL '-4 days'),
('link_test_009', 'proj_teamsync_001', 'test_msg_009', 'feat_msg_012', 'tests', '{}', NOW() - INTERVAL '59 days', NOW() - INTERVAL '-6 days'),
('link_test_010', 'proj_teamsync_001', 'test_msg_010', 'feat_msg_011', 'tests', '{}', NOW() - INTERVAL '57 days', NOW() - INTERVAL '-8 days'),

-- ADDITIONAL CHANNEL STORY MAPPINGS
('link_chan_story_001', 'proj_teamsync_001', 'story_chan_001', 'feat_chan_001', 'related_to', '{}', NOW() - INTERVAL '75 days', NOW() - INTERVAL '10 days'),
('link_chan_story_002', 'proj_teamsync_001', 'story_chan_002', 'feat_chan_002', 'related_to', '{}', NOW() - INTERVAL '73 days', NOW() - INTERVAL '8 days'),
('link_chan_story_003', 'proj_teamsync_001', 'story_chan_003', 'feat_chan_003', 'related_to', '{}', NOW() - INTERVAL '71 days', NOW() - INTERVAL '6 days'),
('link_chan_story_004', 'proj_teamsync_001', 'story_chan_004', 'feat_chan_004', 'related_to', '{}', NOW() - INTERVAL '69 days', NOW() - INTERVAL '4 days'),

-- ADDITIONAL DM STORY MAPPINGS
('link_dm_story_001', 'proj_teamsync_001', 'story_dm_001', 'feat_dm_001', 'related_to', '{}', NOW() - INTERVAL '77 days', NOW() - INTERVAL '12 days'),
('link_dm_story_002', 'proj_teamsync_001', 'story_dm_002', 'feat_dm_002', 'related_to', '{}', NOW() - INTERVAL '75 days', NOW() - INTERVAL '10 days'),
('link_dm_story_003', 'proj_teamsync_001', 'story_dm_003', 'feat_dm_003', 'related_to', '{}', NOW() - INTERVAL '73 days', NOW() - INTERVAL '8 days'),

-- ADDITIONAL FILE STORY MAPPINGS
('link_file_story_001', 'proj_teamsync_001', 'story_file_001', 'feat_file_001', 'related_to', '{}', NOW() - INTERVAL '72 days', NOW() - INTERVAL '7 days'),
('link_file_story_002', 'proj_teamsync_001', 'story_file_002', 'feat_file_002', 'related_to', '{}', NOW() - INTERVAL '70 days', NOW() - INTERVAL '5 days'),
('link_file_story_003', 'proj_teamsync_001', 'story_file_003', 'feat_file_003', 'related_to', '{}', NOW() - INTERVAL '68 days', NOW() - INTERVAL '3 days'),

-- CHANNEL TASK MAPPINGS
('link_chan_task_001', 'proj_teamsync_001', 'task_chan_001', 'feat_chan_001', 'depends_on', '{}', NOW() - INTERVAL '70 days', NOW() - INTERVAL '5 days'),
('link_chan_task_002', 'proj_teamsync_001', 'task_chan_002', 'feat_chan_002', 'depends_on', '{}', NOW() - INTERVAL '68 days', NOW() - INTERVAL '3 days'),
('link_chan_task_003', 'proj_teamsync_001', 'task_chan_003', 'feat_chan_003', 'depends_on', '{}', NOW() - INTERVAL '66 days', NOW() - INTERVAL '1 days'),

-- FILE SHARING TASK MAPPINGS
('link_file_task_001', 'proj_teamsync_001', 'task_file_001', 'feat_file_001', 'depends_on', '{}', NOW() - INTERVAL '68 days', NOW() - INTERVAL '3 days'),
('link_file_task_002', 'proj_teamsync_001', 'task_file_002', 'feat_file_002', 'depends_on', '{}', NOW() - INTERVAL '66 days', NOW() - INTERVAL '1 days'),
('link_file_task_003', 'proj_teamsync_001', 'task_file_003', 'feat_file_003', 'depends_on', '{}', NOW() - INTERVAL '64 days', NOW() - INTERVAL '-1 days'),

-- MENTION FEATURE TO TEST MAPPINGS
('link_mention_test_001', 'proj_teamsync_001', 'test_mention_001', 'feat_mention_001', 'tests', '{}', NOW() - INTERVAL '70 days', NOW() - INTERVAL '5 days'),
('link_mention_test_002', 'proj_teamsync_001', 'test_mention_002', 'feat_mention_002', 'tests', '{}', NOW() - INTERVAL '68 days', NOW() - INTERVAL '3 days'),

-- THREAD STORY MAPPINGS
('link_thread_story_001', 'proj_teamsync_001', 'story_thread_001', 'feat_thread_001', 'related_to', '{}', NOW() - INTERVAL '72 days', NOW() - INTERVAL '7 days'),
('link_thread_story_002', 'proj_teamsync_001', 'story_thread_002', 'feat_thread_002', 'related_to', '{}', NOW() - INTERVAL '70 days', NOW() - INTERVAL '5 days'),

-- ADDITIONAL API ENDPOINT CROSS-REFERENCES
('link_api_ref_100', 'proj_teamsync_001', 'api_chan_001', 'feat_chan_001', 'implements', '{}', NOW() - INTERVAL '72 days', NOW() - INTERVAL '7 days'),
('link_api_ref_101', 'proj_teamsync_001', 'api_dm_001', 'feat_dm_001', 'implements', '{}', NOW() - INTERVAL '70 days', NOW() - INTERVAL '5 days'),
('link_api_ref_102', 'proj_teamsync_001', 'api_file_001', 'feat_file_001', 'implements', '{}', NOW() - INTERVAL '68 days', NOW() - INTERVAL '3 days'),
('link_api_ref_103', 'proj_teamsync_001', 'api_thread_001', 'feat_thread_001', 'implements', '{}', NOW() - INTERVAL '66 days', NOW() - INTERVAL '1 days'),

-- REQUIREMENT TO API ENDPOINT MAPPINGS
('link_req_api_001', 'proj_teamsync_001', 'req_msg_001', 'api_msg_001', 'traces_to', '{}', NOW() - INTERVAL '70 days', NOW() - INTERVAL '5 days'),
('link_req_api_002', 'proj_teamsync_001', 'req_msg_001', 'api_msg_002', 'traces_to', '{}', NOW() - INTERVAL '68 days', NOW() - INTERVAL '3 days'),
('link_req_api_003', 'proj_teamsync_001', 'req_msg_002', 'api_msg_006', 'traces_to', '{}', NOW() - INTERVAL '66 days', NOW() - INTERVAL '1 days'),
('link_req_api_004', 'proj_teamsync_001', 'req_msg_003', 'api_msg_003', 'traces_to', '{}', NOW() - INTERVAL '64 days', NOW() - INTERVAL '-1 days'),
('link_req_api_005', 'proj_teamsync_001', 'req_msg_003', 'api_msg_004', 'traces_to', '{}', NOW() - INTERVAL '62 days', NOW() - INTERVAL '-3 days'),
('link_req_api_006', 'proj_teamsync_001', 'req_msg_005', 'api_msg_005', 'traces_to', '{}', NOW() - INTERVAL '60 days', NOW() - INTERVAL '-5 days'),
('link_req_api_007', 'proj_teamsync_001', 'req_msg_007', 'api_msg_007', 'traces_to', '{}', NOW() - INTERVAL '58 days', NOW() - INTERVAL '-7 days'),
('link_req_api_008', 'proj_teamsync_001', 'req_chan_001', 'api_chan_001', 'traces_to', '{}', NOW() - INTERVAL '68 days', NOW() - INTERVAL '3 days'),
('link_req_api_009', 'proj_teamsync_001', 'req_dm_001', 'api_dm_001', 'traces_to', '{}', NOW() - INTERVAL '66 days', NOW() - INTERVAL '1 days'),
('link_req_api_010', 'proj_teamsync_001', 'req_file_001', 'api_file_001', 'traces_to', '{}', NOW() - INTERVAL '64 days', NOW() - INTERVAL '-1 days'),
('link_req_api_011', 'proj_teamsync_001', 'req_thread_001', 'api_thread_001', 'traces_to', '{}', NOW() - INTERVAL '62 days', NOW() - INTERVAL '-3 days'),

-- ADDITIONAL REQUIREMENT RELATIONSHIPS
('link_req_rel_013', 'proj_teamsync_001', 'req_msg_006', 'req_msg_007', 'related_to', '{}', NOW() - INTERVAL '75 days', NOW() - INTERVAL '10 days'),
('link_req_rel_014', 'proj_teamsync_001', 'req_chan_005', 'req_chan_006', 'related_to', '{}', NOW() - INTERVAL '73 days', NOW() - INTERVAL '8 days'),
('link_req_rel_015', 'proj_teamsync_001', 'req_dm_002', 'req_dm_003', 'related_to', '{}', NOW() - INTERVAL '71 days', NOW() - INTERVAL '6 days'),
('link_req_rel_016', 'proj_teamsync_001', 'req_file_002', 'req_file_003', 'related_to', '{}', NOW() - INTERVAL '69 days', NOW() - INTERVAL '4 days'),
('link_req_rel_017', 'proj_teamsync_001', 'req_performance_001', 'req_msg_001', 'related_to', '{}', NOW() - INTERVAL '67 days', NOW() - INTERVAL '2 days'),
('link_req_rel_018', 'proj_teamsync_001', 'req_performance_002', 'req_search_001', 'related_to', '{}', NOW() - INTERVAL '65 days', NOW() - INTERVAL '0 days'),

-- FEATURE TO FEATURE TRACEABILITY
('link_feat_trace_001', 'proj_teamsync_001', 'feat_msg_002', 'feat_msg_003', 'depends_on', '{}', NOW() - INTERVAL '77 days', NOW() - INTERVAL '12 days'),
('link_feat_trace_002', 'proj_teamsync_001', 'feat_msg_010', 'feat_msg_001', 'depends_on', '{}', NOW() - INTERVAL '75 days', NOW() - INTERVAL '10 days'),
('link_feat_trace_003', 'proj_teamsync_001', 'feat_msg_009', 'feat_msg_001', 'depends_on', '{}', NOW() - INTERVAL '73 days', NOW() - INTERVAL '8 days'),
('link_feat_trace_004', 'proj_teamsync_001', 'feat_dm_003', 'feat_msg_001', 'depends_on', '{}', NOW() - INTERVAL '71 days', NOW() - INTERVAL '6 days'),
('link_feat_trace_005', 'proj_teamsync_001', 'feat_file_001', 'feat_msg_001', 'depends_on', '{}', NOW() - INTERVAL '69 days', NOW() - INTERVAL '4 days'),

-- ADDITIONAL STORY TO STORY RELATIONSHIPS
('link_story_rel_001', 'proj_teamsync_001', 'story_msg_002', 'story_msg_001', 'related_to', '{}', NOW() - INTERVAL '72 days', NOW() - INTERVAL '7 days'),
('link_story_rel_002', 'proj_teamsync_001', 'story_msg_003', 'story_msg_001', 'related_to', '{}', NOW() - INTERVAL '70 days', NOW() - INTERVAL '5 days'),
('link_story_rel_003', 'proj_teamsync_001', 'story_msg_004', 'story_msg_003', 'related_to', '{}', NOW() - INTERVAL '68 days', NOW() - INTERVAL '3 days'),
('link_story_rel_004', 'proj_teamsync_001', 'story_msg_005', 'story_msg_001', 'related_to', '{}', NOW() - INTERVAL '66 days', NOW() - INTERVAL '1 days'),
('link_story_rel_005', 'proj_teamsync_001', 'story_msg_006', 'story_msg_002', 'related_to', '{}', NOW() - INTERVAL '64 days', NOW() - INTERVAL '-1 days'),

-- TASK TO FEATURE DIRECT MAPPINGS
('link_task_feat_001', 'proj_teamsync_001', 'task_msg_001', 'feat_msg_001', 'implements', '{}', NOW() - INTERVAL '75 days', NOW() - INTERVAL '10 days'),
('link_task_feat_002', 'proj_teamsync_001', 'task_msg_002', 'feat_msg_002', 'implements', '{}', NOW() - INTERVAL '73 days', NOW() - INTERVAL '8 days'),
('link_task_feat_003', 'proj_teamsync_001', 'task_msg_003', 'feat_msg_005', 'implements', '{}', NOW() - INTERVAL '71 days', NOW() - INTERVAL '6 days'),
('link_task_feat_004', 'proj_teamsync_001', 'task_msg_004', 'feat_msg_007', 'implements', '{}', NOW() - INTERVAL '69 days', NOW() - INTERVAL '4 days'),
('link_task_feat_005', 'proj_teamsync_001', 'task_msg_005', 'feat_msg_008', 'implements', '{}', NOW() - INTERVAL '67 days', NOW() - INTERVAL '2 days'),
('link_task_feat_006', 'proj_teamsync_001', 'task_msg_006', 'feat_msg_010', 'implements', '{}', NOW() - INTERVAL '65 days', NOW() - INTERVAL '0 days'),
('link_task_feat_007', 'proj_teamsync_001', 'task_msg_007', 'feat_msg_011', 'implements', '{}', NOW() - INTERVAL '63 days', NOW() - INTERVAL '-2 days'),
('link_task_feat_008', 'proj_teamsync_001', 'task_msg_008', 'feat_msg_012', 'implements', '{}', NOW() - INTERVAL '61 days', NOW() - INTERVAL '-4 days'),
('link_task_feat_009', 'proj_teamsync_001', 'task_msg_009', 'feat_msg_014', 'implements', '{}', NOW() - INTERVAL '59 days', NOW() - INTERVAL '-6 days'),
('link_task_feat_010', 'proj_teamsync_001', 'task_msg_010', 'feat_msg_015', 'implements', '{}', NOW() - INTERVAL '57 days', NOW() - INTERVAL '-8 days'),

-- DATABASE SCHEMA DEPENDENCIES
('link_schema_dep_001', 'proj_teamsync_001', 'schema_messages', 'feat_msg_003', 'related_to', '{}', NOW() - INTERVAL '72 days', NOW() - INTERVAL '7 days'),
('link_schema_dep_002', 'proj_teamsync_001', 'schema_reactions', 'feat_msg_009', 'related_to', '{}', NOW() - INTERVAL '70 days', NOW() - INTERVAL '5 days'),
('link_schema_dep_003', 'proj_teamsync_001', 'schema_read_receipts', 'feat_msg_007', 'related_to', '{}', NOW() - INTERVAL '68 days', NOW() - INTERVAL '3 days'),
('link_schema_dep_004', 'proj_teamsync_001', 'schema_message_versions', 'feat_msg_003', 'related_to', '{}', NOW() - INTERVAL '66 days', NOW() - INTERVAL '1 days'),

-- UI COMPONENT DEPENDENCIES
('link_ui_dep_001', 'proj_teamsync_001', 'ui_message_bubble', 'ui_message_input', 'related_to', '{}', NOW() - INTERVAL '72 days', NOW() - INTERVAL '7 days'),
('link_ui_dep_002', 'proj_teamsync_001', 'ui_emoji_picker', 'ui_message_input', 'depends_on', '{}', NOW() - INTERVAL '70 days', NOW() - INTERVAL '5 days'),
('link_ui_dep_003', 'proj_teamsync_001', 'ui_typing_indicator', 'ui_message_input', 'related_to', '{}', NOW() - INTERVAL '68 days', NOW() - INTERVAL '3 days'),
('link_ui_dep_004', 'proj_teamsync_001', 'ui_reaction_selector', 'ui_message_bubble', 'depends_on', '{}', NOW() - INTERVAL '66 days', NOW() - INTERVAL '1 days'),
('link_ui_dep_005', 'proj_teamsync_001', 'ui_search_bar', 'ui_message_bubble', 'related_to', '{}', NOW() - INTERVAL '64 days', NOW() - INTERVAL '-1 days'),

-- FINAL BATCH: COMPREHENSIVE CROSS-LINKING
('link_final_001', 'proj_teamsync_001', 'feat_msg_014', 'task_msg_009', 'implements', '{}', NOW() - INTERVAL '70 days', NOW() - INTERVAL '5 days'),
('link_final_002', 'proj_teamsync_001', 'feat_msg_015', 'task_msg_010', 'implements', '{}', NOW() - INTERVAL '68 days', NOW() - INTERVAL '3 days'),
('link_final_003', 'proj_teamsync_001', 'req_access_001', 'feat_access_001', 'implements', '{}', NOW() - INTERVAL '66 days', NOW() - INTERVAL '1 days'),
('link_final_004', 'proj_teamsync_001', 'req_access_002', 'feat_access_002', 'implements', '{}', NOW() - INTERVAL '64 days', NOW() - INTERVAL '-1 days'),
('link_final_005', 'proj_teamsync_001', 'feat_access_001', 'api_chan_006', 'traces_to', '{}', NOW() - INTERVAL '62 days', NOW() - INTERVAL '-3 days'),
('link_final_006', 'proj_teamsync_001', 'feat_access_002', 'api_chan_007', 'traces_to', '{}', NOW() - INTERVAL '60 days', NOW() - INTERVAL '-5 days'),
('link_final_007', 'proj_teamsync_001', 'feat_admin_001', 'api_chan_008', 'implements', '{}', NOW() - INTERVAL '58 days', NOW() - INTERVAL '-7 days'),
('link_final_008', 'proj_teamsync_001', 'feat_admin_002', 'api_chan_009', 'implements', '{}', NOW() - INTERVAL '56 days', NOW() - INTERVAL '-9 days'),
('link_final_009', 'proj_teamsync_001', 'req_admin_001', 'feat_admin_001', 'implements', '{}', NOW() - INTERVAL '68 days', NOW() - INTERVAL '3 days'),
('link_final_010', 'proj_teamsync_001', 'req_admin_002', 'feat_admin_002', 'implements', '{}', NOW() - INTERVAL '66 days', NOW() - INTERVAL '1 days'),
('link_final_011', 'proj_teamsync_001', 'feat_search_001', 'task_msg_003', 'depends_on', '{}', NOW() - INTERVAL '65 days', NOW() - INTERVAL '0 days'),
('link_final_012', 'proj_teamsync_001', 'feat_search_002', 'task_chan_003', 'depends_on', '{}', NOW() - INTERVAL '63 days', NOW() - INTERVAL '-2 days'),
('link_final_013', 'proj_teamsync_001', 'feat_search_003', 'task_file_003', 'depends_on', '{}', NOW() - INTERVAL '61 days', NOW() - INTERVAL '-4 days'),
('link_final_014', 'proj_teamsync_001', 'feat_analytics_001', 'api_file_005', 'traces_to', '{}', NOW() - INTERVAL '59 days', NOW() - INTERVAL '-6 days'),
('link_final_015', 'proj_teamsync_001', 'feat_analytics_002', 'schema_messages', 'related_to', '{}', NOW() - INTERVAL '57 days', NOW() - INTERVAL '-8 days'),
('link_final_016', 'proj_teamsync_001', 'feat_analytics_003', 'schema_reactions', 'related_to', '{}', NOW() - INTERVAL '55 days', NOW() - INTERVAL '-10 days'),
('link_final_017', 'proj_teamsync_001', 'req_api_001', 'feat_api_001', 'implements', '{}', NOW() - INTERVAL '62 days', NOW() - INTERVAL '-2 days'),
('link_final_018', 'proj_teamsync_001', 'req_api_002', 'feat_api_002', 'implements', '{}', NOW() - INTERVAL '60 days', NOW() - INTERVAL '-4 days'),
('link_final_019', 'proj_teamsync_001', 'req_api_003', 'feat_api_003', 'implements', '{}', NOW() - INTERVAL '58 days', NOW() - INTERVAL '-6 days'),
('link_final_020', 'proj_teamsync_001', 'feat_api_001', 'api_dm_005', 'relates_to', '{}', NOW() - INTERVAL '56 days', NOW() - INTERVAL '-8 days'),
('link_final_021', 'proj_teamsync_001', 'feat_api_002', 'schema_read_receipts', 'related_to', '{}', NOW() - INTERVAL '54 days', NOW() - INTERVAL '-10 days'),
('link_final_022', 'proj_teamsync_001', 'feat_api_003', 'ui_message_input', 'related_to', '{}', NOW() - INTERVAL '52 days', NOW() - INTERVAL '-12 days'),
('link_final_023', 'proj_teamsync_001', 'story_chan_001', 'task_chan_001', 'depends_on', '{}', NOW() - INTERVAL '68 days', NOW() - INTERVAL '3 days'),
('link_final_024', 'proj_teamsync_001', 'story_chan_002', 'task_chan_002', 'depends_on', '{}', NOW() - INTERVAL '66 days', NOW() - INTERVAL '1 days'),
('link_final_025', 'proj_teamsync_001', 'story_dm_001', 'task_chan_001', 'depends_on', '{}', NOW() - INTERVAL '64 days', NOW() - INTERVAL '-1 days'),
('link_final_026', 'proj_teamsync_001', 'story_dm_002', 'task_file_001', 'depends_on', '{}', NOW() - INTERVAL '62 days', NOW() - INTERVAL '-3 days'),
('link_final_027', 'proj_teamsync_001', 'story_file_001', 'test_msg_005', 'tests', '{}', NOW() - INTERVAL '60 days', NOW() - INTERVAL '-5 days'),
('link_final_028', 'proj_teamsync_001', 'story_file_002', 'test_msg_006', 'tests', '{}', NOW() - INTERVAL '58 days', NOW() - INTERVAL '-7 days'),
('link_final_029', 'proj_teamsync_001', 'story_thread_001', 'test_msg_007', 'tests', '{}', NOW() - INTERVAL '56 days', NOW() - INTERVAL '-9 days'),
('link_final_030', 'proj_teamsync_001', 'story_thread_002', 'test_msg_008', 'tests', '{}', NOW() - INTERVAL '54 days', NOW() - INTERVAL '-11 days');
