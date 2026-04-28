const DEFAULT_DESCRIPTION = 'No description provided for this item.';

function capitalize(input: string): string {
  if (input.length === 0) {
    return input;
  }
  return `${input.charAt(0).toUpperCase()}${input.slice(1).toLowerCase()}`;
}

function formatViewTypeLabel(view: unknown, type: string): string {
  if (typeof view !== 'string') {
    return type;
  }
  const trimmed = view.trim();
  if (trimmed.length === 0) {
    return type;
  }
  return `${capitalize(trimmed)} · ${type}`;
}

function descriptionOrDefault(description: string | null | undefined): string {
  if (description === null || description === undefined) {
    return DEFAULT_DESCRIPTION;
  }
  const trimmed = description.trim();
  if (trimmed.length === 0) {
    return DEFAULT_DESCRIPTION;
  }
  return description;
}

export { descriptionOrDefault, formatViewTypeLabel };
