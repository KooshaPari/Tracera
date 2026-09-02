const http = require('http');

const agents = [
  { id: 'agent-1', name: 'researcher', type: 'researcher', status: 'active', capabilities: ['search', 'analysis', 'writing'] },
  { id: 'agent-2', name: 'coder', type: 'coder', status: 'active', capabilities: ['rust', 'typescript', 'python'] },
  { id: 'agent-3', name: 'reviewer', type: 'reviewer', status: 'idle', capabilities: ['code-review', 'security-audit'] },
  { id: 'agent-4', name: 'orchestrator', type: 'orchestrator', status: 'active', capabilities: ['planning', 'delegation', 'monitoring'] },
  { id: 'agent-5', name: 'deployer', type: 'deployer', status: 'idle', capabilities: ['docker', 'kubernetes', 'vercel'] }
];

const tasks = [
  { id: 'task-1', name: 'Audit scorecard', description: 'Comprehensive 155-pillar audit', priority: 'high', status: 'completed', assignedAgent: 'agent-1' },
  { id: 'task-2', name: 'Build SWEE graph CRUD', description: 'Wire graph schema into store trait', priority: 'high', status: 'in_progress', assignedAgent: 'agent-2' },
  { id: 'task-3', name: 'Review PR #1001', description: 'Code review for audit scorecard PR', priority: 'medium', status: 'completed', assignedAgent: 'agent-3' },
  { id: 'task-4', name: 'Plan integration pipeline', description: 'Design AgCord-Tracera data flow', priority: 'high', status: 'completed', assignedAgent: 'agent-4' },
  { id: 'task-5', name: 'Deploy to production', description: 'Full stack deployment', priority: 'critical', status: 'pending', assignedAgent: 'agent-5' },
  { id: 'task-6', name: 'Memory distillation pipeline', description: 'Event ingestion into graph patterns', priority: 'medium', status: 'in_progress', assignedAgent: 'agent-2' },
  { id: 'task-7', name: 'Desktop client build', description: 'Windows tray client via Electron', priority: 'medium', status: 'pending', assignedAgent: 'agent-5' },
  { id: 'task-8', name: 'OpenTelemetry setup', description: 'Observability pipeline', priority: 'low', status: 'pending', assignedAgent: 'agent-4' }
];

const decisions = [
  { id: 'dec-1', title: 'Use SQLite for local dev', status: 'accepted', rationale: 'ADR-DATA-001: dual-store strategy' },
  { id: 'dec-2', title: 'Hexagonal architecture', status: 'accepted', rationale: 'ADR-ARCH-001: isolate core from infrastructure' },
  { id: 'dec-3', title: 'Signed commits required', status: 'accepted', rationale: 'ADR-GOV-003: branch protection' }
];

const server = http.createServer((req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Access-Control-Allow-Origin', '*');
  
  if (req.method === 'OPTIONS') { res.writeHead(200); res.end(); return; }
  
  const url = req.url.split('?')[0];
  
  if (url === '/api/agents') {
    res.writeHead(200); res.end(JSON.stringify(agents));
  } else if (url === '/api/tasks') {
    res.writeHead(200); res.end(JSON.stringify(tasks));
  } else if (url === '/api/decisions') {
    res.writeHead(200); res.end(JSON.stringify(decisions));
  } else if (url === '/api/status') {
    res.writeHead(200); res.end(JSON.stringify({ status: 'ok', agents: agents.length, tasks: tasks.length }));
  } else if (url === '/health') {
    res.writeHead(200); res.end(JSON.stringify({ status: 'ok' }));
  } else {
    res.writeHead(404); res.end(JSON.stringify({ error: 'not found' }));
  }
});

const PORT = process.env.AGCORD_PORT || 3001;
server.listen(PORT, () => console.log(`Mock AgCord server on http://localhost:${PORT}`));
