'use client';

import type { ReactNode } from 'react';

import { Copy, Download, ExternalLink, Moon, Sun } from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { RedocStandalone } from 'redoc';

import { logger } from '@/lib/logger';

interface RedocWrapperProps {
  specUrl?: string;
  spec?: object;
  scrollYOffset?: number;
  hideDownloadButton?: boolean;
  disableSearch?: boolean;
  expandResponses?: string;
  requiredPropsFirst?: boolean;
  sortPropsAlphabetically?: boolean;
  showExtensions?: boolean;
  nativeScrollbars?: boolean;
  pathInMiddlePanel?: boolean;
  hideHostname?: boolean;
  expandSingleSchemaField?: boolean;
}

const COPY_RESET_MS = 2000;
const DEFAULT_SCROLL_Y_OFFSET = 80;
const ICON_SIZE = 18;
const JSON_INDENT = 2;
const REDOC_DEFAULTS = {
  disableSearch: false,
  expandResponses: '200,201',
  expandSingleSchemaField: true,
  hideDownloadButton: false,
  hideHostname: false,
  nativeScrollbars: false,
  pathInMiddlePanel: false,
  requiredPropsFirst: true,
  scrollYOffset: DEFAULT_SCROLL_Y_OFFSET,
  showExtensions: false,
  sortPropsAlphabetically: false,
  specUrl: '/specs/openapi.json',
};

const DARK_COLORS = {
  border: {
    dark: '#404040',
    light: '#505050',
  },
  http: {
    basic: '#999',
    delete: '#e27a7a',
    get: '#6bbd5b',
    head: '#c167e4',
    link: '#31bbb6',
    options: '#d3ca12',
    patch: '#e09d43',
    post: '#248fb2',
    put: '#9b708b',
  },
  primary: {
    main: '#4a90e2',
  },
  text: {
    primary: '#f0f0f0',
    secondary: '#b0b0b0',
  },
};

const LIGHT_COLORS = {
  border: {
    dark: '#e0e0e0',
    light: '#f0f0f0',
  },
  http: {
    basic: '#999',
    delete: '#f93e3e',
    get: '#61affe',
    head: '#c167e4',
    link: '#31bbb6',
    options: '#d3ca12',
    patch: '#50e3c2',
    post: '#49cc90',
    put: '#fca130',
  },
  primary: {
    main: '#4a90e2',
  },
  text: {
    primary: '#333',
    secondary: '#666',
  },
};

const TYPOGRAPHY = {
  code: {
    fontFamily: '"Fira Code", "Courier New", monospace',
    fontSize: '14px',
    fontWeight: '400',
  },
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  fontSize: '16px',
  headings: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    fontWeight: '700',
  },
};

const downloadOpenApiJson = (data: unknown): void => {
  const blob = new Blob([JSON.stringify(data, null, JSON_INDENT)], {
    type: 'application/json',
  });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = 'openapi-spec.json';
  document.body.append(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
};

const openInSwagger = (): void => {
  window.open('/api-docs/swagger', '_blank');
};

const resolveDarkModePreference = (): boolean =>
  document.documentElement.classList.contains('dark') ||
  globalThis.matchMedia('(prefers-color-scheme: dark)').matches;

const writeToClipboard = async (value: string) => {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(value);
    return;
  }

  const textarea = document.createElement('textarea');
  textarea.value = value;
  textarea.setAttribute('readonly', 'true');
  textarea.style.position = 'absolute';
  textarea.style.left = '-9999px';
  document.body.append(textarea);
  textarea.select();
  document.execCommand('copy');
  document.body.removeChild(textarea);
};

const fetchSpecFromUrl = async (specUrl?: string) => {
  if (!specUrl) {
    return null;
  }

  const response = await fetch(specUrl);
  return response.json();
};

const normalizeRedocProps = (props: RedocWrapperProps) => ({
  ...REDOC_DEFAULTS,
  ...props,
});

