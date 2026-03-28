interface PreflightResult {
  errors: string[];
  ok: boolean;
}

interface PreflightCheck {
  name: string;
  url: string;
}

type PreflightState = 'checking' | 'healthy' | 'unhealthy';

interface PreflightUpdate {
  error?: string | undefined;
  hint?: string | undefined;
  isRetrying?: boolean | undefined;
  ok: boolean;
}

interface HealthCheckResult {
  error: string | null;
  hint?: string | undefined;
}

type InfraStatus = 'degraded' | 'healthy' | 'unknown' | 'unhealthy';

interface InfraDisplay {
  color: string;
  label: string;
  state: PreflightState;
}

const DEFAULT_TIMEOUT_MS = Number('8000');
const FULL_PERCENT = Number('100');
const RELOAD_DELAY_MS = Number('240');
const HTTP_UNAUTHORIZED = Number('401');
const HTTP_FORBIDDEN = Number('403');
const MIN_ITEM_OPACITY = Number('0.2');
const OPACITY_STEP = Number('0.15');

const PREFLIGHT_STATE_COLORS: Record<PreflightState, string> = {
  checking: '#f59e0b',
  healthy: '#22c55e',
  unhealthy: '#ef4444',
};

const INFRA_STATUS_COLORS: Record<InfraStatus, string> = {
  degraded: '#f59e0b',
  healthy: '#22c55e',
  unknown: '#6b7280',
  unhealthy: '#ef4444',
};

const INFRA_STATUS_LABELS: Record<InfraStatus, string> = {
  degraded: 'Degraded',
  healthy: 'Healthy',
  unknown: 'Checking',
  unhealthy: 'Down',
};

const INFRA_STATUS_STATES: Record<InfraStatus, PreflightState> = {
  degraded: 'checking',
  healthy: 'healthy',
  unknown: 'checking',
  unhealthy: 'unhealthy',
};

const PREFLIGHT_STATUS_ICONS: Record<PreflightState, string> = {
  checking: '●',
  healthy: '✓',
  unhealthy: '✕',
};

const INFRA_DISPLAY_NAMES: Record<string, string> = {
  database: 'Database',
  redis: 'Redis',
  nats: 'NATS',
  go_backend: 'Go Backend',
  mcp: 'MCP',
};

const PREFLIGHT_ITEMS_TOKEN = '__PREFLIGHT_ITEMS__';
const PREFLIGHT_INFRA_TOKEN = '__PREFLIGHT_INFRA__';
const PREFLIGHT_TEMPLATE = `
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
		.preflight-list {
			list-style: none;
			padding: 0;
			margin: 0;
			max-height: 260px;
			overflow-y: auto;
			scroll-behavior: smooth;
		}
		.preflight-item {
			transition: opacity 260ms ease, transform 260ms ease;
		}
		.preflight-item[data-active="true"] {
			opacity: 1;
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
				<ul data-preflight-list class="preflight-list">${PREFLIGHT_ITEMS_TOKEN}</ul>
				${PREFLIGHT_INFRA_TOKEN}
				<div data-preflight-footer style="margin-top:16px;color:#9aa4b2;font-size:14px;display:none;">
					Status updates will appear as checks complete.
				</div>
			</div>
		</div>
	`;

const fetchWithTimeout = async (url: string, timeoutMs = DEFAULT_TIMEOUT_MS): Promise<Response> => {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, {
      credentials: 'omit',
      method: 'GET',
      mode: 'cors',
      signal: controller.signal,
    });
    return response;
  } finally {
    clearTimeout(timer);
  }
};

