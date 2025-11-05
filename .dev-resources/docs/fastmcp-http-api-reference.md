# FastMCP HTTP API Reference

**Document Version:** 1.0
**FastMCP Version:** 2.0+
**Date:** November 5, 2025
**Source:** Official FastMCP documentation at gofastmcp.com

---

## Overview

FastMCP is the fast, Pythonic way to build Model Context Protocol (MCP) servers and clients. When deployed with HTTP transport, FastMCP servers expose tools and resources as a web service accessible via HTTP endpoints. This reference document details how to make HTTP requests to FastMCP tools, the endpoint structure, request/response formats, and working curl examples.

### Key Concepts

- **MCP (Model Context Protocol):** A standardized protocol for providing context and tools to LLMs
- **Tools:** Server-side functions that clients can execute with arguments (similar to POST/PUT endpoints)
- **Resources:** Read-only data sources (similar to GET endpoints)
- **HTTP Transport:** Network-based transport using the Streamable HTTP protocol (recommended) or SSE (legacy)
- **Endpoint:** Single HTTP endpoint typically at `/mcp` for all tool calls and server operations

### Important Note

An MCP server exposes **one endpoint** (usually `/mcp`), not individual endpoints per tool. The tool name is specified in the JSON request payload, not in the URL.

---

## Installation & Setup

### Install FastMCP

```bash
uv pip install fastmcp
```

Or with pip:

```bash
pip install fastmcp
```

### Create a Simple FastMCP Server

```python
from fastmcp import FastMCP

mcp = FastMCP("Demo Server")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

@mcp.tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

if __name__ == "__main__":
    # Start HTTP server on port 8000
    mcp.run(transport="http", host="0.0.0.0", port=8000)
```

### Start the Server

```bash
python server.py
```

The server will be accessible at: `http://localhost:8000/mcp`

---

## HTTP Transport Types

FastMCP supports multiple HTTP transports when deployed as a web service:

### Streamable HTTP (Recommended)

The modern, full-featured HTTP transport for MCP.

**Advantages:**
- Full bidirectional communication
- Supports streaming responses
- Efficient session management
- Single endpoint for all operations
- Recommended for production deployments

**Starting the server:**

```python
mcp.run(transport="http", host="0.0.0.0", port=8000)
```

**Accessing the endpoint:**

```
http://localhost:8000/mcp
```

### SSE Transport (Legacy)

Server-Sent Events transport - supported for backward compatibility only.

**Disadvantages:**
- Unidirectional server-to-client streaming
- Less efficient bidirectional communication
- Slower than Streamable HTTP

**Starting the server:**

```python
mcp.run(transport="sse", host="0.0.0.0", port=8000)
```

**Not recommended for new projects.**

---

## Request/Response Protocol

FastMCP uses the **JSON-RPC 2.0 protocol** for all HTTP communication. All requests must follow this structure.

### Generic Request Format

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "method_name",
  "params": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

### Generic Response Format

**Success Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "data": "response_data"
  }
}
```

**Error Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32600,
    "message": "Invalid Request",
    "data": "Additional error details"
  }
}
```

### Required HTTP Headers

When making requests to FastMCP HTTP endpoints:

```
Content-Type: application/json
Accept: application/json, text/event-stream
```

### Optional Headers for Session Management

```
Mcp-Session-Id: <session-id>           # Preserve session state across requests
Mcp-Protocol-Version: 2025-03-26       # Protocol version
Authorization: Bearer <token>          # For authenticated servers
```

---

## Core API Methods

### 1. Initialize (Required First Step)

Initializes the session and establishes connection with the MCP server. Must be called before other operations.