const useSpecData = (specUrl?: string, spec?: object) => {
  const [specData, setSpecData] = useState<object | null>(null);

  useEffect(() => {
    if (spec) {
      setSpecData(spec);
      return;
    }

    if (!specUrl) {
      setSpecData(null);
      return;
    }

    fetch(specUrl)
      .then(async (res) => res.json())
      .then((data) => {
        setSpecData(data);
      })
      .catch((error) => {
        logger.error('Failed to load OpenAPI spec:', error);
      });
  }, [spec, specUrl]);

  return specData;
};

const useDarkMode = () => {
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    setDarkMode(resolveDarkModePreference());
  }, []);

  const toggleDarkMode = useCallback(() => {
    setDarkMode((prev) => {
      const next = !prev;
      document.documentElement.classList.toggle('dark', next);
      return next;
    });
  }, []);

  return { darkMode, toggleDarkMode };
};

const useCopySpecUrl = (specUrl?: string) => {
  const [copied, setCopied] = useState(false);

  const copySpecUrl = useCallback(async () => {
    if (!specUrl) {
      return;
    }

    const fullUrl = new URL(specUrl, globalThis.location.origin).toString();
    try {
      await writeToClipboard(fullUrl);
      setCopied(true);
      window.setTimeout(() => {
        setCopied(false);
      }, COPY_RESET_MS);
    } catch (error) {
      logger.error('Failed to copy spec URL:', error);
    }
  }, [specUrl]);

  return { copied, copySpecUrl };
};

const useDownloadSpec = (resolvedSpec: object | null, specUrl?: string) =>
  useCallback(async () => {
    const dataToDownload = resolvedSpec ?? (await fetchSpecFromUrl(specUrl));
    if (!dataToDownload) {
      return;
    }

    downloadOpenApiJson(dataToDownload);
  }, [resolvedSpec, specUrl]);

const buildTheme = (darkMode: boolean) => ({
  colors: darkMode ? DARK_COLORS : LIGHT_COLORS,
  rightPanel: {
    backgroundColor: darkMode ? '#1a1a1a' : '#263238',
    textColor: '#ffffff',
  },
  sidebar: {
    activeTextColor: '#4a90e2',
    backgroundColor: darkMode ? '#2d2d2d' : '#fafafa',
    textColor: darkMode ? '#f0f0f0' : '#333',
    width: '280px',
  },
  typography: TYPOGRAPHY,
});

const buildOptions = (props: {
  darkMode: boolean;
  disableSearch: boolean;
  expandResponses: string;
  expandSingleSchemaField: boolean;
  hideDownloadButton: boolean;
  hideHostname: boolean;
  nativeScrollbars: boolean;
  pathInMiddlePanel: boolean;
  requiredPropsFirst: boolean;
  scrollYOffset: number;
  showExtensions: boolean;
  sortPropsAlphabetically: boolean;
}) => ({
  disableSearch: props.disableSearch,
  expandResponses: props.expandResponses,
  expandSingleSchemaField: props.expandSingleSchemaField,
  hideDownloadButton: props.hideDownloadButton,
  hideHostname: props.hideHostname,
  nativeScrollbars: props.nativeScrollbars,
  pathInMiddlePanel: props.pathInMiddlePanel,
  requiredPropsFirst: props.requiredPropsFirst,
  scrollYOffset: props.scrollYOffset,
  showExtensions: props.showExtensions,
  sortPropsAlphabetically: props.sortPropsAlphabetically,
  theme: buildTheme(props.darkMode),
});

