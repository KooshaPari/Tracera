# Detailed User Journeys - Extended & Enhanced

**Date**: 2025-11-22  
**Version**: 2.0 (EXTENDED)  
**Status**: APPROVED

---

## JOURNEY 1: PROJECT MANAGER - "PLAN AND TRACK PROJECT" (EXTENDED)

### User Profile
- **Name**: Sarah Chen
- **Role**: Senior Product Manager
- **Experience**: 8 years in product management
- **Goals**: Plan complex projects, track progress, identify risks
- **Pain Points**: Manual tracking, lack of visibility, communication overhead
- **Tech Savviness**: High (comfortable with complex tools)

### Journey Duration
- **Total Time**: 45 minutes
- **Frequency**: Daily (5-10 minutes), Weekly (30 minutes planning)
- **Devices**: Desktop (primary), Tablet (secondary)

### Pre-Journey Context
- Sarah has 3 projects to manage
- Team of 12 people (designers, developers, QA)
- Current project: Q1 2025 Product Launch
- Deadline: March 31, 2025 (10 weeks away)
- Status: Planning phase

---

### STEP 1: LOGIN & AUTHENTICATION (2 minutes)

**Trigger**: Sarah opens TraceRTM in browser

**Actions**:
```
1. Sarah navigates to https://tracertm.app
2. Sees login page with "Sign in with WorkOS" button
3. Clicks "Sign in with WorkOS"
4. Redirected to WorkOS login
5. Enters company email: sarah@company.com
6. Enters password
7. Completes MFA (authenticator app)
8. Redirected back to TraceRTM
9. Dashboard loads
```

**System Behavior**:
- Verify JWT token with WorkOS
- Load user profile and permissions
- Load user's organizations
- Load user's projects
- Load user's recent items
- Load user's assigned items
- Initialize real-time subscriptions
- Load user preferences (theme, layout, etc.)

**Expected Outcome**:
- ✅ Sarah is authenticated
- ✅ Dashboard displays
- ✅ Real-time subscriptions active
- ✅ User profile loaded

**Error Scenarios**:
- ❌ MFA fails → Retry MFA
- ❌ Network error → Retry login
- ❌ Session expired → Re-authenticate

---

### STEP 2: VIEW DASHBOARD (3 minutes)

**Trigger**: Sarah lands on dashboard after login

**Dashboard Components**:
```
┌─────────────────────────────────────────────────────────┐
│ TraceRTM Dashboard                                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Welcome, Sarah! 👋                                       │
│                                                          │
│ ┌──────────────────┐  ┌──────────────────┐             │
│ │ Q1 2025 Launch   │  │ Q2 Planning      │             │
│ │ 45% Complete     │  │ 10% Complete     │             │
│ │ 2 weeks behind   │  │ On track         │             │
│ └──────────────────┘  └──────────────────┘             │
│                                                          │
│ ┌──────────────────────────────────────────────────────┐│
│ │ Items by Status                                      ││
│ │ DRAFT: 15  ACTIVE: 8  ARCHIVED: 2                   ││
│ │ ████████░░ 80% Complete                             ││
│ └──────────────────────────────────────────────────────┘│
│                                                          │
│ ┌──────────────────────────────────────────────────────┐│
│ │ Team Status                                          ││
│ │ IDLE: 5  WORKING: 6  ERROR: 1                       ││
│ │ ████████░░ 85% Utilization                          ││
│ └──────────────────────────────────────────────────────┘│
│                                                          │
│ ┌──────────────────────────────────────────────────────┐│
│ │ Recent Activity                                      ││
│ │ • Alice completed "Design Phase" (2h ago)           ││
│ │ • Bob started "Implementation Phase" (1h ago)       ││
│ │ • Quality check failed on "API Design" (30m ago)    ││
│ └──────────────────────────────────────────────────────┘│
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Sarah's Actions**:
```
1. Scans dashboard for project status
2. Notices "Q1 2025 Launch" is 2 weeks behind
3. Sees 1 team member has ERROR status
4. Reads recent activity
5. Identifies quality check failure
6. Decides to investigate quality check failure first
```

**System Behavior**:
- Calculate project completion percentage
- Calculate team utilization
- Fetch recent activity (last 24 hours)
- Fetch quality check results
- Fetch team status
- Real-time updates (every 30 seconds)

**Expected Outcome**:
- ✅ Dashboard displays all metrics
- ✅ Sarah has visibility into project status
- ✅ Sarah identifies issues
- ✅ Real-time updates working

---

### STEP 3: INVESTIGATE QUALITY CHECK FAILURE (5 minutes)

**Trigger**: Sarah clicks on quality check failure notification

**Actions**:
```
1. Sarah clicks "Quality check failed on 'API Design'"
2. Navigates to Quality Checks view
3. Sees failed quality check details:
   - Check Type: Consistency Check
   - Status: FAILED
   - Result: "API endpoints not consistent with design spec"
   - Recommendations:
     * Review API design specification
     * Update API endpoints to match spec
     * Re-run quality check