**Method:** `initialize`

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "sampling": {},
      "roots": {
        "listChanged": true
      }
    },
    "clientInfo": {
      "name": "my-client",
      "version": "1.0.0"
    }
  }
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "tools": {
        "listChanged": true
      },
      "resources": {
        "subscribe": true
      }
    },
    "serverInfo": {
      "name": "Demo Server",
      "version": "1.0.0"
    }
  }
}
```

**After initialization, send:**

```json
{
  "jsonrpc": "2.0",
  "method": "initialized"
}
```

### 2. List Tools

Get a list of all available tools on the server.

**Method:** `tools/list`

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "add",
        "description": "Add two numbers together.",
        "inputSchema": {
          "type": "object",
          "properties": {
            "a": {
              "type": "integer",
              "description": "First number"
            },
            "b": {
              "type": "integer",
              "description": "Second number"
            }
          },
          "required": ["a", "b"]
        }
      },
      {
        "name": "multiply",
        "description": "Multiply two numbers.",
        "inputSchema": {
          "type": "object",
          "properties": {
            "a": {
              "type": "number",
              "description": "First number"
            },
            "b": {
              "type": "number",
              "description": "Second number"
            }
          },
          "required": ["a", "b"]
        }
      }
    ]
  }
}
```

### 3. Call Tool

Execute a specific tool with provided arguments.

**Method:** `tools/call`

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "add",
    "arguments": {
      "a": 10,
      "b": 5
    }
  }
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "type": "text",
    "text": "15"
  }
}
```

### 4. List Resources

Get a list of all available resources on the server.

**Method:** `resources/list`

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "resources/list",
  "params": {}
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "resources": [
      {
        "uri": "file:///config/settings.json",
        "name": "Settings",
        "description": "Server configuration settings",
        "mimeType": "application/json"
      }
    ]
  }
}
```

### 5. Read Resource

Read the contents of a specific resource.

**Method:** `resources/read`

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "resources/read",
  "params": {
    "uri": "file:///config/settings.json"
  }
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "contents": [
      {
        "uri": "file:///config/settings.json",
        "mimeType": "application/json",
        "text": "{\"debug\": true, \"port\": 8000}"
      }
    ]
  }
}
```

---

## curl Command Examples

All curl examples assume the FastMCP server is running at `http://localhost:8000/mcp`.

### Complete Workflow Example

This example demonstrates the full workflow: initialize, list tools, and call a tool.

**Step 1: Initialize the connection**

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
      "capabilities": {
        "sampling": {},
        "roots": {"listChanged": true}
      },
      "clientInfo": {
        "name": "curl-client",
        "version": "1.0.0"
      }
    }
  }'
```

**Expected output:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "tools": {"listChanged": true},
      "resources": {"subscribe": true}
    },
    "serverInfo": {
      "name": "Demo Server",
      "version": "1.0.0"
    }
  }
}
```

**Step 2: Send initialization confirmation**

```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialized"
  }'
```

**Step 3: List available tools**

```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

**Step 4: Call a tool (add two numbers)**

```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "add",
      "arguments": {
        "a": 10,
        "b": 5
      }
    }
  }'
```

**Expected response:**

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "type": "text",
    "text": "15"
  }
}
```

### Basic Tool Call (Simplified)

If you already have an established session:

```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: your-session-id" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "multiply",
      "arguments": {
        "a": 6.5,
        "b": 2.0
      }
    }
  }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "type": "text",
    "text": "13.0"
  }
}
```

### Tool Call with Complex Arguments

```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "process_data",
      "arguments": {
        "text": "Hello, World!",
        "max_length": 50,
        "format": "json",
        "options": {
          "case": "lower",
          "trim": true
        }
      }
    }
  }'
```

### Health Check Endpoint

Most FastMCP servers include a health check endpoint:

```bash
curl -X GET "http://localhost:8000/health"
```

**Response:**

```json
{
  "status": "ok",
  "transport": "streamable_http"
}
```

### Using Session ID for Persistent Connection

```bash
# Call with explicit session ID
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: abc-123-def-456" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "add",
      "arguments": {"a": 3, "b": 7}
    }
  }'
```

### Authentication with Bearer Token