const useRedocOptions = (params: {
  darkMode: boolean;
  disableSearch: boolean;
  expandResponses: string;
  expandSingleSchemaField: boolean;
  hideDownloadButton: boolean;
  hideHostname: boolean;
  nativeScrollbars: boolean;
  pathInMiddlePanel: boolean;
  requiredPropsFirst: boolean;
  scrollYOffset: number;
  showExtensions: boolean;
  sortPropsAlphabetically: boolean;
}) =>
  useMemo(
    () =>
      buildOptions({
        darkMode: params.darkMode,
        disableSearch: params.disableSearch,
        expandResponses: params.expandResponses,
        expandSingleSchemaField: params.expandSingleSchemaField,
        hideDownloadButton: params.hideDownloadButton,
        hideHostname: params.hideHostname,
        nativeScrollbars: params.nativeScrollbars,
        pathInMiddlePanel: params.pathInMiddlePanel,
        requiredPropsFirst: params.requiredPropsFirst,
        scrollYOffset: params.scrollYOffset,
        showExtensions: params.showExtensions,
        sortPropsAlphabetically: params.sortPropsAlphabetically,
      }),
    [
      params.darkMode,
      params.disableSearch,
      params.expandResponses,
      params.expandSingleSchemaField,
      params.hideDownloadButton,
      params.hideHostname,
      params.nativeScrollbars,
      params.pathInMiddlePanel,
      params.requiredPropsFirst,
      params.scrollYOffset,
      params.showExtensions,
      params.sortPropsAlphabetically,
    ],
  );

const useStandaloneProps = (
  resolvedSpec: object | null,
  specUrl: string | undefined,
  options: ReturnType<typeof buildOptions>,
) =>
  useMemo(() => {
    if (resolvedSpec) {
      return { options, spec: resolvedSpec };
    }

    return { options, specUrl };
  }, [options, resolvedSpec, specUrl]);

const LoadingState = ({ label }: { label: string }) => (
  <div className='redoc-loading'>
    <div className='spinner' />
    <p>{label}</p>
  </div>
);

const IconLabelButton = ({
  icon,
  label,
  onClick,
  title,
}: {
  icon: ReactNode;
  label: string;
  onClick: () => void;
  title: string;
}) => (
  <button type='button' onClick={onClick} className='redoc-btn' title={title}>
    <span className='redoc-btn-icon'>{icon}</span>
    <span>{label}</span>
  </button>
);

const RedocToolbar = ({
  copied,
  darkMode,
  onCopy,
  onDownload,
  onOpenSwagger,
  onToggleDarkMode,
}: {
  copied: boolean;
  darkMode: boolean;
  onCopy: () => void;
  onDownload: () => void;
  onOpenSwagger: () => void;
  onToggleDarkMode: () => void;
}) => (
  <div className='redoc-controls'>
    <div className='redoc-toolbar'>
      <h1 className='redoc-title'>API Reference</h1>
      <div className='redoc-actions'>
        <IconLabelButton
          onClick={onCopy}
          icon={<Copy size={ICON_SIZE} />}
          label={copied ? 'Copied!' : 'Copy URL'}
          title='Copy Spec URL'
        />
        <IconLabelButton
          onClick={onDownload}
          icon={<Download size={ICON_SIZE} />}
          label='Download'
          title='Download OpenAPI Spec'
        />
        <IconLabelButton
          onClick={onOpenSwagger}
          icon={<ExternalLink size={ICON_SIZE} />}
          label='Swagger UI'
          title='Open in Swagger UI'
        />
        <IconLabelButton
          onClick={onToggleDarkMode}
          icon={darkMode ? <Sun size={ICON_SIZE} /> : <Moon size={ICON_SIZE} />}
          label={darkMode ? 'Light' : 'Dark'}
          title='Toggle Dark Mode'
        />
      </div>
    </div>
  </div>
);

const RedocContent = ({
  hasSpec,
  standaloneProps,
}: {
  hasSpec: boolean;
  standaloneProps: { options: ReturnType<typeof buildOptions> } & (
    | { spec: object; specUrl?: never }
    | { spec?: never; specUrl?: string | undefined }
  );
}) =>
  hasSpec ? (
    <RedocStandalone {...(standaloneProps as Parameters<typeof RedocStandalone>[0])} />
  ) : (
    <LoadingState label='Loading API Reference...' />
  );

