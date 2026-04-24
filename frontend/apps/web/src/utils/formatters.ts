// Time constants for relative/duration formatting
const MS_PER_SEC = Number('1000');
const SEC_PER_MIN = Number('60');
const SEC_PER_HOUR = Number('3600');
const SEC_PER_DAY = Number('86400');
const SEC_PER_WEEK = Number('604800');
const SEC_PER_MONTH = Number('2592000');
const PERCENT_DENOM = Number('100');
const BYTES_K = Number('1024');
const ZERO = Number('0');
const DEFAULT_DECIMALS = Number('2');

// Date formatting utilities
const formatDate = function formatDate(
  date: string | Date,
  format: 'short' | 'long' | 'relative' = 'short',
): string {
  const d = typeof date === 'string' ? new Date(date) : date;

  if (format === 'relative') {
    return formatRelativeTime(d);
  }

  const options: Intl.DateTimeFormatOptions =
    format === 'long'
      ? {
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          month: 'long',
          year: 'numeric',
        }
      : { day: 'numeric', month: 'short', year: 'numeric' };

  return d.toLocaleDateString('en-US', options);
};

const formatRelativeTime = function formatRelativeTime(date: Date): string {
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / MS_PER_SEC);

  if (diffInSeconds < SEC_PER_MIN) {
    return 'just now';
  }
  if (diffInSeconds < SEC_PER_HOUR) {
    return `${Math.floor(diffInSeconds / SEC_PER_MIN)}m ago`;
  }
  if (diffInSeconds < SEC_PER_DAY) {
    return `${Math.floor(diffInSeconds / SEC_PER_HOUR)}h ago`;
  }
  if (diffInSeconds < SEC_PER_WEEK) {
    return `${Math.floor(diffInSeconds / SEC_PER_DAY)}d ago`;
  }
  if (diffInSeconds < SEC_PER_MONTH) {
    return `${Math.floor(diffInSeconds / SEC_PER_WEEK)}w ago`;
  }

  return formatDate(date, 'short');
};

const formatTime = function formatTime(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });
};

// Number formatting utilities
const formatNumber = function formatNumber(
  num: number,
  options?: Intl.NumberFormatOptions,
): string {
  return new Intl.NumberFormat('en-US', options).format(num);
};

const formatPercentage = function formatPercentage(
  value: number,
  total: number,
  decimals = ZERO,
): string {
  if (total === ZERO) {
    return '0%';
  }
  const percentage = (value / total) * PERCENT_DENOM;
  return `${percentage.toFixed(decimals)}%`;
};

const formatBytes = function formatBytes(bytes: number, decimals = DEFAULT_DECIMALS): string {
  if (bytes === ZERO) {
    return '0 Bytes';
  }

  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const index = Math.floor(Math.log(bytes) / Math.log(BYTES_K));

  return `${Number.parseFloat((bytes / BYTES_K ** index).toFixed(decimals))} ${sizes[index]}`;
};

// String formatting utilities
const truncate = function truncate(text: string, length: number, suffix = '...'): string {
  if (text.length <= length) {
    return text;
  }
  return text.slice(0, length - suffix.length) + suffix;
};

const capitalize = function capitalize(text: string): string {
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
};

const titleCase = function titleCase(text: string): string {
  return text
    .split(' ')
    .map((word) => capitalize(word))
    .join(' ');
};

const kebabCase = function kebabCase(text: string): string {
  return text
    .toLowerCase()
    .replaceAll(/\s+/g, '-')
    .replaceAll(/[^\w-]/g, '');
};

const camelCase = function camelCase(text: string): string {
  return text.toLowerCase().replaceAll(/[^a-zA-Z0-9]+(.)/g, (_, chr) => chr.toUpperCase());
};

// Status formatting
const formatStatus = function formatStatus(status: string): string {
  return status
    .split('_')
    .map((word) => capitalize(word))
    .join(' ');
};

// Priority formatting with colors
const getPriorityColor = function getPriorityColor(priority: string): string {
  const colors: Record<string, string> = {
    critical: 'red',
    high: 'orange',
    low: 'green',
    medium: 'yellow',
  };
  return colors[priority.toLowerCase()] ?? 'gray';
};

// Status formatting with colors
const getStatusColor = function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    blocked: 'red',
    cancelled: 'gray',
    done: 'green',
    in_progress: 'blue',
    todo: 'gray',
  };
  return colors[status.toLowerCase()] ?? 'gray';
};

// Duration formatting
const formatDuration = function formatDuration(seconds: number): string {
  if (seconds < SEC_PER_MIN) {
    return `${seconds}s`;
  }
  if (seconds < SEC_PER_HOUR) {
    return `${Math.floor(seconds / SEC_PER_MIN)}m ${seconds % SEC_PER_MIN}s`;
  }

  const hours = Math.floor(seconds / SEC_PER_HOUR);
  const minutes = Math.floor((seconds % SEC_PER_HOUR) / SEC_PER_MIN);
  return `${hours}h ${minutes}m`;
};

export {
  camelCase,
  capitalize,
  formatBytes,
  formatDate,
  formatDuration,
  formatNumber,
  formatPercentage,
  formatRelativeTime,
  formatStatus,
  formatTime,
  getPriorityColor,
  getStatusColor,
  kebabCase,
  titleCase,
  truncate,
};