4. Sarah clicks on "API Design" item
5. Views item details
6. Sees incoming links (Design Phase depends on this)
7. Sees outgoing links (Implementation Phase depends on this)
8. Sees quality check recommendations
```

**System Behavior**:
- Load quality check details
- Load item details
- Load linked items
- Load quality check history
- Load recommendations

**Expected Outcome**:
- ✅ Sarah understands the issue
- ✅ Sarah sees impact (linked items)
- ✅ Sarah has recommendations

---

### STEP 4: CREATE PROJECT STRUCTURE (15 minutes)

**Trigger**: Sarah decides to create project structure

**Actions**:
```
1. Sarah clicks "New Item" button
2. Sees item creation form
3. Enters title: "Q1 2025 Product Launch"
4. Selects type: "REQUIREMENT"
5. Enters description: "Launch new product features for Q1 2025"
6. Adds tags: ["Q1", "Launch", "Product"]
7. Sets priority: "CRITICAL"
8. Sets estimated effort: "50 story points"
9. Sets due date: "2025-03-31"
10. Clicks "Create"
11. Item created successfully
12. Sarah sees item in dashboard
13. Sarah clicks "Add Sub-Item"
14. Creates "Design Phase" (DESIGN type, 15 story points)
15. Creates "Implementation Phase" (IMPLEMENTATION type, 25 story points)
16. Creates "Testing Phase" (TEST type, 10 story points)
17. Creates "Deployment Phase" (DEPLOYMENT type, 5 story points)
```

**Item Creation Form**:
```
┌─────────────────────────────────────────────────────────┐
│ Create Item                                              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Title: [Q1 2025 Product Launch________________]         │
│                                                          │
│ Type: [REQUIREMENT ▼]                                   │
│                                                          │
│ Description:                                             │
│ [Launch new product features for Q1 2025_____________]  │
│ [_________________________________________________]      │
│                                                          │
│ Tags: [Q1] [Launch] [Product] [+ Add Tag]              │
│                                                          │
│ Priority: [CRITICAL ▼]                                  │
│                                                          │
│ Estimated Effort: [50 ▼] story points                   │
│                                                          │
│ Due Date: [2025-03-31]                                  │
│                                                          │
│ Assignees: [+ Add Assignee]                             │
│                                                          │
│ [Cancel] [Create]                                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**System Behavior**:
- Validate input
- Create item in database
- Broadcast real-time event
- Update search index
- Add to activity feed
- Send notifications

**Expected Outcome**:
- ✅ All items created
- ✅ Items appear in dashboard
- ✅ Real-time updates working
- ✅ Notifications sent

---

### STEP 5: CREATE LINKS (10 minutes)

**Trigger**: Sarah wants to show dependencies

**Actions**:
```
1. Sarah clicks "Create Link"
2. Sees link creation form
3. Selects source: "Design Phase"
4. Selects target: "Implementation Phase"
5. Selects type: "DEPENDS_ON"
6. Sets priority: "HIGH"
7. Clicks "Create"
8. Link created successfully
9. Sarah creates more links:
   - "Implementation Phase" DEPENDS_ON "Design Phase"
   - "Testing Phase" DEPENDS_ON "Implementation Phase"
   - "Deployment Phase" DEPENDS_ON "Testing Phase"
10. Sarah sees circular dependency warning (none in this case)
11. Sarah views graph visualization
```