```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-token-here" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

---

## Tool Definition & @app.tool Decorator

In FastMCP, tools are defined using the `@mcp.tool` decorator on Python functions.

### Basic Tool Definition

```python
from fastmcp import FastMCP

mcp = FastMCP("Calculator")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b
```

**How it exposes over HTTP:**

1. Function name becomes tool name: `add`
2. Docstring becomes tool description: `"Add two numbers together."`
3. Type annotations generate JSON schema for validation
4. Function is callable via HTTP POST to `/mcp` with `method: "tools/call"`

### Tool with Custom Metadata

```python
@mcp.tool(
    name="add_numbers",
    description="Adds two integer numbers and returns the sum.",
    tags={"math", "calculator"},
    meta={"version": "1.0", "author": "team"}
)
def add_implementation(a: int, b: int) -> int:
    """Internal docstring (overridden by description parameter)."""
    return a + b
```

### Tool with Optional Parameters

```python
@mcp.tool
def search(query: str, max_results: int = 10, sort_by: str = "relevance") -> list:
    """Search the database.

    Args:
        query: The search query (required)
        max_results: Maximum number of results to return (optional, default=10)
        sort_by: Sort results by field (optional, default='relevance')

    Returns:
        List of search results
    """
    # Implementation...
    return [{"result": "example"}]
```

**HTTP call with optional parameters:**

```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "search",
      "arguments": {
        "query": "python",
        "max_results": 5,
        "sort_by": "date"
      }
    }
  }'
```

### Async Tools

```python
import asyncio

@mcp.tool
async def fetch_data(url: str) -> dict:
    """Fetch data from a URL asynchronously."""
    # Simulated async operation
    await asyncio.sleep(1)
    return {"status": "success", "url": url}
```

FastMCP automatically handles both sync and async tools over HTTP.

### Tool Return Types

Tools can return various types:

```python
@mcp.tool
def return_string() -> str:
    """Returns text."""
    return "Hello, World!"

@mcp.tool
def return_dict() -> dict:
    """Returns JSON-serializable dictionary."""
    return {"name": "Alice", "age": 30, "active": True}

@mcp.tool
def return_list() -> list:
    """Returns a list."""
    return [1, 2, 3, 4, 5]

@mcp.tool
def return_number() -> float:
    """Returns a number."""
    return 3.14159

@mcp.tool
def return_bool() -> bool:
    """Returns a boolean."""
    return True
```

---

## Common Use Cases & Examples

### Use Case 1: Simple Calculator

**Server Code:**

```python
from fastmcp import FastMCP

mcp = FastMCP("Calculator")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@mcp.tool
def subtract(a: int, b: int) -> int:
    """Subtract b from a."""
    return a - b

@mcp.tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

@mcp.tool
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
```

**curl Examples:**

```bash
# Add
curl -X POST "http://localhost:8000/mcp" -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "add", "arguments": {"a": 10, "b": 20}}}'

# Divide
curl -X POST "http://localhost:8000/mcp" -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "divide", "arguments": {"a": 100.0, "b": 4.0}}}'
```

### Use Case 2: Text Processing

**Server Code:**

```python
from fastmcp import FastMCP

mcp = FastMCP("TextProcessor")

@mcp.tool
def uppercase(text: str) -> str:
    """Convert text to uppercase."""
    return text.upper()

@mcp.tool
def count_words(text: str) -> int:
    """Count the number of words in text."""
    return len(text.split())

@mcp.tool
def truncate(text: str, length: int = 50) -> str:
    """Truncate text to specified length."""
    return text[:length]

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
```

**curl Example:**

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
        "text": "This is a long piece of text that should be truncated",
        "length": 20
      }
    }
  }'
```

### Use Case 3: Data Transformation

**Server Code:**

