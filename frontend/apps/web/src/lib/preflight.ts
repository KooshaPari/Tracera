type PreflightResult = {
	ok: boolean;
	errors: string[];
};

type PreflightCheck = {
	name: string;
	url: string;
};

const DEFAULT_TIMEOUT_MS = 8000;

async function fetchWithTimeout(url: string, timeoutMs = DEFAULT_TIMEOUT_MS) {
	const controller = new AbortController();
	const timer = setTimeout(() => controller.abort(), timeoutMs);
	try {
		const response = await fetch(url, {
			method: "GET",
			credentials: "omit",
			mode: "cors",
			signal: controller.signal,
		});
		return response;
	} finally {
		clearTimeout(timer);
	}
}

function renderPreflightLoading(checks: PreflightCheck[]): void {
	const root = document.getElementById("root");
	if (!root) {
		throw new Error("Root element not found");
	}

	const items = checks
		.map(
			(check) =>
				`<li data-check="${check.name}" data-state="checking" class="preflight-item" style="display:none;align-items:flex-start;gap:12px;padding:12px;border-radius:12px;margin-bottom:10px;">
					<span data-status style="width:16px;height:16px;border-radius:999px;background:#f59e0b;display:inline-block;margin-top:4px;"></span>
					<div style="flex:1;">
						<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
							<span data-label style="color:#e6edf3;font-weight:600;">${check.name}</span>
							<span data-icon style="font-size:14px;color:#f59e0b;">…</span>
							<span data-status-text style="font-size:12px;color:#fcd34d;font-weight:600;text-transform:uppercase;letter-spacing:0.04em;">Checking</span>
						</div>
					<div data-error style="margin-top:4px;color:#fca5a5;font-size:13px;display:none;"></div>
					<div data-hint style="margin-top:4px;color:#f59e0b;font-size:12px;display:none;"></div>
					<div data-skeleton class="preflight-skeleton" style="width:60%;margin-top:6px;display:none;"></div>
				</div>
					<button data-retry style="margin-left:8px;display:none;padding:6px 10px;border-radius:8px;border:1px solid #f59e0b;background:#f59e0b;color:#0b0f14;font-weight:600;cursor:pointer;">Retry</button>
				</li>`,
		)
		.join("");

	const infraItems: string[] = [];
	const infraSkeleton = infraItems
		.map(
			(name) =>
				`<li data-infra="${name}" data-state="checking" class="infra-item" style="display:flex;align-items:center;gap:12px;padding:10px;border-radius:10px;margin-bottom:8px;">
					<span data-infra-status style="width:12px;height:12px;border-radius:999px;background:#f59e0b;display:inline-block;"></span>
					<span style="flex:1;color:#e6edf3;">${name}</span>
					<span data-infra-text style="font-size:11px;color:#fcd34d;font-weight:600;text-transform:uppercase;letter-spacing:0.04em;">Checking</span>
					<div class="preflight-skeleton" style="width:120px;"></div>
				</li>`,
		)
		.join("");

	root.innerHTML = `
		<style>
		@keyframes shimmer {
			0% { background-position: -400px 0; }
			100% { background-position: 400px 0; }
		}
		@keyframes dots {
			0% { content: ""; }
			33% { content: "."; }
			66% { content: ".."; }
			100% { content: "..."; }
		}
		@keyframes fadePulse {
			0% { opacity: 1; }
			50% { opacity: 0.35; }
			100% { opacity: 1; }
		}
		.preflight-skeleton {
			background: linear-gradient(90deg, #1f2a37 25%, #273444 37%, #1f2a37 63%);
			background-size: 400px 100%;
			animation: shimmer 1.2s ease-in-out infinite;
			height: 10px; border-radius: 999px;
		}
		.preflight-item[data-state="healthy"] { border: 1px solid rgba(34,197,94,0.4); background: rgba(34,197,94,0.08); }
		.preflight-item[data-state="unhealthy"] { border: 1px solid rgba(239,68,68,0.4); background: rgba(239,68,68,0.08); }
		.preflight-item[data-state="checking"] { border: 1px solid rgba(245,158,11,0.4); background: rgba(245,158,11,0.08); }
		.infra-item[data-state="healthy"] { border: 1px solid rgba(34,197,94,0.35); background: rgba(34,197,94,0.06); }
		.infra-item[data-state="unhealthy"] { border: 1px solid rgba(239,68,68,0.35); background: rgba(239,68,68,0.06); }
		.infra-item[data-state="checking"] { border: 1px solid rgba(245,158,11,0.35); background: rgba(245,158,11,0.06); }
		.preflight-fade { animation: fadePulse 520ms ease-in-out; }
		</style>
		<div style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:#0b0f14;color:#e6edf3;font-family:ui-sans-serif,system-ui,-apple-system;">
			<div data-preflight-card style="max-width:780px;padding:32px;border:1px solid #1f2a37;border-radius:16px;background:#0f1720;width:100%;">
				<h1 style="font-size:24px;margin:0 0 8px 0;">Checking service readiness</h1>
				<p style="margin:0 0 16px 0;color:#9aa4b2;">Validating required backend resources before startup.</p>
				<div data-preflight-connecting style="margin:0 0 18px 0;padding:14px 16px;border-radius:12px;background-image:linear-gradient(120deg,rgba(245,158,11,0.35),rgba(245,158,11,0.08) 55%,rgba(251,191,36,0.22));border:1px solid rgba(245,158,11,0.45);color:#fde68a;font-weight:600;">
					<span>Connecting</span><span data-connecting-dots></span>
				</div>
				<div style="height:10px;background:#111827;border-radius:999px;overflow:hidden;margin-bottom:16px;">
					<div data-progress style="width:0%;height:100%;background:#f59e0b;transition:width 200ms ease;"></div>
				</div>
				<ul data-preflight-list style="list-style:none;padding:0;margin:0;display:none;">${items}</ul>
				${
					infraItems.length
						? `<details data-infra-panel style="margin-top:18px;padding-top:12px;border-top:1px solid #1f2a37;display:none;">
					<summary style="cursor:pointer;color:#9aa4b2;font-weight:600;">Infrastructure checks</summary>
					<ul data-infra-list style="list-style:none;padding:0;margin:12px 0 0 0;">${infraSkeleton}</ul>
				</details>`
						: ""
				}
				<div data-preflight-footer style="margin-top:16px;color:#9aa4b2;font-size:14px;display:none;">
					Status updates will appear as checks complete.
				</div>
			</div>
		</div>
	`;
}