**Link Creation Form**:
```
┌─────────────────────────────────────────────────────────┐
│ Create Link                                              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Source Item: [Design Phase ▼]                           │
│                                                          │
│ Target Item: [Implementation Phase ▼]                   │
│                                                          │
│ Link Type: [DEPENDS_ON ▼]                               │
│                                                          │
│ Priority: [HIGH ▼]                                      │
│                                                          │
│ Description: [_________________________________]        │
│                                                          │
│ [Cancel] [Create]                                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**System Behavior**:
- Validate input
- Detect circular dependencies
- Create link in database
- Broadcast real-time event
- Update graph visualization
- Update search index
- Add to activity feed

**Expected Outcome**:
- ✅ All links created
- ✅ No circular dependencies
- ✅ Graph visualization updated
- ✅ Real-time updates working

---

### STEP 6: VIEW GRAPH VISUALIZATION (5 minutes)

**Trigger**: Sarah clicks "Graph View"

**Graph Display**:
```
                    ┌─────────────┐
                    │ Q1 2025     │
                    │ Launch      │
                    └────┬────────┘
                         │ DEPENDS_ON
                    ┌────▼────────┐
                    │ Design      │
                    │ Phase       │
                    └────┬────────┘
                         │ DEPENDS_ON
                    ┌────▼────────────┐
                    │ Implementation  │
                    │ Phase           │
                    └────┬────────────┘
                         │ DEPENDS_ON
                    ┌────▼────────┐
                    │ Testing     │
                    │ Phase       │
                    └────┬────────┘
                         │ DEPENDS_ON
                    ┌────▼────────┐
                    │ Deployment  │
                    │ Phase       │
                    └─────────────┘
```

**Sarah's Actions**:
```
1. Sarah views graph visualization
2. Sees all items and links
3. Zooms to see full structure
4. Hovers over nodes to see details
5. Clicks on "Design Phase" node
6. Views item details in side panel
7. Sees incoming/outgoing links
8. Sees assigned agents
9. Sees quality checks
10. Closes side panel
11. Filters graph by status
12. Searches for items
```

**System Behavior**:
- Render graph with Cytoscape.js
- Apply force-directed layout
- Optimize performance (1000+ nodes)
- Handle pan/zoom events
- Show node/edge details on hover
- Update in real-time

**Expected Outcome**:
- ✅ Graph renders correctly
- ✅ Performance is good (60 FPS)
- ✅ Interactions work smoothly
- ✅ Real-time updates working

---

### STEP 7: ASSIGN AGENTS (5 minutes)

**Trigger**: Sarah wants to assign work to team members

**Actions**:
```
1. Sarah clicks on "Design Phase" item
2. Sees item details panel
3. Clicks "Assign Agent"
4. Sees list of available agents:
   - Alice (Designer, IDLE)
   - Bob (Developer, IDLE)
   - Charlie (QA, WORKING)
   - Diana (Designer, IDLE)
5. Sarah selects "Alice" (Designer)
6. Clicks "Assign"
7. Alice is assigned to "Design Phase"
8. Sarah assigns:
   - "Implementation Phase" → Bob
   - "Testing Phase" → Charlie
   - "Deployment Phase" → Diana
9. All assignments complete
```

**Assignment Panel**:
```
┌─────────────────────────────────────────────────────────┐
│ Assign Agent                                             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Available Agents:                                        │
│                                                          │
│ ☐ Alice (Designer, IDLE)                                │
│ ☐ Bob (Developer, IDLE)                                 │
│ ☐ Charlie (QA, WORKING)                                 │
│ ☐ Diana (Designer, IDLE)                                │
│                                                          │
│ [Cancel] [Assign]                                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**System Behavior**:
- Load available agents
- Filter by status (IDLE, WORKING)
- Filter by capabilities
- Create assignment
- Update agent status
- Broadcast real-time event
- Send notification to agent

**Expected Outcome**:
- ✅ All agents assigned
- ✅ Agents notified
- ✅ Real-time updates working

---

### STEP 8: MONITOR PROGRESS (5 minutes)

**Trigger**: Sarah wants to track project progress