```python
from fastmcp import FastMCP
import json

mcp = FastMCP("DataTransformer")

@mcp.tool
def parse_json(json_string: str) -> dict:
    """Parse a JSON string into a dictionary."""
    return json.loads(json_string)

@mcp.tool
def filter_dict(data: dict, keys: list) -> dict:
    """Filter a dictionary to only include specified keys."""
    return {k: v for k, v in data.items() if k in keys}

@mcp.tool
def merge_dicts(dict1: dict, dict2: dict) -> dict:
    """Merge two dictionaries."""
    result = dict1.copy()
    result.update(dict2)
    return result

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
```

---

## Error Handling

### Common Error Codes

| Code | Message | Meaning |
|------|---------|---------|
| -32700 | Parse error | Server received invalid JSON |
| -32600 | Invalid Request | JSON-RPC request is malformed |
| -32601 | Method not found | Requested method doesn't exist |
| -32602 | Invalid params | Invalid method parameters |
| -32603 | Internal error | Internal server error |
| -32000 | Server error | Application-specific error |

### Error Response Example

**Request with invalid tool name:**

```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "nonexistent_tool",
      "arguments": {}
    }
  }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32601,
    "message": "Method not found",
    "data": "Tool 'nonexistent_tool' does not exist"
  }
}
```

### Error Response with Invalid Parameters

**Request with missing required argument:**

```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "add",
      "arguments": {
        "a": 10
      }
    }
  }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32602,
    "message": "Invalid params",
    "data": "Missing required parameter: b"
  }
}
```

---

## Best Practices

### 1. Always Initialize First

Always call `initialize` before making tool calls:

```bash
# First: Initialize
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {...}}'

# Then: Make calls
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {...}}'
```

### 2. Use Session IDs for Persistent Connections

Maintain session state by including the session ID in subsequent requests:

```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: your-session-id" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {...}}'
```

### 3. Validate Parameters Before Calling

Always provide valid arguments according to the tool's schema:

```bash
# First: List tools to see schemas
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'

# Then: Call with proper arguments
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "add", "arguments": {"a": 10, "b": 20}}}'
```

### 4. Handle Errors Gracefully

Always check for error responses:

```bash
# Save response to file and inspect
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {...}}' > response.json

# Check if response contains "error" field
cat response.json | grep -q '"error"' && echo "Error occurred" || echo "Success"
```

### 5. Set Appropriate Timeouts

For long-running operations, set appropriate curl timeouts:

```bash
curl --max-time 30 \
  -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {...}}'
```

### 6. Log Request/Response for Debugging

Use curl's verbose mode:

```bash
curl -v -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {...}}'
```

Or save request/response:

```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {...}}' \
  -w "\n%{http_code}\n" > response.txt 2>&1
```

---

## Advanced Features

### Custom Routes (Additional Endpoints)

FastMCP allows adding custom HTTP routes alongside the MCP endpoint:

```python
from fastmcp import FastMCP
from starlette.responses import JSONResponse

mcp = FastMCP("MyServer")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    return JSONResponse({"status": "healthy", "mcp": "ready"})

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
```

**Accessing custom routes:**

```bash
# MCP endpoint
curl http://localhost:8000/mcp

# Custom health check endpoint
curl http://localhost:8000/health
```

### Mounting FastMCP in FastAPI

```python
from fastapi import FastAPI
from fastmcp import FastMCP

# Create FastAPI app
api = FastAPI()

# Create MCP server
mcp = FastMCP("Tools")

@mcp.tool
def process(data: str) -> str:
    return f"Processed: {data}"

# Mount MCP at /api/mcp
api.mount("/api/mcp", mcp.http_app())

# Run with: uvicorn app:api --host 0.0.0.0 --port 8000
```

**Accessing mounted MCP:**

```bash
curl -X POST "http://localhost:8000/api/mcp/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {...}}'
```

### Authentication with Bearer Token