const buildCheckItems = (checks: PreflightCheck[]): string =>
  checks
    .map(
      (check) =>
        `<li data-check="${check.name}" data-state="checking" data-active="false" class="preflight-item" style="display:none;align-items:flex-start;gap:12px;padding:12px;border-radius:12px;margin-bottom:10px;opacity:0.25;">
					<span data-status style="width:16px;height:16px;border-radius:999px;background:#f59e0b;display:inline-flex;align-items:center;justify-content:center;margin-top:4px;color:#0b0f14;font-weight:700;font-size:10px;">●</span>
					<div style="flex:1;">
						<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
							<span data-label style="color:#e6edf3;font-weight:600;">${check.name}</span>
							<span data-icon style="font-size:14px;color:#f59e0b;">●</span>
							<span data-status-text style="font-size:12px;color:#fcd34d;font-weight:600;text-transform:uppercase;letter-spacing:0.04em;">Checking</span>
						</div>
					<div data-error style="margin-top:4px;color:#fca5a5;font-size:13px;display:none;"></div>
					<div data-hint style="margin-top:4px;color:#f59e0b;font-size:12px;display:none;"></div>
					<div data-skeleton class="preflight-skeleton" style="width:60%;margin-top:6px;display:none;"></div>
				</div>
					<button data-retry style="margin-left:8px;display:none;padding:6px 10px;border-radius:8px;border:1px solid #f59e0b;background:#f59e0b;color:#0b0f14;font-weight:600;cursor:pointer;">Retry</button>
				</li>`,
    )
    .join('');

const getInfraItems = (checks: PreflightCheck[]): string[] => {
  const dependsOnBackend = checks.some((check) => check.name.includes('backend'));
  if (!dependsOnBackend) {
    return [];
  }
  return ['database', 'redis', 'nats', 'go_backend', 'mcp'];
};

const buildInfraSkeleton = (infraItems: string[]): string =>
  infraItems
    .map(
      (name) =>
        `<li data-infra="${name}" data-state="checking" class="infra-item" style="display:flex;align-items:center;gap:12px;padding:10px;border-radius:10px;margin-bottom:8px;">
					<span data-infra-status style="width:12px;height:12px;border-radius:999px;background:#f59e0b;display:inline-block;"></span>
					<span style="flex:1;color:#e6edf3;">${INFRA_DISPLAY_NAMES[name] || name}</span>
					<span data-infra-text style="font-size:11px;color:#fcd34d;font-weight:600;text-transform:uppercase;letter-spacing:0.04em;">Checking</span>
					<div class="preflight-skeleton" style="width:120px;"></div>
				</li>`,
    )
    .join('');

const buildInfraSection = (infraItems: string[]): string => {
  if (infraItems.length === 0) {
    return '';
  }

  const infraSkeleton = buildInfraSkeleton(infraItems);
  return `
			<details data-infra-panel open style="margin-top:18px;padding-top:12px;border-top:1px solid #1f2a37;">
				<summary style="cursor:pointer;color:#9aa4b2;font-weight:600;">Dependencies</summary>
				<ul data-infra-list style="list-style:none;padding:0;margin:12px 0 0 0;">${infraSkeleton}</ul>
			</details>`;
};

const renderPreflightLoading = (checks: PreflightCheck[]): void => {
  const root = document.querySelector<HTMLElement>('#root');
  if (!root) {
    throw new Error('Root element not found');
  }

  const items = buildCheckItems(checks);
  const infraItems = getInfraItems(checks);
  const infraSection = buildInfraSection(infraItems);

  root.innerHTML = PREFLIGHT_TEMPLATE.replace(PREFLIGHT_ITEMS_TOKEN, items).replace(
    PREFLIGHT_INFRA_TOKEN,
    infraSection,
  );

  setRevealOrder(checks);
};

const revealFailurePanel = (): void => {
  const list = document.querySelector('[data-preflight-list]') as HTMLElement | null;
  const infra = document.querySelector('[data-infra-panel]') as HTMLElement | null;
  const footer = document.querySelector('[data-preflight-footer]') as HTMLElement | null;
  if (list) {
    list.style.display = 'block';
  }
  if (infra) {
    infra.style.display = 'block';
  }
  if (footer) {
    footer.style.display = 'block';
  }
};

