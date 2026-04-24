/**
 * Utility functions for converting project slugs/IDs to human-readable names.
 */

/**
 * Converts a project slug/ID to a human-readable name.
 *
 * Examples:
 * - "proj_staynest_001" → "StayNest Project"
 * - "Proj_staynest_001s" → "StayNest Project" (handles uppercase and trailing 's')
 * - "proj_todo_graph_001" → "Todo Graph Project"
 * - "proj_myapp_002" → "MyApp Project"
 * - "My Project Name" → "My Project Name" (already human-readable)
 *
 * @param slugOrName - Project ID/slug or existing name
 * @returns Human-readable project name
 */
export function slugToDisplayName(slugOrName: string | null | undefined): string {
  if (slugOrName == null || typeof slugOrName !== 'string') {
    return 'Project';
  }
  const trimmed = slugOrName.trim();
  if (!trimmed) return 'Project';
  // If it's already human-readable (doesn't match slug pattern), return as-is
  // Pattern matches: Proj_*, proj_* (case-insensitive), with optional trailing 's'
  if (!trimmed.match(/^[Pp]roj_[a-z0-9_]+s?$/i)) {
    return trimmed || slugOrName;
  }

  // Normalize: convert to lowercase and remove trailing 's' if present
  let normalized = trimmed.toLowerCase();
  if (normalized.endsWith('s') && normalized !== 'proj_s') {
    normalized = normalized.slice(0, -1);
  }

  // Extract the meaningful part (remove "proj_" prefix and numeric suffix)
  const parts = normalized
    .replace(/^proj_/, '')
    .split('_')
    .filter(Boolean);

  // Remove trailing numeric parts (like "001", "002")
  const meaningfulParts = parts.filter((part) => !/^\d+$/.test(part));

  if (meaningfulParts.length === 0) {
    // Fallback: use the original slug with better formatting
    return `${normalized
      .replace(/^proj_/, '')
      .replace(/_/g, ' ')
      .split(' ')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ')} Project`;
  }

  // Convert parts to title case and join
  const displayName = meaningfulParts
    .map((part) => {
      // Handle camelCase or PascalCase
      if (/[a-z][A-Z]/.test(part)) {
        return part.replace(/([a-z])([A-Z])/g, '$1 $2');
      }
      // Handle snake_case or kebab-case
      return part.replace(/[-_]/g, ' ');
    })
    .join(' ')
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');

  return `${displayName} Project`;
}

/**
 * Gets the display name for a project, preferring the name field if it's human-readable,
 * otherwise converting the ID/slug to a human-readable format.
 *
 * @param project - Project object with id and name fields
 * @returns Human-readable project name
 */
export function getProjectDisplayName(
  project:
    | {
        id?: string | null;
        name?: string | null;
      }
    | null
    | undefined,
): string {
  if (project == null) {
    return 'Project';
  }
  const name = project.name;
  const id = project.id ?? '';
  // If name exists and is human-readable (not a slug), use it
  // Pattern matches: Proj_*, proj_* (case-insensitive), with optional trailing 's'
  if (
    name != null &&
    typeof name === 'string' &&
    name.trim() &&
    !name.match(/^[Pp]roj_[a-z0-9_]+s?$/i)
  ) {
    return name;
  }
  // Otherwise, convert the ID to a human-readable name (handles null/undefined id)
  return slugToDisplayName(id);
}
