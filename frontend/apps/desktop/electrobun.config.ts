import type { ElectrobunConfig } from "electrobun/bun";

const config: ElectrobunConfig = {
  app: {
    name: "Tracera",
    identifier: "ai.kooshapari.tracera",
    version: "0.1.0",
    description: "Tracera — traceability analysis desktop shell",
  },

  build: {
    bun: {
      entrypoint: "src/index.ts",
    },
    // No bundled views or sidecars: the window loads an external URL.
    // assets/icons are referenced by the Tray at runtime via absolute paths.
    mac: {
      icons: "assets/icons/Tracera.iconset",
    },
  },
};

export default config;
