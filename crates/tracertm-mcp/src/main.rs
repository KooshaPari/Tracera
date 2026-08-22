//! Tracera MCP stdio server (native Rust; replaces python -m tracertm.mcp).
//! Hand-rolled JSON-RPC 2.0 over stdio with Content-Length framing (MCP transport).
//! Proxies tool calls to the tracera-server HTTP API.

use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use tokio::io::{AsyncReadExt, AsyncWriteExt};

fn api_base() -> String {
    std::env::var("TRACERA_API_URL").unwrap_or_else(|_| "http://127.0.0.1:3000".to_string())
}

fn auth_token() -> Option<String> {
    std::env::var("TRACERA_AUTH_TOKEN").ok().filter(|t| !t.is_empty())
}

#[derive(Debug, Deserialize)]
struct CreateIssueInput {
    title: String,
    #[serde(default)]
    description: String,
    #[serde(default = "default_priority")]
    priority: String,
}

fn default_priority() -> String { "medium".to_string() }

#[derive(Debug, Deserialize)]
struct TraceLinkInput {
    source_id: String,
    target_id: String,
    #[serde(default = "default_relationship")]
    relationship: String,
    #[serde(default = "default_confidence")]
    confidence: f64,
}

fn default_relationship() -> String { "satisfies".to_string() }
fn default_confidence() -> f64 { 1.0 }

#[derive(Debug, Deserialize)]
struct QueryTraceInput { artifact_id: String }

#[derive(Debug, Deserialize)]
struct CoverageMatrixInput { links: Vec<CoverageLink> }

#[derive(Debug, Deserialize, Serialize)]
struct CoverageLink {
    source_id: String,
    target_id: String,
    relationship: String,
    confidence: f64,
}

async fn http_get(path: &str) -> Result<String, String> {
    let url = format!("{}{}", api_base(), path);
    let client = reqwest::Client::new();
    let mut req = client.get(&url);
    if let Some(token) = auth_token() {
        req = req.bearer_auth(token);
    }
    let resp = req.send().await.map_err(|e| format!("HTTP request failed: {e}"))?;
    let status = resp.status();
    let body = resp.text().await.map_err(|e| format!("Failed to read response body: {e}"))?;
    if !status.is_success() { return Err(format!("HTTP {status}: {body}")); }
    Ok(body)
}

async fn http_post(path: &str, payload: &Value) -> Result<String, String> {
    let url = format!("{}{}", api_base(), path);
    let client = reqwest::Client::new();
    let mut req = client.post(&url).json(payload);
    if let Some(token) = auth_token() {
        req = req.bearer_auth(token);
    }
    let resp = req.send().await.map_err(|e| format!("HTTP request failed: {e}"))?;
    let status = resp.status();
    let body = resp.text().await.map_err(|e| format!("Failed to read response body: {e}"))?;
    if !status.is_success() { return Err(format!("HTTP {status}: {body}")); }
    Ok(body)
}

async fn handle_tool_call(name: &str, args: &Value) -> Value {
    match name {
        "create_issue" => {
            let input: CreateIssueInput = match serde_json::from_value(args.clone()) {
                Ok(v) => v,
                Err(e) => return tool_error(&format!("invalid arguments: {e}")),
            };
            let id = format!("story-{}", uuid_v4());
            let payload = json!({"id": id, "title": input.title, "description": input.description, "priority": input.priority, "status": "open", "story_points": null});
            match http_post("/api/v1/stories", &payload).await {
                Ok(body) => tool_result(&body),
                Err(e) => tool_error(&e),
            }
        }
        "trace_link" => {
            let input: TraceLinkInput = match serde_json::from_value(args.clone()) {
                Ok(v) => v,
                Err(e) => return tool_error(&format!("invalid arguments: {e}")),
            };
            let id = format!("tl-{}", uuid_v4());
            let payload = json!({"id": id, "source_id": input.source_id, "target_id": input.target_id, "relationship": input.relationship, "confidence": input.confidence, "source": "mcp"});
            match http_post("/api/v1/trace", &payload).await {
                Ok(body) => tool_result(&body),
                Err(e) => tool_error(&e),
            }
        }
        "query_trace" => {
            let input: QueryTraceInput = match serde_json::from_value(args.clone()) {
                Ok(v) => v,
                Err(e) => return tool_error(&format!("invalid arguments: {e}")),
            };
            let path = format!("/api/v1/trace/{}/links", input.artifact_id);
            match http_get(&path).await {
                Ok(body) => tool_result(&body),
                Err(e) => tool_error(&e),
            }
        }
        "coverage_matrix" => {
            let input: CoverageMatrixInput = match serde_json::from_value(args.clone()) {
                Ok(v) => v,
                Err(e) => return tool_error(&format!("invalid arguments: {e}")),
            };
            let links: Vec<Value> = input.links.iter().map(|l| json!({"source_id": l.source_id, "target_id": l.target_id, "relationship": l.relationship, "confidence": l.confidence})).collect();
            let payload = json!({"links": links, "stale_after_days": 30});
            match http_post("/api/v1/coverage-matrix", &payload).await {
                Ok(body) => tool_result(&body),
                Err(e) => tool_error(&e),
            }
        }
        "list_issues" => match http_get("/api/v1/stories").await {
            Ok(body) => tool_result(&body),
            Err(e) => tool_error(&e),
        },
        _ => tool_error(&format!("unknown tool: {name}")),
    }
}

