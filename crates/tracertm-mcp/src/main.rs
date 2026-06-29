use serde_json::{json, Value};
use tokio::io::{self, AsyncBufReadExt, AsyncReadExt, AsyncWriteExt, BufReader};

type Result<T> = std::result::Result<T, Box<dyn std::error::Error>>;

#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<()> {
    let stdin = io::stdin();
    let mut reader = BufReader::new(stdin);
    let mut stdout = io::stdout();

    while let Some(request) = read_message(&mut reader).await? {
        if let Some(response) = handle(request) {
            write_message(&mut stdout, &response).await?;
        }
    }

    Ok(())
}

async fn read_message<R>(reader: &mut BufReader<R>) -> Result<Option<Value>>
where
    R: AsyncReadExt + Unpin,
{
    let mut content_len = None;

    loop {
        let mut line = String::new();
        if reader.read_line(&mut line).await? == 0 {
            return Ok(None);
        }

        let trimmed = line.trim_end_matches(['\r', '\n']);
        if trimmed.is_empty() {
            break;
        }

        if let Some(value) = trimmed.strip_prefix("Content-Length:") {
            content_len = Some(value.trim().parse::<usize>()?);
        }
    }

    let len = content_len.ok_or("missing Content-Length")?;
    let mut body = vec![0; len];
    reader.read_exact(&mut body).await?;
    Ok(Some(serde_json::from_slice(&body)?))
}

async fn write_message<W>(writer: &mut W, response: &Value) -> Result<()>
where
    W: AsyncWriteExt + Unpin,
{
    let body = serde_json::to_vec(response)?;
    writer
        .write_all(format!("Content-Length: {}\r\n\r\n", body.len()).as_bytes())
        .await?;
    writer.write_all(&body).await?;
    writer.flush().await?;
    Ok(())
}

fn handle(request: Value) -> Option<Value> {
    let id = request.get("id").cloned();
    let method = request.get("method")?.as_str()?;

    let result = match method {
        "initialize" => json!({
            "protocolVersion": "2024-11-05",
            "capabilities": { "tools": {} },
            "serverInfo": { "name": "tracertm-mcp", "version": "0.1.0" }
        }),
        "tools/list" => json!({
            "tools": [{
                "name": "get_health",
                "description": "Tracera health",
                "inputSchema": { "type": "object" }
            }]
        }),
        "tools/call" => {
            let name = request.pointer("/params/name").and_then(Value::as_str);
            if name != Some("get_health") {
                return id.map(|id| error(id, -32602, "unknown tool"));
            }
            json!({
                "content": [{
                    "type": "text",
                    "text": "{\"status\":\"ok\"}"
                }]
            })
        }
        _ => return id.map(|id| error(id, -32601, "method not found")),
    };

    id.map(|id| json!({ "jsonrpc": "2.0", "id": id, "result": result }))
}

fn error(id: Value, code: i64, message: &str) -> Value {
    json!({ "jsonrpc": "2.0", "id": id, "error": { "code": code, "message": message } })
}
