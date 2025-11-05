# FastMCP curl Command Patterns Summary

**Quick Reference Guide for HTTP Requests to FastMCP Tools**

---

## Quick Start Pattern

### Basic Setup

1. Start FastMCP server:
```bash
python server.py  # Must be running before curl requests
```

2. Server accessible at: `http://localhost:8000/mcp`

---

## Essential curl Headers

All FastMCP requests require these headers:

```bash
-H "Content-Type: application/json"
-H "Accept: application/json, text/event-stream"
```

Optional headers:

```bash
-H "Mcp-Session-Id: <session-id>"        # For session persistence
-H "Authorization: Bearer <token>"       # For authenticated servers
```

---

## Core curl Patterns

### Pattern 1: Initialize Connection

**When to use:** First request to establish session

```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-03-26",
      "capabilities": {"sampling": {}, "roots": {"listChanged": true}},
      "clientInfo": {"name": "my-client", "version": "1.0.0"}
    }
  }'
```

Then send initialization confirmation:

```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "initialized"}'
```

### Pattern 2: List Available Tools

**When to use:** Discover what tools are available

```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'
```

### Pattern 3: Call a Tool (Basic)

**When to use:** Execute a tool with simple arguments

```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "TOOL_NAME",
      "arguments": {
        "param1": "value1",
        "param2": "value2"
      }
    }
  }'
```

### Pattern 4: Call a Tool (With Session)

**When to use:** Reuse session for multiple calls

```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: abc-123-def" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "TOOL_NAME",
      "arguments": {"param1": "value1"}
    }
  }'
```

### Pattern 5: Call a Tool (With Authentication)

**When to use:** Access protected tools with bearer token

```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-token" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "TOOL_NAME",
      "arguments": {"param1": "value1"}
    }
  }'
```

### Pattern 6: List Resources

**When to use:** Discover available resources

```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "resources/list", "params": {}}'
```

### Pattern 7: Read a Resource

**When to use:** Access static or templated resource content

```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "resources/read",
    "params": {"uri": "file:///config/settings.json"}
  }'
```

### Pattern 8: Health Check

**When to use:** Verify server is running

```bash
curl http://localhost:8000/health
```

---

## Real-World Examples

### Example 1: Add Two Numbers

**Tool definition:**
```python
@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
```

**curl command:**
```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "add",
      "arguments": {"a": 10, "b": 20}
    }
  }'
```

**Expected response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {"type": "text", "text": "30"}
}
```

---

### Example 2: Text Processing with Optional Parameters

**Tool definition:**
```python
@mcp.tool
def truncate(text: str, length: int = 50) -> str:
    """Truncate text to specified length."""
    return text[:length]
```

**curl command:**
```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "truncate",
      "arguments": {
        "text": "This is a long text that will be truncated",
        "length": 20
      }
    }
  }'
```

---

### Example 3: Complex Tool with Object Parameters

**Tool definition:**
```python
@mcp.tool
def process_order(order_id: int, items: list, apply_discount: bool = False) -> dict:
    """Process an order."""
    return {"order_id": order_id, "items": items, "discount": apply_discount}
```

**curl command:**
```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "process_order",
      "arguments": {
        "order_id": 12345,
        "items": ["item1", "item2", "item3"],
        "apply_discount": true
      }
    }
  }'
```

---

### Example 4: Multi-Step Workflow with Session

**Step 1: Initialize**
```bash
SESSION_INIT=$(curl -s -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "cli", "version": "1.0"}}}')

echo "$SESSION_INIT"
```

**Step 2: Extract Session ID (if provided)**
```bash
SESSION_ID=$(echo "$SESSION_INIT" | grep -o '"Mcp-Session-Id":"[^"]*"' | cut -d'"' -f4)
```

**Step 3: List Tools**
```bash
curl -s -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}'
```

**Step 4: Call Multiple Tools in Sequence**
```bash
# First call
curl -s -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "add", "arguments": {"a": 10, "b": 5}}}'

