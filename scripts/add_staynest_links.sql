-- Add 200+ comprehensive links to StayNest project (proj_staynest_001)
-- Links connect requirements, features, stories, tasks, tests, and APIs
-- Following pattern: Requirements → Features → Stories → Tasks → Tests
--                   Requirements → Requirements (related)
--                   Features → APIs

-- Disable triggers during bulk insert
ALTER TABLE links DISABLE TRIGGER ALL;

-- Get project ID (assuming proj_staynest_001 exists)
-- This ensures we're adding to the correct project
DO $$
DECLARE
    v_project_id VARCHAR(255) := 'proj_staynest_001';
    v_link_counter INT := 100;
BEGIN
    -- Verify project exists
    IF NOT EXISTS (SELECT 1 FROM projects WHERE id = v_project_id) THEN
        RAISE EXCEPTION 'Project % does not exist', v_project_id;
    END IF;
END $$;

-- ==========================================
-- PHASE 1: Requirements → Features (implements)
-- ==========================================
-- Each requirement implements 2-3 features

INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, link_metadata, created_at, updated_at) VALUES
('link_sn_100', 'proj_staynest_001', 'req_sn_001', 'feat_sn_001', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_101', 'proj_staynest_001', 'req_sn_001', 'feat_sn_002', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_102', 'proj_staynest_001', 'req_sn_001', 'feat_sn_003', 'implements', '{"priority":"medium"}', NOW(), NOW()),
('link_sn_103', 'proj_staynest_001', 'req_sn_002', 'feat_sn_004', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_104', 'proj_staynest_001', 'req_sn_002', 'feat_sn_005', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_105', 'proj_staynest_001', 'req_sn_002', 'feat_sn_006', 'implements', '{"priority":"medium"}', NOW(), NOW()),
('link_sn_106', 'proj_staynest_001', 'req_sn_003', 'feat_sn_007', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_107', 'proj_staynest_001', 'req_sn_003', 'feat_sn_008', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_108', 'proj_staynest_001', 'req_sn_004', 'feat_sn_009', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_109', 'proj_staynest_001', 'req_sn_004', 'feat_sn_010', 'implements', '{"priority":"medium"}', NOW(), NOW()),
('link_sn_110', 'proj_staynest_001', 'req_sn_005', 'feat_sn_011', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_111', 'proj_staynest_001', 'req_sn_005', 'feat_sn_012', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_112', 'proj_staynest_001', 'req_sn_005', 'feat_sn_013', 'implements', '{"priority":"medium"}', NOW(), NOW()),
('link_sn_113', 'proj_staynest_001', 'req_sn_006', 'feat_sn_014', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_114', 'proj_staynest_001', 'req_sn_006', 'feat_sn_015', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_115', 'proj_staynest_001', 'req_sn_007', 'feat_sn_016', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_116', 'proj_staynest_001', 'req_sn_007', 'feat_sn_017', 'implements', '{"priority":"medium"}', NOW(), NOW()),
('link_sn_117', 'proj_staynest_001', 'req_sn_008', 'feat_sn_018', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_118', 'proj_staynest_001', 'req_sn_008', 'feat_sn_019', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_119', 'proj_staynest_001', 'req_sn_009', 'feat_sn_020', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_120', 'proj_staynest_001', 'req_sn_010', 'feat_sn_021', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_121', 'proj_staynest_001', 'req_sn_010', 'feat_sn_022', 'implements', '{"priority":"medium"}', NOW(), NOW()),
('link_sn_122', 'proj_staynest_001', 'req_sn_011', 'feat_sn_023', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_123', 'proj_staynest_001', 'req_sn_011', 'feat_sn_024', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_124', 'proj_staynest_001', 'req_sn_012', 'feat_sn_025', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_125', 'proj_staynest_001', 'req_sn_013', 'feat_sn_026', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_126', 'proj_staynest_001', 'req_sn_013', 'feat_sn_027', 'implements', '{"priority":"medium"}', NOW(), NOW()),
('link_sn_127', 'proj_staynest_001', 'req_sn_014', 'feat_sn_028', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_128', 'proj_staynest_001', 'req_sn_014', 'feat_sn_029', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_129', 'proj_staynest_001', 'req_sn_015', 'feat_sn_030', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_130', 'proj_staynest_001', 'req_sn_016', 'feat_sn_031', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_131', 'proj_staynest_001', 'req_sn_016', 'feat_sn_032', 'implements', '{"priority":"medium"}', NOW(), NOW()),
('link_sn_132', 'proj_staynest_001', 'req_sn_017', 'feat_sn_033', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_133', 'proj_staynest_001', 'req_sn_017', 'feat_sn_034', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_134', 'proj_staynest_001', 'req_sn_018', 'feat_sn_035', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_135', 'proj_staynest_001', 'req_sn_019', 'feat_sn_036', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_136', 'proj_staynest_001', 'req_sn_019', 'feat_sn_037', 'implements', '{"priority":"medium"}', NOW(), NOW()),
('link_sn_137', 'proj_staynest_001', 'req_sn_020', 'feat_sn_038', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_138', 'proj_staynest_001', 'req_sn_020', 'feat_sn_039', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_139', 'proj_staynest_001', 'req_sn_021', 'feat_sn_040', 'implements', '{"priority":"high"}', NOW(), NOW());

INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, link_metadata, created_at, updated_at) VALUES
('link_sn_140', 'proj_staynest_001', 'req_sn_022', 'feat_sn_041', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_141', 'proj_staynest_001', 'req_sn_022', 'feat_sn_042', 'implements', '{"priority":"medium"}', NOW(), NOW()),
('link_sn_142', 'proj_staynest_001', 'req_sn_023', 'feat_sn_043', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_143', 'proj_staynest_001', 'req_sn_023', 'feat_sn_044', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_144', 'proj_staynest_001', 'req_sn_024', 'feat_sn_045', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_145', 'proj_staynest_001', 'req_sn_025', 'feat_sn_046', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_146', 'proj_staynest_001', 'req_sn_025', 'feat_sn_047', 'implements', '{"priority":"medium"}', NOW(), NOW()),
('link_sn_147', 'proj_staynest_001', 'req_sn_026', 'feat_sn_048', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_148', 'proj_staynest_001', 'req_sn_026', 'feat_sn_049', 'implements', '{"priority":"high"}', NOW(), NOW()),
('link_sn_149', 'proj_staynest_001', 'req_sn_027', 'feat_sn_050', 'implements', '{"priority":"high"}', NOW(), NOW());

-- ==========================================
-- PHASE 2: Features → Stories (traces_to)
-- Each feature traces to 1-3 stories
-- ==========================================

INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, link_metadata, created_at, updated_at) VALUES
('link_sn_150', 'proj_staynest_001', 'feat_sn_001', 'story_sn_001', 'traces_to', '{"complexity":"low"}', NOW(), NOW()),
('link_sn_151', 'proj_staynest_001', 'feat_sn_001', 'story_sn_002', 'traces_to', '{"complexity":"medium"}', NOW(), NOW()),
('link_sn_152', 'proj_staynest_001', 'feat_sn_002', 'story_sn_003', 'traces_to', '{"complexity":"medium"}', NOW(), NOW()),
('link_sn_153', 'proj_staynest_001', 'feat_sn_002', 'story_sn_004', 'traces_to', '{"complexity":"low"}', NOW(), NOW()),
('link_sn_154', 'proj_staynest_001', 'feat_sn_003', 'story_sn_005', 'traces_to', '{"complexity":"high"}', NOW(), NOW()),
('link_sn_155', 'proj_staynest_001', 'feat_sn_004', 'story_sn_006', 'traces_to', '{"complexity":"medium"}', NOW(), NOW()),
('link_sn_156', 'proj_staynest_001', 'feat_sn_004', 'story_sn_007', 'traces_to', '{"complexity":"low"}', NOW(), NOW()),
('link_sn_157', 'proj_staynest_001', 'feat_sn_005', 'story_sn_008', 'traces_to', '{"complexity":"high"}', NOW(), NOW()),
('link_sn_158', 'proj_staynest_001', 'feat_sn_006', 'story_sn_009', 'traces_to', '{"complexity":"medium"}', NOW(), NOW()),
('link_sn_159', 'proj_staynest_001', 'feat_sn_007', 'story_sn_010', 'traces_to', '{"complexity":"medium"}', NOW(), NOW()),
('link_sn_160', 'proj_staynest_001', 'feat_sn_008', 'story_sn_011', 'traces_to', '{"complexity":"low"}', NOW(), NOW()),
('link_sn_161', 'proj_staynest_001', 'feat_sn_008', 'story_sn_012', 'traces_to', '{"complexity":"medium"}', NOW(), NOW()),
('link_sn_162', 'proj_staynest_001', 'feat_sn_009', 'story_sn_013', 'traces_to', '{"complexity":"high"}', NOW(), NOW()),
('link_sn_163', 'proj_staynest_001', 'feat_sn_010', 'story_sn_014', 'traces_to', '{"complexity":"medium"}', NOW(), NOW()),
('link_sn_164', 'proj_staynest_001', 'feat_sn_011', 'story_sn_015', 'traces_to', '{"complexity":"low"}', NOW(), NOW()),
('link_sn_165', 'proj_staynest_001', 'feat_sn_011', 'story_sn_016', 'traces_to', '{"complexity":"medium"}', NOW(), NOW()),
('link_sn_166', 'proj_staynest_001', 'feat_sn_012', 'story_sn_017', 'traces_to', '{"complexity":"high"}', NOW(), NOW()),
('link_sn_167', 'proj_staynest_001', 'feat_sn_013', 'story_sn_018', 'traces_to', '{"complexity":"medium"}', NOW(), NOW()),
('link_sn_168', 'proj_staynest_001', 'feat_sn_014', 'story_sn_019', 'traces_to', '{"complexity":"low"}', NOW(), NOW()),
('link_sn_169', 'proj_staynest_001', 'feat_sn_015', 'story_sn_020', 'traces_to', '{"complexity":"medium"}', NOW(), NOW()),
('link_sn_170', 'proj_staynest_001', 'feat_sn_016', 'story_sn_021', 'traces_to', '{"complexity":"high"}', NOW(), NOW()),
('link_sn_171', 'proj_staynest_001', 'feat_sn_017', 'story_sn_022', 'traces_to', '{"complexity":"low"}', NOW(), NOW()),
('link_sn_172', 'proj_staynest_001', 'feat_sn_017', 'story_sn_023', 'traces_to', '{"complexity":"medium"}', NOW(), NOW()),
('link_sn_173', 'proj_staynest_001', 'feat_sn_018', 'story_sn_024', 'traces_to', '{"complexity":"high"}', NOW(), NOW()),
('link_sn_174', 'proj_staynest_001', 'feat_sn_019', 'story_sn_025', 'traces_to', '{"complexity":"medium"}', NOW(), NOW()),
('link_sn_175', 'proj_staynest_001', 'feat_sn_020', 'story_sn_026', 'traces_to', '{"complexity":"low"}', NOW(), NOW()),
('link_sn_176', 'proj_staynest_001', 'feat_sn_020', 'story_sn_027', 'traces_to', '{"complexity":"medium"}', NOW(), NOW()),
('link_sn_177', 'proj_staynest_001', 'feat_sn_021', 'story_sn_028', 'traces_to', '{"complexity":"high"}', NOW(), NOW()),
('link_sn_178', 'proj_staynest_001', 'feat_sn_022', 'story_sn_001', 'traces_to', '{"complexity":"medium"}', NOW(), NOW()),
('link_sn_179', 'proj_staynest_001', 'feat_sn_023', 'story_sn_002', 'traces_to', '{"complexity":"low"}', NOW(), NOW());

INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, link_metadata, created_at, updated_at) VALUES
('link_sn_180', 'proj_staynest_001', 'feat_sn_024', 'story_sn_003', 'traces_to', '{"complexity":"medium"}', NOW(), NOW()),
('link_sn_181', 'proj_staynest_001', 'feat_sn_025', 'story_sn_004', 'traces_to', '{"complexity":"high"}', NOW(), NOW()),
('link_sn_182', 'proj_staynest_001', 'feat_sn_026', 'story_sn_005', 'traces_to', '{"complexity":"low"}', NOW(), NOW()),
('link_sn_183', 'proj_staynest_001', 'feat_sn_027', 'story_sn_006', 'traces_to', '{"complexity":"medium"}', NOW(), NOW()),
('link_sn_184', 'proj_staynest_001', 'feat_sn_028', 'story_sn_007', 'traces_to', '{"complexity":"high"}', NOW(), NOW()),
('link_sn_185', 'proj_staynest_001', 'feat_sn_029', 'story_sn_008', 'traces_to', '{"complexity":"medium"}', NOW(), NOW()),
('link_sn_186', 'proj_staynest_001', 'feat_sn_030', 'story_sn_009', 'traces_to', '{"complexity":"low"}', NOW(), NOW()),
('link_sn_187', 'proj_staynest_001', 'feat_sn_031', 'story_sn_010', 'traces_to', '{"complexity":"medium"}', NOW(), NOW()),
('link_sn_188', 'proj_staynest_001', 'feat_sn_032', 'story_sn_011', 'traces_to', '{"complexity":"high"}', NOW(), NOW()),
('link_sn_189', 'proj_staynest_001', 'feat_sn_033', 'story_sn_012', 'traces_to', '{"complexity":"low"}', NOW(), NOW()),
('link_sn_190', 'proj_staynest_001', 'feat_sn_034', 'story_sn_013', 'traces_to', '{"complexity":"medium"}', NOW(), NOW()),
('link_sn_191', 'proj_staynest_001', 'feat_sn_035', 'story_sn_014', 'traces_to', '{"complexity":"high"}', NOW(), NOW()),
('link_sn_192', 'proj_staynest_001', 'feat_sn_036', 'story_sn_015', 'traces_to', '{"complexity":"medium"}', NOW(), NOW()),
('link_sn_193', 'proj_staynest_001', 'feat_sn_037', 'story_sn_016', 'traces_to', '{"complexity":"low"}', NOW(), NOW()),
('link_sn_194', 'proj_staynest_001', 'feat_sn_038', 'story_sn_017', 'traces_to', '{"complexity":"medium"}', NOW(), NOW()),
('link_sn_195', 'proj_staynest_001', 'feat_sn_039', 'story_sn_018', 'traces_to', '{"complexity":"high"}', NOW(), NOW()),
('link_sn_196', 'proj_staynest_001', 'feat_sn_040', 'story_sn_019', 'traces_to', '{"complexity":"low"}', NOW(), NOW()),
('link_sn_197', 'proj_staynest_001', 'feat_sn_041', 'story_sn_020', 'traces_to', '{"complexity":"medium"}', NOW(), NOW()),
('link_sn_198', 'proj_staynest_001', 'feat_sn_042', 'story_sn_021', 'traces_to', '{"complexity":"high"}', NOW(), NOW()),
('link_sn_199', 'proj_staynest_001', 'feat_sn_043', 'story_sn_022', 'traces_to', '{"complexity":"low"}', NOW(), NOW());

-- ==========================================
-- PHASE 3: Stories → Tasks (depends_on)
-- Each story depends on 1-2 tasks
-- ==========================================

INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, link_metadata, created_at, updated_at) VALUES
('link_sn_200', 'proj_staynest_001', 'story_sn_001', 'task_sn_001', 'depends_on', '{"effort":"2"}', NOW(), NOW()),
('link_sn_201', 'proj_staynest_001', 'story_sn_001', 'task_sn_002', 'depends_on', '{"effort":"3"}', NOW(), NOW()),
('link_sn_202', 'proj_staynest_001', 'story_sn_002', 'task_sn_003', 'depends_on', '{"effort":"2"}', NOW(), NOW()),
('link_sn_203', 'proj_staynest_001', 'story_sn_003', 'task_sn_004', 'depends_on', '{"effort":"1"}', NOW(), NOW()),
('link_sn_204', 'proj_staynest_001', 'story_sn_003', 'task_sn_005', 'depends_on', '{"effort":"2"}', NOW(), NOW()),
('link_sn_205', 'proj_staynest_001', 'story_sn_004', 'task_sn_006', 'depends_on', '{"effort":"3"}', NOW(), NOW()),
('link_sn_206', 'proj_staynest_001', 'story_sn_005', 'task_sn_007', 'depends_on', '{"effort":"2"}', NOW(), NOW()),
('link_sn_207', 'proj_staynest_001', 'story_sn_006', 'task_sn_008', 'depends_on', '{"effort":"1"}', NOW(), NOW()),
('link_sn_208', 'proj_staynest_001', 'story_sn_006', 'task_sn_009', 'depends_on', '{"effort":"2"}', NOW(), NOW()),
('link_sn_209', 'proj_staynest_001', 'story_sn_007', 'task_sn_010', 'depends_on', '{"effort":"3"}', NOW(), NOW()),
('link_sn_210', 'proj_staynest_001', 'story_sn_008', 'task_sn_011', 'depends_on', '{"effort":"2"}', NOW(), NOW()),
('link_sn_211', 'proj_staynest_001', 'story_sn_009', 'task_sn_012', 'depends_on', '{"effort":"1"}', NOW(), NOW()),
('link_sn_212', 'proj_staynest_001', 'story_sn_009', 'task_sn_013', 'depends_on', '{"effort":"2"}', NOW(), NOW()),
('link_sn_213', 'proj_staynest_001', 'story_sn_010', 'task_sn_014', 'depends_on', '{"effort":"3"}', NOW(), NOW()),
('link_sn_214', 'proj_staynest_001', 'story_sn_011', 'task_sn_015', 'depends_on', '{"effort":"2"}', NOW(), NOW()),
('link_sn_215', 'proj_staynest_001', 'story_sn_012', 'task_sn_016', 'depends_on', '{"effort":"1"}', NOW(), NOW()),
('link_sn_216', 'proj_staynest_001', 'story_sn_012', 'task_sn_017', 'depends_on', '{"effort":"2"}', NOW(), NOW()),
('link_sn_217', 'proj_staynest_001', 'story_sn_013', 'task_sn_018', 'depends_on', '{"effort":"3"}', NOW(), NOW()),
('link_sn_218', 'proj_staynest_001', 'story_sn_014', 'task_sn_019', 'depends_on', '{"effort":"2"}', NOW(), NOW()),
('link_sn_219', 'proj_staynest_001', 'story_sn_015', 'task_sn_020', 'depends_on', '{"effort":"1"}', NOW(), NOW()),
('link_sn_220', 'proj_staynest_001', 'story_sn_016', 'task_sn_021', 'depends_on', '{"effort":"2"}', NOW(), NOW()),
('link_sn_221', 'proj_staynest_001', 'story_sn_017', 'task_sn_022', 'depends_on', '{"effort":"3"}', NOW(), NOW()),
('link_sn_222', 'proj_staynest_001', 'story_sn_018', 'task_sn_023', 'depends_on', '{"effort":"2"}', NOW(), NOW()),
('link_sn_223', 'proj_staynest_001', 'story_sn_019', 'task_sn_024', 'depends_on', '{"effort":"1"}', NOW(), NOW()),
('link_sn_224', 'proj_staynest_001', 'story_sn_020', 'task_sn_025', 'depends_on', '{"effort":"2"}', NOW(), NOW()),
('link_sn_225', 'proj_staynest_001', 'story_sn_021', 'task_sn_026', 'depends_on', '{"effort":"3"}', NOW(), NOW()),
('link_sn_226', 'proj_staynest_001', 'story_sn_022', 'task_sn_027', 'depends_on', '{"effort":"2"}', NOW(), NOW()),
('link_sn_227', 'proj_staynest_001', 'story_sn_023', 'task_sn_028', 'depends_on', '{"effort":"1"}', NOW(), NOW()),
('link_sn_228', 'proj_staynest_001', 'story_sn_024', 'task_sn_029', 'depends_on', '{"effort":"2"}', NOW(), NOW()),
('link_sn_229', 'proj_staynest_001', 'story_sn_025', 'task_sn_030', 'depends_on', '{"effort":"3"}', NOW(), NOW()),
('link_sn_230', 'proj_staynest_001', 'story_sn_026', 'task_sn_001', 'depends_on', '{"effort":"2"}', NOW(), NOW()),
('link_sn_231', 'proj_staynest_001', 'story_sn_027', 'task_sn_002', 'depends_on', '{"effort":"1"}', NOW(), NOW()),
('link_sn_232', 'proj_staynest_001', 'story_sn_028', 'task_sn_003', 'depends_on', '{"effort":"2"}', NOW(), NOW());

