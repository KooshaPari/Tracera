import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, cleanup } from "@testing-library/react";
import { toast } from "sonner";

const writeText = vi.fn().mockResolvedValue(undefined);
const webhooks = [
  {
    id: "wh-1",
    projectId: "p",
    name: "CI hook",
    description: "",
    provider: "custom",
    status: "active",
    webhookSecret: "secret-once",
    apiKey: "",
    enabledEvents: ["test.completed"],
    eventFilters: {},
    callbackUrl: "https://example.test/hook",
    callbackHeaders: {},
    defaultSuiteId: "",
    rateLimitPerMinute: 60,
    autoCreateRun: true,
    autoCompleteRun: true,
    verifySignatures: true,
    totalRequests: 0,
    successfulRequests: 0,
    failedRequests: 0,
    lastRequestAt: undefined,
    lastSuccessAt: undefined,
    lastFailureAt: undefined,
    lastErrorMessage: undefined,
    metadata: {},
    version: 1,
    createdAt: "2026-11-20T00:00:00Z",
    updatedAt: "2026-11-20T00:00:00Z",
  },
];

vi.mock("@/hooks/useWebhooks", () => ({
  useWebhooks: () => ({ data: { webhooks }, isLoading: false, error: undefined }),
  useWebhookStats: () => ({ data: undefined }),
  useCreateWebhook: () => ({ mutateAsync: vi.fn() }),
  useSetWebhookStatus: () => ({ mutate: vi.fn() }),
  useDeleteWebhook: () => ({ mutate: vi.fn() }),
}));

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

import { WebhookIntegrationsView } from "./WebhookIntegrationsView";

describe("webhook interaction outcomes", () => {
  beforeEach(() => {
    writeText.mockClear();
    vi.mocked(toast.success).mockClear();
    vi.mocked(toast.error).mockClear();
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: { writeText },
    });
  });

  it("writes the secret to the clipboard when copy is clicked", async () => {
    render(<WebhookIntegrationsView projectId="p" />);
    const copyButton = document.querySelector("button:has(svg.lucide-copy)");
    expect(copyButton).not.toBeNull();
    fireEvent.click(copyButton as HTMLButtonElement);
    await vi.waitFor(() => {
      expect(writeText).toHaveBeenCalledWith("secret-once");
      expect(toast.success).toHaveBeenCalledWith("Webhook secret copied");
    });
    cleanup();
  });

  it("does not offer a secret rotation control", () => {
    render(<WebhookIntegrationsView projectId="p" />);
    expect(screen.queryByTitle("Regenerate Secret")).toBeNull();
    cleanup();
  });
});
