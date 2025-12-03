# Requirements Traceability - Use Cases & Integration Patterns

## Use Case 1: Agile Software Development

### Scenario
Team building SaaS application with 50 user stories, 200 test cases, 5000 lines of code.

### Flow
```
1. Create Epic: "User Management System"
2. Decompose to Features: "Authentication", "Authorization", "Profile"
3. Decompose to Stories: "Login", "Logout", "Password Reset"
4. Create Test Cases: "Test valid login", "Test invalid credentials"
5. Link to Code: Extract @req:STORY-1 from implementation
6. Query Coverage: Find untested stories
7. Impact Analysis: Show all affected tests when story changes
```

### Benefits
- 100% traceability from epic to code
- Automatic coverage reporting
- Change impact analysis
- Regression test identification

## Use Case 2: Systems Engineering (Aerospace/Defense)

### Scenario
Complex embedded system with 1000+ requirements, strict traceability.

### Flow
```
1. Create System Requirements (SysReq)
2. Decompose to Software Requirements (SWReq)
3. Decompose to Design Specifications (DesSpec)
4. Link to Code Modules
5. Link to Test Cases
6. Generate RTM for compliance
7. Track requirement status through lifecycle
```

### Benefits
- Compliance-ready traceability matrix
- Bidirectional linking
- Temporal versioning for audits
- Change impact analysis

## Use Case 3: Smart Contract Development

### Scenario
DeFi protocol with security-critical contracts.

### Flow
```
1. Create Security Requirements
2. Create Contract Specifications
3. Link to Solidity/Rust contract functions
4. Link to Test Cases (unit + integration)
5. Link to Audit Reports
6. Track requirement status through audits
7. Generate audit trail for compliance
```

### Benefits
- Immutable audit trail
- Security requirement traceability
- Test coverage verification
- Compliance documentation

## Use Case 4: Multi-Team Coordination

### Scenario
10 teams building interconnected microservices.

### Flow
```
1. Create Product Epics (shared)
2. Each team decomposes to their features
3. Link cross-team dependencies
4. Query impact of changes across teams
5. Identify blocking dependencies
6. Track integration points
```

### Benefits
- Dependency visibility
- Cross-team impact analysis
- Integration point tracking
- Coordination efficiency

## Use Case 5: Regulatory Compliance

### Scenario
Healthcare software with FDA/HIPAA requirements.

### Flow
```
1. Create Regulatory Requirements (FDA, HIPAA)
2. Map to Product Features
3. Link to Test Cases
4. Link to Documentation
5. Generate compliance report
6. Track requirement status
7. Audit trail for inspections
```

### Benefits
- Compliance documentation
- Audit trail
- Requirement traceability
- Regulatory reporting

## Integration Patterns

### Pattern 1: Git-Based Workflow
```
1. Requirements stored in git (version-controlled)
2. Annotations in code: @req:REQ-123
3. CI/CD extracts and validates
4. Generates coverage report
5. Blocks merge if coverage < threshold
```

### Pattern 2: IDE Integration
```
1. IDE plugin shows linked requirements
2. Hover over @req annotation → show requirement
3. Quick link to test cases
4. Quick link to related code
5. Inline coverage indicator
```

### Pattern 3: CI/CD Pipeline
```
1. Extract requirements from code
2. Run tests
3. Link test results to requirements
4. Generate coverage report
5. Fail build if coverage < threshold
6. Generate RTM artifact
```

### Pattern 4: MCP Agent Integration
```
1. Agent receives task: "Implement feature X"
2. Agent queries requirements via MCP
3. Agent creates test cases
4. Agent implements code
5. Agent links code to requirements
6. Agent verifies coverage
```

### Pattern 5: Documentation Generation
```
1. Query all requirements by type
2. Generate markdown documentation
3. Include test coverage
4. Include implementation status
5. Generate RTM matrix
6. Generate compliance report
```

## Advanced Queries

### Query 1: Coverage Analysis
```
Find all stories without test cases
→ Identify gaps in testing
```

### Query 2: Impact Analysis
```
Find all requirements affected by change to REQ-123
→ Identify regression tests needed
```

### Query 3: Dependency Chain
```
Find all requirements blocking REQ-456
→ Identify critical path
```

### Query 4: Status Report
```
Count requirements by status
→ Generate project health report
```

### Query 5: Traceability Completeness
```
Find orphaned requirements (no links)
→ Identify incomplete specifications
```

## Integration with Existing Tools

### GitHub Integration
- Extract requirements from issues
- Link to pull requests
- Link to commits
- Generate RTM in PR

### Jira Integration
- Sync requirements bidirectionally
- Link to Jira issues
- Generate RTM in Jira
- Webhook for updates

### Azure DevOps Integration
- Sync work items
- Link to test plans
- Generate RTM
- Pipeline integration

### Slack Integration
- Notify on requirement changes
- Query requirements from Slack
- Generate reports in Slack
- Approval workflows

## Success Metrics by Use Case

### Agile Teams
- Test coverage > 80%
- All stories linked to tests
- Zero orphaned requirements

### Systems Engineering
- 100% bidirectional traceability
- RTM generated automatically
- Compliance audit-ready

### Smart Contracts
- 100% requirement coverage
- Immutable audit trail
- Security verification complete

### Multi-Team
- Zero untracked dependencies
- Cross-team impact visible
- Integration points documented

### Regulatory
- Compliance documentation complete
- Audit trail immutable
- Inspection-ready