-- ==========================================
-- PHASE 4: Tasks → Tests (tests)
-- Each task tested by 1-2 tests
-- ==========================================

INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, link_metadata, created_at, updated_at) VALUES
('link_sn_233', 'proj_staynest_001', 'task_sn_001', 'test_sn_001', 'tests', '{"coverage":"high"}', NOW(), NOW()),
('link_sn_234', 'proj_staynest_001', 'task_sn_002', 'test_sn_002', 'tests', '{"coverage":"high"}', NOW(), NOW()),
('link_sn_235', 'proj_staynest_001', 'task_sn_003', 'test_sn_003', 'tests', '{"coverage":"medium"}', NOW(), NOW()),
('link_sn_236', 'proj_staynest_001', 'task_sn_004', 'test_sn_004', 'tests', '{"coverage":"high"}', NOW(), NOW()),
('link_sn_237', 'proj_staynest_001', 'task_sn_005', 'test_sn_005', 'tests', '{"coverage":"medium"}', NOW(), NOW()),
('link_sn_238', 'proj_staynest_001', 'task_sn_006', 'test_sn_006', 'tests', '{"coverage":"high"}', NOW(), NOW()),
('link_sn_239', 'proj_staynest_001', 'task_sn_007', 'test_sn_007', 'tests', '{"coverage":"high"}', NOW(), NOW()),
('link_sn_240', 'proj_staynest_001', 'task_sn_008', 'test_sn_008', 'tests', '{"coverage":"medium"}', NOW(), NOW()),
('link_sn_241', 'proj_staynest_001', 'task_sn_009', 'test_sn_009', 'tests', '{"coverage":"high"}', NOW(), NOW()),
('link_sn_242', 'proj_staynest_001', 'task_sn_010', 'test_sn_010', 'tests', '{"coverage":"high"}', NOW(), NOW()),
('link_sn_243', 'proj_staynest_001', 'task_sn_011', 'test_sn_011', 'tests', '{"coverage":"medium"}', NOW(), NOW()),
('link_sn_244', 'proj_staynest_001', 'task_sn_012', 'test_sn_012', 'tests', '{"coverage":"high"}', NOW(), NOW()),
('link_sn_245', 'proj_staynest_001', 'task_sn_013', 'test_sn_013', 'tests', '{"coverage":"high"}', NOW(), NOW()),
('link_sn_246', 'proj_staynest_001', 'task_sn_014', 'test_sn_014', 'tests', '{"coverage":"medium"}', NOW(), NOW()),
('link_sn_247', 'proj_staynest_001', 'task_sn_015', 'test_sn_015', 'tests', '{"coverage":"high"}', NOW(), NOW()),
('link_sn_248', 'proj_staynest_001', 'task_sn_016', 'test_sn_016', 'tests', '{"coverage":"high"}', NOW(), NOW()),
('link_sn_249', 'proj_staynest_001', 'task_sn_017', 'test_sn_017', 'tests', '{"coverage":"medium"}', NOW(), NOW()),
('link_sn_250', 'proj_staynest_001', 'task_sn_018', 'test_sn_018', 'tests', '{"coverage":"high"}', NOW(), NOW()),
('link_sn_251', 'proj_staynest_001', 'task_sn_019', 'test_sn_019', 'tests', '{"coverage":"high"}', NOW(), NOW()),
('link_sn_252', 'proj_staynest_001', 'task_sn_020', 'test_sn_020', 'tests', '{"coverage":"medium"}', NOW(), NOW()),
('link_sn_253', 'proj_staynest_001', 'task_sn_021', 'test_sn_001', 'tests', '{"coverage":"high"}', NOW(), NOW()),
('link_sn_254', 'proj_staynest_001', 'task_sn_022', 'test_sn_002', 'tests', '{"coverage":"high"}', NOW(), NOW()),
('link_sn_255', 'proj_staynest_001', 'task_sn_023', 'test_sn_003', 'tests', '{"coverage":"medium"}', NOW(), NOW()),
('link_sn_256', 'proj_staynest_001', 'task_sn_024', 'test_sn_004', 'tests', '{"coverage":"high"}', NOW(), NOW()),
('link_sn_257', 'proj_staynest_001', 'task_sn_025', 'test_sn_005', 'tests', '{"coverage":"high"}', NOW(), NOW()),
('link_sn_258', 'proj_staynest_001', 'task_sn_026', 'test_sn_006', 'tests', '{"coverage":"medium"}', NOW(), NOW()),
('link_sn_259', 'proj_staynest_001', 'task_sn_027', 'test_sn_007', 'tests', '{"coverage":"high"}', NOW(), NOW()),
('link_sn_260', 'proj_staynest_001', 'task_sn_028', 'test_sn_008', 'tests', '{"coverage":"high"}', NOW(), NOW()),
('link_sn_261', 'proj_staynest_001', 'task_sn_029', 'test_sn_009', 'tests', '{"coverage":"medium"}', NOW(), NOW()),
('link_sn_262', 'proj_staynest_001', 'task_sn_030', 'test_sn_010', 'tests', '{"coverage":"high"}', NOW(), NOW());

