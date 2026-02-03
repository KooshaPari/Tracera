"use client";

import "swagger-ui-react/swagger-ui.css";

import { Copy, Download, Moon, Sun } from "lucide-react";
import { type ReactNode, useCallback, useEffect, useMemo, useState } from "react";
import SwaggerUI, { type SwaggerUIProps } from "swagger-ui-react";
import { logger } from "@/lib/logger";

interface SwaggerUIWrapperProps {
	specUrl?: string;
	spec?: object;
	tryItOutEnabled?: boolean;
	persistAuthorization?: boolean;
	displayRequestDuration?: boolean;
	filter?: boolean;
	deepLinking?: boolean;
	requestInterceptor?: SwaggerUIProps["requestInterceptor"];
	responseInterceptor?: SwaggerUIProps["responseInterceptor"];
}

const COPY_RESET_MS = 2000;
const DEFAULT_MODELS_EXPAND_DEPTH = 1;
const ICON_SIZE = 18;
const JSON_INDENT = 2;
const SWAGGER_DEFAULTS = {
	deepLinking: true,
	displayRequestDuration: true,
	filter: true,
	persistAuthorization: true,
	specUrl: "/specs/openapi.json",
	tryItOutEnabled: true,
};

const SUPPORTED_SUBMIT_METHODS: NonNullable<
	SwaggerUIProps["supportedSubmitMethods"]
> = ["get", "put", "post", "delete", "options", "head", "patch", "trace"];

const downloadOpenApiJson = (data: unknown): void => {
	const blob = new Blob([JSON.stringify(data, null, JSON_INDENT)], {
		type: "application/json",
	});
	const url = URL.createObjectURL(blob);
	const anchor = document.createElement("a");
	anchor.href = url;
	anchor.download = "openapi-spec.json";
	document.body.append(anchor);
	anchor.click();
	document.body.removeChild(anchor);
	URL.revokeObjectURL(url);
};

const resolveDarkModePreference = (): boolean =>
	document.documentElement.classList.contains("dark") ||
	globalThis.matchMedia("(prefers-color-scheme: dark)").matches;

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
			.then((res) => res.json())
			.then((data) => setSpecData(data))
			.catch((error) => logger.error("Failed to load OpenAPI spec:", error));
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
			document.documentElement.classList.toggle("dark", next);
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
			if (navigator.clipboard?.writeText) {
				await navigator.clipboard.writeText(fullUrl);
			} else {
				const textarea = document.createElement("textarea");
				textarea.value = fullUrl;
				textarea.setAttribute("readonly", "true");
				textarea.style.position = "absolute";
				textarea.style.left = "-9999px";
				document.body.append(textarea);
				textarea.select();
				document.execCommand("copy");
				document.body.removeChild(textarea);
			}

			setCopied(true);
			window.setTimeout(() => setCopied(false), COPY_RESET_MS);
		} catch (error) {
			logger.error("Failed to copy spec URL:", error);
		}
	}, [specUrl]);

	return { copied, copySpecUrl };
};

const LoadingState = ({ label }: { label: string }) => (
	<div className="swagger-loading">
		<div className="spinner" />
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
	<button type="button" onClick={onClick} className="swagger-btn" title={title}>
		<span className="swagger-btn-icon">{icon}</span>
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
	<div className="swagger-controls">
		<div className="swagger-toolbar">
			<h1 className="swagger-title">API Documentation</h1>
			<div className="swagger-actions">
				<IconLabelButton
					onClick={onCopy}
					icon={<Copy size={ICON_SIZE} />}
					label={copied ? "Copied!" : "Copy URL"}
					title="Copy Spec URL"
				/>
				<IconLabelButton
					onClick={onDownload}
					icon={<Download size={ICON_SIZE} />}
					label="Download Spec"
					title="Download OpenAPI Spec"
				/>
				<IconLabelButton
					onClick={onToggleDarkMode}
					icon={darkMode ? <Sun size={ICON_SIZE} /> : <Moon size={ICON_SIZE} />}
					label={darkMode ? "Light" : "Dark"}
					title="Toggle Dark Mode"
				/>
			</div>
		</div>
	</div>
);

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