const REDOC_STYLES = `
  .redoc-container {
    min-height: 100vh;
    background-color: #fafafa;
    transition: background-color 0.3s ease;
  }

  .redoc-container.dark-mode {
    background-color: #1a1a1a;
  }

  .redoc-controls {
    position: sticky;
    top: 0;
    z-index: 100;
    background-color: white;
    border-bottom: 1px solid #e0e0e0;
    padding: 1rem 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .dark-mode .redoc-controls {
    background-color: #2d2d2d;
    border-bottom-color: #404040;
  }

  .redoc-toolbar {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .redoc-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #333;
    margin: 0;
  }

  .dark-mode .redoc-title {
    color: #f0f0f0;
  }

  .redoc-actions {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
  }

  .redoc-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background-color: #4a90e2;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
  }

  .redoc-btn:hover {
    background-color: #357abd;
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(74, 144, 226, 0.3);
  }

  .redoc-btn:active {
    transform: translateY(0);
  }

  .redoc-btn-icon {
    display: inline-flex;
    align-items: center;
  }

  .dark-mode .redoc-btn {
    background-color: #3a7bc8;
  }

  .dark-mode .redoc-btn:hover {
    background-color: #2e6ab3;
  }

  .redoc-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    gap: 1rem;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #4a90e2;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  .dark-mode .spinner {
    border-color: #404040;
    border-top-color: #3a7bc8;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .redoc-loading p {
    color: #666;
    font-size: 1rem;
  }

  .dark-mode .redoc-loading p {
    color: #aaa;
  }

  @media (max-width: 768px) {
    .redoc-toolbar {
      flex-direction: column;
      align-items: stretch;
    }

    .redoc-actions {
      justify-content: stretch;
    }

    .redoc-btn {
      flex: 1;
      justify-content: center;
    }
  }
`;

export const RedocWrapper = (props: RedocWrapperProps) => {
  const normalized = normalizeRedocProps(props);
  const { darkMode, toggleDarkMode } = useDarkMode();
  const { copied, copySpecUrl } = useCopySpecUrl(normalized.specUrl);
  const specData = useSpecData(normalized.specUrl, normalized.spec);
  const resolvedSpec = specData ?? normalized.spec ?? null;
  const redocOptions = useRedocOptions({
    darkMode,
    disableSearch: normalized.disableSearch,
    expandResponses: normalized.expandResponses,
    expandSingleSchemaField: normalized.expandSingleSchemaField,
    hideDownloadButton: normalized.hideDownloadButton,
    hideHostname: normalized.hideHostname,
    nativeScrollbars: normalized.nativeScrollbars,
    pathInMiddlePanel: normalized.pathInMiddlePanel,
    requiredPropsFirst: normalized.requiredPropsFirst,
    scrollYOffset: normalized.scrollYOffset,
    showExtensions: normalized.showExtensions,
    sortPropsAlphabetically: normalized.sortPropsAlphabetically,
  });
  const standaloneProps = useStandaloneProps(resolvedSpec, normalized.specUrl, redocOptions);
  const downloadSpec = useDownloadSpec(resolvedSpec, normalized.specUrl);

  return (
    <div className={`redoc-container ${darkMode ? 'dark-mode' : ''}`}>
      <RedocToolbar
        copied={copied}
        darkMode={darkMode}
        onCopy={copySpecUrl}
        onDownload={downloadSpec}
        onOpenSwagger={openInSwagger}
        onToggleDarkMode={toggleDarkMode}
      />
      <RedocContent
        hasSpec={Boolean(resolvedSpec ?? normalized.specUrl)}
        standaloneProps={standaloneProps}
      />
      <style>{REDOC_STYLES}</style>
    </div>
  );
};
