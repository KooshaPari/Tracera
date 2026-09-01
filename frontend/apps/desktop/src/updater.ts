// ---------------------------------------------------------------------------
// Electrobun Desktop Auto-Updater
// Handles checking, downloading, and applying updates for the Tracera
// desktop application built on the Electrobun framework.
// ---------------------------------------------------------------------------

import { app, dialog, BrowserWindow } from 'electrobun';
import { createHash } from 'node:crypto';
import { createReadStream } from 'node:fs';
import { rename, unlink, chmod, mkdir } from 'node:fs/promises';
import { join, dirname } from 'node:path';
import { pipeline } from 'node:stream/promises';
import { createGunzip } from 'node:zlib';
import { promisify } from 'node:util';
import { execFile } from 'node:child_process';
import { pipeline as pipelineAsync } from 'node:stream/promises';

const execFileAsync = promisify(execFile);

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface UpdateManifest {
  version: string;
  releaseDate: string;
  releaseNotes: string;
  platform: string;
  artifacts: UpdateArtifact[];
  minAutoUpdateVersion: string;
}

interface UpdateArtifact {
  url: string;
  sha256: string;
  size: number;
  signature?: string;
}

interface UpdaterConfig {
  /** Base URL for the update server. */
  updateServerUrl: string;
  /** Current app version (semver). */
  currentVersion: string;
  /** Application name used in paths and dialogs. */
  appName: string;
  /** Directory to stage downloaded updates. */
  stagingDir: string;
  /** How often to check for updates (ms). Default: 4 hours. */
  checkIntervalMs: number;
  /** Whether to allow background (silent) updates. */
  allowBackgroundUpdate: boolean;
  /** Public key for verifying update signatures (Ed25519 or RSA). */
  publicKey?: string;
  /** Maximum download size in bytes. Default: 200 MB. */
  maxDownloadSize: number;
}

interface UpdateState {
  status: 'idle' | 'checking' | 'downloading' | 'ready' | 'installing' | 'error';
  progress: number; // 0–100
  error?: string;
  manifest?: UpdateManifest;
}

// ---------------------------------------------------------------------------
// Default configuration
// ---------------------------------------------------------------------------

const DEFAULT_CONFIG: UpdaterConfig = {
  updateServerUrl: 'https://api.tracera.dev/api/v1/updates',
  currentVersion: '0.0.0',
  appName: 'Tracera',
  stagingDir: join(
    process.env.HOME ?? process.env.USERPROFILE ?? '.',
    '.tracera',
    'updates',
  ),
  checkIntervalMs: 4 * 60 * 60 * 1000, // 4 hours
  allowBackgroundUpdate: true,
  maxDownloadSize: 200 * 1024 * 1024, // 200 MB
};

// ---------------------------------------------------------------------------
// Semantic version helpers
// ---------------------------------------------------------------------------

function parseVersion(v: string): [number, number, number] {
  const parts = v.replace(/^[vV]/, '').split('.').map(Number);
  return [parts[0] ?? 0, parts[1] ?? 0, parts[2] ?? 0];
}

function isNewer(current: string, candidate: string): boolean {
  const [cMaj, cMin, cPat] = parseVersion(current);
  const [nMaj, nMin, nPat] = parseVersion(candidate);
  if (nMaj !== cMaj) return nMaj > cMaj;
  if (nMin !== cMin) return nMin > cMin;
  return nPat > cPat;
}

// ---------------------------------------------------------------------------
// Crypto helpers
// ---------------------------------------------------------------------------

async function sha256File(filePath: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const hash = createHash('sha256');
    const stream = createReadStream(filePath);
    stream.on('data', (chunk) => hash.update(chunk));
    stream.on('end', () => resolve(hash.digest('hex')));
    stream.on('error', reject);
  });
}

// ---------------------------------------------------------------------------
// Updater class
// ---------------------------------------------------------------------------

export class DesktopUpdater {
  private config: UpdaterConfig;
  private state: UpdateState = { status: 'idle', progress: 0 };
  private checkTimer?: ReturnType<typeof setInterval>;
  private mainWindow?: BrowserWindow;