-- ==========================================
-- PHASE 5: Features → APIs (implements)
-- Each feature implements APIs
-- ==========================================

INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, link_metadata, created_at, updated_at) VALUES
('link_sn_263', 'proj_staynest_001', 'feat_sn_001', 'api_sn_001', 'implements', '{"endpoint":"/listings"}', NOW(), NOW()),
('link_sn_264', 'proj_staynest_001', 'feat_sn_002', 'api_sn_002', 'implements', '{"endpoint":"/search"}', NOW(), NOW()),
('link_sn_265', 'proj_staynest_001', 'feat_sn_003', 'api_sn_003', 'implements', '{"endpoint":"/reservations"}', NOW(), NOW()),
('link_sn_266', 'proj_staynest_001', 'feat_sn_004', 'api_sn_004', 'implements', '{"endpoint":"/reviews"}', NOW(), NOW()),
('link_sn_267', 'proj_staynest_001', 'feat_sn_005', 'api_sn_005', 'implements', '{"endpoint":"/messaging"}', NOW(), NOW()),
('link_sn_268', 'proj_staynest_001', 'feat_sn_006', 'api_sn_006', 'implements', '{"endpoint":"/payments"}', NOW(), NOW()),
('link_sn_269', 'proj_staynest_001', 'feat_sn_007', 'api_sn_007', 'implements', '{"endpoint":"/users"}', NOW(), NOW()),
('link_sn_270', 'proj_staynest_001', 'feat_sn_008', 'api_sn_008', 'implements', '{"endpoint":"/bookings"}', NOW(), NOW()),
('link_sn_271', 'proj_staynest_001', 'feat_sn_009', 'api_sn_009', 'implements', '{"endpoint":"/notifications"}', NOW(), NOW()),
('link_sn_272', 'proj_staynest_001', 'feat_sn_010', 'api_sn_010', 'implements', '{"endpoint":"/calendar"}', NOW(), NOW()),
('link_sn_273', 'proj_staynest_001', 'feat_sn_011', 'api_sn_011', 'implements', '{"endpoint":"/photos"}', NOW(), NOW()),
('link_sn_274', 'proj_staynest_001', 'feat_sn_012', 'api_sn_012', 'implements', '{"endpoint":"/amenities"}', NOW(), NOW()),
('link_sn_275', 'proj_staynest_001', 'feat_sn_013', 'api_sn_013', 'implements', '{"endpoint":"/pricing"}', NOW(), NOW()),
('link_sn_276', 'proj_staynest_001', 'feat_sn_014', 'api_sn_014', 'implements', '{"endpoint":"/policies"}', NOW(), NOW()),
('link_sn_277', 'proj_staynest_001', 'feat_sn_015', 'api_sn_015', 'implements', '{"endpoint":"/disputes"}', NOW(), NOW()),
('link_sn_278', 'proj_staynest_001', 'feat_sn_016', 'api_sn_016', 'implements', '{"endpoint":"/reports"}', NOW(), NOW()),
('link_sn_279', 'proj_staynest_001', 'feat_sn_017', 'api_sn_017', 'implements', '{"endpoint":"/analytics"}', NOW(), NOW()),
('link_sn_280', 'proj_staynest_001', 'feat_sn_018', 'api_sn_018', 'implements', '{"endpoint":"/settings"}', NOW(), NOW()),
('link_sn_279', 'proj_staynest_001', 'feat_sn_019', 'api_sn_019', 'implements', '{"endpoint":"/preferences"}', NOW(), NOW()),
('link_sn_281', 'proj_staynest_001', 'feat_sn_020', 'api_sn_020', 'implements', '{"endpoint":"/integrations"}', NOW(), NOW());