**Actions**:
```
1. Sarah views dashboard
2. Sees project completion: 45%
3. Sees team status: 5 IDLE, 6 WORKING, 1 ERROR
4. Sees recent activity:
   - Alice started "Design Phase" (just now)
   - Bob is waiting for "Design Phase" to complete
   - Charlie is waiting for "Implementation Phase" to start
5. Sarah sees quality check results
6. Sarah sees risk assessment
7. Sarah sees critical path
8. Sarah sees timeline
```

**Dashboard Metrics**:
```
Project: Q1 2025 Launch
├─ Completion: 45%
├─ Status: On Track (2 weeks behind)
├─ Team Utilization: 85%
├─ Quality Score: 92%
├─ Risk Level: MEDIUM
├─ Critical Path: Design → Implementation → Testing → Deployment
└─ Timeline:
   ├─ Design Phase: 2 weeks (Alice working)
   ├─ Implementation Phase: 3 weeks (waiting for Design)
   ├─ Testing Phase: 1 week (waiting for Implementation)
   └─ Deployment Phase: 1 week (waiting for Testing)
```

**System Behavior**:
- Calculate project metrics
- Calculate team utilization
- Calculate quality score
- Calculate risk level
- Calculate critical path
- Real-time updates (every 30 seconds)

**Expected Outcome**:
- ✅ Sarah has visibility into project status
- ✅ Sarah can identify bottlenecks
- ✅ Sarah can make informed decisions
- ✅ Real-time updates working

---

## JOURNEY 2: DEVELOPER - "IMPLEMENT FEATURE" (EXTENDED)

### User Profile
- **Name**: Bob Martinez
- **Role**: Senior Software Engineer
- **Experience**: 10 years in software development
- **Goals**: Implement features efficiently, maintain code quality, collaborate with team
- **Pain Points**: Context switching, unclear requirements, integration issues
- **Tech Savviness**: Very High (comfortable with complex tools)

### Journey Duration
- **Total Time**: 2 hours
- **Frequency**: Daily (multiple times)
- **Devices**: Desktop (primary)

### Pre-Journey Context
- Bob is assigned to "Implementation Phase"
- Waiting for "Design Phase" to complete
- Design Phase just completed
- Bob can now start implementation
- Requirements are in "API Design" item
- Tests are in "API Tests" item

---

### STEP 1: LOGIN & FIND WORK (5 minutes)

**Trigger**: Bob starts his workday

**Actions**:
```
1. Bob opens TraceRTM
2. Authenticates with WorkOS
3. Lands on dashboard
4. Sees "Implementation Phase" is now available
5. Clicks on "Implementation Phase"
6. Views item details
7. Sees it's assigned to him
8. Sees dependencies:
   - Depends on: "Design Phase" (COMPLETED)
   - Blocks: "Testing Phase" (WAITING)
9. Sees quality checks
10. Sees estimated effort: 25 story points
11. Sees due date: 2 weeks
```

**Expected Outcome**:
- ✅ Bob finds his work
- ✅ Bob understands dependencies
- ✅ Bob understands requirements

---

### STEP 2: CLAIM WORK (2 minutes)

**Trigger**: Bob is ready to start working

**Actions**:
```
1. Bob clicks "Claim Work"
2. Item status changes to ACTIVE
3. Bob's status changes to WORKING
4. Bob sees confirmation: "You are now working on Implementation Phase"
5. Other team members see Bob is working on this item
6. Bob receives notification: "Work claimed successfully"
```

**System Behavior**:
- Update item status to ACTIVE
- Update agent status to WORKING
- Broadcast real-time event
- Send notifications
- Start time tracking

**Expected Outcome**:
- ✅ Bob is now working on the item
- ✅ Team sees Bob is working
- ✅ Real-time updates working

---

### STEP 3: VIEW REQUIREMENTS (5 minutes)

**Trigger**: Bob needs to understand requirements

**Actions**:
```
1. Bob clicks on "API Design" (dependency)
2. Views item details
3. Sees description: "Design RESTful API for user management"
4. Sees quality checks: All PASSED
5. Sees linked items:
   - Implements: "User Management Feature"
   - Tests: "API Tests"
6. Sees comments from Alice (designer):
   - "API endpoints: GET /users, POST /users, GET /users/:id, etc."
   - "Authentication: JWT tokens"
   - "Rate limiting: 100 requests/minute"
7. Bob reads all comments
8. Bob understands requirements
```