```python
from fastmcp import FastMCP
from fastmcp.server.auth import require_auth, BearerAuth

mcp = FastMCP("SecureServer")

# Require authentication
auth = BearerAuth(tokens=["secret-token-123"])
mcp.auth = auth

@mcp.tool
def secure_operation(data: str) -> str:
    """This tool requires authentication."""
    return f"Secure result: {data}"

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
```

**curl with authentication:**

```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer secret-token-123" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {...}}'
```

---

## Testing FastMCP Servers

### Using the FastMCP Client (Python)

```python
import asyncio
from fastmcp import Client

async def test_server():
    client = Client("http://localhost:8000/mcp")

    async with client:
        # List tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")

        # Call a tool
        result = await client.call_tool("add", {"a": 10, "b": 5})
        print(f"Result: {result}")

asyncio.run(test_server())
```

### Using Postman

1. Create a new POST request
2. URL: `http://localhost:8000/mcp`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "add",
    "arguments": {"a": 10, "b": 5}
  }
}
```

### Using Python Requests Library

```python
import requests
import json

url = "http://localhost:8000/mcp"
headers = {"Content-Type": "application/json"}

# Call tool
payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "add",
        "arguments": {"a": 10, "b": 5}
    }
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

---

## Resources & Documentation

### Official FastMCP Documentation
- Main site: https://gofastmcp.com/
- GitHub: https://github.com/jlowin/fastmcp
- PyPI: https://pypi.org/project/fastmcp/

### Key Documentation Pages
- Installation: https://gofastmcp.com/getting-started/installation
- Servers: https://gofastmcp.com/servers/fastmcp
- Tools: https://gofastmcp.com/servers/tools
- HTTP Deployment: https://gofastmcp.com/deployment/http
- Clients: https://gofastmcp.com/clients/client
- Transports: https://gofastmcp.com/clients/transports

### Model Context Protocol (MCP)
- Official MCP: https://modelcontextprotocol.io/
- Python SDK: https://github.com/modelcontextprotocol/python-sdk

### Community
- Discord: https://discord.gg/uu8dJCgttd
- GitHub Discussions: https://github.com/jlowin/fastmcp/discussions

---

## Troubleshooting

### Issue: Connection Refused on localhost:8000

**Solution:** Ensure the server is running:

```bash
python server.py  # Start the server first
```

Then test:

```bash
curl http://localhost:8000/health
```

### Issue: Invalid JSON Response

**Check:**
- JSON syntax is valid (use `jq` to validate)
- Content-Type header is set to `application/json`
- No newlines in JSON-RPC payload

```bash
# Validate JSON
echo '{"test": "value"}' | jq . > /dev/null && echo "Valid JSON"
```

### Issue: Tool Not Found Error

**Check:**
- Tool name matches exactly (case-sensitive)
- Tool is properly decorated with `@mcp.tool`
- Server was restarted after adding new tools

```bash
# List available tools
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'
```

### Issue: Invalid Parameters Error

**Check:**
- All required parameters are provided
- Parameter types match the schema (int vs string, etc.)
- Parameter names match exactly

```bash
# List tools to see parameter schema
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'
```

### Issue: Timeout on Tool Execution

**Check:**
- Tool is not blocking indefinitely
- Set appropriate timeout in curl: `--max-time 30`
- Consider using async functions for I/O operations

```bash
curl --max-time 30 -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {...}}'
```

---

## Summary

FastMCP provides a straightforward way to expose Python functions as MCP tools over HTTP. Key points:

1. **Single Endpoint:** All requests go to `/mcp` (or custom path)
2. **JSON-RPC Protocol:** Use JSON-RPC 2.0 format for all requests
3. **Initialize First:** Always call `initialize` before using tools
4. **Tool Calls:** Use `tools/call` method with tool name and arguments
5. **Session Management:** Use `Mcp-Session-Id` header for persistent connections
6. **Error Handling:** Always check for error responses in JSON-RPC format

For more information, visit the official documentation at https://gofastmcp.com/ or the GitHub repository at https://github.com/jlowin/fastmcp.