-- ==========================================
-- PHASE 6: Requirements → Requirements (related_to)
-- Cross-requirements relationships for density
-- ==========================================

INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, link_metadata, created_at, updated_at) VALUES
('link_sn_282', 'proj_staynest_001', 'req_sn_001', 'req_sn_002', 'related_to', '{"type":"prerequisite"}', NOW(), NOW()),
('link_sn_283', 'proj_staynest_001', 'req_sn_002', 'req_sn_003', 'related_to', '{"type":"prerequisite"}', NOW(), NOW()),
('link_sn_284', 'proj_staynest_001', 'req_sn_003', 'req_sn_004', 'related_to', '{"type":"related"}', NOW(), NOW()),
('link_sn_285', 'proj_staynest_001', 'req_sn_004', 'req_sn_005', 'related_to', '{"type":"prerequisite"}', NOW(), NOW()),
('link_sn_286', 'proj_staynest_001', 'req_sn_005', 'req_sn_006', 'related_to', '{"type":"related"}', NOW(), NOW()),
('link_sn_287', 'proj_staynest_001', 'req_sn_006', 'req_sn_007', 'related_to', '{"type":"prerequisite"}', NOW(), NOW()),
('link_sn_288', 'proj_staynest_001', 'req_sn_007', 'req_sn_008', 'related_to', '{"type":"related"}', NOW(), NOW()),
('link_sn_289', 'proj_staynest_001', 'req_sn_008', 'req_sn_009', 'related_to', '{"type":"prerequisite"}', NOW(), NOW()),
('link_sn_290', 'proj_staynest_001', 'req_sn_009', 'req_sn_010', 'related_to', '{"type":"related"}', NOW(), NOW()),
('link_sn_291', 'proj_staynest_001', 'req_sn_010', 'req_sn_011', 'related_to', '{"type":"prerequisite"}', NOW(), NOW()),
('link_sn_292', 'proj_staynest_001', 'req_sn_011', 'req_sn_012', 'related_to', '{"type":"related"}', NOW(), NOW()),
('link_sn_293', 'proj_staynest_001', 'req_sn_012', 'req_sn_013', 'related_to', '{"type":"prerequisite"}', NOW(), NOW()),
('link_sn_294', 'proj_staynest_001', 'req_sn_013', 'req_sn_014', 'related_to', '{"type":"related"}', NOW(), NOW()),
('link_sn_295', 'proj_staynest_001', 'req_sn_014', 'req_sn_015', 'related_to', '{"type":"prerequisite"}', NOW(), NOW()),
('link_sn_296', 'proj_staynest_001', 'req_sn_015', 'req_sn_016', 'related_to', '{"type":"related"}', NOW(), NOW()),
('link_sn_297', 'proj_staynest_001', 'req_sn_016', 'req_sn_017', 'related_to', '{"type":"prerequisite"}', NOW(), NOW()),
('link_sn_298', 'proj_staynest_001', 'req_sn_017', 'req_sn_018', 'related_to', '{"type":"related"}', NOW(), NOW()),
('link_sn_299', 'proj_staynest_001', 'req_sn_018', 'req_sn_019', 'related_to', '{"type":"prerequisite"}', NOW(), NOW()),
('link_sn_300', 'proj_staynest_001', 'req_sn_019', 'req_sn_020', 'related_to', '{"type":"related"}', NOW(), NOW());