**Expected Outcome**:
- ✅ Bob understands requirements
- ✅ Bob sees design decisions
- ✅ Bob sees quality checks

---

### STEP 4: WRITE CODE (30 minutes)

**Trigger**: Bob is ready to write code

**Actions**:
```
1. Bob clicks "Code Editor"
2. Sees code editor with syntax highlighting
3. Starts writing implementation code
4. Code editor shows:
   - Syntax highlighting (TypeScript)
   - Auto-completion suggestions
   - Error detection (real-time)
   - Line numbers
   - Minimap
5. Bob writes API endpoints:
   - GET /users
   - POST /users
   - GET /users/:id
   - PATCH /users/:id
   - DELETE /users/:id
6. Bob adds authentication middleware
7. Bob adds rate limiting
8. Bob formats code (Ctrl+Shift+F)
9. Code is formatted automatically
10. Bob saves code (Ctrl+S)
```

**Code Editor Features**:
```
┌─────────────────────────────────────────────────────────┐
│ Code Editor                                              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 1  import express from 'express';                       │
│ 2  import jwt from 'jsonwebtoken';                      │
│ 3                                                        │
│ 4  const app = express();                               │
│ 5  const users = [];                                    │
│ 6                                                        │
│ 7  // Authentication middleware                         │
│ 8  const auth = (req, res, next) => {                   │
│ 9    const token = req.headers.authorization;           │
│ 10   if (!token) return res.status(401).json({...});    │
│ 11   try {                                              │
│ 12     const decoded = jwt.verify(token, 'secret');     │
│ 13     req.user = decoded;                              │
│ 14     next();                                          │
│ 15   } catch (err) {                                    │
│ 16     res.status(401).json({ error: 'Invalid token' });│
│ 17   }                                                  │
│ 18 };                                                   │
│ 19                                                       │
│ 20 // GET /users                                        │
│ 21 app.get('/users', auth, (req, res) => {             │
│ 22   res.json(users);                                  │
│ 23 });                                                  │
│                                                          │
│ [Format] [Run] [Preview] [Save]                         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**System Behavior**:
- Provide syntax highlighting
- Provide auto-completion
- Detect errors in real-time
- Format code on demand
- Save code to database
- Version code changes
- Track code history

**Expected Outcome**:
- ✅ Bob writes code efficiently
- ✅ Code is formatted correctly
- ✅ Errors are detected
- ✅ Code is saved

---

### STEP 5: PREVIEW CODE (10 minutes)

**Trigger**: Bob wants to test his code

**Actions**:
```
1. Bob clicks "Live Preview"
2. Sees code execution in iframe
3. Sees console output
4. Sees any errors
5. Bob tests API endpoints:
   - GET /users → Returns empty array
   - POST /users → Creates new user
   - GET /users/:id → Returns user
   - PATCH /users/:id → Updates user
   - DELETE /users/:id → Deletes user
6. Bob sees all tests pass
7. Bob sees console output:
   - "Server running on port 3000"
   - "User created: {id: 1, name: 'John'}"
   - "User retrieved: {id: 1, name: 'John'}"
8. Bob is satisfied with implementation
```

**Live Preview**:
```
┌─────────────────────────────────────────────────────────┐
│ Live Preview                                             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Console Output:                                          │
│ > Server running on port 3000                           │
│ > GET /users                                            │
│ > Response: []                                          │
│ > POST /users                                           │
│ > Response: {id: 1, name: 'John'}                       │
│ > GET /users/1                                          │
│ > Response: {id: 1, name: 'John'}                       │
│ > PATCH /users/1                                        │
│ > Response: {id: 1, name: 'John Doe'}                   │
│ > DELETE /users/1                                       │
│ > Response: {success: true}                             │
│                                                          │
│ Errors: None                                             │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**System Behavior**:
- Execute code in sandbox
- Capture console output
- Capture errors
- Display results in real-time
- Allow testing of API endpoints

