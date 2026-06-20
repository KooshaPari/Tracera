# Perfsprint fixes for internal/services

Apply these in the **backend** repo (paths relative to backend root). Ensure `"errors"` and `"strings"` are in imports where used.

## 1. item_service_impl.go

- **error-format:** Replace every `fmt.Errorf("...")` (no `%`) with `errors.New("...")`.
  - Line 86: `return fmt.Errorf("items list cannot be empty")` → `return errors.New("items list cannot be empty")`
  - Line 133: `return nil, fmt.Errorf("item ID is required")` → `return nil, errors.New("item ID is required")`
  - Line 265: `return fmt.Errorf("item ID is required")` → `return errors.New("item ID is required")`
  - Line 268: `return fmt.Errorf("status is required")` → `return errors.New("status is required")`
  - Line 315: `return fmt.Errorf("items list cannot be empty")` → `return errors.New("items list cannot be empty")`
  - Line 361: `return fmt.Errorf("item ID is required")` → `return errors.New("item ID is required")`
  - Line 399: `return fmt.Errorf("IDs list cannot be empty")` → `return errors.New("IDs list cannot be empty")`
  - Line 459: `return false, fmt.Errorf("item ID is required")` → `return false, errors.New("item ID is required")`
  - Line 524: `return fmt.Errorf("item ID is required")` → `return errors.New("item ID is required")`
  - Line 527: `return fmt.Errorf("project ID is required")` → `return errors.New("project ID is required")`
  - Line 530: `return fmt.Errorf("item title is required")` → `return errors.New("item title is required")`
  - Line 533: `return fmt.Errorf("item title must be less than 255 characters")` → `return errors.New("item title must be less than 255 characters")`

## 2. link_service_impl.go

- **error-format:** Same rule: `fmt.Errorf("...")` → `errors.New("...")`.
  - Lines 58, 61, 64: source/target/link type required
  - Line 113: `return nil, fmt.Errorf("link ID is required")`
  - Lines 159, 208, 245: link ID / item ID required
  - Lines 328, 333: items same project, no self-link
- **string-format:** Replace:
  - `fmt.Sprintf("link:%s", id)` → `"link:" + id`
  - `fmt.Sprintf("dependencies:%s", itemID)` → `"dependencies:" + itemID`
  - `fmt.Sprintf("link:%s", link.ID)` → `"link:" + link.ID`
  - `fmt.Sprintf("dependencies:%s", link.SourceID)` → `"dependencies:" + link.SourceID`
  - `fmt.Sprintf("dependencies:%s", link.TargetID)` → `"dependencies:" + link.TargetID`
  - `fmt.Sprintf("links.%s", eventType)` → `"links." + eventType`

## 3. notification_service.go

- **error-format:** Lines 136, 188: `return fmt.Errorf("notification not found")` → `return errors.New("notification not found")`
- **string-format:** Line 264: `fmt.Sprintf("notifications:%s", userID)` → `"notifications:" + userID`

## 4. project_service_impl.go

- **error-format:** Replace all listed `fmt.Errorf("...")` with `errors.New("...")` (project ID/name/description required, project cannot be nil, length limits).
- **string-format:** Line 465: `return fmt.Sprintf("project:%s", id)` → `return "project:" + id`

## 5. project_service_test.go

- **concat-loop:** Line 389: replace loop that does `longName += "..."` with a `strings.Builder`:
  - `var b strings.Builder` then in loop `b.WriteString("This is a very long project name component ")`, then `longName = b.String()`.

## 6. search_service.go

- **error-format:** Replace all listed `fmt.Errorf("...")` with `errors.New("...")` (query/prefix/item ID required, no item IDs, max 100 items).

## 7. services.go

- **error-format:** Replace all listed `fmt.Errorf("...")` with `errors.New("...")` (item/project/agent title/ID required, link type, NATS not available).
- **string-format:**
  - `fmt.Sprintf("item:%s", id)` → `"item:" + id`
  - `fmt.Sprintf("item:%s", item.ID)` → `"item:" + item.ID`
  - Same for `s.redisClient.Del(ctx, ...)` key args.

## 8. snapshot_service.go

- **error-format:** Replace all listed `fmt.Errorf("...")` with `errors.New("...")` (session ID, sandbox root, S3 key, target directory required).

---

**Import check:** In each file, ensure you have:
```go
import (
    "errors"
    // "fmt" — remove if no longer used, or keep if fmt is still used elsewhere
    "strings"  // only for project_service_test.go concat-loop fix
)
```