const revealItem = (name: string): void => {
  const item = document.querySelector(`[data-check="${name}"]`) as HTMLElement | null;
  if (item) {
    item.style.display = 'flex';
    item.dataset['active'] = 'true';
  }
};

const revealState: { index: number; order: string[] } = {
  index: 0,
  order: [],
};

const setRevealOrder = (checks: PreflightCheck[]): void => {
  revealState.order = checks.map((check) => check.name);
  revealState.index = 0;
  revealNext();
};

const revealNext = (): void => {
  if (revealState.index >= revealState.order.length) {
    return;
  }
  const nextName = revealState.order.at(revealState.index);
  if (!nextName) {
    return;
  }
  revealState.index += 1;
  revealItem(nextName);
  setListOpacity();
};

const setListOpacity = (): void => {
  const list = document.querySelector('[data-preflight-list]') as HTMLElement | null;
  if (!list) {
    return;
  }
  const items = [...list.querySelectorAll<HTMLElement>('[data-check]')];
  const total = items.length;
  items.forEach((item, index) => {
    const distance = total - index - 1;
    const opacity = Math.max(MIN_ITEM_OPACITY, 1 - distance * OPACITY_STEP);
    item.style.opacity = `${opacity}`;
  });
};

const scrollToLatest = (name: string): void => {
  const list = document.querySelector('[data-preflight-list]') as HTMLElement | null;
  const item = document.querySelector(`[data-check="${name}"]`) as HTMLElement | null;
  if (!list || !item) {
    return;
  }
  const top = item.offsetTop - 12;
  list.scrollTo({ top, behavior: 'smooth' });
  item.animate(
    [
      { transform: 'translateY(0)' },
      { transform: 'translateY(-6px)' },
      { transform: 'translateY(0)' },
    ],
    { duration: 260, easing: 'cubic-bezier(0.2, 0.9, 0.2, 1)' },
  );
};

const getPreflightState = (update: PreflightUpdate): PreflightState => {
  if (update.ok) {
    return 'healthy';
  }
  if (update.isRetrying) {
    return 'checking';
  }
  return 'unhealthy';
};

const getStatusLabel = (update: PreflightUpdate): string => {
  if (update.ok) {
    return 'Healthy';
  }
  if (update.isRetrying) {
    return 'Retrying';
  }
  return 'Down';
};

const setElementState = (element: Element, state: PreflightState): void => {
  if (element instanceof HTMLElement) {
    element.dataset['state'] = state;
  }
};

const setCheckStatusVisuals = (
  item: Element,
  state: PreflightState,
  update: PreflightUpdate,
): void => {
  const status = item.querySelector('[data-status]') as HTMLElement | null;
  const icon = item.querySelector('[data-icon]') as HTMLElement | null;
  const errorEl = item.querySelector('[data-error]') as HTMLElement | null;
  const hintEl = item.querySelector('[data-hint]') as HTMLElement | null;
  const skeleton = item.querySelector('[data-skeleton]') as HTMLElement | null;
  const retryBtn = item.querySelector('[data-retry]') as HTMLButtonElement | null;
  const statusText = item.querySelector('[data-status-text]') as HTMLElement | null;

  if (status) {
    status.style.background = PREFLIGHT_STATE_COLORS[state];
    status.textContent = PREFLIGHT_STATUS_ICONS[state];
  }
  if (icon) {
    icon.textContent = PREFLIGHT_STATUS_ICONS[state];
    icon.style.color = PREFLIGHT_STATE_COLORS[state];
  }
  updateStatusDetails(update, errorEl, hintEl, skeleton, retryBtn);
  if (statusText) {
    const statusLabel = getStatusLabel(update);
    statusText.textContent = statusLabel;
    statusText.style.color = PREFLIGHT_STATE_COLORS[state];
  }
};

