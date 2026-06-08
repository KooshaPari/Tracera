import type { ElectrobunConfig } from "electrobun";

/**
 * Tracera Electrobun desktop shell
 *
 * Renderer URL resolution order:
 *   1. TRACERTM_RENDERER_URL env var (dev: http://localhost:3000)
 *   2. Falls back to the bundled @tracertm/web static assets at views://web/index.html
 *
 * Service boot: on launch the Bun main process shells out to
 *   `process-compose up -d` in the repo root, bringing up
 *   PG/Redis/NATS + Go backend + web (see process-compose.yml).
 */
export default {
  app: {
    name: "TraceRTM",
    identifier: "com.tracertm.desktop",
    version: "0.1.0",
  },
  runtime: {
    exitOnLastWindowClosed: true,
    // custom keys accessible at runtime via BuildConfig.get()
    rendererUrl: process.env.TRACERTM_RENDERER_URL ?? "http://localhost:3000",
    gatewayUrl: process.env.TRACERTM_GATEWAY_URL ?? "http://localhost:4000",
  },
  build: {
    bun: {
      entrypoint: "src/main.ts",
    },
    // Bundled web assets (for production – built @tracertm/web dist)
    views: [
      {
        name: "web",
        entrypoint: "../web/dist/index.html",
      },
    ],
    /**
     * macOS code-signing & notarization wiring.
     * Reads: MACOS_SIGNING_IDENTITY (Developer ID, "Developer ID Application: ...")
     *        MACOS_NOTARYTOOL_PROFILE (xcrun notarytool keychain profile)
     *        MACOS_TEAM_ID (optional fallback when profile is absent)
     */
    mac: {
      codesign: Boolean(process.env.MACOS_SIGNING_IDENTITY),
      notarize: Boolean(process.env.MACOS_NOTARYTOOL_PROFILE),
      category: "public.app-category.developer-tools",
      entitlements: "build/entitlements.mac.plist",
      signingIdentity: process.env.MACOS_SIGNING_IDENTITY,
      notarytoolProfile:
        process.env.MACOS_NOTARYTOOL_PROFILE ?? process.env.MACOS_TEAM_ID,
    },
    /**
     * Windows code-signing & installer targets.
     * Reads: WINDOWS_CERT_PATH (PFX/P12 path), WINDOWS_CERT_PASSWORD (env, not embedded)
     */
    win: {
      signingCertPath: process.env.WINDOWS_CERT_PATH,
      publisherName: "Phenotype Inc.",
      target: ["nsis", "msi", "appx"],
    },
    /**
     * Linux packaging targets & desktop-entry metadata.
     */
    linux: {
      target: ["deb", "rpm", "AppImage"],
      category: "Development",
      maintainer: "dev@tracertm.dev",
    },
  },
} satisfies ElectrobunConfig;