export const SwaggerUIWrapper = ({
	specUrl = SWAGGER_DEFAULTS.specUrl,
	spec,
	tryItOutEnabled = SWAGGER_DEFAULTS.tryItOutEnabled,
	persistAuthorization = SWAGGER_DEFAULTS.persistAuthorization,
	displayRequestDuration = SWAGGER_DEFAULTS.displayRequestDuration,
	filter = SWAGGER_DEFAULTS.filter,
	deepLinking = SWAGGER_DEFAULTS.deepLinking,
	requestInterceptor,
	responseInterceptor,
}: SwaggerUIWrapperProps) => {
	const { darkMode, toggleDarkMode } = useDarkMode();
	const { copied, copySpecUrl } = useCopySpecUrl(specUrl);
	const specData = useSpecData(specUrl, spec);
	const resolvedSpec = specData ?? spec ?? null;

	const downloadSpec = useCallback(async () => {
		const dataToDownload = resolvedSpec;
		if (dataToDownload) {
			downloadOpenApiJson(dataToDownload);
			return;
		}

		if (!specUrl) {
			return;
		}

		const response = await fetch(specUrl);
		const data = await response.json();
		downloadOpenApiJson(data);
	}, [resolvedSpec, specUrl]);

	const defaultRequestInterceptor = useCallback<
		NonNullable<SwaggerUIProps["requestInterceptor"]>
	>(
		(req) => {
			const isStorageAvailable =
				typeof localStorage !== "undefined" &&
				typeof localStorage.getItem === "function";
			const token = isStorageAvailable ? localStorage.getItem("api_token") : null;
			const apiKey = isStorageAvailable ? localStorage.getItem("api_key") : null;

			if (token) {
				req.headers.set("Authorization", `Bearer ${token}`);
			}
			if (apiKey) {
				req.headers.set("X-API-Key", apiKey);
			}

			return requestInterceptor ? requestInterceptor(req) : req;
		},
		[requestInterceptor],
	);

	const defaultResponseInterceptor = useCallback<
		NonNullable<SwaggerUIProps["responseInterceptor"]>
	>(
		(res) => {
			logger.info("API Response:", {
				status: res.status,
				url: res.url,
			});

			return responseInterceptor ? responseInterceptor(res) : res;
		},
		[responseInterceptor],
	);

	const swaggerProps = useMemo<SwaggerUIProps>(
		() => ({
			deepLinking,
			defaultModelExpandDepth: DEFAULT_MODELS_EXPAND_DEPTH,
			defaultModelsExpandDepth: DEFAULT_MODELS_EXPAND_DEPTH,
			displayOperationId: false,
			displayRequestDuration,
			docExpansion: "list",
			filter,
			persistAuthorization,
			requestInterceptor: defaultRequestInterceptor,
			responseInterceptor: defaultResponseInterceptor,
			showCommonExtensions: false,
			showExtensions: false,
			spec: resolvedSpec ?? undefined,
			supportedSubmitMethods: SUPPORTED_SUBMIT_METHODS,
			tryItOutEnabled,
			url: resolvedSpec ? undefined : specUrl,
		}),
		[
			deepLinking,
			displayRequestDuration,
			filter,
			persistAuthorization,
			defaultRequestInterceptor,
			defaultResponseInterceptor,
			resolvedSpec,
			specUrl,
			tryItOutEnabled,
		],
	);

	return (
		<div className={`swagger-ui-container ${darkMode ? "dark-mode" : ""}`}>
			<SwaggerToolbar
				copied={copied}
				darkMode={darkMode}
				onCopy={copySpecUrl}
				onDownload={downloadSpec}
				onToggleDarkMode={toggleDarkMode}
			/>
			{resolvedSpec || specUrl ? (
				<SwaggerUI {...swaggerProps} />
			) : (
				<LoadingState label="Loading API Documentation..." />
			)}
			<style>{SWAGGER_STYLES}</style>
		</div>
	);
};
