const SETTINGS_KEY = "tracera.desktop.settings";
const CACHE_KEY = "tracera.desktop.endpointCache";
const DEFAULTS = {
  baseUrl: "https://api.tracera.app",
  cacheTtlMinutes: 15,
};

function el(id) {
  return document.getElementById(id);
}

function normalizeBaseUrl(raw) {
  const trimmed = String(raw || "").trim().replace(/\/+$/, "");
  return trimmed || DEFAULTS.baseUrl;
}

function loadSettings() {
  const stored = localStorage.getItem(SETTINGS_KEY);
  if (!stored) return { ...DEFAULTS };
  try {
    const parsed = JSON.parse(stored);
    return {
      baseUrl: normalizeBaseUrl(parsed.baseUrl),
      cacheTtlMinutes: Number(parsed.cacheTtlMinutes) > 0 ? Number(parsed.cacheTtlMinutes) : DEFAULTS.cacheTtlMinutes,
    };
  } catch {
    return { ...DEFAULTS };
  }
}

function saveSettings(next) {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(next));
}

function loadCache() {
  const raw = localStorage.getItem(CACHE_KEY);
  if (!raw) return {};
  try {
    return JSON.parse(raw);
  } catch {
    return {};
  }
}

function setCache(key, value, baseUrl) {
  const cache = loadCache();
  cache[key] = {
    value,
    baseUrl,
    cachedAtMs: Date.now(),
  };
  localStorage.setItem(CACHE_KEY, JSON.stringify(cache));
}

function getCache(key, baseUrl, ttlMinutes) {
  const cache = loadCache();
  const item = cache[key];
  if (!item || item.baseUrl !== baseUrl) return null;
  const ttl = ttlMinutes * 60 * 1000;
  if (Date.now() - item.cachedAtMs > ttl) return null;
  return item.value;
}

function clearCache() {
  localStorage.removeItem(CACHE_KEY);
}

function updateStatus(elm, text, tone = "") {
  elm.textContent = text;
  elm.style.color = tone || "var(--muted)";
}

function renderOutput(data, fromCache, endpoint) {
  const out = JSON.stringify(data, null, 2);
  el("payloadOutput").textContent =
    `${fromCache ? "[cache] " : "[live] "}${endpoint}\n\n${out}`;
}

async function fetchEndpoint(endpoint, settings) {
  const base = normalizeBaseUrl(settings.baseUrl);
  const url = `${base}/${endpoint}`;
  const cacheHit = getCache(endpoint, base, settings.cacheTtlMinutes);

  updateStatus(el("endpointStatus"), `Fetching ${endpoint} ...`, "var(--warn)");
  try {
    const response = await fetch(url, {
      headers: {
        Accept: "application/json",
      },
      method: "GET",
      cache: "no-store",
    });
    if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
    const json = await response.json();
    setCache(endpoint, json, base);
    updateStatus(
      el("endpointStatus"),
      `Live response from ${base} (${endpoint})`,
      "var(--ok)",
    );
    return { data: json, fromCache: false };
  } catch (error) {
    if (cacheHit !== null) {
      updateStatus(
        el("endpointStatus"),
        `Network failed. Using offline cache for ${endpoint}: ${String(error)}`,
        "var(--warn)",
      );
      return { data: cacheHit, fromCache: true };
    }
    throw error;
  }
}

function initUI() {
  const settings = loadSettings();
  el("baseUrl").value = settings.baseUrl;
  el("ttlMinutes").value = String(settings.cacheTtlMinutes);
  updateStatus(el("settingsStatus"), `Loaded settings. Base URL: ${settings.baseUrl}`, "var(--muted)");

  el("saveSettings").addEventListener("click", () => {
    const next = {
      baseUrl: normalizeBaseUrl(el("baseUrl").value),
      cacheTtlMinutes: Number(el("ttlMinutes").value) || DEFAULTS.cacheTtlMinutes,
    };
    saveSettings(next);
    updateStatus(el("settingsStatus"), `Saved base URL: ${next.baseUrl}`, "var(--ok)");
  });

  el("testConnection").addEventListener("click", async () => {
    const current = loadSettings();
    current.baseUrl = normalizeBaseUrl(el("baseUrl").value);
    current.cacheTtlMinutes = Number(el("ttlMinutes").value) || DEFAULTS.cacheTtlMinutes;
    try {
      await fetchEndpoint("coverage-matrix", current);
      updateStatus(el("settingsStatus"), `Connection OK for ${current.baseUrl}`, "var(--ok)");
    } catch {
      updateStatus(el("settingsStatus"), `Connection failed for ${current.baseUrl}`, "var(--bad)");
    }
  });

  el("loadCoverage").addEventListener("click", async () => {
    const s = loadSettings();
    s.baseUrl = normalizeBaseUrl(el("baseUrl").value);
    s.cacheTtlMinutes = Number(el("ttlMinutes").value) || DEFAULTS.cacheTtlMinutes;
    try {
      const res = await fetchEndpoint("coverage-matrix", s);
      renderOutput(res.data, res.fromCache, "coverage-matrix");
    } catch (error) {
      updateStatus(el("endpointStatus"), `Unable to load coverage-matrix: ${error}`, "var(--bad)");
    }
  });

  el("loadGovernance").addEventListener("click", async () => {
    const s = loadSettings();
    s.baseUrl = normalizeBaseUrl(el("baseUrl").value);
    s.cacheTtlMinutes = Number(el("ttlMinutes").value) || DEFAULTS.cacheTtlMinutes;
    try {
      const res = await fetchEndpoint("governance", s);
      renderOutput(res.data, res.fromCache, "governance");
    } catch (error) {
      updateStatus(el("endpointStatus"), `Unable to load governance: ${error}`, "var(--bad)");
    }
  });

  el("clearCache").addEventListener("click", () => {
    clearCache();
    updateStatus(el("endpointStatus"), "Local cache cleared.", "var(--muted)");
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initUI);
} else {
  initUI();
}
