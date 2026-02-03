import type EventSourcePolyfill from "event-source-polyfill";

type JsonRpcRequest = {
	id: string | number;
	jsonrpc: "2.0";
	method: string;
	params?: Record<string, unknown>;
};

type JsonRpcResponse<TResult = unknown> = {
	error?: {
		code: number;
		data?: unknown;
		message: string;
	};
	id: string | number;
	jsonrpc: "2.0";
	result?: TResult;
};

type MCPToolParam = {
	description?: string;
	default?: unknown;
	name: string;
	required?: boolean;
	type: string;
};

type MCPTool = {
	description: string;
	name: string;
	parameters: MCPToolParam[];
};

type MCPResource = {
	description?: string;
	mimeType?: string;
	name: string;
	uri: string;
};

type MCPPrompt = {
	arguments?: MCPToolParam[];
	description?: string;
	name: string;
};

type ProgressNotification = {
	message?: string;
	progress: number;
	total?: number;
};

type MCPClientConfig = {
	baseUrl: string;
	token?: string;
	timeout?: number;
};

type MCPEventSource = InstanceType<typeof EventSourcePolyfill>;

type MCPClientTypes = {
	JsonRpcRequest: JsonRpcRequest;
	JsonRpcResponse: JsonRpcResponse;
	MCPClientConfig: MCPClientConfig;
	MCPEventSource: MCPEventSource;
	MCPPrompt: MCPPrompt;
	MCPResource: MCPResource;
	MCPTool: MCPTool;
	MCPToolParam: MCPToolParam;
	ProgressNotification: ProgressNotification;
};

export type {
	JsonRpcRequest,
	JsonRpcResponse,
	MCPClientConfig,
	MCPClientTypes,
	MCPEventSource,
	MCPPrompt,
	MCPResource,
	MCPTool,
	MCPToolParam,
	ProgressNotification,
};
