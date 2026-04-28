import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { getCurrentWindow } from '@tauri-apps/api/window';
import SyncIndicator from './components/SyncIndicator';
import DeepLinkHandler from './components/DeepLinkHandler';
import './App.css';

interface AppInfo {
  version: string;
  platform: string;
  arch: string;
}

function App() {
  const [appInfo, setAppInfo] = useState<AppInfo | null>(null);
  const [syncStatus, setSyncStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load app info
    invoke<AppInfo>('get_app_info')
      .then(setAppInfo)
      .catch(console.error);

    // Load initial sync status
    loadSyncStatus();

    // Listen for sync events
    const unlistenSyncStarted = listen('sync-started', () => {
      console.log('Sync started');
      loadSyncStatus();
    });

    const unlistenSyncCompleted = listen('sync-completed', (event) => {
      console.log('Sync completed', event.payload);
      setSyncStatus(event.payload);
    });

    const unlistenSyncError = listen('sync-error', (event) => {
      console.error('Sync error', event.payload);
      loadSyncStatus();
    });

    // Listen for menu events
    const unlistenNewRequirement = listen('menu:new-requirement', () => {
      console.log('New requirement requested');
      // Handle new requirement creation
    });

    const unlistenNewTest = listen('menu:new-test', () => {
      console.log('New test requested');
      // Handle new test creation
    });

    const unlistenSave = listen('menu:save', () => {
      console.log('Save requested');
      // Handle save
    });

    setLoading(false);

    return () => {
      unlistenSyncStarted.then((fn) => fn());
      unlistenSyncCompleted.then((fn) => fn());
      unlistenSyncError.then((fn) => fn());
      unlistenNewRequirement.then((fn) => fn());
      unlistenNewTest.then((fn) => fn());
      unlistenSave.then((fn) => fn());
    };
  }, []);

  const loadSyncStatus = async () => {
    try {
      const status = await invoke('get_sync_status');
      setSyncStatus(status);
    } catch (error) {
      console.error('Failed to load sync status:', error);
    }
  };

  const handleSyncNow = async () => {
    try {
      await invoke('force_sync');
      console.log('Manual sync initiated');
    } catch (error) {
      console.error('Sync failed:', error);
    }
  };

  if (loading) {
    return (
      <div className="app loading">
        <div className="spinner">Loading TraceRTM...</div>
      </div>
    );
  }

  return (
    <div className="app">
      <DeepLinkHandler />

      <header className="app-header">
        <div className="header-content">
          <h1>TraceRTM Desktop</h1>
          {appInfo && (
            <div className="app-info">
              v{appInfo.version} | {appInfo.platform} | {appInfo.arch}
            </div>
          )}
        </div>
        <SyncIndicator status={syncStatus} onSyncClick={handleSyncNow} />
      </header>

      <main className="app-main">
        <div className="welcome-container">
          <div className="welcome-card">
            <h2>Welcome to TraceRTM Desktop</h2>
            <p>
              Your offline-first requirements traceability management tool.
            </p>

            <div className="features">
              <div className="feature">
                <div className="feature-icon">🔄</div>
                <h3>Offline First</h3>
                <p>Work without internet, sync when connected</p>
              </div>

              <div className="feature">
                <div className="feature-icon">⚡</div>
                <h3>Native Performance</h3>
                <p>Built with Rust and Tauri for maximum speed</p>
              </div>

              <div className="feature">
                <div className="feature-icon">🔐</div>
                <h3>Secure</h3>
                <p>Your data stays on your device until you sync</p>
              </div>

              <div className="feature">
                <div className="feature-icon">🚀</div>
                <h3>Auto Updates</h3>
                <p>Always get the latest features and fixes</p>
              </div>
            </div>

            <div className="actions">
              <button className="btn btn-primary">
                Create New Project
              </button>
              <button className="btn btn-secondary">
                Open Existing Project
              </button>
            </div>
          </div>
        </div>
      </main>

      <footer className="app-footer">
        <div className="footer-content">
          <span>TraceRTM &copy; 2024</span>
          <span>|</span>
          <a href="#" onClick={() => invoke('menu:documentation')}>
            Documentation
          </a>
          <span>|</span>
          <a href="#" onClick={() => invoke('menu:report_issue')}>
            Report Issue
          </a>
        </div>
      </footer>
    </div>
  );
}

export default App;
