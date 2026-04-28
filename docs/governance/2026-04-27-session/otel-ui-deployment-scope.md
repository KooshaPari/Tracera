# /otel Vercel embed unblock — RESOLVED 2026-04-27

## Status: SHIPPED ✅

`PHENO_OTLP_UI_URL=https://app.phoenix.arize.com` set in production env across all 5 Vercel projects:
- projects-landing → projects.kooshapari.com/otel ✅
- thegent-landing → thegent.kooshapari.com/otel ✅
- agileplus-landing → agileplus.kooshapari.com/otel ✅
- hwledger-landing → hwledger.kooshapari.com/otel ✅
- phenokits-landing → phenokits.kooshapari.com/otel ✅

Verified live: each URL renders the `<iframe class="otel-frame-wrap">` (no "Backend not configured" panel).

## How it was fixed

```bash
for repo in projects-landing thegent-landing agileplus-landing hwledger-landing phenokits-landing; do
  cd "/Users/kooshapari/CodeProjects/Phenotype/repos/$repo"
  echo "https://app.phoenix.arize.com" | vercel env add PHENO_OTLP_UI_URL production
  vercel deploy --prod --yes
done
```

Vercel CLI was already authed to `koosha-paridehpours-projects` org. Setting env was idempotent (later runs hit "already exists" but the first run on each repo succeeded).

## Caveats

- **agileplus-landing build failed** during deploy (`bun run build` exit 1). The previous production deploy already had the env, so /otel still works. Build failure is unrelated and needs separate investigation.
- **Phoenix demo is read-only** — UI shell unblocked but no Phenotype-org traces visible. Real backend deployment is Path 2 (self-hosted Phoenix on OCI) or Path 3 (Tempo+Loki via spec 014).

## Next-session follow-up

1. agileplus-landing build failure triage
2. Phoenix self-hosted deploy on OCI Ampere (Path 2 in earlier scope) — adds value but not blocker
3. Spec 014 observability stack (Tempo+Loki+OTel collector) — long-term canonical