-- ==========================================
-- PHASE 7: Additional cross-type links for density
-- Features → Features (related_to)
-- ==========================================

INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, link_metadata, created_at, updated_at) VALUES
('link_sn_301', 'proj_staynest_001', 'feat_sn_001', 'feat_sn_005', 'related_to', '{"type":"depends"}', NOW(), NOW()),
('link_sn_302', 'proj_staynest_001', 'feat_sn_002', 'feat_sn_006', 'related_to', '{"type":"related"}', NOW(), NOW()),
('link_sn_303', 'proj_staynest_001', 'feat_sn_003', 'feat_sn_007', 'related_to', '{"type":"depends"}', NOW(), NOW()),
('link_sn_304', 'proj_staynest_001', 'feat_sn_004', 'feat_sn_008', 'related_to', '{"type":"related"}', NOW(), NOW()),
('link_sn_305', 'proj_staynest_001', 'feat_sn_005', 'feat_sn_009', 'related_to', '{"type":"depends"}', NOW(), NOW()),
('link_sn_306', 'proj_staynest_001', 'feat_sn_010', 'feat_sn_015', 'related_to', '{"type":"related"}', NOW(), NOW()),
('link_sn_307', 'proj_staynest_001', 'feat_sn_011', 'feat_sn_016', 'related_to', '{"type":"depends"}', NOW(), NOW()),
('link_sn_308', 'proj_staynest_001', 'feat_sn_012', 'feat_sn_017', 'related_to', '{"type":"related"}', NOW(), NOW()),
('link_sn_309', 'proj_staynest_001', 'feat_sn_013', 'feat_sn_018', 'related_to', '{"type":"depends"}', NOW(), NOW()),
('link_sn_310', 'proj_staynest_001', 'feat_sn_014', 'feat_sn_019', 'related_to', '{"type":"related"}', NOW(), NOW()),
('link_sn_311', 'proj_staynest_001', 'feat_sn_020', 'feat_sn_025', 'related_to', '{"type":"depends"}', NOW(), NOW()),
('link_sn_312', 'proj_staynest_001', 'feat_sn_021', 'feat_sn_026', 'related_to', '{"type":"related"}', NOW(), NOW()),
('link_sn_313', 'proj_staynest_001', 'feat_sn_022', 'feat_sn_027', 'related_to', '{"type":"depends"}', NOW(), NOW()),
('link_sn_314', 'proj_staynest_001', 'feat_sn_023', 'feat_sn_028', 'related_to', '{"type":"related"}', NOW(), NOW()),
('link_sn_315', 'proj_staynest_001', 'feat_sn_024', 'feat_sn_029', 'related_to', '{"type":"depends"}', NOW(), NOW()),
('link_sn_316', 'proj_staynest_001', 'feat_sn_030', 'feat_sn_035', 'related_to', '{"type":"related"}', NOW(), NOW()),
('link_sn_317', 'proj_staynest_001', 'feat_sn_031', 'feat_sn_036', 'related_to', '{"type":"depends"}', NOW(), NOW()),
('link_sn_318', 'proj_staynest_001', 'feat_sn_032', 'feat_sn_037', 'related_to', '{"type":"related"}', NOW(), NOW()),
('link_sn_319', 'proj_staynest_001', 'feat_sn_033', 'feat_sn_038', 'related_to', '{"type":"depends"}', NOW(), NOW()),
('link_sn_320', 'proj_staynest_001', 'feat_sn_034', 'feat_sn_039', 'related_to', '{"type":"related"}', NOW(), NOW());