# Second call (reusing session)
curl -s -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "multiply", "arguments": {"a": 10, "b": 5}}}'
```

---

## Argument Types & Examples

### String Arguments

```bash
"arguments": {"name": "Alice", "city": "New York"}
```

### Integer & Float Arguments

```bash
"arguments": {"count": 5, "price": 19.99}
```

### Boolean Arguments

```bash
"arguments": {"enabled": true, "debug": false}
```

### List Arguments

```bash
"arguments": {"items": ["apple", "banana", "cherry"], "numbers": [1, 2, 3]}
```

### Object/Dictionary Arguments

```bash
"arguments": {"config": {"debug": true, "timeout": 30}, "metadata": {"version": "1.0"}}
```

### Null/None Arguments

```bash
"arguments": {"optional_field": null}
```

---

## Advanced Patterns

### Pattern: With Verbose Output

**For debugging requests/responses:**

```bash
curl -v -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "add", "arguments": {"a": 1, "b": 2}}}'
```

### Pattern: With Timeout

**For long-running operations:**

```bash
curl --max-time 30 \
  -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "process", "arguments": {}}}'
```

### Pattern: Save to File

**For processing responses:**

```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' \
  > response.json

cat response.json | jq .
```

### Pattern: Pretty Print Response

**For readability:**

```bash
curl -s -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' \
  | jq .
```

### Pattern: Extract Specific Field from Response

**For scripting:**

```bash
RESULT=$(curl -s -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "add", "arguments": {"a": 10, "b": 20}}}')

echo "$RESULT" | jq '.result.text'  # Output: "30"
```

---

## Error Handling Patterns

### Pattern: Check for Errors

```bash
RESPONSE=$(curl -s -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "nonexistent", "arguments": {}}}')

if echo "$RESPONSE" | grep -q '"error"'; then
  echo "Error occurred:"
  echo "$RESPONSE" | jq '.error'
else
  echo "Success:"
  echo "$RESPONSE" | jq '.result'
fi
```

### Pattern: Retry on Failure

```bash
MAX_RETRIES=3
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  RESPONSE=$(curl -s -X POST "http://localhost:8000/mcp" \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "add", "arguments": {"a": 10, "b": 20}}}')

  if echo "$RESPONSE" | grep -q '"error"'; then
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "Attempt $RETRY_COUNT failed, retrying..."
    sleep 2
  else
    echo "Success!"
    echo "$RESPONSE" | jq .
    break
  fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
  echo "Failed after $MAX_RETRIES attempts"
  exit 1
fi
```

---

## One-Liners

### List all tools:
```bash
curl -s http://localhost:8000/mcp -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | jq
```

### Call add tool:
```bash
curl -s http://localhost:8000/mcp -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"add","arguments":{"a":10,"b":20}}}' | jq
```

### Check server health:
```bash
curl -s http://localhost:8000/health | jq
```

### Initialize connection:
```bash
curl -s http://localhost:8000/mcp -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"curl","version":"1.0"}}}' | jq
```

---

## Key Points to Remember

1. **Single Endpoint:** All requests go to `/mcp` (POST method)
2. **JSON-RPC 2.0:** Must use proper JSON-RPC format with `jsonrpc`, `id`, `method`, `params`
3. **Required Headers:** `Content-Type: application/json` and `Accept: application/json, text/event-stream`
4. **Initialize First:** Always call `initialize` before calling tools
5. **Tool Names:** Case-sensitive, must match exactly
6. **Arguments:** Must match parameter names and types from tool schema
7. **Session ID:** Optional header for maintaining state across multiple calls
8. **Error Responses:** Check for `"error"` field in JSON-RPC response

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Connection refused | Start server first with `python server.py` |
| Invalid JSON error | Validate JSON syntax with `jq` before sending |
| Tool not found | Check tool name exactly (case-sensitive) |
| Invalid parameters | List tools first to see parameter schema |
| Timeout | Add `--max-time 30` to curl command |
| No response | Check if server is still running |

---

## Testing Tools

### Using jq for JSON validation:
```bash
echo '{"test": "value"}' | jq .
```

### Using jq to extract fields:
```bash
curl -s http://localhost:8000/mcp -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | jq '.result.tools[].name'
```

### Pretty printing with jq:
```bash
curl -s http://localhost:8000/mcp -H "Content-Type: application/json" \
  -d '{...}' | jq '.' --indent 2
```

---

## Related Documentation

- Official FastMCP: https://gofastmcp.com/
- HTTP Deployment: https://gofastmcp.com/deployment/http
- Tools Documentation: https://gofastmcp.com/servers/tools
- Client Documentation: https://gofastmcp.com/clients/client
- GitHub Repository: https://github.com/jlowin/fastmcp

---

**Last Updated:** November 5, 2025
**FastMCP Version:** 2.0+
**Protocol Version:** 2025-03-26 (MCP)