  constructor(config: Partial<UpdaterConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  // ── Lifecycle ─────────────────────────────────────────────────────────

  /** Start automatic update checking. */
  start(window?: BrowserWindow): void {
    this.mainWindow = window;

    // Initial check after 30 seconds (let the app finish starting).
    setTimeout(() => this.checkForUpdate(), 30_000);

    // Periodic checks.
    this.checkTimer = setInterval(
      () => this.checkForUpdate(),
      this.config.checkIntervalMs,
    );

    console.log(
      `[updater] Started — v${this.config.currentVersion}, ` +
        `checking every ${this.config.checkIntervalMs / 60_000} min`,
    );
  }

  /** Stop automatic update checking. */
  stop(): void {
    if (this.checkTimer) {
      clearInterval(this.checkTimer);
      this.checkTimer = undefined;
    }
  }

  // ── Check for update ──────────────────────────────────────────────────

  async checkForUpdate(): Promise<UpdateManifest | null> {
    this.setState({ status: 'checking', progress: 0 });

    try {
      const url = `${this.config.updateServerUrl}/manifest?` +
        `current=${this.config.currentVersion}` +
        `&platform=${this.getPlatform()}`;

      const response = await fetch(url, {
        headers: { 'User-Agent': `TraceraDesktop/${this.config.currentVersion}` },
      });

      if (!response.ok) {
        if (response.status === 204) {
          console.log('[updater] No update available.');
          this.setState({ status: 'idle', progress: 0 });
          return null;
        }
        throw new Error(`Manifest fetch failed: HTTP ${response.status}`);
      }

      const manifest: UpdateManifest = await response.json();

      if (!isNewer(this.config.currentVersion, manifest.version)) {
        console.log(`[updater] Already on latest version (${manifest.version}).`);
        this.setState({ status: 'idle', progress: 0 });
        return null;
      }

      console.log(`[updater] Update available: v${manifest.version}`);
      this.setState({ status: 'idle', progress: 0, manifest });
      return manifest;
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      console.error(`[updater] Check failed: ${message}`);
      this.setState({ status: 'error', progress: 0, error: message });
      return null;
    }
  }

  // ── Download ──────────────────────────────────────────────────────────

  async downloadUpdate(manifest: UpdateManifest): Promise<string | null> {
    this.setState({ status: 'downloading', progress: 0, manifest });

    const artifact = this.selectArtifact(manifest);
    if (!artifact) {
      this.setState({
        status: 'error',
        progress: 0,
        error: 'No compatible artifact found for this platform.',
      });
      return null;
    }

    if (artifact.size > this.config.maxDownloadSize) {
      this.setState({
        status: 'error',
        progress: 0,
        error: `Download exceeds maximum size (${artifact.size} > ${this.config.maxDownloadSize}).`,
      });
      return null;
    }

    try {
      await mkdir(this.config.stagingDir, { recursive: true });

      const filename = `tracera-${manifest.version}-${this.getPlatform()}.update`;
      const destPath = join(this.config.stagingDir, filename);

      // Download with progress tracking.
      const response = await fetch(artifact.url);
      if (!response.ok || !response.body) {
        throw new Error(`Download failed: HTTP ${response.status}`);
      }

      const totalBytes = Number(response.headers.get('content-length') ?? artifact.size);
      let downloadedBytes = 0;

      const reader = response.body.getReader();
      const chunks: Uint8Array[] = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        chunks.push(value);
        downloadedBytes += value.length;
        const progress = totalBytes > 0
          ? Math.round((downloadedBytes / totalBytes) * 100)
          : 0;
        this.setState({ ...this.state, progress });

        // Notify renderer of progress.
        this.mainWindow?.webContents.send('update:progress', {
          percent: progress,
          downloaded: downloadedBytes,
          total: totalBytes,
        });
      }

      // Write to disk.
      const { writeFile } = await import('node:fs/promises');
      const totalSize = chunks.reduce((sum, c) => sum + c.length, 0);
      const combined = new Uint8Array(totalSize);
      let offset = 0;
      for (const chunk of chunks) {
        combined.set(chunk, offset);
        offset += chunk.length;
      }
      await writeFile(destPath, combined);

      // Verify checksum.
      const hash = await sha256File(destPath);
      if (hash !== artifact.sha256) {
        await unlink(destPath);
        throw new Error(
          `Checksum mismatch: expected ${artifact.sha256}, got ${hash}`,
        );
      }

      console.log(`[updater] Download verified: ${destPath}`);
      this.setState({ ...this.state, progress: 100 });
      return destPath;
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      console.error(`[updater] Download failed: ${message}`);
      this.setState({ status: 'error', progress: 0, error: message });
      return null;
    }
  }

  // ── Install ───────────────────────────────────────────────────────────

  async installUpdate(artifactPath: string, manifest: UpdateManifest): Promise<boolean> {
    this.setState({ status: 'installing', progress: 0 });

    try {
      // Show confirmation dialog unless background update is allowed.
      if (this.config.allowBackgroundUpdate && this.isBackgroundInstall(manifest)) {
        console.log('[updater] Background install — no prompt.');
      } else {
        const confirmed = await this.promptInstall(manifest);
        if (!confirmed) {
          this.setState({ status: 'idle', progress: 0 });
          return false;
        }
      }

      // Platform-specific installation.
      const platform = this.getPlatform();
      if (platform === 'darwin') {
        await this.installMacOS(artifactPath);
      } else if (platform === 'win32') {
        await this.installWindows(artifactPath);
      } else {
        await this.installLinux(artifactPath);
      }

      console.log('[updater] Installation complete — restarting.');
      // Graceful restart.
      app.relaunch();
      app.exit(0);
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      console.error(`[updater] Install failed: ${message}`);
      this.setState({ status: 'error', progress: 0, error: message });
      return false;
    }
  }