fn tool_result(text: &str) -> Value {
    json!({ "content": [{ "type": "text", "text": text }] })
}

fn tool_error(text: &str) -> Value {
    json!({ "content": [{ "type": "text", "text": text }], "isError": true })
}

fn uuid_v4() -> String {
    use std::time::{SystemTime, UNIX_EPOCH};
    let t = SystemTime::now().duration_since(UNIX_EPOCH).unwrap_or_default().as_nanos();
    format!("{:032x}", t)
}

fn tool_definitions() -> Value {
    json!({
        "tools": [
            {
                "name": "create_issue",
                "description": "Create a new issue/story in Tracera with a title, description, and priority",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": { "type": "string", "description": "Short summary of the issue" },
                        "description": { "type": "string", "description": "Detailed description", "default": "" },
                        "priority": { "type": "string", "enum": ["low", "medium", "high", "critical"], "default": "medium" }
                    },
                    "required": ["title"]
                }
            },
            {
                "name": "trace_link",
                "description": "Create a directed trace link between two artifacts",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "source_id": { "type": "string", "description": "Source artifact ID" },
                        "target_id": { "type": "string", "description": "Target artifact ID" },
                        "relationship": { "type": "string", "description": "Relationship type", "default": "satisfies" },
                        "confidence": { "type": "number", "description": "Confidence 0.0-1.0", "default": 1.0 }
                    },
                    "required": ["source_id", "target_id"]
                }
            },
            {
                "name": "query_trace",
                "description": "Query trace links for a given artifact ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "artifact_id": { "type": "string", "description": "The artifact ID to trace" }
                    },
                    "required": ["artifact_id"]
                }
            },
            {
                "name": "coverage_matrix",
                "description": "Compute a coverage matrix from a set of trace links",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "links": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "source_id": { "type": "string" },
                                    "target_id": { "type": "string" },
                                    "relationship": { "type": "string" },
                                    "confidence": { "type": "number" }
                                },
                                "required": ["source_id", "target_id", "relationship", "confidence"]
                            }
                        }
                    },
                    "required": ["links"]
                }
            },
            {
                "name": "list_issues",
                "description": "List all issues/stories in Tracera",
                "inputSchema": { "type": "object", "properties": {}, "required": [] }
            }
        ]
    })
}

#[tokio::main(flavor = "current_thread")]
async fn main() {
    let mut stdin = tokio::io::stdin();
    let mut stdout = tokio::io::stdout();
    let mut buf: Vec<u8> = Vec::new();
    loop {
        let body = match read_message(&mut stdin, &mut buf).await {
            Some(b) => b,
            None => break,
        };
        let req: Value = match serde_json::from_slice(&body) {
            Ok(v) => v,
            Err(_) => continue,
        };
        let id = req.get("id").cloned();
        let method = req.get("method").and_then(|m| m.as_str()).unwrap_or("");
        let result = match method {
            "initialize" => Some(json!({
                "protocolVersion": "2024-11-05",
                "capabilities": { "tools": {} },
                "serverInfo": { "name": "tracertm-mcp", "version": "0.2.0" }
            })),
            "tools/list" => Some(tool_definitions()),
            "tools/call" => {
                let name = req.pointer("/params/name").and_then(|v| v.as_str()).unwrap_or("");
                let args = req.pointer("/params/arguments").cloned().unwrap_or(json!({}));
                Some(handle_tool_call(name, &args).await)
            }
            _ => None,
        };
        if let (Some(id), Some(result)) = (id, result) {
            let resp = json!({ "jsonrpc": "2.0", "id": id, "result": result });
            write_message(&mut stdout, &resp).await;
        }
    }
}

async fn read_message<R: AsyncReadExt + Unpin>(r: &mut R, buf: &mut Vec<u8>) -> Option<Vec<u8>> {
    loop {
        if let Some(hdr_end) = find_subslice(buf, b"\r\n\r\n") {
            let header = String::from_utf8_lossy(&buf[..hdr_end]).to_string();
            let len = header.lines().find_map(|l| l.strip_prefix("Content-Length:")).and_then(|v| v.trim().parse::<usize>().ok());
            if let Some(len) = len {
                let body_start = hdr_end + 4;
                if buf.len() >= body_start + len {
                    let body = buf[body_start..body_start + len].to_vec();
                    buf.drain(..body_start + len);
                    return Some(body);
                }
            } else {
                buf.drain(..hdr_end + 4);
                continue;
            }
        }
        let mut tmp = [0u8; 4096];
        match r.read(&mut tmp).await {
            Ok(0) => return None,
            Ok(n) => buf.extend_from_slice(&tmp[..n]),
            Err(_) => return None,
        }
    }
}

async fn write_message<W: AsyncWriteExt + Unpin>(w: &mut W, msg: &Value) {
    let body = serde_json::to_vec(msg).unwrap();
    let header = format!("Content-Length: {}\r\n\r\n", body.len());
    let _ = w.write_all(header.as_bytes()).await;
    let _ = w.write_all(&body).await;
    let _ = w.flush().await;
}

fn find_subslice(hay: &[u8], needle: &[u8]) -> Option<usize> {
    hay.windows(needle.len()).position(|w| w == needle)
}
