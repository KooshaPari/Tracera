import type { CanonicalExport } from "@/api/endpoints";

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const readString = (record: Record<string, unknown>, key: string): string | undefined => {
  const value = record[key];
  if (typeof value === "string") {
    return value;
  }
  return undefined;
};

const readOptionalString = (record: Record<string, unknown>, key: string): string | undefined => {
  const value = record[key];
  if (value === undefined) {
    return undefined;
  }
  if (typeof value === "string") {
    return value;
  }
  return undefined;
};

const readOptionalNumber = (record: Record<string, unknown>, key: string): number | undefined => {
  const value = record[key];
  if (value === undefined) {
    return undefined;
  }
  if (typeof value === "number") {
    return value;
  }
  return undefined;
};

const safeJsonParse = (jsonText: string): unknown => {
  try {
    return JSON.parse(jsonText) as unknown;
  } catch {
    return undefined;
  }
};

const parseCanonicalProject = (value: unknown): CanonicalExport["project"] | undefined => {
  if (!isRecord(value)) {
    return undefined;
  }

  const projectId = readString(value, "id");
  const projectName = readString(value, "name");
  if (projectId === undefined || projectName === undefined) {
    return undefined;
  }

  const project: CanonicalExport["project"] = {
    id: projectId,
    name: projectName,
  };
  const description = readOptionalString(value, "description");
  if (description !== undefined) {
    project.description = description;
  }
  const created_at = readOptionalString(value, "created_at");
  if (created_at !== undefined) {
    project.created_at = created_at;
  }
  return project;
};

const parseCanonicalItem = (value: unknown): CanonicalExport["items"][number] | undefined => {
  if (!isRecord(value)) {
    return undefined;
  }

  const id = readString(value, "id");
  const title = readString(value, "title");
  const view = readString(value, "view");
  const type = readString(value, "type");
  const status = readString(value, "status");
  if (
    id === undefined ||
    title === undefined ||
    view === undefined ||
    type === undefined ||
    status === undefined
  ) {
    return undefined;
  }

  const canonicalItem: CanonicalExport["items"][number] = {
    id,
    status,
    title,
    type,
    view,
  };

  const description = readOptionalString(value, "description");
  if (description !== undefined) {
    canonicalItem.description = description;
  }

  const version = readOptionalNumber(value, "version");
  if (version !== undefined) {
    canonicalItem.version = version;
  }

  for (const key of ["source_url", "source_repo", "source_kind"] as const) {
    const provenance = readOptionalString(value, key);
    if (provenance !== undefined) {
      canonicalItem[key] = provenance;
    }
  }

  return canonicalItem;
};

const parseCanonicalItems = (value: unknown): CanonicalExport["items"] | undefined => {
  if (!Array.isArray(value)) {
    return undefined;
  }

  const items: CanonicalExport["items"] = [];
  for (const itemValue of value) {
    const canonicalItem = parseCanonicalItem(itemValue);
    if (canonicalItem === undefined) {
      return undefined;
    }
    items.push(canonicalItem);
  }
  return items;
};

const parseCanonicalLinks = (value: unknown): CanonicalExport["links"] | undefined => {
  if (!Array.isArray(value)) {
    return undefined;
  }

  const links: CanonicalExport["links"] = [];
  for (const linkValue of value) {
    if (!isRecord(linkValue)) {
      return undefined;
    }
    const source_id = readString(linkValue, "source_id");
    const target_id = readString(linkValue, "target_id");
    const type = readString(linkValue, "type");
    if (source_id === undefined || target_id === undefined || type === undefined) {
      return undefined;
    }
    links.push({ source_id, target_id, type });
  }
  return links;
};

export const parseCanonicalExport = (jsonText: string): CanonicalExport | undefined => {
  const parsed = safeJsonParse(jsonText);
  if (!isRecord(parsed)) {
    return undefined;
  }

  const project = parseCanonicalProject(parsed["project"]);
  const items = parseCanonicalItems(parsed["items"]);
  const links = parseCanonicalLinks(parsed["links"]);
  if (project === undefined || items === undefined || links === undefined) {
    return undefined;
  }
  return { items, links, project };
};


