/**
 * Data Generators for k6 Load Tests
 *
 * Provides realistic test data generation for various entities
 * to simulate production-like load patterns.
 */

import { randomString, randomIntBetween, randomItem } from 'k6';

// Realistic data pools for generation
const ITEM_TYPES = ['requirement', 'feature', 'task', 'bug', 'epic', 'story'];
const ITEM_STATUSES = ['open', 'in_progress', 'review', 'done', 'blocked'];
const PRIORITIES = ['low', 'medium', 'high', 'critical'];
const TAGS = ['frontend', 'backend', 'api', 'database', 'ui', 'performance', 'security', 'testing'];

const REQUIREMENT_PREFIXES = [
  'User shall be able to',
  'System must',
  'Application should',
  'Platform needs to',
  'Service will',
];

const FEATURE_NAMES = [
  'Dashboard Analytics',
  'User Profile Management',
  'Search Enhancement',
  'Report Generation',
  'Data Export',
  'Real-time Notifications',
  'Graph Visualization',
  'API Integration',
];

const BUG_DESCRIPTIONS = [
  'Page fails to load under high traffic',
  'Incorrect data displayed in dashboard',
  'Memory leak in graph rendering',
  'Slow query performance on large datasets',
  'WebSocket connection drops intermittently',
  'Export fails for datasets over 10k records',
];

/**
 * Generate a random item (requirement, feature, task, etc.)
 *
 * @param {Object} options - Generation options
 * @returns {Object} - Generated item
 */
export function generateItem(options = {}) {
  const type = options.type || randomItem(ITEM_TYPES);
  const projectId = options.projectId || randomIntBetween(1, 100);

  let title, description;

  switch (type) {
    case 'requirement':
      title = `${randomItem(REQUIREMENT_PREFIXES)} ${randomString(20)}`;
      description = `Detailed requirement: ${randomString(100)}`;
      break;
    case 'feature':
      title = randomItem(FEATURE_NAMES);
      description = `Feature implementation for ${randomString(50)}`;
      break;
    case 'bug':
      title = `Bug: ${randomItem(BUG_DESCRIPTIONS)}`;
      description = `Steps to reproduce: ${randomString(80)}`;
      break;
    default:
      title = `${type.charAt(0).toUpperCase() + type.slice(1)}: ${randomString(30)}`;
      description = randomString(100);
  }

  return {
    project_id: projectId,
    type: type,
    title: title,
    description: description,
    status: options.status || randomItem(ITEM_STATUSES),
    priority: options.priority || randomItem(PRIORITIES),
    tags: generateTags(options.tagCount || randomIntBetween(1, 4)),
    metadata: {
      created_by: `user_${randomIntBetween(1, 1000)}`,
      estimated_hours: randomIntBetween(1, 40),
      complexity: randomItem(['low', 'medium', 'high']),
    },
  };
}

/**
 * Generate multiple items
 *
 * @param {number} count - Number of items to generate
 * @param {Object} options - Generation options
 * @returns {Array} - Array of generated items
 */
export function generateItems(count, options = {}) {
  const items = [];
  for (let i = 0; i < count; i++) {
    items.push(generateItem(options));
  }
  return items;
}

/**
 * Generate a random link between items
 *
 * @param {Object} options - Link options
 * @returns {Object} - Generated link
 */
export function generateLink(options = {}) {
  return {
    source_id: options.sourceId || randomIntBetween(1, 10000),
    target_id: options.targetId || randomIntBetween(1, 10000),
    link_type: options.linkType || randomItem(['depends_on', 'blocks', 'relates_to', 'implements', 'tests']),
    metadata: {
      created_at: new Date().toISOString(),
      strength: randomIntBetween(1, 10),
    },
  };
}

/**
 * Generate a test case
 *
 * @param {Object} options - Test case options
 * @returns {Object} - Generated test case
 */
export function generateTestCase(options = {}) {
  return {
    project_id: options.projectId || randomIntBetween(1, 100),
    title: `Test Case: ${randomString(40)}`,
    description: `Verify that ${randomString(80)}`,
    steps: [
      { step: 1, action: `Navigate to ${randomString(20)}`, expected: `Page loads successfully` },
      { step: 2, action: `Click on ${randomString(15)}`, expected: `Modal appears` },
      { step: 3, action: `Enter ${randomString(10)}`, expected: `Data is saved` },
    ],
    priority: options.priority || randomItem(PRIORITIES),
    status: options.status || randomItem(['passed', 'failed', 'skipped', 'pending']),
    automated: options.automated !== undefined ? options.automated : randomIntBetween(0, 1) === 1,
    tags: generateTags(2),
  };
}

