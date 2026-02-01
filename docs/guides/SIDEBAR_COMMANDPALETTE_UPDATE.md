# Sidebar and Command Palette Navigation Updates

## Summary

Updated the sidebar navigation and command palette to provide comprehensive access to specification routes and commands.

## Changes Made

### 1. Sidebar Navigation (`src/components/layout/Sidebar.tsx`)

**Added Icons:**
- Imported `FileCode` from lucide-react for better visual distinction

**Updated Specifications Section:**
- Changed Dashboard icon from `FileText` to `FileCode` (more appropriate for specifications overview)
- Changed ADRs icon from `ClipboardCheck` to `FileText` (document-like icon)
- Kept Contracts icon as `ClipboardCheck` (checklist/compliance-like)
- Changed Compliance icon from `ClipboardCheck` to `Shield` (security/protection focus)

**Route Structure:**
- Dashboard: `/projects/{projectId}/specifications`
- ADRs: `/projects/{projectId}/adrs`
- Contracts: `/projects/{projectId}/contracts`
- Compliance: `/projects/{projectId}/compliance`

### 2. Command Palette (`src/components/CommandPalette.tsx`)

**Added New Command Category:** `SPECS`

**New Commands Added:**

1. **specs-dashboard** - Specifications Dashboard
   - Description: View all specifications
   - Icon: FileCode
   - Route: `/projects/$projectId/specifications`
   - Keywords: specifications, specs, dashboard

2. **specs-adr** - Architecture Decision Records
   - Description: ADRs for this project
   - Icon: FileText
   - Route: `/projects/$projectId/adrs`
   - Keywords: adr, architecture, decision

3. **specs-contracts** - Contracts
   - Description: Service and API contracts
   - Icon: ClipboardCheck
   - Route: `/projects/$projectId/contracts`
   - Keywords: contract, api, service

4. **specs-compliance** - Compliance
   - Description: Compliance and regulatory requirements
   - Icon: Shield
   - Route: `/projects/$projectId/compliance`
   - Keywords: compliance, regulatory, requirements

**Category Display Order:** `NAVIGATE`, `VIEWS`, `SPECS`, `SYSTEM`, `ACTIONS`

## Usage

### Sidebar Navigation
- Users can see the Specifications section in the left sidebar when a project is active
- All routes follow the established pattern with proper projectId parameter passing
- Consistent icon system makes quick visual navigation easier

### Command Palette
- Press `Cmd+K` (or `Ctrl+K` on Windows/Linux) to open the command palette
- Type "specifications", "adr", "contracts", or "compliance" to filter the SPECS category
- Use arrow keys to navigate and Enter to select a command
- Commands only appear when a project is active

## Files Modified

1. `/frontend/apps/web/src/components/layout/Sidebar.tsx`
   - Updated icon imports
   - Updated Specifications section icons
   
2. `/frontend/apps/web/src/components/CommandPalette.tsx`
   - Added new icons (FileCode, FileText, ClipboardCheck)
   - Updated CommandItem interface to support "SPECS" category
   - Added specCommands array with 4 new specification-related commands
   - Updated categories array to include "SPECS"

## Icon Mapping

| Section | Item | Icon | Purpose |
|---------|------|------|---------|
| Specifications | Dashboard | FileCode | Overview of all specs |
| Specifications | ADRs | FileText | Architecture decisions |
| Specifications | Contracts | ClipboardCheck | Service contracts |
| Specifications | Compliance | Shield | Regulatory requirements |

## Testing Recommendations

1. Verify sidebar displays correctly with collapsed/expanded states
2. Test Command Palette search with specification keywords
3. Confirm all routes navigate correctly with proper projectId
4. Check icon display in both light and dark themes
5. Verify keyboard shortcuts work (Cmd/Ctrl+K for command palette)

## Pattern Consistency

These updates follow the established patterns in the codebase:
- Route structure matches existing projects/{projectId}/... convention
- CommandItem interface and categories match existing structure
- Icon selection follows semantic meaning (FileCode for overview, FileText for documents, etc.)
- Command keywords provide multiple search options for user discoverability
