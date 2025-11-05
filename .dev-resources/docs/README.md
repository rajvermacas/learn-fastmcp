# FastMCP HTTP API & curl Commands Documentation

**Research Completion Date:** November 5, 2025
**Status:** Complete and Ready for Use

---

## Overview

This directory contains comprehensive documentation on how to make HTTP requests to FastMCP tools, including detailed API references, curl command patterns, and practical examples.

All documentation is based on official FastMCP 2.0+ documentation and has been verified against the latest releases.

---

## Documentation Files

### 1. fastmcp-http-api-reference.md
**The Complete API Reference (27 KB)**

Comprehensive guide covering:
- Overview and core concepts
- Installation & setup instructions
- HTTP transport types (Streamable HTTP vs SSE)
- Request/response protocol and formats
- Core API methods with examples:
  - initialize (establish connection)
  - tools/list (discover available tools)
  - tools/call (execute tools)
  - resources/list (discover resources)
  - resources/read (access resource content)
- Extensive curl command examples with explanations
- Tool definition with @mcp.tool decorator
- Common use cases (Calculator, Text Processing, Data Transformation)
- Error handling and error codes
- Best practices for production use
- Advanced features (custom routes, FastAPI integration, authentication)
- Multiple testing approaches
- Troubleshooting guide
- Complete resource links

**Use this file for:** Complete understanding of FastMCP HTTP API, detailed examples, best practices, troubleshooting

---

### 2. curl-command-patterns.md
**Quick Reference Guide (13 KB)**

Fast lookup guide featuring:
- Quick start patterns
- Essential HTTP headers (required and optional)
- 8 core curl patterns with copy-paste ready examples:
  1. Initialize connection
  2. List available tools
  3. Call a tool (basic)
  4. Call a tool (with session)
  5. Call a tool (with authentication)
  6. List resources
  7. Read a resource
  8. Health check
- Real-world examples with 4 detailed scenarios
- Argument types and examples
- Advanced patterns (verbose, timeout, file save, pretty print)
- Error handling patterns
- One-liners for quick commands
- Common issues & solutions
- Testing tools with jq

**Use this file for:** Quick lookup during development, copy-paste curl examples, pattern reference

---

### 3. RESEARCH-SUMMARY.md
**Executive Summary & Findings (20 KB)**

High-level summary covering:
- Executive summary of key findings
- Research methodology and sources
- How HTTP requests to FastMCP tools work (architecture)
- Endpoint structure and access
- Request/response formats
- HTTP transport types comparison
- Complete workflow steps (initialize → list → call)
- @mcp.tool decorator mechanics
- curl command patterns summary
- Real-world curl examples
- Critical implementation details
- Error handling reference
- Best practices
- Key insights and recommendations
- Answers to all original research questions

**Use this file for:** Understanding the big picture, executive summaries, research insights

---

## Quick Start Examples

### Example 1: Simple Calculator Tool

**Python Server:**
```python
from fastmcp import FastMCP

mcp = FastMCP("Calculator")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
```

**Run:**
```bash
python server.py
```

**curl Command:**
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

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "type": "text",
    "text": "30"
  }
}
```

---

### Example 2: Complete Workflow

**Step 1: Initialize Connection**
```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-03-26",
      "capabilities": {},
      "clientInfo": {"name": "my-client", "version": "1.0"}
    }
  }'
```

**Step 2: List Tools**
```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}'
```

**Step 3: Call Tool**
```bash
curl -X POST "http://localhost:8000/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "add",
      "arguments": {"a": 10, "b": 5}
    }
  }'
```

---

## Key Concepts at a Glance

### Single Endpoint Architecture
- All requests go to `http://localhost:8000/mcp`
- Tool name specified in JSON body, NOT in URL
- All operations use HTTP POST method

### JSON-RPC 2.0 Protocol
- Every request has `jsonrpc: "2.0"`, `id`, `method`, `params`
- Every response has `jsonrpc: "2.0"`, `id`, and either `result` or `error`

### Required Headers
```
Content-Type: application/json
Accept: application/json, text/event-stream
```

### Optional Headers
```
Mcp-Session-Id: <session-id>        # For session persistence
Authorization: Bearer <token>       # For authentication
```

### @mcp.tool Decorator
```python
@mcp.tool
def function_name(param1: type, param2: type = default) -> return_type:
    """Description of what this tool does."""
    # Implementation
    return result
```
- Function name becomes tool name
- Docstring becomes tool description
- Type hints generate validation schema
- Automatically exposed at `/mcp` endpoint

---

## Transport Types

| Feature | Streamable HTTP (Recommended) | SSE (Legacy) |
|---------|------------------------------|--------------|
| **Use Case** | Production, new projects | Backward compatibility only |
| **Communication** | Full bidirectional | Unidirectional server-to-client |
| **Streaming** | Supported | Supported but limited |
| **Performance** | Excellent | Moderate |
| **Recommended** | YES | NO - Deprecated |

---

## Common curl Patterns

### List Tools
```bash
curl -s http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

### Call Tool (No Args)
```bash
curl -s http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"tool_name","arguments":{}}}'
```

### Call Tool (With Args)
```bash
curl -s http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"add","arguments":{"a":10,"b":20}}}'
```

### With Session ID
```bash
curl -s http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: abc-123" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"tool","arguments":{}}}'
```

### With Authentication
```bash
curl -s http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer token" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

