# Vercel AI SDK, Codex & OAuth – Research Summary

Quick reference for using OAuth (or keyless auth) with Vercel AI SDK and Claude Code / Codex so you don’t depend on `ANTHROPIC_API_KEY`.

---

## Target: Chat agent with provider OAuth (like Codex)

**Goal:** Vercel AI powers the chat agent in the frontend. Users **log in with OpenAI or Anthropic** (OAuth — "Sign in with OpenAI" / "Sign in with Anthropic"). **Not BYOK** (no pasting API keys). Same OAuth pattern as Codex: user authenticates with the provider once; the app uses that identity for API calls.

- **Frontend:** useChat → POST to your `/api/chat` (or similar).
- **Auth:** User chooses "Sign in with Anthropic" or "Sign in with OpenAI"; OAuth completes; your app stores a provider access token (or equivalent) for that user.
- **Backend:** For each chat request, backend uses the **user's** provider token to call the model (so usage is on the user's account, not a shared server key).

**Vercel AI SDK + Gateway support:**

1. **useChat** can send per-request headers/body (e.g. `Authorization: Bearer <user_provider_token>` or `body: { provider: 'anthropic', accessToken: '...' }`). Your backend reads the token from the request.
2. **AI Gateway request-scoped BYOK:** When calling `streamText` / `generateText`, you can pass the **user's** credentials per request via `providerOptions.gateway.byok`:
   - `byok: { 'anthropic': [{ apiKey: userAnthropicAccessToken }] }` or
   - `byok: { 'openai': [{ apiKey: userOpenAIAccessToken }] }`
   So the Gateway uses the end-user's token for that request instead of a server API key. No pasted keys — the token comes from your OAuth flow.

**What you need to implement:**

1. **Provider OAuth (Sign in with OpenAI / Sign in with Anthropic)**  
   Your app must implement OAuth with OpenAI and/or Anthropic so that:
   - User clicks "Sign in with Anthropic" (or OpenAI).
   - User is redirected to the provider, authorizes your app.
   - Provider redirects back with an authorization code; your backend exchanges it for an **access token** (and optionally refresh token).
   - You store that token against the user (session or DB) and optionally refresh it.

   **Important:** Public OAuth docs for **Anthropic** (third-party "Sign in with Anthropic" for API access) and **OpenAI** (e.g. Platform OAuth) need to be confirmed. If a provider only offers API keys and no OAuth for third-party apps, you cannot do true "Sign in with X" without BYOK (user pasting key). Codex/Claude Code use a **first-party** login (`claude login` / ChatGPT subscription); for a **third-party** web app you need the provider to offer OAuth or a similar delegated-auth API.

2. **Frontend:** When the user is "logged in" with a provider, send the provider token (or a session id that lets the backend resolve it) on each chat request, e.g. via `DefaultChatTransport` headers or body (see SDK docs: custom headers/body).