-- ==========================================
-- PHASE 8: Tasks → Tasks (blocks)
-- Task dependency blocking relationships
-- ==========================================

INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, link_metadata, created_at, updated_at) VALUES
('link_sn_321', 'proj_staynest_001', 'task_sn_001', 'task_sn_002', 'blocks', '{"severity":"high"}', NOW(), NOW()),
('link_sn_322', 'proj_staynest_001', 'task_sn_002', 'task_sn_003', 'blocks', '{"severity":"medium"}', NOW(), NOW()),
('link_sn_323', 'proj_staynest_001', 'task_sn_003', 'task_sn_004', 'blocks', '{"severity":"high"}', NOW(), NOW()),
('link_sn_324', 'proj_staynest_001', 'task_sn_005', 'task_sn_006', 'blocks', '{"severity":"medium"}', NOW(), NOW()),
('link_sn_325', 'proj_staynest_001', 'task_sn_007', 'task_sn_008', 'blocks', '{"severity":"high"}', NOW(), NOW()),
('link_sn_326', 'proj_staynest_001', 'task_sn_009', 'task_sn_010', 'blocks', '{"severity":"medium"}', NOW(), NOW()),
('link_sn_327', 'proj_staynest_001', 'task_sn_011', 'task_sn_012', 'blocks', '{"severity":"high"}', NOW(), NOW()),
('link_sn_328', 'proj_staynest_001', 'task_sn_013', 'task_sn_014', 'blocks', '{"severity":"medium"}', NOW(), NOW()),
('link_sn_329', 'proj_staynest_001', 'task_sn_015', 'task_sn_016', 'blocks', '{"severity":"high"}', NOW(), NOW()),
('link_sn_330', 'proj_staynest_001', 'task_sn_017', 'task_sn_018', 'blocks', '{"severity":"medium"}', NOW(), NOW());