const updateStatusDetails = (
  update: PreflightUpdate,
  errorEl: HTMLElement | null,
  hintEl: HTMLElement | null,
  skeleton: HTMLElement | null,
  retryBtn: HTMLButtonElement | null,
): void => {
  if (errorEl) {
    errorEl.textContent = update.error || '';
    errorEl.style.display = update.ok ? 'none' : 'block';
    errorEl.style.color = update.isRetrying ? '#f59e0b' : '#fca5a5';
  }
  if (hintEl) {
    hintEl.textContent = update.hint || '';
    hintEl.style.display = update.hint && !update.ok ? 'block' : 'none';
  }
  if (skeleton) {
    skeleton.style.display = update.ok ? 'none' : 'block';
  }
  if (retryBtn) {
    retryBtn.style.display = update.ok ? 'none' : 'inline-flex';
  }
};

const updatePreflightCheck = (name: string, update: PreflightUpdate): void => {
  const item = document.querySelector(`[data-check="${name}"]`);
  if (!item) {
    return;
  }
  const state = getPreflightState(update);

  revealNext();
  setCheckStatusVisuals(item, state, update);
  setElementState(item, state);
  setListOpacity();
  scrollToLatest(name);
};

const updatePreflightProgress = (percent: number): void => {
  const bar = document.querySelector('[data-progress]') as HTMLElement | null;
  if (bar) {
    bar.style.width = `${percent}%`;
    bar.style.background =
      percent >= FULL_PERCENT ? PREFLIGHT_STATE_COLORS.healthy : PREFLIGHT_STATE_COLORS.checking;
  }
};

const getInfraDisplay = (status: InfraStatus): InfraDisplay => ({
  color: INFRA_STATUS_COLORS[status],
  label: INFRA_STATUS_LABELS[status],
  state: INFRA_STATUS_STATES[status],
});

const updateInfraStatus = (map: Record<string, InfraStatus>): void => {
  const list = document.querySelector('[data-infra-list]');
  if (!list) {
    return;
  }

  const entries = [...list.querySelectorAll('[data-infra]')];
  entries.forEach((entry) => {
    const key = entry instanceof HTMLElement ? entry.dataset['infra'] || '' : '';
    const status = (map[key] || 'unknown') as InfraStatus;
    const display = getInfraDisplay(status);
    const dot = entry.querySelector('[data-infra-status]') as HTMLElement | null;
    const shimmer = entry.querySelector('.preflight-skeleton') as HTMLElement | null;
    const text = entry.querySelector('[data-infra-text]') as HTMLElement | null;
    if (dot) {
      dot.style.background = display.color;
    }
    if (shimmer) {
      shimmer.style.display = status === 'unknown' ? 'block' : 'none';
    }
    setElementState(entry, display.state);
    if (text) {
      text.textContent = display.label;
      text.style.color = display.color;
    }
  });
};

const pulseItem = (element: Element | null): void => {
  if (!element) {
    return;
  }
  element.classList.remove('preflight-fade');
  requestAnimationFrame(() => {
    element.classList.add('preflight-fade');
  });
};

const fadeOutAndReload = (): void => {
  const card = document.querySelector('[data-preflight-card]') as HTMLElement | null;
  if (!card) {
    window.location.reload();
    return;
  }
  card.style.transition = 'opacity 220ms ease';
  card.style.opacity = '0';
  setTimeout(() => window.location.reload(), RELOAD_DELAY_MS);
};

const checkHealth = async (target: string): Promise<HealthCheckResult> => {
  const normalized = target.replace(/\/$/, '');
  const explicit = normalized.includes('/api/');
  const paths = explicit ? [''] : ['/health', '/api/v1/health'];

  for (const path of paths) {
    const url = `${normalized}${path}`;
    try {
      const response = await fetchWithTimeout(url);
      if (response.ok) {
        return { error: null };
      }
      if (response.status === HTTP_UNAUTHORIZED || response.status === HTTP_FORBIDDEN) {
        return {
          error: `Health check failed for ${normalized}`,
          hint: 'Blocked by auth; verify health endpoints allow public GET.',
        };
      }
      if (response.type === 'opaque') {
        return {
          error: `Health check failed for ${normalized}`,
          hint: 'Blocked by CORS. Check allowed origins for this service.',
        };
      }
    } catch (error) {
      const message = error instanceof DOMException ? error.name : String(error);
      if (message === 'AbortError') {
        return {
          error: `Health check failed for ${normalized}`,
          hint: 'Timed out. Service may be slow or blocked by the browser.',
        };
      }
      // Try next path
    }
  }

  return {
    error: `Health check failed for ${normalized}`,
    hint: 'Check service URL and local firewall/CORS settings.',
  };
};

