# Visual Feedback Examples

This guide showcases the enhanced visual feedback in TraceRTM CLI with real examples.

## Error Display Examples

### 1. Basic Error with Suggestion

**Code**:
```python
raise TraceRTMError(
    "Failed to connect to database",
    "Check if PostgreSQL is running: `pg_ctl status`"
)
```

**Output**:
```
┌─ Error ──────────────────────────────────────────────────────┐
│ ✗ Failed to connect to database                              │
│                                                               │
│ 💡 Suggestion: Check if PostgreSQL is running: `pg_ctl       │
│    status`                                                    │
└───────────────────────────────────────────────────────────────┘
```

### 2. Validation Error Table

**Code**:
```python
errors = [
    {
        "field": "username",
        "value": "ab",
        "error": "Too short (minimum 3 characters)"
    },
    {
        "field": "email",
        "value": "invalid-email",
        "error": "Invalid email format - must contain @"
    },
    {
        "field": "age",
        "value": "-5",
        "error": "Must be a positive number"
    }
]

raise ValidationError("User registration failed", errors=errors)
```

**Output**:
```
┌─ Validation Errors ──────────────────────────────────────────┐
│ Field      Value           Error                             │
├──────────────────────────────────────────────────────────────┤
│ username   ab              Too short (minimum 3 characters)  │
│ email      invalid-email   Invalid email format - must       │
│                            contain @                          │
│ age        -5              Must be a positive number         │
└──────────────────────────────────────────────────────────────┘

💡 Suggestion: Fix the validation errors shown above and try again
```

### 3. Item Not Found Error

**Code**:
```python
raise ItemNotFoundError("epic", "EPIC-12345")
```

**Output**:
```
┌─ Error ──────────────────────────────────────────────────────┐
│ ✗ Epic with ID 'EPIC-12345' not found                        │
│                                                               │
│ 💡 Suggestion: List available epics: `rtm item list --type   │
│    epic`                                                      │
└───────────────────────────────────────────────────────────────┘
```

### 4. Invalid Format Error

**Code**:
```python
raise InvalidFormatError("JSON", "Unexpected token at line 5, column 12")
```

**Output**:
```
┌─ Error ──────────────────────────────────────────────────────┐
│ ✗ Invalid JSON format: Unexpected token at line 5, column 12 │
│                                                               │
│ 💡 Suggestion: Check the JSON syntax and try again           │
└───────────────────────────────────────────────────────────────┘
```

## Syntax Highlighting Examples

### 1. JSON Export

**Command**:
```bash
rtm export --format json
```

**Output**:
```
┌─ Export: JSON ───────────────────────────────────────────────┐
│  1  {                                                         │
│  2    "project": {                                            │
│  3      "id": "proj-abc123",                                  │
│  4      "name": "My Awesome Project",                         │
│  5      "description": "A sample project"                     │
│  6    },                                                      │
│  7    "items": [                                              │
│  8      {                                                     │
│  9        "id": "ITEM-001",                                   │
│ 10        "title": "Implement user authentication",          │
│ 11        "type": "story",                                    │
│ 12        "status": "in_progress",                            │
│ 13        "priority": "high"                                  │
│ 14      },                                                    │
│ 15      {                                                     │
│ 16        "id": "ITEM-002",                                   │
│ 17        "title": "Add password reset flow",                │
│ 18        "type": "task",                                     │
│ 19        "status": "todo",                                   │
│ 20        "priority": "medium"                                │
│ 21      }                                                     │
│ 22    ]                                                       │
│ 23  }                                                         │
└──────────────────────────────────────────────────────────────┘
```

### 2. YAML Configuration

**Command**:
```bash
rtm export --format yaml
```

**Output**:
```
┌─ Export: YAML ───────────────────────────────────────────────┐
│  1  project:                                                  │
│  2    id: proj-abc123                                         │
│  3    name: My Awesome Project                                │
│  4    description: A sample project                           │
│  5                                                            │
│  6  items:                                                    │
│  7    - id: ITEM-001                                          │
│  8      title: Implement user authentication                  │
│  9      type: story                                           │
│ 10      status: in_progress                                   │
│ 11      priority: high                                        │
│ 12                                                            │
│ 13    - id: ITEM-002                                          │
│ 14      title: Add password reset flow                        │
│ 15      type: task                                            │
│ 16      status: todo                                          │
│ 17      priority: medium                                      │
└──────────────────────────────────────────────────────────────┘
```

### 3. Python Code

**Code**:
```python
code = """
from datetime import datetime
from typing import Optional

class User:
    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email
        self.created_at = datetime.now()

    def activate(self, activation_code: Optional[str] = None):
        \"\"\"Activate the user account.\"\"\"
        if not activation_code:
            raise ValueError("Activation code required")

        # Verify and activate
        self.is_active = True
        return True
"""

display_python(code, title="User Model")
```

