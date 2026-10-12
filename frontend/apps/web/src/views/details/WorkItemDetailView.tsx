/**
 * WorkItemDetailView - detail page for user stories, tasks and defects.
 * Replaces the former "Coming Soon" placeholders. Authored by Instinct.
 */
import type { TypedItem } from "@tracertm/types";

import { BaseDetailView } from "./BaseDetailView";

interface WorkItemDetailViewProps {
  item: TypedItem;
  projectId: string;
}

type Row = [string, string | number | boolean | string[] | undefined];

function Field({ label, value }: { label: string; value: Row[1] }) {
  if (value === undefined || value === null || value === "" || (Array.isArray(value) && value.length === 0)) {
    return null;
  }
  return (
    <div className="border-border/40 grid grid-cols-[10rem_1fr] gap-3 border-b py-2 text-sm">
      <dt className="text-muted-foreground font-medium">{label}</dt>
      <dd className="min-w-0 break-words">
        {Array.isArray(value) ? (
          <ul className="list-disc space-y-1 pl-5">
            {value.map((v, i) => (
              <li key={i}>{v}</li>
            ))}
          </ul>
        ) : (
          String(value)
        )}
      </dd>
    </div>
  );
}

function Fields({ rows }: { rows: Row[] }) {
  return (
    <dl>
      {rows.map(([l, v]) => (
        <Field key={l} label={l} value={v} />
      ))}
    </dl>
  );
}

export function WorkItemDetailView({ item, projectId }: WorkItemDetailViewProps) {
  const it = item as unknown as Record<string, unknown>;
  const s = (k: string) => (typeof it[k] === "string" ? (it[k] as string) : undefined);
  const n = (k: string) => (typeof it[k] === "number" ? (it[k] as number) : undefined);
  const a = (k: string) => (Array.isArray(it[k]) ? (it[k] as string[]) : undefined);
  const kind = String(it["type"] ?? "item");

  const typeRows: Row[] =
    kind === "task"
      ? [
          ["Assignee", s("assignee")],
          ["Due date", s("dueDate")],
          ["Estimated hours", n("estimatedHours")],
          ["Actual hours", n("actualHours")],
        ]
      : kind === "bug" || kind === "defect"
        ? [
            ["Severity", s("severity")],
            ["Environment", s("environment")],
            ["Found in", s("foundInVersion")],
            ["Fixed in", s("fixedInVersion")],
            ["Steps to reproduce", a("stepsToReproduce")],
          ]
        : [
            ["As a", s("asA")],
            ["I want", s("iWant")],
            ["So that", s("soThat")],
            ["Story points", n("storyPoints")],
            ["Acceptance criteria", a("acceptanceCriteria")],
          ];

  const common: Row[] = [
    ["Type", kind],
    ["Status", s("status")],
    ["Priority", s("priority")],
    ["View", s("view")],
    ["Project", projectId],
    ["Item ID", s("id")],
    ["Created", s("createdAt") ?? s("created_at")],
    ["Updated", s("updatedAt") ?? s("updated_at")],
  ];

  return (
    <BaseDetailView
      item={item}
      defaultTab="overview"
      tabs={[
        {
          id: "overview",
          label: "Overview",
          content: (
            <div className="space-y-6">
              <p className="text-sm leading-relaxed whitespace-pre-wrap">
                {s("description") || "No description."}
              </p>
              <Fields rows={common} />
            </div>
          ),
        },
        {
          id: "details",
          label: kind === "task" ? "Task" : kind === "story" || kind === "user_story" ? "Story" : "Defect",
          content: <Fields rows={typeRows} />,
        },
        {
          id: "raw",
          label: "Raw",
          content: (
            <pre className="bg-muted/40 max-h-[60vh] overflow-auto rounded-md p-4 text-xs">
              {JSON.stringify(item, null, 2)}
            </pre>
          ),
        },
      ]}
    />
  );
}
