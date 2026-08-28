import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { runFrontendPreflight } from './preflight';

const RUST_READY_RESPONSE = {
  backend: 'sqlite',
  service: 'tracera-server',
  status: 'ready',
  uptime_seconds: 1,
  version: '0.1.3-test',
};

describe('frontend preflight', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="root"></div>';
    Object.defineProperty(HTMLElement.prototype, 'animate', {
      configurable: true,
      value: vi.fn(),
    });
    Object.defineProperty(HTMLElement.prototype, 'scrollTo', {
      configurable: true,
      value: vi.fn(),
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders only the dependencies advertised by the Rust readiness contract', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(
        () =>
          new Response(JSON.stringify(RUST_READY_RESPONSE), {
            headers: { 'content-type': 'application/json' },
            status: 200,
          }),
      ),
    );

    await expect(runFrontendPreflight()).resolves.toEqual({ errors: [], ok: true });

    expect(document.querySelectorAll('[data-infra]')).toHaveLength(1);
    expect(document.querySelector('[data-infra="database"]')).not.toBeNull();
    expect(document.querySelector('[data-infra-list]')).not.toHaveTextContent('Checking');
  });

  it('uses a failure color with WCAG AA contrast against the preflight card', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() => {
        throw new Error('offline');
      }),
    );

    await runFrontendPreflight();

    const status = document.querySelector<HTMLElement>('[data-status-text]');
    if (!status) {
      throw new Error('Expected a preflight status element');
    }
    expect(status).toHaveTextContent('Down');
    expect(contrastRatio(status.style.color, '#211b23')).toBeGreaterThanOrEqual(4.5);
  });
});

function contrastRatio(foreground: string, background: string): number {
  const toLinear = (component: number): number => {
    const normalized = component / 255;
    return normalized <= 0.039_28 ? normalized / 12.92 : ((normalized + 0.055) / 1.055) ** 2.4;
  };
  const luminance = (value: string): number => {
    const channels = value.startsWith('#')
      ? [0, 2, 4].map((offset) => Number.parseInt(value.slice(offset + 1, offset + 3), 16))
      : (value.match(/\d+/g) ?? []).slice(0, 3).map(Number);
    const [red, green, blue] = channels;
    return 0.2126 * toLinear(red) + 0.7152 * toLinear(green) + 0.0722 * toLinear(blue);
  };
  const first = luminance(foreground);
  const second = luminance(background);
  const [lighter, darker] = first >= second ? [first, second] : [second, first];
  return (lighter + 0.05) / (darker + 0.05);
}
