"use client";

import { Copy, Download, ExternalLink, Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";
import { RedocStandalone } from "redoc";

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

export function RedocWrapper({
	specUrl = "/specs/openapi.json",
	spec,
	scrollYOffset = 80,
	hideDownloadButton = false,
	disableSearch = false,
	expandResponses = "200,201",
	requiredPropsFirst = true,
	sortPropsAlphabetically = false,
	showExtensions = false,
	nativeScrollbars = false,
	pathInMiddlePanel = false,
	hideHostname = false,
	expandSingleSchemaField = true,
}: RedocWrapperProps) {
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

	const openInSwagger = () => {
		const swaggerUrl = `/api-docs/swagger`;
		window.open(swaggerUrl, "_blank");
	};

	const redocOptions = {
		scrollYOffset,
		hideDownloadButton,
		disableSearch,
		expandResponses,
		requiredPropsFirst,
		sortPropsAlphabetically,
		showExtensions,
		nativeScrollbars,
		pathInMiddlePanel,
		hideHostname,
		expandSingleSchemaField,
		theme: {
			colors: darkMode
				? {
						primary: {
							main: "#4a90e2",
						},
						text: {
							primary: "#f0f0f0",
							secondary: "#b0b0b0",
						},
						border: {
							dark: "#404040",
							light: "#505050",
						},
						http: {
							get: "#6bbd5b",
							post: "#248fb2",
							put: "#9b708b",
							options: "#d3ca12",
							patch: "#e09d43",
							delete: "#e27a7a",
							basic: "#999",
							link: "#31bbb6",
							head: "#c167e4",
						},
					}
				: {
						primary: {
							main: "#4a90e2",
						},
						text: {
							primary: "#333",
							secondary: "#666",
						},
						border: {
							dark: "#e0e0e0",
							light: "#f0f0f0",
						},
						http: {
							get: "#61affe",
							post: "#49cc90",
							put: "#fca130",
							options: "#d3ca12",
							patch: "#50e3c2",
							delete: "#f93e3e",
							basic: "#999",
							link: "#31bbb6",
							head: "#c167e4",
						},
					},
			typography: {
				fontSize: "16px",
				fontFamily:
					'-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
				headings: {
					fontFamily:
						'-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
					fontWeight: "700",
				},
				code: {
					fontSize: "14px",
					fontFamily: '"Fira Code", "Courier New", monospace',
					fontWeight: "400",
				},
			},
			sidebar: {
				backgroundColor: darkMode ? "#2d2d2d" : "#fafafa",
				textColor: darkMode ? "#f0f0f0" : "#333",
				activeTextColor: "#4a90e2",
				width: "280px",
			},
			rightPanel: {
				backgroundColor: darkMode ? "#1a1a1a" : "#263238",
				textColor: "#ffffff",
			},
		},
	};

	return (
		<div className={`redoc-container ${darkMode ? "dark-mode" : ""}`}>
			<div className="redoc-controls">
				<div className="redoc-toolbar">
					<h1 className="redoc-title">API Reference</h1>
					<div className="redoc-actions">
						<button
							type="button"
							onClick={copySpecUrl}
							className="redoc-btn"
							title="Copy Spec URL"
						>
							<Copy size={18} />
							{copied ? "Copied!" : "Copy URL"}
						</button>
						<button
							type="button"
							onClick={downloadSpec}
							className="redoc-btn"
							title="Download OpenAPI Spec"
						>
							<Download size={18} />
							Download
						</button>
						<button
							type="button"
							onClick={openInSwagger}
							className="redoc-btn"
							title="Open in Swagger UI"
						>
							<ExternalLink size={18} />
							Swagger UI
						</button>
						<button
							type="button"
							onClick={toggleDarkMode}
							className="redoc-btn"
							title="Toggle Dark Mode"
						>
							{darkMode ? <Sun size={18} /> : <Moon size={18} />}
							{darkMode ? "Light" : "Dark"}
						</button>
					</div>
				</div>
			</div>

			{specData || spec ? (
				<RedocStandalone
					spec={specData || spec}
					{...(specUrl && !spec && !specData ? { specUrl } : {})}
					options={redocOptions}
				/>
			) : (
				<div className="redoc-loading">
					<div className="spinner" />
					<p>Loading API Reference...</p>
				</div>
			)}

			<style>{`
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

        /* Responsive design */
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
      `}</style>
		</div>
	);
}