**Output**:
```
┌─ User Model ─────────────────────────────────────────────────┐
│  1  from datetime import datetime                            │
│  2  from typing import Optional                              │
│  3                                                            │
│  4  class User:                                               │
│  5      def __init__(self, username: str, email: str):       │
│  6          self.username = username                          │
│  7          self.email = email                                │
│  8          self.created_at = datetime.now()                  │
│  9                                                            │
│ 10      def activate(self, activation_code: Optional[str] =  │
│         None):                                                │
│ 11          """Activate the user account."""                 │
│ 12          if not activation_code:                           │
│ 13              raise ValueError("Activation code required")  │
│ 14                                                            │
│ 15          # Verify and activate                            │
│ 16          self.is_active = True                             │
│ 17          return True                                       │
└──────────────────────────────────────────────────────────────┘
```

### 4. SQL Query

**Code**:
```python
query = """
SELECT
    u.id,
    u.username,
    u.email,
    COUNT(p.id) as project_count,
    MAX(p.updated_at) as last_activity
FROM users u
LEFT JOIN projects p ON u.id = p.owner_id
WHERE u.status = 'active'
    AND u.created_at >= '2024-01-01'
GROUP BY u.id, u.username, u.email
HAVING COUNT(p.id) > 0
ORDER BY last_activity DESC
LIMIT 10;
"""

display_sql(query, title="Active Users Report")
```

**Output**:
```
┌─ Active Users Report ────────────────────────────────────────┐
│  1  SELECT                                                    │
│  2      u.id,                                                 │
│  3      u.username,                                           │
│  4      u.email,                                              │
│  5      COUNT(p.id) as project_count,                        │
│  6      MAX(p.updated_at) as last_activity                   │
│  7  FROM users u                                              │
│  8  LEFT JOIN projects p ON u.id = p.owner_id                │
│  9  WHERE u.status = 'active'                                 │
│ 10      AND u.created_at >= '2024-01-01'                     │
│ 11  GROUP BY u.id, u.username, u.email                        │
│ 12  HAVING COUNT(p.id) > 0                                    │
│ 13  ORDER BY last_activity DESC                               │
│ 14  LIMIT 10;                                                 │
└──────────────────────────────────────────────────────────────┘
```

### 5. Code Diff

**Code**:
```python
old_code = """
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price
    return total
"""

new_code = """
def calculate_total(items):
    \"\"\"Calculate total price with tax.\"\"\"
    subtotal = sum(item.price for item in items)
    tax = subtotal * 0.1
    return subtotal + tax
"""

display_diff(old_code, new_code, title="Pricing Update")
```

**Output**:
```
┌─ Pricing Update ─────────────────────────────────────────────┐
│ --- original                                                  │
│ +++ modified                                                  │
│ @@ -1,5 +1,6 @@                                               │
│  def calculate_total(items):                                  │
│ -    total = 0                                                │
│ -    for item in items:                                       │
│ -        total += item.price                                  │
│ -    return total                                             │
│ +    """Calculate total price with tax."""                   │
│ +    subtotal = sum(item.price for item in items)            │
│ +    tax = subtotal * 0.1                                     │
│ +    return subtotal + tax                                    │
└──────────────────────────────────────────────────────────────┘
```

### 6. JavaScript Code

**Code**:
```python
js_code = """
import React, { useState, useEffect } from 'react';

const UserProfile = ({ userId }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchUser() {
      try {
        const response = await fetch(`/api/users/${userId}`);
        const data = await response.json();
        setUser(data);
      } catch (error) {
        console.error('Failed to fetch user:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchUser();
  }, [userId]);

  if (loading) return <div>Loading...</div>;
  if (!user) return <div>User not found</div>;

  return (
    <div className="user-profile">
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
};

export default UserProfile;
"""

display_code(js_code, "javascript", title="React Component")
```

**Output**:
```
┌─ React Component ────────────────────────────────────────────┐
│  1  import React, { useState, useEffect } from 'react';      │
│  2                                                            │
│  3  const UserProfile = ({ userId }) => {                    │
│  4    const [user, setUser] = useState(null);                │
│  5    const [loading, setLoading] = useState(true);          │
│  6                                                            │
│  7    useEffect(() => {                                       │
│  8      async function fetchUser() {                          │
│  9        try {                                               │
│ 10          const response = await fetch(`/api/users/${      │
│             userId}`);                                        │
│ 11          const data = await response.json();              │
│ 12          setUser(data);                                    │
│ 13        } catch (error) {                                   │
│ 14          console.error('Failed to fetch user:', error);   │
│ 15        } finally {                                         │
│ 16          setLoading(false);                                │
│ 17        }                                                   │
│ 18      }                                                     │
│ 19                                                            │
│ 20      fetchUser();                                          │
│ 21    }, [userId]);                                           │
│ 22                                                            │
│ 23    if (loading) return <div>Loading...</div>;             │
│ 24    if (!user) return <div>User not found</div>;           │
│ 25                                                            │
│ 26    return (                                                │
│ 27      <div className="user-profile">                        │
│ 28        <h1>{user.name}</h1>                                │
│ 29        <p>{user.email}</p>                                 │
│ 30      </div>                                                │
│ 31    );                                                      │
│ 32  };                                                        │
│ 33                                                            │
│ 34  export default UserProfile;                               │
└──────────────────────────────────────────────────────────────┘
```