const normalizeInfraStatus = (value?: string | null): InfraStatus | null => {
  if (!value) {
    return null;
  }
  const lower = value.toLowerCase();
  if (lower === 'healthy' || lower === 'ok') {
    return 'healthy';
  }
  if (lower === 'degraded') {
    return 'degraded';
  }
  if (lower === 'unhealthy' || lower === 'down') {
    return 'unhealthy';
  }
  return null;
};

const fetchPythonInfra = async (baseUrl: string): Promise<Record<string, InfraStatus>> => {
  const normalized = baseUrl.replace(/\/$/, '');
  const status: Record<string, InfraStatus> = {};

  try {
    const response = await fetchWithTimeout(`${normalized}/api/v1/health`);
    if (!response.ok) {
      return status;
    }
    const data = (await response.json()) as {
      components?: Record<string, { status?: string }> | undefined;
      integration?: Record<string, { status?: string }> | undefined;
    };

    const components = data.components || {};
    const integration = data.integration || {};
    const databaseStatus = normalizeInfraStatus(components['database']?.status);
    if (databaseStatus) {
      status['database'] = databaseStatus;
    }
    const redisStatus = normalizeInfraStatus(components['redis']?.status);
    if (redisStatus) {
      status['redis'] = redisStatus;
    }
    const natsStatus = normalizeInfraStatus(components['nats']?.status);
    if (natsStatus) {
      status['nats'] = natsStatus;
    }
    const goStatus = normalizeInfraStatus(integration['go_backend']?.status);
    if (goStatus) {
      status['go_backend'] = goStatus;
    }
  } catch {
    return status;
  }

  return status;
};

const fetchMcpStatus = async (baseUrl: string): Promise<Record<string, InfraStatus>> => {
  const normalized = baseUrl.replace(/\/$/, '');
  try {
    const response = await fetchWithTimeout(`${normalized}/api/v1/mcp/config`);
    if (!response.ok) {
      return { mcp: 'unhealthy' };
    }
    const data = (await response.json()) as { mcp_base_url?: string | null };
    if (data.mcp_base_url && data.mcp_base_url.trim().length > 0) {
      return { mcp: 'healthy' };
    }
    return { mcp: 'degraded' };
  } catch {
    return { mcp: 'unhealthy' };
  }
};

const getDevHost = (): string =>
  window.location.hostname && window.location.hostname !== 'localhost'
    ? window.location.hostname
    : '127.0.0.1';

const buildChecks = (): PreflightCheck[] => {
  const checks: PreflightCheck[] = [];
  if (import.meta.env.PROD) {
    const baseUrl = import.meta.env?.VITE_API_URL || window.location.origin;
    checks.push({ name: 'backend', url: baseUrl });
    return checks;
  }

  // Use single Caddy URL when app is served via gateway (port 4000) or VITE_API_URL points at Caddy
  const devHost = getDevHost();
  const useCaddy =
    window.location.port === '4000' || (import.meta.env?.VITE_API_URL ?? '').includes(':4000');
  const caddyBase =
    window.location.port === '4000'
      ? window.location.origin
      : (import.meta.env?.VITE_API_URL ?? '').replace(/\/$/, '') || `http://${devHost}:4000`;

  if (useCaddy) {
    checks.push({ name: 'backend', url: caddyBase });
    return checks;
  }

  checks.push({ name: 'python-backend', url: `http://${devHost}:8000` });
  checks.push({ name: 'go-backend', url: `http://${devHost}:8080` });
  return checks;
};