function revealFailurePanel(): void {
	const list = document.querySelector(
		"[data-preflight-list]",
	) as HTMLElement | null;
	const infra = document.querySelector(
		"[data-infra-panel]",
	) as HTMLElement | null;
	const footer = document.querySelector(
		"[data-preflight-footer]",
	) as HTMLElement | null;
	if (list) {
		list.style.display = "block";
	}
	if (infra) {
		infra.style.display = "block";
	}
	if (footer) {
		footer.style.display = "block";
	}
}

function revealItem(name: string): void {
	const item = document.querySelector(
		`[data-check="${name}"]`,
	) as HTMLElement | null;
	if (item) {
		item.style.display = "flex";
	}
}

function updatePreflightCheck(
	name: string,
	ok: boolean,
	error?: string,
	hint?: string,
): void {
	const item = document.querySelector(`[data-check="${name}"]`);
	if (!item) return;
	const status = item.querySelector("[data-status]") as HTMLElement | null;
	const icon = item.querySelector("[data-icon]") as HTMLElement | null;
	const errorEl = item.querySelector("[data-error]") as HTMLElement | null;
	const hintEl = item.querySelector("[data-hint]") as HTMLElement | null;
	const skeleton = item.querySelector("[data-skeleton]") as HTMLElement | null;
	const retryBtn = item.querySelector(
		"[data-retry]",
	) as HTMLButtonElement | null;
	const statusText = item.querySelector(
		"[data-status-text]",
	) as HTMLElement | null;
	const isRetrying = error?.toLowerCase().startsWith("retrying") ?? false;
	const state = ok ? "healthy" : isRetrying ? "checking" : "unhealthy";
	if (!ok && !isRetrying) {
		revealItem(name);
		revealFailurePanel();
	}
	if (status) {
		status.style.background =
			state === "healthy"
				? "#22c55e"
				: state === "checking"
					? "#f59e0b"
					: "#ef4444";
	}
	if (icon) {
		icon.textContent =
			state === "healthy" ? "✓" : state === "checking" ? "…" : "✕";
		icon.style.color =
			state === "healthy"
				? "#22c55e"
				: state === "checking"
					? "#f59e0b"
					: "#ef4444";
	}
	if (errorEl) {
		errorEl.textContent = error || "";
		errorEl.style.display = ok ? "none" : "block";
		errorEl.style.color = isRetrying ? "#f59e0b" : "#fca5a5";
	}
	if (hintEl) {
		hintEl.textContent = hint || "";
		hintEl.style.display = hint && !ok ? "block" : "none";
	}
	if (skeleton) {
		skeleton.style.display = ok ? "none" : "block";
	}
	if (retryBtn) {
		retryBtn.style.display = ok ? "none" : "inline-flex";
	}
	item.setAttribute("data-state", state);
	if (statusText) {
		statusText.textContent = ok ? "Healthy" : isRetrying ? "Retrying" : "Down";
		statusText.style.color = ok
			? "#22c55e"
			: isRetrying
				? "#f59e0b"
				: "#ef4444";
	}
}