## Command Examples

### Query with JSON Output

**Command**:
```bash
rtm query --status in_progress --json
```

**Output**:
```
┌─ Query Results (3 items) ────────────────────────────────────┐
│  1  {                                                         │
│  2    "items": [                                              │
│  3      {                                                     │
│  4        "id": "ITEM-005",                                   │
│  5        "title": "Implement search functionality",         │
│  6        "view": "FEATURE",                                  │
│  7        "type": "story",                                    │
│  8        "status": "in_progress",                            │
│  9        "priority": "high",                                 │
│ 10        "owner": "alice"                                    │
│ 11      },                                                    │
│ 12      {                                                     │
│ 13        "id": "ITEM-008",                                   │
│ 14        "title": "Fix login validation",                    │
│ 15        "view": "CODE",                                     │
│ 16        "type": "defect",                                   │
│ 17        "status": "in_progress",                            │
│ 18        "priority": "critical",                             │
│ 19        "owner": "bob"                                      │
│ 20      },                                                    │
│ 21      {                                                     │
│ 22        "id": "ITEM-012",                                   │
│ 23        "title": "Update API documentation",                │
│ 24        "view": "DESIGN",                                   │
│ 25        "type": "task",                                     │
│ 26        "status": "in_progress",                            │
│ 27        "priority": "medium",                               │
│ 28        "owner": "carol"                                    │
│ 29      }                                                     │
│ 30    ],                                                      │
│ 31    "count": 3                                              │
│ 32  }                                                         │
└──────────────────────────────────────────────────────────────┘
```

### Export Markdown

**Command**:
```bash
rtm export --format markdown
```

**Output**:
```markdown
# My Awesome Project

A comprehensive requirements traceability system

**Generated:** 2026-01-31T10:30:00

## FEATURE

### Implement user authentication

- **ID:** `ITEM-001`
- **Type:** story
- **Status:** in_progress
- **Version:** 1
- **Description:** Users should be able to log in with email and password

### Add OAuth support

- **ID:** `ITEM-003`
- **Type:** story
- **Status:** todo
- **Version:** 1
- **Description:** Support Google and GitHub OAuth

## CODE

### Fix login validation

- **ID:** `ITEM-008`
- **Type:** defect
- **Status:** in_progress
- **Version:** 2
- **Description:** Login form doesn't validate empty fields
```

## Real-World Scenarios

### Scenario 1: Creating an Item with Validation

**Command**:
```bash
rtm item create --title "A" --type story --status invalid
```

**Output**:
```
┌─ Validation Errors ──────────────────────────────────────────┐
│ Field    Value     Error                                     │
├──────────────────────────────────────────────────────────────┤
│ title    A         Too short (minimum 3 characters)          │
│ status   invalid   Must be one of: todo, in_progress, done,  │
│                    blocked                                    │
└──────────────────────────────────────────────────────────────┘

💡 Suggestion: Fix the validation errors shown above and try again
```

### Scenario 2: Database Connection Error

**Command**:
```bash
rtm db check
```

**Output**:
```
┌─ Error ──────────────────────────────────────────────────────┐
│ ✗ Failed to connect to database: postgresql://localhost/     │
│   tracertm                                                    │
│                                                               │
│ 💡 Suggestion: Check if PostgreSQL is running: `pg_ctl       │
│    status` or `brew services list`                           │
└───────────────────────────────────────────────────────────────┘
```

### Scenario 3: Configuration Issue

**Command**:
```bash
rtm config get invalid_key
```

**Output**:
```
┌─ Error ──────────────────────────────────────────────────────┐
│ ✗ Invalid configuration for 'invalid_key'                    │
│                                                               │
│ 💡 Suggestion: Update configuration: `rtm config set         │
│    invalid_key <value>`                                      │
└───────────────────────────────────────────────────────────────┘
```

## Benefits Demonstrated

1. **Clear Visual Hierarchy**: Panels and borders make errors stand out
2. **Actionable Feedback**: Every error includes a suggestion
3. **Beautiful Output**: Syntax highlighting makes data readable
4. **Consistent Experience**: All commands use the same styling
5. **Professional Appearance**: CLI looks polished and modern

## See Also

- [Visual Feedback Quick Reference](/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/docs/reference/VISUAL_FEEDBACK_QUICK_REFERENCE.md)
- [Implementation Report](/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/docs/reports/VISUAL_FEEDBACK_ENHANCEMENTS.md)
- [Test Suite](/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/cli/test_visual_feedback.py)