3. **Backend chat route:** In your `/api/chat` (or equivalent):
   - Authenticate the user (e.g. your app's session/WorkOS).
   - Read the **provider** token for that user (from session/DB).
   - Call `streamText` with the Gateway and pass that token as request-scoped BYOK:
     - `providerOptions: { gateway: { byok: { anthropic: [{ apiKey: userAnthropicToken }] } } }` or `openai: [{ apiKey: userOpenAIToken }]`.
   - Return the stream to the client (e.g. `toUIMessageStreamResponse()`).

That gives you: **Vercel AI as the chat agent, login with OpenAI/Anthropic via OAuth, no BYOK (no pasted keys), same idea as Codex** — with the caveat that provider OAuth availability must be verified.

---

## Existing solutions: CLIProxyAPI, VibeProxy, CCS (OAuth pattern exists)

These projects already implement the same OAuth pattern: **login with OpenAI/Anthropic (or Gemini/Codex) via OAuth, no BYOK**. You can integrate with them or mirror their approach for your Vercel AI chat agent.

### CLIProxyAPI (core OAuth proxy)

- **Repo:** [router-for-me/CLIProxyAPI](https://github.com/router-for-me/CLIProxyAPI)
- **What it is:** A proxy server that exposes **OpenAI/Gemini/Claude/Codex compatible API** endpoints. Users authenticate via **OAuth** (browser login); no API keys pasted.
- **OAuth support:** OpenAI Codex (GPT), Claude Code, Qwen Code, iFlow, Gemini — "CLI authentication flows" and multi-account round-robin.
- **Use from web:** Exposes OpenAI/Anthropic-compatible API; any client (including your frontend chat) can send requests to the proxy. You either:
  - Run CLIProxyAPI (or a hosted instance) and have users "Sign in with Claude/Codex/Gemini" through the proxy's OAuth flow; then your backend forwards chat requests to the proxy with the user's session/token, or
  - Use the **Go SDK** ([docs/sdk-usage.md](https://github.com/router-for-me/CLIProxyAPI/blob/main/docs/sdk-usage.md)) to embed the proxy logic in your own service so your app does OAuth and then calls providers with the user's token.
- **Management API:** [help.router-for.me/management/api](https://help.router-for.me/management/api) — for managing accounts and proxy config.
- **Guides:** [https://help.router-for.me/](https://help.router-for.me/)

### VibeProxy

- **Repo:** [automazeio/vibeproxy](https://github.com/automazeio/vibeproxy) (listed in CLIProxyAPI "Who is with us?")
- **What it is:** Native macOS menu bar app that uses **Claude Code & ChatGPT subscriptions** with AI coding tools — **no API keys needed**; OAuth only.
- **Pattern:** Same as CLIProxyAPI: OAuth with providers, then proxy exposes a compatible API for tools/Clients.

### CCS (Claude Code Switch)

- **Repo:** [kaitranntt/ccs](https://github.com/kaitranntt/ccs)
- **What it is:** CLI + dashboard to switch between **Claude, Gemini, Codex, Copilot, Antigravity, OpenRouter** (300+ models). Uses **CLIProxyAPI OAuth proxy** for Gemini, Codex, Antigravity; multi-account Claude; API profiles for GLM, Kimi, etc.
- **OAuth providers:** "OAuth providers authenticate via browser on first run. Tokens are cached in `~/.ccs/cliproxy/auth/`."
- **Remote proxy:** CCS v7.x can connect to a **remote CLIProxyAPI** instance — so one team can run one CLIProxyAPI server and many clients (or a web app) use it.
- **Docs:** [docs.ccs.kaitran.ca](https://docs.ccs.kaitran.ca) — OAuth providers, API profiles, remote proxy.

### 9Router (Next.js port of the idea)

- **Repo:** [decolua/9router](https://github.com/decolua/9router)
- **What it is:** Next.js implementation inspired by CLIProxyAPI: format translation (OpenAI/Claude/Gemini/Ollama), combo/fallback, multi-account, **Next.js web dashboard**, support for Cursor, Claude Code, Cline, RooCode — **no API keys needed** (OAuth).
- **Relevance:** Shows the same OAuth proxy pattern implemented in a **web stack** (Next.js), so your Vercel AI frontend could talk to a similar backend or to CLIProxyAPI.

### Summary for your stack

| Solution       | Role                         | Use for your Vercel AI chat agent                                      |
|----------------|------------------------------|-------------------------------------------------------------------------|
| **CLIProxyAPI**| OAuth proxy server           | Self-host or use hosted; point your `/api/chat` backend at it with user session, or embed via Go SDK. |
| **VibeProxy**  | Desktop app using OAuth proxy | Reference for "no API keys" OAuth UX.                                  |
| **CCS**        | CLI + dashboard + remote proxy | Reference for multi-provider OAuth and remote CLIProxyAPI usage.    |
| **9Router**    | Next.js OAuth proxy + dashboard | Reference for doing the same in a web/Next.js app.                  |

So: **the OAuth pattern you want does exist.** CLIProxyAPI + VibeProxy/CCS/9Router prove it. For your frontend chat agent you can:

1. **Option A – Use CLIProxyAPI as backend:** Run (or subscribe to) CLIProxyAPI; implement "Sign in with Claude/Codex/Gemini" via its OAuth flows; have your Vercel AI `useChat` send requests to your backend, which forwards to CLIProxyAPI with the user's auth (session/token from the proxy).
2. **Option B – Same pattern, your backend:** Implement OAuth with the same providers (using the same or similar OAuth endpoints/clients that CLIProxyAPI uses), store user tokens, and call Vercel AI Gateway with request-scoped BYOK (user's token) as in the "Target" section above. CLIProxyAPI and 9Router are references for how the OAuth flow and proxy API are structured.

---

## 1. Vercel AI SDK – How auth works

- **AI SDK** talks to models either via:
  - **Dedicated providers** (e.g. `@ai-sdk/anthropic`) → need provider API keys (e.g. `ANTHROPIC_API_KEY`), or
  - **Vercel AI Gateway** → one endpoint, one auth method (API key or OIDC).

- **Vercel AI Gateway** supports two auth methods:
  1. **API key**: `AI_GATEWAY_API_KEY` (create in [Vercel → AI Gateway → API Keys](https://vercel.com/d?to=/[team]/~/ai-gateway/api-keys)).
  2. **OIDC (OAuth-style, no API key)** when running on Vercel:
     - **Production/Preview**: OIDC is automatic; no env var needed.
     - **Local**: `vercel link` then `vercel env pull` to get the token (or use `vercel dev` for auto-refresh). Token lifetime ~12 hours, then pull again.

With Gateway you use model strings like `anthropic/claude-sonnet-4.5` and the SDK routes to the right provider; no per-provider keys required when using OIDC on Vercel.

**Docs:** [Choosing a provider](https://sdk.vercel.ai/docs/getting-started/choosing-a-provider), [AI Gateway provider](https://sdk.vercel.ai/providers/ai-sdk-providers/ai-gateway), [Authentication](https://vercel.com/docs/ai-gateway/authentication-and-byok/authentication).

---

## 2. Codex (OpenAI) – Auth

- **Codex CLI** ([OpenAI Codex](https://github.com/openai/codex)) is a community provider for the AI SDK: [Codex CLI provider](https://sdk.vercel.ai/providers/community-providers/codex-cli).
- Auth is **not** OAuth in the OIDC sense:
  - Uses **ChatGPT Plus/Pro** (subscription) via the Codex CLI, or
  - **OpenAI API key** via env (e.g. `OPENAI_API_KEY`).
- So “OAuth for Codex” here means: use your existing OpenAI/ChatGPT login through the CLI or API key; there’s no separate “Codex OAuth” flow in the SDK.

---

## 3. Claude Code – Auth (your “OAuth” for Claude)

Two different things:

### A) Claude Code **CLI** (terminal app)

- **Auth**: `claude login` → browser OAuth with Anthropic (Claude Pro/Max). No API key.
- **Using it with Vercel AI Gateway** (so traffic goes through your Gateway):
  - [Claude Code + AI Gateway](https://vercel.com/docs/ai-gateway/coding-agents/claude-code):
  - Set in shell (e.g. `~/.zshrc`):
    - `ANTHROPIC_BASE_URL="https://ai-gateway.vercel.sh"`
    - `ANTHROPIC_AUTH_TOKEN="your-ai-gateway-api-key"`
    - `ANTHROPIC_API_KEY=""`  (must be empty so Claude Code uses `ANTHROPIC_AUTH_TOKEN`).
  - Then run `claude`. Requests go through Vercel AI Gateway (billing/observability on Vercel; you can still use your own keys via [BYOK](https://vercel.com/docs/ai-gateway/authentication-and-byok/byok) if you want).

So for the **CLI**: “your OAuth” is `claude login`; to route via Gateway you add the Gateway API key as above (Gateway itself can later use OIDC when called from a Vercel deployment).

### B) Claude Code **provider for AI SDK** (in your app)

- **Provider**: [ai-sdk-provider-claude-code](https://github.com/ben-vargas/ai-sdk-provider-claude-code) (community).
- **Auth**: Same as CLI — **`claude login`** (browser OAuth). No API key. Uses Claude Pro/Max subscription.
- **Use case**: Apps that call Claude via the Claude Agent SDK and want to use the user’s existing Claude login instead of `ANTHROPIC_API_KEY`.

**Docs:** [Claude Code provider](https://sdk.vercel.ai/providers/community-providers/claude-code).

---

## 4. Using “your OAuth” for Claude Code / Codex in practice

### Option 1: TraceRTM Assistant on Vercel – no ANTHROPIC_API_KEY (OIDC)

- Use **Vercel AI Gateway** as the default provider and model strings (e.g. `anthropic/claude-sonnet-4.5`).
- **Deployed on Vercel**: Do **not** set `ANTHROPIC_API_KEY`. Rely on **OIDC** (automatic). Set `AI_GATEWAY_API_KEY` only if you want to force API key auth.
- **Local**: `vercel link` → `vercel env pull` (and/or `vercel dev`). OIDC token is used when no API key is present.
- Result: “OAuth” = Vercel’s OIDC; no Anthropic API key needed for the app.

### Option 2: Claude Code CLI – “OAuth” + Gateway

- **OAuth**: Run `claude login` once (browser).
- **Gateway**: Add the three env vars above (`ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_API_KEY=""`) so the CLI uses Vercel AI Gateway. Your “identity” is still Claude login; the “key” you add is only the Gateway key for routing.

### Option 3: App uses Claude via Claude Code provider (subscription OAuth)

- Install `ai-sdk-provider-claude-code`, use `claudeCode('sonnet')` (or similar) in the AI SDK.
- Ensure the **environment where the app runs** has completed **`claude login`** (same machine / user that runs the Node process).
- No `ANTHROPIC_API_KEY`; auth is the existing Claude Pro/Max subscription (OAuth via `claude login`).

### Option 4: Codex (OpenAI) in app

- Use **Codex CLI** provider or **OpenAI** provider with **API key** (`OPENAI_API_KEY`) or **ChatGPT subscription** via Codex CLI. There is no separate “Codex OAuth” in the SDK; it’s subscription or API key.

---

## 5. Claude Code CLI → GPT 5.2 Codex + per-session sandbox (recommended pattern)

**Goal:** Use the **literal Claude Code CLI** (or equivalent UX) but **configured to route to GPT 5.2 Codex** (e.g. medium). OAuth via **CLIProxyAPI + Claude Code** (or a "Claude Code router"). **Per-session filesystem sandboxing** in a store that **persists with the chat**.

### 5.0 Claude Code native endpoint override and CCR

**Claude Code natively allows changing its endpoints via environment variables.** No extra package is required to point the CLI at a different API:

- **Base URL and auth:** Set in the environment (e.g. in `~/.zshrc` or when spawning the CLI):
  - `ANTHROPIC_BASE_URL` – base URL of the API (e.g. `https://ai-gateway.vercel.sh` or your proxy).
  - `ANTHROPIC_AUTH_TOKEN` – bearer token for that endpoint (e.g. AI Gateway API key or proxy token).
  - `ANTHROPIC_API_KEY=""` – must be empty so Claude Code uses `ANTHROPIC_AUTH_TOKEN` instead of a raw API key.
- **Claude Code Max (subscription):** Can use `ANTHROPIC_BASE_URL` and `ANTHROPIC_CUSTOM_HEADERS` (e.g. `x-ai-gateway-api-key: Bearer your-key`) so traffic goes through a gateway while keeping subscription auth.

So for a **single proxy** (e.g. CLIProxyAPI or Vercel AI Gateway), you only need to set these env vars; the CLI then talks to that URL. No "router" package required.

**Claude Code Router (CCR)** is a real package that **simplifies** the process when you want more than one backend or routing rules:

- **Package:** [@musistudio/claude-code-router](https://github.com/musistudio/claude-code-router) (npm: `claude-code-router`). Enhanced CLI variant: [@dedenlabs/claude-code-router-cli](https://github.com/dedenlabs/claude-code-router-cli).
- **What it does:** CCR runs a **local proxy server** that speaks the Anthropic-compatible API. You point Claude Code at CCR using the **same env vars** (`ANTHROPIC_BASE_URL` = CCR’s URL, e.g. `http://127.0.0.1:3456`). CCR then:
  - Routes requests to **multiple providers** (OpenRouter, DeepSeek, Ollama, Gemini, Volcengine, etc.) from one config file (`~/.claude-code-router/config.json`).
  - Applies **request/response transformers** per provider so different APIs work with Claude Code’s protocol.
  - Supports **routing rules** (e.g. by model name, context length, background vs thinking) and dynamic model switching via `/model` in Claude Code.
- **When to use:** Use **native env only** when you have one Anthropic-compatible endpoint (e.g. CLIProxyAPI or Vercel Gateway). Use **CCR** when you want multi-provider routing, transformers, and rules in one place without changing Claude Code itself.
- **Comparison for "Claude Code → Codex with OAuth":** CCR is strong for **multi-provider routing and transformation**. For **OAuth + Codex** specifically, **CLIProxyAPI** is built for OAuth and Codex/Claude/Gemini CLI flows; CCR focuses on routing to OpenRouter, DeepSeek, Ollama, Gemini, etc., and may not bundle Codex OAuth. So: **simplest for one proxy (e.g. Codex via CLIProxyAPI) = native env vars only; more features (many providers, rules) = CCR; OAuth + Codex = CLIProxyAPI (or proxy that does Anthropic API → Codex + OAuth) with native env pointing at it.**

### 5.1 Routing: Claude Code CLI → Codex

- **Claude Code CLI** talks to Anthropic's API (or a custom base URL). To use **Codex (GPT 5.2)** as the backend:
  - **Option A – Proxy that accepts Claude Code protocol and routes to Codex:** Run a proxy (e.g. **CLIProxyAPI** or a custom router) that:
    - Accepts requests in the format Claude Code CLI sends (Anthropic-compatible or Claude Code–specific).
    - Routes them to **Codex / GPT 5.2** (e.g. OpenAI/Codex API) and returns responses in the format the CLI expects.
  - **Option B – Point Claude Code at CLIProxyAPI:** If CLIProxyAPI can expose an Anthropic-compatible endpoint that is backed by Codex, set Claude Code env (e.g. `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`) to that proxy so the CLI uses Codex without changing the CLI binary.
  - **Option C – Use Codex CLI, same UX:** If "Claude Code CLI" is mainly about UX (session, sandbox, OAuth), run **Codex CLI** instead, pointed at **CLIProxyAPI** for OAuth; keep the same **per-session sandbox** and **chat-persisted store** below. The "router" is then: frontend/chat → your backend → Codex CLI (cwd = session sandbox, env = CLIProxyAPI auth).

**Conclusion:** **CLIProxyAPI + Claude Code** or **Claude Code router** is the right place for OAuth and routing. Either (1) Claude Code CLI → proxy → Codex, or (2) Codex CLI → CLIProxyAPI, with session sandbox and persistence shared.

### 5.2 Per-session FS sandbox that persists with the chat

- **Session store:** Introduce a **chat session** entity keyed by `session_id` (and optionally `user_id`, `project_id`). Persist in DB, e.g. `chat_sessions(session_id, user_id, project_id, provider, model, sandbox_path, created_at, updated_at)`.
- **Sandbox path:** One directory per session, e.g. `SANDBOX_BASE / session_id`. Create the directory on **first message** of that session; reuse for all subsequent messages in that session. This is the **per-session FS sandbox**.
- **Persistence with chat:**
  - **Live:** All tool runs (file edits, runs) for that chat use `cwd = sandbox_path`. So the FS state is "persisted" for the lifetime of the session (same path for the whole conversation).
  - **Durable:** To persist across server restarts or "resume chat later", either:
    - Keep the directory on a durable volume (same path after restart), or
    - Snapshot the sandbox (e.g. tar/zip) to blob storage when the session is closed or periodically, and restore it when the user resumes that session (optional).
- **Invocation:** When running **Claude Code CLI** (or Codex CLI) for a given chat request:
  - Resolve or create `session_id` (from request body or create new).
  - Resolve or create `sandbox_path` for that `session_id` (create dir if missing).
  - Run the CLI with `cwd = sandbox_path` and env set for OAuth/proxy (e.g. CLIProxyAPI token or `ANTHROPIC_BASE_URL` + auth for Claude Code router).

### 5.3 Fit with existing code

- **Chat:** `/api/v1/chat/stream` and `ChatRequest` today have no `session_id`. Add an optional `session_id`; if absent, create a new session and return it in the stream (e.g. first SSE event or header) so the client can send it on subsequent requests. Persist messages per session if you want history in the store.
- **AIService:** Already has `working_directory` for tool runs. For the CLI-based flow, the **session sandbox path** is that working directory: pass it when starting the CLI (e.g. CodexAgentService / Claude Code runner) so all CLI activity is scoped to that directory.
- **CodexAgentService:** Already uses `--cwd`, `--sandbox`, env. Extend it (or add a session-aware runner) to: take `session_id` → resolve `sandbox_path` from session store → run CLI with `cwd = sandbox_path` and proxy auth in env.

### 5.4 Summary

| Piece | Solution |
|--------|----------|
| **CLI** | Claude Code CLI (routed to Codex) or Codex CLI. |
| **OAuth / routing** | CLIProxyAPI + Claude Code, or Claude Code router (proxy that speaks Claude Code protocol and calls Codex). |
| **Per-session sandbox** | One directory per `session_id`; create on first use; pass as `cwd` to CLI. |
| **Persists with chat** | Session store (DB) holds `session_id ↔ sandbox_path`; optionally snapshot sandbox to blob for resume. |

---

## 6. References

| Topic | Link |
|--------|------|
| AI SDK intro | https://sdk.vercel.ai/docs |
| Choosing provider / Gateway | https://sdk.vercel.ai/docs/getting-started/choosing-a-provider |
| AI Gateway provider (OIDC, API key) | https://sdk.vercel.ai/providers/ai-sdk-providers/ai-gateway |
| Vercel AI Gateway auth | https://vercel.com/docs/ai-gateway/authentication-and-byok/authentication |
| OIDC (Vercel) | https://vercel.com/docs/oidc |
| Claude Code + AI Gateway | https://vercel.com/docs/ai-gateway/coding-agents/claude-code |
| Claude Code provider (AI SDK) | https://sdk.vercel.ai/providers/community-providers/claude-code |
| Codex CLI provider | https://sdk.vercel.ai/providers/community-providers/codex-cli |
| Chatbot (useChat, transport) | https://sdk.vercel.ai/docs/ai-sdk-ui/chatbot |
| **Embedded CLIProxy + Agent SDK (subagents)** | [EMBEDDED_CLIPROXY_AND_AGENT_SDK_RESEARCH.md](EMBEDDED_CLIPROXY_AND_AGENT_SDK_RESEARCH.md) (this repo) |

---

## 7. TL;DR for “use my OAuth for Claude Code / Codex”

- **Claude Code**: Your OAuth is **`claude login`** (Claude Pro/Max). For the **CLI** you can then add Vercel AI Gateway env vars so traffic goes through Gateway. For an **app**, use either (1) Vercel AI Gateway + OIDC (no API key on Vercel) or (2) `ai-sdk-provider-claude-code` and rely on `claude login` on the host.
- **Codex**: No OAuth in the SDK; use ChatGPT subscription (via Codex CLI) or `OPENAI_API_KEY`.
- **TraceRTM Assistant “no response / configure AI provider”**: Prefer **Vercel AI Gateway + OIDC** (deploy on Vercel, no `ANTHROPIC_API_KEY`) or, if you stay off Vercel, set `AI_GATEWAY_API_KEY` or `ANTHROPIC_API_KEY` as appropriate.