**Expected Outcome**:
- ✅ Code executes successfully
- ✅ All tests pass
- ✅ No errors

---

### STEP 6: RUN QUALITY CHECKS (5 minutes)

**Trigger**: Bob wants to ensure code quality

**Actions**:
```
1. Bob clicks "Quality Checks"
2. Sees quality check options:
   - Completeness Check
   - Consistency Check
   - Performance Check
   - Security Check
   - Code Quality Check
3. Bob clicks "Run All Checks"
4. Checks run automatically
5. Results:
   - Completeness Check: PASS
   - Consistency Check: PASS
   - Performance Check: PASS
   - Security Check: PASS (with 1 warning)
   - Code Quality Check: PASS
6. Bob sees security warning:
   - "JWT secret should not be hardcoded"
   - Recommendation: "Use environment variable"
7. Bob fixes the issue
8. Runs checks again
9. All checks PASS
```

**Quality Checks Panel**:
```
┌─────────────────────────────────────────────────────────┐
│ Quality Checks                                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ ✓ Completeness Check: PASS                              │
│ ✓ Consistency Check: PASS                               │
│ ✓ Performance Check: PASS                               │
│ ⚠ Security Check: PASS (1 warning)                      │
│   - JWT secret should not be hardcoded                  │
│   - Use environment variable                            │
│ ✓ Code Quality Check: PASS                              │
│                                                          │
│ Overall: PASS (1 warning)                               │
│                                                          │
│ [Run All Checks] [Run Selected]                         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**System Behavior**:
- Run quality checks
- Analyze code
- Detect issues
- Provide recommendations
- Display results
- Track quality metrics

**Expected Outcome**:
- ✅ All quality checks pass
- ✅ Issues identified and fixed
- ✅ Code quality ensured

---

### STEP 7: COMPLETE WORK (3 minutes)

**Trigger**: Bob is done with implementation

**Actions**:
```
1. Bob clicks "Complete Work"
2. Sees confirmation dialog:
   - "Are you sure you want to complete this work?"
   - "This will mark the item as ACTIVE (done)"
   - "The next item 'Testing Phase' will be notified"
3. Bob clicks "Complete"
4. Item status changes to ACTIVE (done)
5. Bob's status changes to IDLE
6. Bob receives confirmation: "Work completed successfully"
7. Charlie (QA) receives notification: "Implementation Phase is complete, Testing Phase is ready"
8. "Testing Phase" item becomes available
9. Bob sees summary:
   - Time spent: 2 hours
   - Code lines: 150
   - Quality score: 95%
   - Issues fixed: 1
```

**Completion Summary**:
```
┌─────────────────────────────────────────────────────────┐
│ Work Completed                                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Item: Implementation Phase                              │
│ Status: ACTIVE (Done)                                   │
│                                                          │
│ Summary:                                                 │
│ ├─ Time Spent: 2 hours                                  │
│ ├─ Code Lines: 150                                      │
│ ├─ Quality Score: 95%                                   │
│ ├─ Issues Fixed: 1                                      │
│ └─ Tests Passed: 5/5                                    │
│                                                          │
│ Next Item: Testing Phase (Charlie)                      │
│                                                          │
│ [View Item] [View Next Item] [Close]                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**System Behavior**:
- Update item status to ACTIVE (done)
- Update agent status to IDLE
- Notify next item assignee
- Calculate time spent
- Calculate quality metrics
- Update project progress
- Broadcast real-time event
- Add to activity feed

**Expected Outcome**:
- ✅ Work marked as complete
- ✅ Next item notified
- ✅ Project progress updated
- ✅ Real-time updates working

---

## JOURNEY 3: REAL-TIME COLLABORATION - "COLLABORATE ON DESIGN" (EXTENDED)

### User Profiles
- **Alice**: Senior Designer (WORKING on Design Phase)
- **Charlie**: Product Designer (IDLE, wants to collaborate)

### Journey Duration
- **Total Time**: 1 hour
- **Frequency**: Ad-hoc (when collaboration needed)
- **Devices**: Desktop (primary)

### Pre-Journey Context
- Alice is working on "Design Phase"
- Charlie wants to collaborate on design
- Both are in same organization
- Both have access to "Design Phase" item
- Real-time collaboration enabled

