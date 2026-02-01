/**
 * Tests for MCP HTTP Client
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createMCPClient, type MCPClient } from "../../api/mcp-client";

// Mock fetch globally
global.fetch = vi.fn();

describe("MCPClient", () => {
	let client: MCPClient;

	beforeEach(() => {
		client = createMCPClient({
			baseUrl: "http://localhost:4000",
			token: "test-token",
			timeout: 5000,
		});

		// Reset fetch mock
		vi.clearAllMocks();
	});

	afterEach(async () => {
		// Mock close call to prevent errors
		(global.fetch as any).mockResolvedValueOnce({
			ok: true,
			json: async () => ({}),
		});
		await client.close();
	});

	describe("initialization", () => {
		it("should create client with correct config", () => {
			expect(client).toBeDefined();
		});

		it("should initialize with server", async () => {
			const mockResponse = {
				jsonrpc: "2.0",
				id: 1,
				result: {
					protocolVersion: "2024-11-05",
					serverInfo: {
						name: "TraceRTM MCP Server",
						version: "1.0.0",
					},
					capabilities: {
						tools: true,
						resources: true,
						prompts: true,
					},
				},
			};

			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				json: async () => mockResponse,
			});

			const result = await client.initialize();

			expect(result.serverInfo.name).toBe("TraceRTM MCP Server");
			expect(result.protocolVersion).toBe("2024-11-05");
			expect(global.fetch).toHaveBeenCalledWith(
				"http://localhost:4000/mcp/rpc",
				expect.objectContaining({
					method: "POST",
					headers: expect.objectContaining({
						"Content-Type": "application/json",
						Authorization: "Bearer test-token",
					}),
				}),
			);
		});
	});

	describe("tools", () => {
		it("should list available tools", async () => {
			const mockResponse = {
				jsonrpc: "2.0",
				id: 1,
				result: {
					tools: [
						{
							name: "project_manage",
							description: "Manage projects",
							parameters: [],
						},
					],
				},
			};

			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				json: async () => mockResponse,
			});

			const result = await client.listTools();

			expect(result.tools).toHaveLength(1);
			expect(result.tools[0].name).toBe("project_manage");
		});

		it("should call a tool with parameters", async () => {
			const mockResponse = {
				jsonrpc: "2.0",
				id: 1,
				result: {
					projects: [{ id: "1", name: "Test Project" }],
				},
			};

			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				json: async () => mockResponse,
			});

			const result = await client.callTool("project_manage", {
				action: "list",
			});

			expect(result).toHaveProperty("projects");
			expect(result.projects).toHaveLength(1);
		});
	});

	describe("resources", () => {
		it("should list available resources", async () => {
			const mockResponse = {
				jsonrpc: "2.0",
				id: 1,
				result: {
					resources: [
						{
							uri: "tracertm://project/1",
							name: "Project 1",
							mimeType: "application/json",
						},
					],
				},
			};

			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				json: async () => mockResponse,
			});

			const result = await client.listResources();

			expect(result.resources).toHaveLength(1);
			expect(result.resources[0].uri).toBe("tracertm://project/1");
		});

		it("should read a resource by URI", async () => {
			const mockResponse = {
				jsonrpc: "2.0",
				id: 1,
				result: {
					contents: { id: "1", name: "Test Project" },
				},
			};

			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				json: async () => mockResponse,
			});

			const result = await client.readResource("tracertm://project/1");

			expect(result.contents).toHaveProperty("id");
			expect(result.contents).toHaveProperty("name");
		});
	});

	describe("prompts", () => {
		it("should list available prompts", async () => {
			const mockResponse = {
				jsonrpc: "2.0",
				id: 1,
				result: {
					prompts: [
						{
							name: "analyze_requirements",
							description: "Analyze requirements",
						},
					],
				},
			};

			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				json: async () => mockResponse,
			});

			const result = await client.listPrompts();

			expect(result.prompts).toHaveLength(1);
			expect(result.prompts[0].name).toBe("analyze_requirements");
		});

		it("should get a prompt with arguments", async () => {
			const mockResponse = {
				jsonrpc: "2.0",
				id: 1,
				result: {
					messages: [{ role: "user", content: "Analyze this requirement" }],
				},
			};

			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				json: async () => mockResponse,
			});

			const result = await client.getPrompt("analyze_requirements", {
				requirementId: "123",
			});

			expect(result.messages).toHaveLength(1);
		});
	});

	describe("error handling", () => {
		it("should handle HTTP errors", async () => {
			(global.fetch as any).mockResolvedValueOnce({
				ok: false,
				status: 404,
				statusText: "Not Found",
			});

			await expect(client.listTools()).rejects.toThrow("HTTP 404: Not Found");
		});

		it("should handle JSON-RPC errors", async () => {
			const mockResponse = {
				jsonrpc: "2.0",
				id: 1,
				error: {
					code: -32602,
					message: "Invalid params",
				},
			};

			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				json: async () => mockResponse,
			});

			await expect(client.listTools()).rejects.toThrow(
				"JSON-RPC Error -32602: Invalid params",
			);
		});

		it("should handle missing result", async () => {
			const mockResponse = {
				jsonrpc: "2.0",
				id: 1,
			};

			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				json: async () => mockResponse,
			});

			await expect(client.listTools()).rejects.toThrow(
				"Invalid JSON-RPC response: missing result",
			);
		});

		it("should handle network timeout", async () => {
			vi.useFakeTimers();

			const fetchPromise = new Promise(() => {
				// Never resolves
			});

			(global.fetch as any).mockReturnValueOnce(fetchPromise);

			const callPromise = client.listTools();
			const expectation = expect(callPromise).rejects.toThrow();

			// Fast-forward past timeout
			await vi.advanceTimersByTimeAsync(6000);
			await expectation;

			vi.useRealTimers();
		});
	});

	describe("authentication", () => {
		it("should include bearer token in requests", async () => {
			const mockResponse = {
				jsonrpc: "2.0",
				id: 1,
				result: { tools: [] },
			};

			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				json: async () => mockResponse,
			});

			await client.listTools();

			expect(global.fetch).toHaveBeenCalledWith(
				expect.any(String),
				expect.objectContaining({
					headers: expect.objectContaining({
						Authorization: "Bearer test-token",
					}),
				}),
			);
		});

		it("should work without token", async () => {
			const clientNoToken = createMCPClient({
				baseUrl: "http://localhost:4000",
			});

			const mockResponse = {
				jsonrpc: "2.0",
				id: 1,
				result: { tools: [] },
			};

			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				json: async () => mockResponse,
			});

			await clientNoToken.listTools();

			expect(global.fetch).toHaveBeenCalledWith(
				expect.any(String),
				expect.objectContaining({
					headers: expect.not.objectContaining({
						Authorization: expect.any(String),
					}),
				}),
			);

			await clientNoToken.close();
		});

		it("should update token dynamically", async () => {
			client.setToken("new-token");

			const mockResponse = {
				jsonrpc: "2.0",
				id: 1,
				result: { tools: [] },
			};

			(global.fetch as any).mockResolvedValueOnce({
				ok: true,
				json: async () => mockResponse,
			});

			await client.listTools();

			expect(global.fetch).toHaveBeenCalledWith(
				expect.any(String),
				expect.objectContaining({
					headers: expect.objectContaining({
						Authorization: "Bearer new-token",
					}),
				}),
			);
		});
	});
});
