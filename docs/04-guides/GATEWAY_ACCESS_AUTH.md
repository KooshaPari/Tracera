# Vercel gateway authentication to the Tracera Access application

The browser calls same-origin `/api`; the Vercel function forwards to the configured `TRACERA_BACKEND_URL`. The self-hosted Cloudflare Access application and the Rust server's authorization are distinct gates. A healthy tunnel, Vercel Ready deployment, or Cloudflare account connector does not grant the function access to the Rust API.

An existing, appropriately scoped Access service token may be supplied to the function through the server-only environment pair:

- `TRACERA_CF_ACCESS_CLIENT_ID`
- `TRACERA_CF_ACCESS_CLIENT_SECRET`

Both values must be present. A partial, blank, or malformed pair fails closed before an upstream request. When configured, the pair is attached only to the configured HTTPS backend; non-HTTPS URLs and URLs containing userinfo, query, or fragment are rejected. Requests do not follow redirects. Browser-supplied CF Access service headers are ignored and cannot override server credentials. The pair is never included in browser build variables, outgoing response headers, gateway-generated error bodies, or gateway logs.

Do not configure either value with a `VITE_` prefix. Do not paste them into a request, report, source file, screenshot, or test receipt. They remain function runtime settings. The gateway does not create credentials, edit an Access policy, disable Access, or open a host port.

An Access application's policy must separately allow the existing service token. A 401/403 remains a 401/403; configuring this pair cannot be reported as policy acceptance. Browser cookies for a Vercel hostname do not automatically constitute an Access session for `tracera.pheno.studio`.

The Rust bearer authorization remains independent. The gateway continues forwarding the incoming `Authorization`, browser Origin/Referer, cookie, and CSRF headers; it does not invent a Rust bearer credential. Obtain existing supported authentication through the normal approved flow. If the browser has no applicable Rust session, canonical endpoints may still return 401 even after Access accepts the service token.

Configure the values only after the deployed source revision includes this support, the exact existing Access application and token policy have been verified, and the backend URL has been checked against the active ingress route. A redeployment may be required for changed function environment settings. Verify both root health/readiness and actual canonical import/edit/readback through the chosen deployment; health alone does not establish persisted editing or usability.

`node --experimental-strip-types --test scripts/test-gateway-access.mjs` validates configuration, HTTPS-only attachment, ignored browser overrides, no gateway-generated credential disclosure/logging, and preserved policy failure using fake upstream responses. These tests are not live Access policy or deployed backend evidence.