### Health Check
```bash
curl http://localhost:8000/health
```

---

## Error Codes Reference

| Code | Message | Meaning |
|------|---------|---------|
| -32700 | Parse error | Invalid JSON received |
| -32600 | Invalid Request | JSON-RPC request is malformed |
| -32601 | Method not found | Requested tool doesn't exist |
| -32602 | Invalid params | Invalid method parameters |
| -32603 | Internal error | Internal server error |

---

## Tips for Success

### 1. Always Initialize First
```bash
# Initialize connection
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize",...}'

# Then call tools
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call",...}'
```

### 2. Discover Tools First
```bash
# See what tools are available and their parameters
curl -s http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | jq
```

### 3. Validate with jq
```bash
# Validate JSON syntax
echo '{"test": "value"}' | jq . > /dev/null && echo "Valid JSON"

# Pretty print responses
curl -s ... | jq '.'

# Extract specific fields
curl -s ... | jq '.result.text'
```

### 4. Use Session IDs for Multiple Calls
```bash
# Reuse session across multiple tool calls
curl ... -H "Mcp-Session-Id: session-123" ...
```

### 5. Set Timeouts for Long Operations
```bash
# Add timeout for potentially slow tools
curl --max-time 30 -X POST http://localhost:8000/mcp ...
```

---

## Troubleshooting Guide

### Issue: "Connection refused"
**Cause:** Server not running
**Solution:** Start the server first: `python server.py`

### Issue: "Method not found" error
**Cause:** Tool name doesn't exist or is misspelled
**Solution:** List tools first to verify the exact name (case-sensitive)

### Issue: "Invalid params" error
**Cause:** Missing required parameters or wrong types
**Solution:** Use `tools/list` to see the parameter schema

### Issue: Timeout error
**Cause:** Tool execution taking too long
**Solution:** Increase timeout with `--max-time 60` or optimize tool code

### Issue: Invalid JSON error
**Cause:** Malformed JSON in curl command
**Solution:** Validate JSON with `jq` before sending: `echo '...' | jq .`

---

## Related Resources

### Official FastMCP Documentation
- **Main Site:** https://gofastmcp.com/
- **GitHub:** https://github.com/jlowin/fastmcp
- **PyPI:** https://pypi.org/project/fastmcp/
- **Discord Community:** https://discord.gg/uu8dJCgttd

### Key Documentation Pages
- Getting Started: https://gofastmcp.com/getting-started/installation
- Tools Documentation: https://gofastmcp.com/servers/tools
- HTTP Deployment: https://gofastmcp.com/deployment/http
- Client Documentation: https://gofastmcp.com/clients/client
- Transport Documentation: https://gofastmcp.com/clients/transports

### Model Context Protocol (MCP)
- **Official MCP:** https://modelcontextprotocol.io/
- **Python SDK:** https://github.com/modelcontextprotocol/python-sdk
- **Specification:** https://spec.modelcontextprotocol.io/

---

## Document Map

```
.dev-resources/docs/
├── README.md                          (This file - index and quick reference)
├── fastmcp-http-api-reference.md     (Complete API reference - 27 KB)
├── curl-command-patterns.md           (Quick lookup patterns - 13 KB)
└── RESEARCH-SUMMARY.md                (Executive summary & findings - 20 KB)
```

---

## How to Use This Documentation

### For Quick Development
1. Open **curl-command-patterns.md**
2. Find the pattern that matches your use case
3. Copy the curl example and customize

### For Understanding Details
1. Read relevant sections in **fastmcp-http-api-reference.md**
2. Review examples provided
3. Refer to troubleshooting section if issues arise

### For High-Level Understanding
1. Start with **RESEARCH-SUMMARY.md**
2. Review key concepts and findings
3. Navigate to detailed docs for specific topics

### For Complete Learning
1. Read **RESEARCH-SUMMARY.md** for overview
2. Study **fastmcp-http-api-reference.md** for comprehensive details
3. Use **curl-command-patterns.md** as reference while implementing

---

## Version Information

| Component | Version | Date |
|-----------|---------|------|
| FastMCP | 2.0+ | Nov 2025 |
| MCP Protocol | 2025-03-26 | Current |
| Documentation | 1.0 | Nov 5, 2025 |
| Python | 3.8+ | Required |

---

## Support & Questions

For questions or issues:
1. Check the **Troubleshooting Guide** section
2. Consult **fastmcp-http-api-reference.md** for comprehensive coverage
3. Visit official FastMCP Discord: https://discord.gg/uu8dJCgttd
4. Check GitHub issues: https://github.com/jlowin/fastmcp/issues

---

## Notes

- All curl examples assume server running on `http://localhost:8000/mcp`
- Adjust port and host as needed for your setup
- Use `Mcp-Session-Id` header for persistent connections across multiple requests
- Always validate JSON before sending with jq: `echo 'json' | jq .`
- Use `--max-time` for long-running operations
- Use `-v` flag for verbose curl output when debugging

---

**Created:** November 5, 2025
**FastMCP Version:** 2.0+
**MCP Protocol:** 2025-03-26
**Status:** Complete and Production-Ready