const updateInfraIfNeeded = async (check: PreflightCheck, ok: boolean): Promise<void> => {
  const isPythonOrCaddy = check.name === 'python-backend' || check.name === 'backend';
  if (!isPythonOrCaddy || !ok || !document.querySelector('[data-infra-list]')) {
    return;
  }
  const infra = await fetchPythonInfra(check.url);
  const mcpStatus = await fetchMcpStatus(check.url);
  updateInfraStatus({ ...infra, ...mcpStatus });
};

const updateProgress = (completed: number, total: number): void => {
  const percent = Math.round((completed / total) * FULL_PERCENT);
  updatePreflightProgress(percent);
};

const wireRetryButton = (check: PreflightCheck, retryHandler: () => Promise<void>): void => {
  const item = document.querySelector(`[data-check="${check.name}"]`);
  const retryBtn = item?.querySelector('[data-retry]') as HTMLButtonElement | null;
  if (retryBtn) {
    retryBtn.onclick = (): void => {
      retryHandler().catch((error: unknown) => {
        throw error;
      });
    };
  }
};

const handleCheckResult = async (options: {
  check: PreflightCheck;
  completed: number;
  error: string | null;
  errors: string[];
  hint?: string | undefined;
  statusMap: Map<string, boolean>;
  total: number;
}): Promise<number> => {
  const { check, completed, errors, hint, statusMap, total, error } = options;
  const ok = !error;
  statusMap.set(check.name, ok);
  updatePreflightCheck(check.name, { error: error || undefined, hint, ok });
  await updateInfraIfNeeded(check, ok);
  if (error) {
    errors.push(`${check.name}: ${error}`);
  }
  const nextCompleted = completed + 1;
  updateProgress(nextCompleted, total);
  return nextCompleted;
};

export const runFrontendPreflight = async (): Promise<PreflightResult> => {
  const errors: string[] = [];
  const checks = buildChecks();
  const statusMap = new Map<string, boolean>();

  renderPreflightLoading(checks);
  let completed = 0;

  const retryCheck = async (check: PreflightCheck): Promise<void> => {
    const item = document.querySelector(`[data-check="${check.name}"]`);
    pulseItem(item);
    updatePreflightCheck(check.name, {
      error: 'Retrying...',
      isRetrying: true,
      ok: false,
    });
    const { error, hint } = await checkHealth(check.url);
    const ok = !error;
    statusMap.set(check.name, ok);
    updatePreflightCheck(check.name, { error: error || undefined, hint, ok });
    await updateInfraIfNeeded(check, ok);
    const allOk = [...statusMap.values()].every(Boolean);
    if (allOk) {
      fadeOutAndReload();
    }
  };

  for (const check of checks) {
    const { error, hint } = await checkHealth(check.url);
    completed = await handleCheckResult({
      check,
      completed,
      error,
      errors,
      hint,
      statusMap,
      total: checks.length,
    });
    wireRetryButton(check, async (): Promise<void> => {
      await retryCheck(check);
    });
  }

  return { errors, ok: errors.length === 0 };
};

export const renderPreflightFailure = (result: PreflightResult): void => {
  const root = document.querySelector<HTMLElement>('#root');
  if (!root) {
    throw new Error('Root element not found');
  }
  revealFailurePanel();

  const details = result.errors.map((err) => `<li>${err}</li>`).join('');
  const footer = root.querySelector('[data-preflight-footer]') as HTMLElement | null;
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

  const retry = document.querySelector<HTMLElement>('#preflight-retry');
  if (retry) {
    retry.onclick = (): void => fadeOutAndReload();
  }
  const refresh = document.querySelector<HTMLElement>('#preflight-refresh');
  if (refresh) {
    refresh.onclick = (): void => fadeOutAndReload();
  }
};
