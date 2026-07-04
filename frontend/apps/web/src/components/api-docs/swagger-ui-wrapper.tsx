'use client';

import 'swagger-ui-react/swagger-ui.css';
import type { ComponentProps, ReactNode } from 'react';

import { Copy, Download, Moon, Sun } from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';
import SwaggerUI from 'swagger-ui-react';

import { logger } from '@/lib/logger';

interface SwaggerUIWrapperProps {
  specUrl?: string | undefined;
  spec?: object | undefined;
  tryItOutEnabled?: boolean | undefined;
  persistAuthorization?: boolean | undefined;
  displayRequestDuration?: boolean | undefined;
  filter?: boolean | undefined;
  deepLinking?: boolean | undefined;
  requestInterceptor?: SwaggerUIProps['requestInterceptor'] | undefined;
  responseInterceptor?: SwaggerUIProps['responseInterceptor'] | undefined;
}

type SwaggerUIProps = ComponentProps<typeof SwaggerUI>;

type SwaggerRequest = Parameters<NonNullable<SwaggerUIProps['requestInterceptor']>>[0];

type SwaggerResponse = Parameters<NonNullable<SwaggerUIProps['responseInterceptor']>>[0];

const COPY_RESET_MS = 2000;
const DEFAULT_MODELS_EXPAND_DEPTH = 1;
const ICON_SIZE = 18;
const JSON_INDENT = 2;
const SWAGGER_DEFAULTS = {
  deepLinking: true,
  displayRequestDuration: true,
  filter: true,
  persistAuthorization: true,
  specUrl: '/specs/openapi.json',
  tryItOutEnabled: true,
};

const SUPPORTED_SUBMIT_METHODS: NonNullable<SwaggerUIProps['supportedSubmitMethods']> = [
  'get',
  'put',
  'post',
  'delete',
  'options',
  'head',
  'patch',
  'trace',
];

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

const setHeader = (req: SwaggerRequest, name: string, value: string) => {
  const { headers } = req;
  if (headers && typeof headers.set === 'function') {
    headers.set(name, value);
  }
};