/**
 * Generate a graph node
 *
 * @param {Object} options - Node options
 * @returns {Object} - Generated graph node
 */
export function generateGraphNode(options = {}) {
  return {
    id: options.id || `node_${randomString(10)}`,
    type: options.type || randomItem(['requirement', 'feature', 'component', 'service', 'database']),
    label: options.label || randomString(30),
    metadata: {
      weight: randomIntBetween(1, 100),
      layer: randomIntBetween(1, 5),
      status: randomItem(ITEM_STATUSES),
    },
    position: options.position || {
      x: randomIntBetween(0, 1000),
      y: randomIntBetween(0, 1000),
    },
  };
}

/**
 * Generate a graph with nodes and edges
 *
 * @param {number} nodeCount - Number of nodes
 * @param {number} edgeCount - Number of edges
 * @returns {Object} - Graph with nodes and edges
 */
export function generateGraph(nodeCount = 100, edgeCount = 150) {
  const nodes = [];
  const edges = [];

  // Generate nodes
  for (let i = 0; i < nodeCount; i++) {
    nodes.push(generateGraphNode({ id: `node_${i}` }));
  }

  // Generate edges ensuring valid node references
  for (let i = 0; i < edgeCount; i++) {
    const sourceIdx = randomIntBetween(0, nodeCount - 1);
    let targetIdx = randomIntBetween(0, nodeCount - 1);

    // Avoid self-loops
    while (targetIdx === sourceIdx) {
      targetIdx = randomIntBetween(0, nodeCount - 1);
    }

    edges.push({
      id: `edge_${i}`,
      source: `node_${sourceIdx}`,
      target: `node_${targetIdx}`,
      type: randomItem(['depends_on', 'contains', 'implements', 'tests']),
      weight: randomIntBetween(1, 10),
    });
  }

  return { nodes, edges };
}

/**
 * Generate search query parameters
 *
 * @param {Object} options - Search options
 * @returns {Object} - Search query parameters
 */
export function generateSearchQuery(options = {}) {
  const queries = [
    'performance optimization',
    'authentication flow',
    'database migration',
    'API endpoint',
    'user interface',
    'error handling',
    'data validation',
    'security enhancement',
  ];

  return {
    query: options.query || randomItem(queries),
    filters: {
      type: options.type || (randomIntBetween(0, 1) === 1 ? randomItem(ITEM_TYPES) : undefined),
      status: options.status || (randomIntBetween(0, 1) === 1 ? randomItem(ITEM_STATUSES) : undefined),
      priority: options.priority || (randomIntBetween(0, 1) === 1 ? randomItem(PRIORITIES) : undefined),
      tags: randomIntBetween(0, 1) === 1 ? generateTags(randomIntBetween(1, 2)) : undefined,
    },
    sort: options.sort || randomItem(['created_at', 'updated_at', 'priority', 'title']),
    order: options.order || randomItem(['asc', 'desc']),
    limit: options.limit || randomIntBetween(10, 100),
    offset: options.offset || 0,
  };
}

/**
 * Generate random tags
 *
 * @param {number} count - Number of tags to generate
 * @returns {Array} - Array of tag strings
 */
export function generateTags(count = 2) {
  const selectedTags = [];
  const availableTags = [...TAGS];

  for (let i = 0; i < count && availableTags.length > 0; i++) {
    const idx = randomIntBetween(0, availableTags.length - 1);
    selectedTags.push(availableTags[idx]);
    availableTags.splice(idx, 1);
  }

  return selectedTags;
}

/**
 * Generate WebSocket message
 *
 * @param {Object} options - Message options
 * @returns {Object} - WebSocket message
 */
export function generateWebSocketMessage(options = {}) {
  const messageTypes = ['item_created', 'item_updated', 'item_deleted', 'link_created', 'notification'];

  return {
    type: options.type || randomItem(messageTypes),
    payload: options.payload || {
      item_id: randomIntBetween(1, 10000),
      timestamp: new Date().toISOString(),
      data: generateItem(),
    },
    metadata: {
      user_id: `user_${randomIntBetween(1, 1000)}`,
      session_id: randomString(32),
    },
  };
}

/**
 * Generate batch of items for bulk operations
 *
 * @param {number} batchSize - Size of batch
 * @param {Object} options - Generation options
 * @returns {Array} - Batch of items
 */
export function generateBatch(batchSize, options = {}) {
  return generateItems(batchSize, options);
}

export default {
  generateItem,
  generateItems,
  generateLink,
  generateTestCase,
  generateGraphNode,
  generateGraph,
  generateSearchQuery,
  generateTags,
  generateWebSocketMessage,
  generateBatch,
  ITEM_TYPES,
  ITEM_STATUSES,
  PRIORITIES,
  TAGS,
};