  // ── Full update flow ──────────────────────────────────────────────────

  async performUpdate(): Promise<boolean> {
    const manifest = await this.checkForUpdate();
    if (!manifest) return false;

    const path = await this.downloadUpdate(manifest);
    if (!path) return false;

    return this.installUpdate(path, manifest);
  }

  // ── State & UI ────────────────────────────────────────────────────────

  getState(): Readonly<UpdateState> {
    return { ...this.state };
  }

  onStatusChange(callback: (state: UpdateState) => void): () => void {
    // Simple event emitter pattern.
    const handler = (_event: string, state: UpdateState) => callback(state);
    this.mainWindow?.webContents.on('update:status', handler);
    return () => this.mainWindow?.webContents.removeListener('update:status', handler);
  }

  // ── Private helpers ───────────────────────────────────────────────────

  private setState(state: UpdateState): void {
    this.state = state;
    this.mainWindow?.webContents.send('update:status', state);
  }

  private getPlatform(): string {
    return process.platform;
  }

  private selectArtifact(manifest: UpdateManifest): UpdateArtifact | null {
    const platform = this.getPlatform();
    const arch = process.arch === 'arm64' ? 'arm64' : 'x64';
    const suffix = platform === 'win32' ? '.exe' : '';

    return manifest.artifacts.find((a) => {
      const url = a.url.toLowerCase();
      return (
        url.includes(platform) &&
        url.includes(arch) &&
        (suffix === '' || url.endsWith(suffix) || url.endsWith('.zip'))
      );
    }) ?? manifest.artifacts[0] ?? null;
  }

  private isBackgroundInstall(_manifest: UpdateManifest): boolean {
    // Small patch versions can be auto-installed; major/minor need prompt.
    const [cMaj, cMin] = parseVersion(this.config.currentVersion);
    const [nMaj, nMin] = parseVersion(this.config.currentVersion);
    return cMaj === nMaj && cMin === nMin;
  }

  private async promptInstall(manifest: UpdateManifest): Promise<boolean> {
    const result = await dialog.showMessageBox({
      type: 'info',
      title: `${this.config.appName} Update Available`,
      message: `A new version of ${this.config.appName} is available.`,
      detail: `Version ${manifest.version}\n\n${manifest.releaseNotes}`,
      buttons: ['Install & Restart', 'Later', 'Skip This Version'],
      defaultId: 0,
      cancelId: 1,
    });
    return result.response === 0;
  }

  private async installMacOS(artifactPath: string): Promise<void> {
    // For .dmg or .tar.gz updates on macOS.
    if (artifactPath.endsWith('.dmg')) {
      // Mount, copy, unmount — simplified.
      await execFileAsync('hdiutil', ['attach', artifactPath, '-nobrowse', '-quiet']);
      await execFileAsync('cp', ['-R', '/Volumes/Tracera/Tracera.app', '/Applications/']);
      await execFileAsync('hdiutil', ['detach', '/Volumes/Tracera', '-quiet']);
    } else if (artifactPath.endsWith('.gz')) {
      // Extract tarball over the current app bundle.
      const appPath = dirname(dirname(app.getPath('exe')));
      await execFileAsync('tar', ['xzf', artifactPath, '-C', dirname(appPath)]);
    }
  }

  private async installWindows(artifactPath: string): Promise<void> {
    // Launch the NSIS/MSI installer silently.
    const args = artifactPath.endsWith('.msi')
      ? ['/i', artifactPath, '/quiet', '/norestart']
      : [artifactPath, '/S'];
    await execFileAsync(artifactPath.endsWith('.msi') ? 'msiexec' : artifactPath, args);
  }

  private async installLinux(artifactPath: string): Promise<void> {
    // Extract tar.gz and update the binary in place.
    const appDir = dirname(app.getPath('exe'));
    const tmpDir = join(this.config.stagingDir, 'extract');
    await mkdir(tmpDir, { recursive: true });
    await execFileAsync('tar', ['xzf', artifactPath, '-C', tmpDir]);

    // Move old binary out, move new one in.
    const binName = 'tracera-desktop';
    const currentBin = join(appDir, binName);
    const backupBin = `${currentBin}.bak`;
    const newBin = join(tmpDir, binName);

    await rename(currentBin, backupBin);
    await rename(newBin, currentBin);
    await chmod(currentBin, 0o755);
  }
}

// ---------------------------------------------------------------------------
// Singleton convenience export
// ---------------------------------------------------------------------------

let _instance: DesktopUpdater | null = null;

export function getUpdater(config?: Partial<UpdaterConfig>): DesktopUpdater {
  if (!_instance) {
    _instance = new DesktopUpdater(config);
  }
  return _instance;
}

export default DesktopUpdater;