---

### STEP 1: BOTH LOGIN (2 minutes)

**Trigger**: Alice and Charlie both open TraceRTM

**Actions**:
```
Alice:
1. Opens TraceRTM
2. Authenticates
3. Lands on dashboard
4. Sees "Design Phase" is assigned to her
5. Clicks on "Design Phase"
6. Views item details

Charlie:
1. Opens TraceRTM
2. Authenticates
3. Lands on dashboard
4. Sees "Design Phase" item
5. Clicks on "Design Phase"
6. Views item details
```

**Expected Outcome**:
- ✅ Both authenticated
- ✅ Both viewing same item
- ✅ Real-time subscriptions active

---

### STEP 2: SEE PRESENCE (1 minute)

**Trigger**: Both are viewing same item

**Actions**:
```
Alice sees:
- "Charlie is viewing this item" (presence indicator)
- Charlie's avatar in top-right
- Charlie's cursor position (real-time)
- Charlie's selection (real-time)

Charlie sees:
- "Alice is viewing this item" (presence indicator)
- Alice's avatar in top-right
- Alice's cursor position (real-time)
- Alice's selection (real-time)
```

**Presence Indicator**:
```
┌─────────────────────────────────────────────────────────┐
│ Design Phase                                             │
│ Viewing: Alice (you), Charlie                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ [Alice's avatar] [Charlie's avatar]                      │
│                                                          │
│ Description:                                             │
│ [Design RESTful API for user management_____________]   │
│ [_________________________________________________]      │
│                                                          │
│ Charlie is editing...                                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**System Behavior**:
- Track user presence
- Broadcast presence updates
- Show user avatars
- Show user cursor positions
- Show user selections
- Update in real-time (<500ms)

**Expected Outcome**:
- ✅ Both see each other's presence
- ✅ Presence updates in real-time
- ✅ Cursor positions visible

---

### STEP 3: COLLABORATE ON DESCRIPTION (10 minutes)

**Trigger**: Alice and Charlie start collaborating

**Actions**:
```
Alice:
1. Clicks in description field
2. Starts typing: "Design RESTful API for user management"
3. Sees Charlie's cursor in real-time
4. Sees Charlie's selection in real-time

Charlie:
1. Clicks in description field
2. Sees Alice's cursor
3. Sees Alice's text appearing in real-time
4. Waits for Alice to finish
5. Adds comment: "We should also include role-based access control"
6. Sees Alice's cursor move to comment section

Alice:
1. Sees Charlie's comment in real-time
2. Replies: "Good idea, I'll add that to the design"
3. Updates description to include RBAC
4. Sees Charlie's cursor following her edits

Charlie:
1. Sees Alice's reply in real-time
2. Sees Alice's description update in real-time
3. Adds another comment: "Should we support OAuth 2.0?"
4. Sees Alice's cursor move to reply

Alice:
1. Sees Charlie's comment in real-time
2. Replies: "Yes, OAuth 2.0 is a good addition"
3. Updates description to include OAuth 2.0
```

**Collaboration Features**:
- Real-time text editing (CRDT)
- Cursor position tracking
- Selection tracking
- Comment threading
- Mention support (@Charlie)
- Emoji reactions
- Change highlighting

**System Behavior**:
- Detect concurrent edits
- Merge changes using CRDT
- Broadcast changes in real-time (<100ms)
- Track cursor positions
- Track selections
- Prevent conflicts
- Maintain consistency

**Expected Outcome**:
- ✅ Both can edit simultaneously
- ✅ Changes sync in real-time
- ✅ No conflicts
- ✅ Consistency maintained

---

### STEP 4: OFFLINE WORK (5 minutes)

**Trigger**: Charlie loses internet connection

**Actions**:
```
Charlie:
1. Internet connection drops
2. Sees "Offline" indicator
3. Continues editing (changes queued locally)
4. Adds comment: "Let's also support SAML"
5. Updates description
6. Changes are stored locally
7. Sees "Offline" indicator with sync status

