// Global type definitions

/// <reference types="vite/client" />

// Vite environment variables
interface ImportMetaEnv {
	readonly VITE_API_URL: string;
	readonly VITE_WS_URL: string;
	readonly VITE_APP_NAME: string;
	readonly VITE_APP_VERSION: string;
	readonly MODE: string;
	readonly DEV: boolean;
	readonly PROD: boolean;
	readonly SSR: boolean;
}

interface ImportMeta {
	readonly env: ImportMetaEnv;
}

// Window extensions
interface Window {
	__TRACERTM_DEVTOOLS__?: boolean;
	__wsCheckInterval?: ReturnType<typeof setInterval>;
}

// Module declarations
declare module "*.svg" {
	import React from "react";
	export const ReactComponent: React.FC<React.SVGProps<SVGSVGElement>>;
	const src: string;
	export default src;
}

declare module "*.png" {
	const content: string;
	export default content;
}

declare module "*.jpg" {
	const content: string;
	export default content;
}

declare module "*.jpeg" {
	const content: string;
	export default content;
}

declare module "*.gif" {
	const content: string;
	export default content;
}

declare module "*.webp" {
	const content: string;
	export default content;
}

declare module "*.css" {
	const content: Record<string, string>;
	export default content;
}

declare module "*.module.css" {
	const classes: Record<string, string>;
	export default classes;
}

// Extend JSX namespace for custom elements if needed
declare namespace JSX {
	// eslint-disable-next-line @typescript-eslint/no-empty-object-type
	interface IntrinsicElements extends Record<string, unknown> {}
}