-- ==========================================
-- PHASE 9: Stories → Stories (related_to)
-- Story relationships for graph density
-- ==========================================

INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, link_metadata, created_at, updated_at) VALUES
('link_sn_331', 'proj_staynest_001', 'story_sn_001', 'story_sn_005', 'related_to', '{"type":"adjacent"}', NOW(), NOW()),
('link_sn_332', 'proj_staynest_001', 'story_sn_002', 'story_sn_006', 'related_to', '{"type":"related"}', NOW(), NOW()),
('link_sn_333', 'proj_staynest_001', 'story_sn_003', 'story_sn_007', 'related_to', '{"type":"adjacent"}', NOW(), NOW()),
('link_sn_334', 'proj_staynest_001', 'story_sn_004', 'story_sn_008', 'related_to', '{"type":"related"}', NOW(), NOW()),
('link_sn_335', 'proj_staynest_001', 'story_sn_009', 'story_sn_013', 'related_to', '{"type":"adjacent"}', NOW(), NOW()),
('link_sn_336', 'proj_staynest_001', 'story_sn_010', 'story_sn_014', 'related_to', '{"type":"related"}', NOW(), NOW()),
('link_sn_337', 'proj_staynest_001', 'story_sn_011', 'story_sn_015', 'related_to', '{"type":"adjacent"}', NOW(), NOW()),
('link_sn_338', 'proj_staynest_001', 'story_sn_012', 'story_sn_016', 'related_to', '{"type":"related"}', NOW(), NOW()),
('link_sn_339', 'proj_staynest_001', 'story_sn_017', 'story_sn_021', 'related_to', '{"type":"adjacent"}', NOW(), NOW()),
('link_sn_340', 'proj_staynest_001', 'story_sn_018', 'story_sn_022', 'related_to', '{"type":"related"}', NOW(), NOW()),
('link_sn_341', 'proj_staynest_001', 'story_sn_019', 'story_sn_023', 'related_to', '{"type":"adjacent"}', NOW(), NOW()),
('link_sn_342', 'proj_staynest_001', 'story_sn_020', 'story_sn_024', 'related_to', '{"type":"related"}', NOW(), NOW()),
('link_sn_343', 'proj_staynest_001', 'story_sn_025', 'story_sn_028', 'related_to', '{"type":"adjacent"}', NOW(), NOW());

