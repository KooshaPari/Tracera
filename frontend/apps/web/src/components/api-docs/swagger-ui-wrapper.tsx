"use client";

import { useEffect, useState } from "react";
import SwaggerUI from "swagger-ui-react";
import "swagger-ui-react/swagger-ui.css";
import { Copy, Download, Moon, Sun } from "lucide-react";

interface SwaggerUIWrapperProps {
	specUrl?: string;
	spec?: object;
	tryItOutEnabled?: boolean;
	persistAuthorization?: boolean;
	displayRequestDuration?: boolean;
	filter?: boolean;
	deepLinking?: boolean;
	requestInterceptor?: (request: any) => any;
	responseInterceptor?: (response: any) => any;
}

export function SwaggerUIWrapper({
	specUrl = "/specs/openapi.json",
	spec,
	tryItOutEnabled = true,
	persistAuthorization = true,
	displayRequestDuration = true,
	filter = true,
	deepLinking = true,
	requestInterceptor,
	responseInterceptor,
}: SwaggerUIWrapperProps) {
	const [darkMode, setDarkMode] = useState(false);
	const [copied, setCopied] = useState(false);
	const [specData, setSpecData] = useState<any>(null);

	useEffect(() => {
		// Check for dark mode preference
		const isDark =
			document.documentElement.classList.contains("dark") ||
			window.matchMedia("(prefers-color-scheme: dark)").matches;
		setDarkMode(isDark);

		// Load spec if URL is provided and no spec object
		if (specUrl && !spec) {
			fetch(specUrl)
				.then((res) => res.json())
				.then((data) => setSpecData(data))
				.catch((err) => console.error("Failed to load OpenAPI spec:", err));
		} else if (spec) {
			setSpecData(spec);
		}
	}, [specUrl, spec]);

	const toggleDarkMode = () => {
		setDarkMode(!darkMode);
		document.documentElement.classList.toggle("dark");
	};

	const downloadSpec = async () => {
		const dataToDownload = specData || spec;
		if (!dataToDownload) {
			if (specUrl) {
				const response = await fetch(specUrl);
				const data = await response.json();
				downloadJSON(data);
			}
			return;
		}
		downloadJSON(dataToDownload);
	};

	const downloadJSON = (data: any) => {
		const blob = new Blob([JSON.stringify(data, null, 2)], {
			type: "application/json",
		});
		const url = URL.createObjectURL(blob);
		const a = document.createElement("a");
		a.href = url;
		a.download = "openapi-spec.json";
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);
		URL.revokeObjectURL(url);
	};

	const copySpecUrl = () => {
		const fullUrl = window.location.origin + specUrl;
		navigator.clipboard.writeText(fullUrl).then(() => {
			setCopied(true);
			setTimeout(() => setCopied(false), 2000);
		});
	};

	// Default request interceptor to add authentication (SSR-safe)
	const defaultRequestInterceptor = (req: any) => {
		// Check for stored token (SSR-safe)
		const isStorageAvailable =
			typeof localStorage !== "undefined" &&
			typeof localStorage.getItem === "function";
		const token = isStorageAvailable ? localStorage.getItem("api_token") : null;
		const apiKey = isStorageAvailable ? localStorage.getItem("api_key") : null;

		if (token) {
			req.headers.Authorization = `Bearer ${token}`;
		}
		if (apiKey) {
			req.headers["X-API-Key"] = apiKey;
		}

		return requestInterceptor ? requestInterceptor(req) : req;
	};

	// Default response interceptor for logging
	const defaultResponseInterceptor = (res: any) => {
		// Log response for debugging
		console.log("API Response:", {
			url: res.url,
			status: res.status,
			duration: res.duration,
		});

		return responseInterceptor ? responseInterceptor(res) : res;
	};

	return (
		<div className={`swagger-ui-container ${darkMode ? "dark-mode" : ""}`}>
			<div className="swagger-controls">
				<div className="swagger-toolbar">
					<h1 className="swagger-title">API Documentation</h1>
					<div className="swagger-actions">
						<button
							type="button"
							onClick={copySpecUrl}
							className="swagger-btn"
							title="Copy Spec URL"
						>
							<Copy size={18} />
							{copied ? "Copied!" : "Copy URL"}
						</button>
						<button
							type="button"
							onClick={downloadSpec}
							className="swagger-btn"
							title="Download OpenAPI Spec"
						>
							<Download size={18} />
							Download Spec
						</button>
						<button
							type="button"
							onClick={toggleDarkMode}
							className="swagger-btn"
							title="Toggle Dark Mode"
						>
							{darkMode ? <Sun size={18} /> : <Moon size={18} />}
							{darkMode ? "Light" : "Dark"}
						</button>
					</div>
				</div>
			</div>

			{specData || spec ? (
				<SwaggerUI
					spec={specData || spec}
					{...(specUrl && !spec && !specData ? { url: specUrl } : {})}
					tryItOutEnabled={tryItOutEnabled}
					persistAuthorization={persistAuthorization}
					displayRequestDuration={displayRequestDuration}
					filter={filter}
					deepLinking={deepLinking}
					requestInterceptor={defaultRequestInterceptor}
					responseInterceptor={defaultResponseInterceptor}
					docExpansion="list"
					defaultModelsExpandDepth={1}
					defaultModelExpandDepth={1}
					displayOperationId={false}
					showExtensions={false}
					showCommonExtensions={false}
					supportedSubmitMethods={[
						"get",
						"put",
						"post",
						"delete",
						"options",
						"head",
						"patch",
						"trace",
					]}
				/>
			) : (
				<div className="swagger-loading">
					<div className="spinner" />
					<p>Loading API Documentation...</p>
				</div>
			)}

			<style>{`
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

        /* Dark mode Swagger UI overrides */
        .dark-mode .swagger-ui {
          filter: invert(0.88) hue-rotate(180deg);
        }

        .dark-mode .swagger-ui .microlight,
        .dark-mode .swagger-ui .model-box,
        .dark-mode .swagger-ui .prop-type,
        .dark-mode .swagger-ui .response-col_status {
          filter: invert(0.88) hue-rotate(180deg);
        }

        /* Responsive design */
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
      `}</style>
		</div>
	);
}