Alice:
1. Continues editing normally
2. Doesn't see Charlie's changes (Charlie is offline)
3. Adds her own changes
4. Sees "Charlie is offline" indicator
```

**Offline Indicator**:
```
┌─────────────────────────────────────────────────────────┐
│ Design Phase                                             │
│ Viewing: Alice, Charlie (Offline)                        │
│ Status: Offline - Changes will sync when online          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ [Alice's avatar] [Charlie's avatar - grayed out]         │
│                                                          │
│ Description:                                             │
│ [Design RESTful API for user management_____________]   │
│ [_________________________________________________]      │
│                                                          │
│ Charlie's offline changes (not synced yet):              │
│ - Added comment: "Let's also support SAML"              │
│ - Updated description                                   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**System Behavior**:
- Detect offline status
- Queue changes locally
- Show offline indicator
- Store changes in local storage
- Prevent sync until online
- Show pending changes

**Expected Outcome**:
- ✅ Charlie can continue working offline
- ✅ Changes are queued locally
- ✅ Offline status visible to Alice

---

### STEP 5: SYNC WHEN ONLINE (5 minutes)

**Trigger**: Charlie regains internet connection

**Actions**:
```
Charlie:
1. Internet connection restored
2. Sees "Syncing..." indicator
3. Changes sync automatically
4. Sees "Synced" indicator
5. Sees Alice's changes (made while offline)
6. Sees conflict resolution (if any)

Alice:
1. Sees Charlie is back online
2. Sees Charlie's offline changes appear
3. Sees "Charlie is online" indicator
4. Sees Charlie's cursor position
5. Sees conflict resolution (if any)
```

**Sync Process**:
```
1. Detect online status
2. Retrieve pending changes from local storage
3. Retrieve remote changes (made while offline)
4. Detect conflicts (concurrent edits)
5. Resolve conflicts using CRDT
6. Merge changes
7. Send merged changes to server
8. Broadcast to all connected clients
9. Update local state
10. Show "Synced" indicator
```

**Conflict Resolution**:
- Algorithm: CRDT (Conflict-free Replicated Data Type)
- Strategy: Last write wins for scalars, union for arrays
- User notification: Show conflicts if any
- Manual resolution: Allow user to choose resolution

**System Behavior**:
- Detect online status
- Retrieve pending changes
- Retrieve remote changes
- Detect conflicts
- Resolve conflicts using CRDT
- Merge changes
- Broadcast to all clients
- Update local state

**Expected Outcome**:
- ✅ Charlie is back online
- ✅ Changes sync automatically
- ✅ Conflicts resolved
- ✅ Consistency maintained
- ✅ Alice sees Charlie's changes

---

### STEP 6: COMPLETE COLLABORATION (3 minutes)

**Trigger**: Alice and Charlie finish collaborating

**Actions**:
```
Alice:
1. Sees all changes synced
2. Reviews final description
3. Sees all comments
4. Sees all changes
5. Clicks "Mark as Complete"
6. Item status changes to ACTIVE (done)
7. Alice's status changes to IDLE
8. Charlie sees "Design Phase is complete"

Charlie:
1. Sees "Design Phase is complete"
2. Sees Alice marked it as complete
3. Sees "Implementation Phase is ready"
4. Sees Bob (developer) is notified
5. Closes item
```

**Completion Summary**:
```
┌─────────────────────────────────────────────────────────┐
│ Collaboration Complete                                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Item: Design Phase                                       │
│ Status: ACTIVE (Done)                                   │
│                                                          │
│ Collaborators:                                           │
│ ├─ Alice (Primary)                                       │
│ └─ Charlie (Collaborator)                               │
│                                                          │
│ Changes:                                                 │
│ ├─ Description updated                                  │
│ ├─ 5 comments added                                     │
│ ├─ 2 attachments added                                  │
│ └─ Quality checks: PASS                                 │
│                                                          │
│ Next Item: Implementation Phase (Bob)                    │
│                                                          │
│ [View Item] [View Next Item] [Close]                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**System Behavior**:
- Update item status
- Update agent status
- Notify next item assignee
- Calculate collaboration metrics
- Update project progress
- Broadcast real-time event
- Add to activity feed

**Expected Outcome**:
- ✅ Collaboration complete
- ✅ Item marked as done
- ✅ Next item notified
- ✅ Project progress updated
- ✅ Real-time updates working