function updatePreflightProgress(percent: number): void {
	const bar = document.querySelector("[data-progress]") as HTMLElement | null;
	if (bar) {
		bar.style.width = `${percent}%`;
		bar.style.background = percent >= 100 ? "#22c55e" : "#f59e0b";
	}
}

function updateInfraStatus(map: Record<string, string>): void {
	const list = document.querySelector("[data-infra-list]");
	if (!list) return;

	const entries = Array.from(list.querySelectorAll("[data-infra]"));
	entries.forEach((entry) => {
		const key = entry.getAttribute("data-infra") || "";
		const status = map[key] || "unknown";
		const dot = entry.querySelector(
			"[data-infra-status]",
		) as HTMLElement | null;
		const shimmer = entry.querySelector(
			".preflight-skeleton",
		) as HTMLElement | null;
		const text = entry.querySelector("[data-infra-text]") as HTMLElement | null;
		if (dot) {
			dot.style.background =
				status === "healthy"
					? "#22c55e"
					: status === "degraded"
						? "#f59e0b"
						: status === "unhealthy"
							? "#ef4444"
							: "#6b7280";
		}
		if (shimmer) {
			shimmer.style.display = status === "unknown" ? "block" : "none";
		}
		entry.setAttribute(
			"data-state",
			status === "healthy"
				? "healthy"
				: status === "degraded" || status === "unknown"
					? "checking"
					: "unhealthy",
		);
		if (text) {
			const label =
				status === "healthy"
					? "Healthy"
					: status === "degraded"
						? "Degraded"
						: status === "unhealthy"
							? "Down"
							: "Checking";
			text.textContent = label;
			text.style.color =
				status === "healthy"
					? "#22c55e"
					: status === "degraded"
						? "#f59e0b"
						: status === "unhealthy"
							? "#ef4444"
							: "#f59e0b";
		}
	});
}

function pulseItem(element: Element | null): void {
	if (!element) return;
	element.classList.remove("preflight-fade");
	requestAnimationFrame(() => {
		element.classList.add("preflight-fade");
	});
}

function fadeOutAndReload(): void {
	const card = document.querySelector(
		"[data-preflight-card]",
	) as HTMLElement | null;
	if (!card) {
		window.location.reload();
		return;
	}
	card.style.transition = "opacity 220ms ease";
	card.style.opacity = "0";
	setTimeout(() => window.location.reload(), 240);
}

async function checkHealth(
	target: string,
): Promise<{ error: string | null; hint?: string }> {
	const normalized = target.replace(/\/$/, "");
	const explicit = normalized.includes("/api/");
	const paths = explicit ? [""] : ["/health", "/api/v1/health"];

	for (const path of paths) {
		const url = `${normalized}${path}`;
		try {
			const response = await fetchWithTimeout(url);
			if (response.ok) {
				return { error: null };
			}
			if (response.status === 401 || response.status === 403) {
				return {
					error: `Health check failed for ${normalized}`,
					hint: "Blocked by auth; verify health endpoints allow public GET.",
				};
			}
			if (response.type === "opaque") {
				return {
					error: `Health check failed for ${normalized}`,
					hint: "Blocked by CORS. Check allowed origins for this service.",
				};
			}
		} catch {
			const message =
				error instanceof DOMException ? error.name : String(error);
			if (message === "AbortError") {
				return {
					error: `Health check failed for ${normalized}`,
					hint: "Timed out. Service may be slow or blocked by the browser.",
				};
			}
			// Try next path
		}
	}

	return {
		error: `Health check failed for ${normalized}`,
		hint: "Check service URL and local firewall/CORS settings.",
	};
}

async function fetchPythonInfra(
	baseUrl: string,
): Promise<Record<string, string>> {
	const normalized = baseUrl.replace(/\/$/, "");
	const status: Record<string, string> = {};

	try {
		const response = await fetchWithTimeout(`${normalized}/api/v1/health`);
		if (!response.ok) {
			return status;
		}
		const data = (await response.json()) as {
			components?: Record<string, { status?: string }>;
			integration?: Record<string, { status?: string }>;
		};

		const components = data.components || {};
		const integration = data.integration || {};
		if (components.database?.status) {
			status.postgres = components.database.status;
		}
		if (components.redis?.status) {
			status.redis = components.redis.status;
		}
		if (components.nats?.status) {
			status.nats = components.nats.status;
		}
		if (integration.go_backend?.status) {
			status.go_backend = integration.go_backend.status;
		}
	} catch {
		return status;
	}

	return status;
}

