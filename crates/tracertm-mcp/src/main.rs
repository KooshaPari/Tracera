//! Minimal Tracera MCP stdio server (native Rust; replaces `python -m tracertm.mcp`).
//! Hand-rolled JSON-RPC 2.0 over stdio with Content-Length framing (MCP transport).
//! Supports: initialize, tools/list, tools/call (get_health). ponytail: minimal — add tools as needed.

use serde_json::{json, Value};
use tokio::io::{AsyncReadExt, AsyncWriteExt};

#[tokio::main(flavor = "current_thread")]
async fn main() {
    let mut stdin = tokio::io::stdin();
    let mut stdout = tokio::io::stdout();
    let mut buf: Vec<u8> = Vec::new();

    loop {
        // Read one Content-Length-framed message.
        let body = match read_message(&mut stdin, &mut buf).await {
            Some(b) => b,
            None => break, // EOF
        };
        let req: Value = match serde_json::from_slice(&body) {
            Ok(v) => v,
            Err(_) => continue,
        };

        let id = req.get("id").cloned();
        let method = req.get("method").and_then(|m| m.as_str()).unwrap_or("");

        // Notifications (no id) get no response.
        let result = match method {
            "initialize" => Some(json!({
                "protocolVersion": "2024-11-05",
                "capabilities": { "tools": {} },
                "serverInfo": { "name": "tracertm-mcp", "version": "0.1.0" }
            })),
            "tools/list" => Some(json!({
                "tools": [{
                    "name": "get_health",
                    "description": "Tracera health check",
                    "inputSchema": { "type": "object", "properties": {} }
                }]
            })),
            "tools/call" => {
                let name = req
                    .pointer("/params/name")
                    .and_then(|v| v.as_str())
                    .unwrap_or("");
                if name == "get_health" {
                    Some(json!({ "content": [{ "type": "text", "text": "{\"status\":\"ok\"}" }] }))
                } else {
                    Some(
                        json!({ "content": [{ "type": "text", "text": "unknown tool" }], "isError": true }),
                    )
                }
            }
            _ => None,
        };

        if let (Some(id), Some(result)) = (id, result) {
            let resp = json!({ "jsonrpc": "2.0", "id": id, "result": result });
            write_message(&mut stdout, &resp).await;
        }
    }
}

/// Read a single Content-Length-framed JSON-RPC message body. Returns None on EOF.
async fn read_message<R: AsyncReadExt + Unpin>(r: &mut R, buf: &mut Vec<u8>) -> Option<Vec<u8>> {
    loop {
        // Look for the header/body separator already in buf.
        if let Some(hdr_end) = find_subslice(buf, b"\r\n\r\n") {
            let header = String::from_utf8_lossy(&buf[..hdr_end]).to_string();
            let len = header
                .lines()
                .find_map(|l| l.strip_prefix("Content-Length:"))
                .and_then(|v| v.trim().parse::<usize>().ok());
            if let Some(len) = len {
                let body_start = hdr_end + 4;
                if buf.len() >= body_start + len {
                    let body = buf[body_start..body_start + len].to_vec();
                    buf.drain(..body_start + len);
                    return Some(body);
                }
            } else {
                // Malformed header — drop it.
                buf.drain(..hdr_end + 4);
                continue;
            }
        }
        // Need more bytes.
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
