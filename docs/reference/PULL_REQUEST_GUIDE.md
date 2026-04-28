# Pull Request Guidelines

This guide explains how to use the GitHub pull request template for this project.

## Template Location

The PR template is automatically shown when you create a pull request on GitHub:
- **File**: `.github/pull_request_template.md`

## Template Sections

### 1. Summary
Describe what the PR does and why it's needed:
- What problem does it solve?
- What feature does it add?
- Why is this change important?

Example:
```
Fixes the authentication timeout issue that caused users to be logged out
after 5 minutes of inactivity. This change extends the session to 30 minutes
and improves the user experience on slow network connections.
```

### 2. Changes
Provide a bullet list of key changes made:
- One bullet per change
- Be specific about modified files/functions
- Include both additions and removals

Example:
```
- Extended session timeout from 5 to 30 minutes in AuthContext
- Added automatic session refresh mechanism in useAuth hook
- Updated SessionManager to handle network latency better
- Removed deprecated auth.legacy module
```

### 3. Testing
Explain how the changes were validated:
- What unit tests were added?
- What integration tests were updated?
- What manual testing was performed?

Checklist:
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
- [ ] Test coverage maintained or improved

### 4. Screenshots (if applicable)
Include screenshots for UI changes:
- Before and after comparisons recommended
- Annotate key changes
- Show responsive designs on multiple breakpoints

### 5. Checklist
Required validations before merging:

- [ ] **Code builds successfully**
  - Run: `bun run type-check`
  - Ensure no TypeScript errors

- [ ] **Linting passes**
  - Run: `bun run lint:fix`
  - Code follows project style guide

- [ ] **Tests pass**
  - Run: `bun run test:run`
  - All unit and integration tests passing

- [ ] **No console errors in development**
  - Test locally with dev tools open
  - No warnings or errors in console

- [ ] **Documentation updated**
  - README/docs updated if needed
  - Code comments added for complex logic
  - API documentation updated

- [ ] **Commit message is clear and descriptive**
  - Follows conventional commits pattern
  - Explains the why, not just the what

- [ ] **Related issues/tasks linked**
  - Issues referenced: `Closes #123`
  - Tasks linked: `Related to Task #45`

### 6. Related Issues
Link related GitHub issues and tasks:
- `Closes #123` (automatically closes the issue)
- `Related to #456` (manual reference)
- Reference task numbers when applicable

### 7. Migration Notes (if applicable)
Document breaking changes:
- Database migrations required
- Environment variable changes
- API breaking changes
- Configuration updates needed

## Best Practices

### For Reviewers

1. Verify all checklist items are completed
2. Ask questions if anything is unclear
3. Run tests locally if significant logic changes
4. Request changes if standards aren't met

### For Contributors

1. Fill out all sections completely
2. Don't skip the checklist
3. Provide context for reviewers
4. Keep PRs focused on single feature/fix
5. Update docs along with code

## Common Patterns

### Bug Fix PR
```
## Summary
Fix race condition in data synchronization

## Changes
- Added mutex lock to sync handler
- Updated test to catch race conditions
- Added logging for debugging

## Testing
- [ ] Unit tests added/updated ✓
- [ ] Integration tests added/updated ✓
- [ ] Manual testing completed ✓

## Related Issues
Closes #789 (Race condition in sync)
```

### Feature Addition PR
```
## Summary
Add dark mode toggle to user settings

## Changes
- Created DarkModeToggle component
- Added theme context provider
- Updated all components to support both themes
- Added localStorage persistence

## Testing
- [ ] Unit tests added/updated ✓
- [ ] Integration tests added/updated ✓
- [ ] Manual testing completed ✓

## Screenshots
[Before/After screenshots showing dark mode]

## Related Issues
Closes #234 (User request for dark mode)
Related to #456 (UI theme refactoring)
```

## Tips

- **Clear writing**: Use clear, concise language
- **Specific examples**: Provide concrete examples when needed
- **Code snippets**: Include small code snippets showing changes
- **Context matters**: Explain the broader picture, not just code changes
- **Responsive**: Test UI changes on multiple screen sizes
- **Performance**: Consider performance implications
- **Backward compatibility**: Flag any breaking changes clearly

## Review Cycle

1. Create PR with completed template
2. CI/CD runs automatically
3. Request code review from team
4. Address reviewer feedback
5. Update PR description if needed
6. Merge when approved and all checks pass

## Additional Resources

- See `.github/workflows/` for CI/CD pipeline details
- Review `CONTRIBUTING.md` for contribution guidelines
- Check project `README.md` for development setup