export async function runFrontendPreflight(): Promise<PreflightResult> {
	const errors: string[] = [];
	const checks: PreflightCheck[] = [];
	const statusMap = new Map<string, boolean>();
	const devHost =
		window.location.hostname && window.location.hostname !== "localhost"
			? window.location.hostname
			: "127.0.0.1";

	if (import.meta.env.PROD) {
		const baseUrl = import.meta.env?.VITE_API_URL || window.location.origin;
		checks.push({ name: "backend", url: baseUrl });
	} else {
		// Use single Caddy URL when app is served via gateway (port 4000) or VITE_API_URL points at Caddy
		const useCaddy =
			window.location.port === "4000" ||
			(import.meta.env?.VITE_API_URL ?? "").includes(":4000");
		const caddyBase =
			window.location.port === "4000"
				? window.location.origin
				: (import.meta.env?.VITE_API_URL ?? "").replace(/\/$/, "") ||
					`http://${devHost}:4000`;

		if (useCaddy) {
			checks.push({ name: "backend", url: caddyBase });
		} else {
			checks.push({
				name: "python-backend",
				url: `http://${devHost}:8000`,
			});
			checks.push({ name: "go-backend", url: `http://${devHost}:8080` });
		}
	}

	renderPreflightLoading(checks);
	let completed = 0;

	const retryCheck = async (check: PreflightCheck) => {
		const item = document.querySelector(`[data-check="${check.name}"]`);
		pulseItem(item);
		updatePreflightCheck(check.name, false, "Retrying...");
		const { error, hint } = await checkHealth(check.url);
		const ok = !error;
		statusMap.set(check.name, ok);
		updatePreflightCheck(check.name, ok, error || undefined, hint);
		if (
			check.name.includes("python-backend") &&
			ok &&
			document.querySelector("[data-infra-list]")
		) {
			const infra = await fetchPythonInfra(check.url);
			updateInfraStatus(infra);
		}
		const allOk = Array.from(statusMap.values()).every(Boolean);
		if (allOk) {
			fadeOutAndReload();
		}
	};

	for (const check of checks) {
		const { error, hint } = await checkHealth(check.url);
		const ok = !error;
		statusMap.set(check.name, ok);
		updatePreflightCheck(check.name, ok, error || undefined, hint);
		if (
			check.name.includes("python-backend") &&
			ok &&
			document.querySelector("[data-infra-list]")
		) {
			const infra = await fetchPythonInfra(check.url);
			updateInfraStatus(infra);
		}
		const item = document.querySelector(`[data-check="${check.name}"]`);
		const retryBtn = item?.querySelector(
			"[data-retry]",
		) as HTMLButtonElement | null;
		if (retryBtn) {
			retryBtn.onclick = () => {
				retryCheck(check);
			};
		}
		if (error) {
			errors.push(`${check.name}: ${error}`);
		}
		completed += 1;
		updatePreflightProgress(Math.round((completed / checks.length) * 100));
	}

	return { ok: errors.length === 0, errors };
}

export function renderPreflightFailure(result: PreflightResult): void {
	const root = document.getElementById("root");
	if (!root) {
		throw new Error("Root element not found");
	}
	revealFailurePanel();

	const details = result.errors.map((err) => `<li>${err}</li>`).join("");
	const footer = root.querySelector(
		"[data-preflight-footer]",
	) as HTMLElement | null;
	if (!footer) {
		return;
	}

	footer.innerHTML = `
		<div style="margin-top:16px;">
			<h2 style="font-size:18px;margin:0 0 8px 0;color:#fca5a5;">Backend resources unavailable</h2>
			<p style="margin:0 0 12px 0;color:#9aa4b2;">The frontend requires the backend services to be reachable before it can start.</p>
			<ul style="margin:0 0 16px 20px;line-height:1.6;color:#fca5a5;">${details}</ul>
			<div style="display:flex;gap:12px;margin-top:16px;">
				<button id="preflight-retry" style="padding:8px 14px;border-radius:8px;border:1px solid #f59e0b;background:#f59e0b;color:#0b0f14;font-weight:600;cursor:pointer;">Retry all</button>
				<button id="preflight-refresh" style="padding:8px 14px;border-radius:8px;border:1px solid #334155;background:#0f1720;color:#e6edf3;cursor:pointer;">Refresh</button>
			</div>
			<p style="margin:12px 0 0;color:#9aa4b2;">Start the services and retry.</p>
		</div>
	`;

	const retry = document.getElementById("preflight-retry");
	if (retry) {
		retry.onclick = () => fadeOutAndReload();
	}
	const refresh = document.getElementById("preflight-refresh");
	if (refresh) {
		refresh.onclick = () => fadeOutAndReload();
	}
}