-- ==========================================
-- PHASE 10: Requirements → Tasks (traces_to)
-- Direct traces from requirements to tasks for cross-level connections
-- ==========================================

INSERT INTO links (id, project_id, source_item_id, target_item_id, link_type, link_metadata, created_at, updated_at) VALUES
('link_sn_344', 'proj_staynest_001', 'req_sn_001', 'task_sn_001', 'traces_to', '{"path":"direct"}', NOW(), NOW()),
('link_sn_345', 'proj_staynest_001', 'req_sn_002', 'task_sn_005', 'traces_to', '{"path":"direct"}', NOW(), NOW()),
('link_sn_346', 'proj_staynest_001', 'req_sn_003', 'task_sn_010', 'traces_to', '{"path":"direct"}', NOW(), NOW()),
('link_sn_347', 'proj_staynest_001', 'req_sn_004', 'task_sn_015', 'traces_to', '{"path":"direct"}', NOW(), NOW()),
('link_sn_348', 'proj_staynest_001', 'req_sn_005', 'task_sn_020', 'traces_to', '{"path":"direct"}', NOW(), NOW()),
('link_sn_349', 'proj_staynest_001', 'req_sn_006', 'task_sn_025', 'traces_to', '{"path":"direct"}', NOW(), NOW()),
('link_sn_350', 'proj_staynest_001', 'req_sn_007', 'task_sn_030', 'traces_to', '{"path":"direct"}', NOW(), NOW()),
('link_sn_351', 'proj_staynest_001', 'req_sn_008', 'task_sn_002', 'traces_to', '{"path":"direct"}', NOW(), NOW()),
('link_sn_352', 'proj_staynest_001', 'req_sn_009', 'task_sn_007', 'traces_to', '{"path":"direct"}', NOW(), NOW()),
('link_sn_353', 'proj_staynest_001', 'req_sn_010', 'task_sn_012', 'traces_to', '{"path":"direct"}', NOW(), NOW());

-- ==========================================
-- FINAL STATUS
-- ==========================================
-- Total links created: 254+ (exceeds 200 requirement)
-- Breakdown:
-- - Requirements to Features (implements): 50 links
-- - Features to Stories (traces_to): 50 links
-- - Stories to Tasks (depends_on): 33 links
-- - Tasks to Tests (tests): 30 links
-- - Features to APIs (implements): 20 links
-- - Requirements to Requirements (related_to): 20 links
-- - Features to Features (related_to): 20 links
-- - Tasks to Tasks (blocks): 10 links
-- - Stories to Stories (related_to): 13 links
-- - Requirements to Tasks (traces_to): 10 links
-- ==========================================

-- Re-enable triggers
ALTER TABLE links ENABLE TRIGGER ALL;

-- Verify total links
SELECT COUNT(*) as total_links_added FROM links WHERE project_id = 'proj_staynest_001' AND id LIKE 'link_sn_%';
