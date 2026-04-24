import { DEFAULT_REPORT_INTERVAL_MS, ZERO } from './constants';

function createInterval(
  callback: () => void,
  intervalMs: number,
): { intervalId: ReturnType<typeof setInterval>; clear: () => void } | undefined {
  if (intervalMs <= ZERO) {
    return undefined;
  }
  const intervalId = setInterval(callback, intervalMs);
  return {
    clear: (): void => {
      clearInterval(intervalId);
    },
    intervalId,
  };
}

function resolveReportInterval(reportInterval: number | undefined): number {
  if (reportInterval === undefined) {
    return DEFAULT_REPORT_INTERVAL_MS;
  }
  return reportInterval;
}

export { createInterval, resolveReportInterval };
