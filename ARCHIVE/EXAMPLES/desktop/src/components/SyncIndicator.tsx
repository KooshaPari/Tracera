import { useState, useEffect } from 'react';

interface SyncStatus {
  is_syncing: boolean;
  last_sync: string | null;
  sync_error: string | null;
  pending_changes: number;
  online: boolean;
}

interface SyncIndicatorProps {
  status: SyncStatus | null;
  onSyncClick: () => void;
}

function SyncIndicator({ status, onSyncClick }: SyncIndicatorProps) {
  const [showDetails, setShowDetails] = useState(false);

  if (!status) {
    return null;
  }

  const getStatusColor = () => {
    if (status.sync_error) return 'error';
    if (status.is_syncing) return 'syncing';
    if (!status.online) return 'offline';
    return 'online';
  };

  const getStatusText = () => {
    if (status.sync_error) return 'Sync Error';
    if (status.is_syncing) return 'Syncing...';
    if (!status.online) return 'Offline';
    return 'Online';
  };

  const formatLastSync = (timestamp: string | null) => {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  return (
    <div className="sync-indicator">
      <div
        className={`sync-status ${getStatusColor()}`}
        onClick={() => setShowDetails(!showDetails)}
        title="Click for sync details"
      >
        <div className="status-dot" />
        <span className="status-text">{getStatusText()}</span>
        {status.pending_changes > 0 && (
          <span className="pending-badge">{status.pending_changes}</span>
        )}
      </div>

      {showDetails && (
        <div className="sync-details">
          <div className="detail-row">
            <span className="detail-label">Status:</span>
            <span className="detail-value">{getStatusText()}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Last Sync:</span>
            <span className="detail-value">
              {formatLastSync(status.last_sync)}
            </span>
          </div>
          {status.pending_changes > 0 && (
            <div className="detail-row">
              <span className="detail-label">Pending Changes:</span>
              <span className="detail-value">{status.pending_changes}</span>
            </div>
          )}
          {status.sync_error && (
            <div className="detail-row error">
              <span className="detail-label">Error:</span>
              <span className="detail-value">{status.sync_error}</span>
            </div>
          )}
          {!status.is_syncing && status.online && (
            <button
              className="btn btn-small btn-sync"
              onClick={(e) => {
                e.stopPropagation();
                onSyncClick();
                setShowDetails(false);
              }}
            >
              Sync Now
            </button>
          )}
        </div>
      )}
    </div>
  );
}

export default SyncIndicator;
