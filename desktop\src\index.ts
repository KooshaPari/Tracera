import { join } from "node:path";
import { fileURLToPath } from "node:url";

const VIEW_URL = new URL("./views/index.html", import.meta.url).href;

type ElectrobunRuntime = Record<string, unknown> & {
  app?: {
    whenReady?: () => Promise<void>;
    on?: (event: string, handler: () => void) => void;
  };
  createWindow?: (options: Record<string, unknown>) => Promise<unknown> | unknown;
  Window?: new (...args: unknown[]) => unknown;
};

const electrobun = (await import("electrobun").catch(() => null)) as ElectrobunRuntime | null;
if (!electrobun) {
  throw new Error(
    "Electrobun package not available at runtime. This shell is scaffolded and requires electrobun execution context.",
  );
}

const app = electrobun.app;
const openWindow = electrobun.createWindow;
const WindowCtor = electrobun.Window;

async function launchWindow(): Promise<void> {
  if (typeof openWindow === "function") {
    await openWindow({
      title: "Tracera Desktop",
      width: 1140,
      height: 860,
      url: VIEW_URL,
      preload: join(fileURLToPath(import.meta.url), "index.js"),
    });
    return;
  }

  if (typeof WindowCtor === "function") {
    const win: any = new WindowCtor({
      title: "Tracera Desktop",
      width: 1140,
      height: 860,
    });
    if (typeof win.loadURL === "function") {
      await win.loadURL(VIEW_URL);
      return;
    }
    if (typeof win.loadFile === "function") {
      await win.loadFile(VIEW_URL.replace("file://", ""));
      return;
    }
  }

  throw new Error("Could not resolve a supported Electrobun window launcher API.");
}

if (app && typeof app.whenReady === "function") {
  await app.whenReady();
  await launchWindow();
} else if (app && typeof app.on === "function") {
  app.on("ready", () => {
    launchWindow().catch(console.error);
  });
} else {
  await launchWindow();
}