const normalizeSwaggerProps = (props: SwaggerUIWrapperProps) => ({
  ...SWAGGER_DEFAULTS,
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

const useSwaggerInterceptors = (
  requestInterceptor?: SwaggerUIProps['requestInterceptor'],
  responseInterceptor?: SwaggerUIProps['responseInterceptor'],
) => {
  const defaultRequestInterceptor = useCallback(
    (req: SwaggerRequest) => {
      const isStorageAvailable =
        typeof localStorage !== 'undefined' && typeof localStorage.getItem === 'function';
      const token = isStorageAvailable ? localStorage.getItem('api_token') : null;
      const apiKey = isStorageAvailable ? localStorage.getItem('api_key') : null;

      if (token) {
        setHeader(req, 'Authorization', `Bearer ${token}`);
      }
      if (apiKey) {
        setHeader(req, 'X-API-Key', apiKey);
      }

      return requestInterceptor ? requestInterceptor(req) : req;
    },
    [requestInterceptor],
  );

  const defaultResponseInterceptor = useCallback(
    (res: SwaggerResponse) => {
      logger.info('API Response:', {
        status: res['status'],
        url: res['url'],
      });

      return responseInterceptor ? responseInterceptor(res) : res;
    },
    [responseInterceptor],
  );

  return { defaultRequestInterceptor, defaultResponseInterceptor };
};

const useSwaggerProps = (params: {
  deepLinking: boolean;
  displayRequestDuration: boolean;
  filter: boolean;
  persistAuthorization: boolean;
  requestInterceptor: SwaggerUIProps['requestInterceptor'];
  responseInterceptor: SwaggerUIProps['responseInterceptor'];
  resolvedSpec: object | null;
  specUrl?: string | undefined;
  tryItOutEnabled: boolean;
}) =>
  useMemo(
    () =>
      ({
        deepLinking: params.deepLinking,
        defaultModelExpandDepth: DEFAULT_MODELS_EXPAND_DEPTH,
        defaultModelsExpandDepth: DEFAULT_MODELS_EXPAND_DEPTH,
        displayOperationId: false,
        displayRequestDuration: params.displayRequestDuration,
        docExpansion: 'list',
        filter: params.filter,
        persistAuthorization: params.persistAuthorization,
        requestInterceptor: params.requestInterceptor,
        responseInterceptor: params.responseInterceptor,
        showCommonExtensions: false,
        showExtensions: false,
        ...(params.resolvedSpec ? { spec: params.resolvedSpec } : {}),
        supportedSubmitMethods: SUPPORTED_SUBMIT_METHODS,
        tryItOutEnabled: params.tryItOutEnabled,
        ...(params.resolvedSpec ? {} : params.specUrl ? { url: params.specUrl } : {}),
      }) satisfies Record<string, unknown> as SwaggerUIProps,
    [
      params.deepLinking,
      params.displayRequestDuration,
      params.filter,
      params.persistAuthorization,
      params.requestInterceptor,
      params.responseInterceptor,
      params.resolvedSpec,
      params.specUrl,
      params.tryItOutEnabled,
    ],
  );

const LoadingState = ({ label }: { label: string }) => (
  <div className='swagger-loading'>
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
  <button type='button' onClick={onClick} className='swagger-btn' title={title}>
    <span className='swagger-btn-icon'>{icon}</span>
    <span>{label}</span>
  </button>
);

const SwaggerToolbar = ({
  copied,
  darkMode,
  onCopy,
  onDownload,
  onToggleDarkMode,
}: {
  copied: boolean;
  darkMode: boolean;
  onCopy: () => void;
  onDownload: () => void;
  onToggleDarkMode: () => void;
}) => (
  <div className='swagger-controls'>
    <div className='swagger-toolbar'>
      <h1 className='swagger-title'>API Documentation</h1>
      <div className='swagger-actions'>
        <IconLabelButton
          onClick={onCopy}
          icon={<Copy size={ICON_SIZE} />}
          label={copied ? 'Copied!' : 'Copy URL'}
          title='Copy Spec URL'
        />
        <IconLabelButton
          onClick={onDownload}
          icon={<Download size={ICON_SIZE} />}
          label='Download Spec'
          title='Download OpenAPI Spec'
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

const SwaggerContent = ({
  hasSpec,
  swaggerProps,
}: {
  hasSpec: boolean;
  swaggerProps: SwaggerUIProps;
}) =>
  hasSpec ? <SwaggerUI {...swaggerProps} /> : <LoadingState label='Loading API Documentation...' />;

const SWAGGER_STYLES = `
  .swagger-ui-container {
    min-height: 100vh;
    background-color: #fafafa;
    transition: background-color 0.3s ease;
  }

  .swagger-ui-container.dark-mode {
    background-color: #1a1a1a;
  }

  .swagger-controls {
    position: sticky;
    top: 0;
    z-index: 100;
    background-color: white;
    border-bottom: 1px solid #e0e0e0;
    padding: 1rem 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .dark-mode .swagger-controls {
    background-color: #2d2d2d;
    border-bottom-color: #404040;
  }

  .swagger-toolbar {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .swagger-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #333;
    margin: 0;
  }

  .dark-mode .swagger-title {
    color: #f0f0f0;
  }

  .swagger-actions {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
  }

  .swagger-btn {
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

  .swagger-btn:hover {
    background-color: #357abd;
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(74, 144, 226, 0.3);
  }

  .swagger-btn:active {
    transform: translateY(0);
  }

  .swagger-btn-icon {
    display: inline-flex;
    align-items: center;
  }

  .dark-mode .swagger-btn {
    background-color: #3a7bc8;
  }

  .dark-mode .swagger-btn:hover {
    background-color: #2e6ab3;
  }

  .swagger-loading {
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

  .swagger-loading p {
    color: #666;
    font-size: 1rem;
  }

  .dark-mode .swagger-loading p {
    color: #aaa;
  }

  .dark-mode .swagger-ui {
    filter: invert(0.88) hue-rotate(180deg);
  }

  .dark-mode .swagger-ui .microlight,
  .dark-mode .swagger-ui .model-box,
  .dark-mode .swagger-ui .prop-type,
  .dark-mode .swagger-ui .response-col_status {
    filter: invert(0.88) hue-rotate(180deg);
  }

  @media (max-width: 768px) {
    .swagger-toolbar {
      flex-direction: column;
      align-items: stretch;
    }

    .swagger-actions {
      justify-content: stretch;
    }

    .swagger-btn {
      flex: 1;
      justify-content: center;
    }
  }
`;

export const SwaggerUIWrapper = (props: SwaggerUIWrapperProps) => {
  const normalized = normalizeSwaggerProps(props);
  const { darkMode, toggleDarkMode } = useDarkMode();
  const { copied, copySpecUrl } = useCopySpecUrl(normalized.specUrl);
  const specData = useSpecData(normalized.specUrl, normalized.spec);
  const resolvedSpec = specData ?? normalized.spec ?? null;
  const { defaultRequestInterceptor, defaultResponseInterceptor } = useSwaggerInterceptors(
    normalized.requestInterceptor,
    normalized.responseInterceptor,
  );
  const swaggerProps = useSwaggerProps({
    deepLinking: normalized.deepLinking ?? true,
    displayRequestDuration: normalized.displayRequestDuration ?? true,
    filter: normalized.filter ?? true,
    persistAuthorization: normalized.persistAuthorization ?? false,
    requestInterceptor: defaultRequestInterceptor,
    resolvedSpec,
    responseInterceptor: defaultResponseInterceptor,
    specUrl: normalized.specUrl,
    tryItOutEnabled: normalized.tryItOutEnabled ?? false,
  });
  const downloadSpec = useDownloadSpec(resolvedSpec, normalized.specUrl);

  return (
    <div className={`swagger-ui-container ${darkMode ? 'dark-mode' : ''}`}>
      <SwaggerToolbar
        copied={copied}
        darkMode={darkMode}
        onCopy={copySpecUrl}
        onDownload={downloadSpec}
        onToggleDarkMode={toggleDarkMode}
      />
      <SwaggerContent
        hasSpec={Boolean(resolvedSpec ?? normalized.specUrl)}
        swaggerProps={swaggerProps}
      />
      <style>{SWAGGER_STYLES}</style>
    </div>
  );
};
