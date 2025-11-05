# Transport Configuration Guide

This document describes how to configure the FastMCP server to use different transport protocols via environment variables.

## Overview

The FastMCP server supports multiple transport protocols:
- **stdio** - Standard input/output (for local integrations)
- **sse** - Server-Sent Events (default, for HTTP streaming)
- **streamable-http** - Streamable HTTP with chunked transfer encoding

## Environment Variables

You can configure the server using these environment variables:

| Variable | Description | Default | Valid Values |
|----------|-------------|---------|--------------|
| `MCP_TRANSPORT` | Transport protocol to use | `sse` | `stdio`, `sse`, `streamable-http` |
| `MCP_HOST` | Server host address | `127.0.0.1` | Any valid IP or hostname |
| `MCP_PORT` | Server port number | `8000` | 1-65535 |

## Usage Examples

### 1. Default Configuration (SSE Transport)

No environment variables needed:

```bash
uv run learn-fastmcp
```

Output:
```
Starting MCP server with transport: sse
Host: 127.0.0.1, Port: 8000
```

### 2. Explicitly Use SSE Transport

```bash
export MCP_TRANSPORT=sse
uv run learn-fastmcp
```

### 3. Use STDIO Transport

```bash
export MCP_TRANSPORT=stdio
uv run learn-fastmcp
```

### 4. Use Streamable-HTTP with Custom Settings

```bash
export MCP_TRANSPORT=streamable-http
export MCP_HOST=0.0.0.0
export MCP_PORT=8080
uv run learn-fastmcp
```

### 5. One-liner with All Options

```bash
MCP_TRANSPORT=streamable-http MCP_HOST=0.0.0.0 MCP_PORT=8080 uv run learn-fastmcp
```

## Configuration Validation

The server validates all configuration values and exits with an error if invalid:

### Invalid Transport

```bash
MCP_TRANSPORT=invalid uv run learn-fastmcp
```

Output:
```
Configuration error: Invalid transport: 'invalid'. Must be one of {'stdio', 'sse', 'streamable-http'}
Exit code: 1
```

### Invalid Port (Non-numeric)

```bash
MCP_TRANSPORT=sse MCP_PORT=abc uv run learn-fastmcp
```

Output:
```
Configuration error: Invalid port: invalid literal for int() with base 10: 'abc'
Exit code: 1
```

### Invalid Port Range

```bash
MCP_TRANSPORT=sse MCP_PORT=99999 uv run learn-fastmcp
```

Output:
```
Configuration error: Invalid port: Port must be between 1 and 65535, got 99999
Exit code: 1
```

## Transport-Specific Notes

### STDIO Transport

- Default FastMCP transport
- Best for local CLI integrations
- No network port needed
- Communicates via standard input/output

```bash
MCP_TRANSPORT=stdio uv run learn-fastmcp
```

### SSE Transport (Default)

- HTTP-based with Server-Sent Events
- Best for real-time streaming updates
- Persistent connection for continuous data flow
- Default when no environment variable is set

```bash
# Explicit
MCP_TRANSPORT=sse uv run learn-fastmcp

# Or use default
uv run learn-fastmcp
```

### Streamable-HTTP Transport

- HTTP-based with chunked transfer encoding
- Best for progressive data streaming
- Client receives data as it's generated
- Supports large datasets and long computations

```bash
MCP_TRANSPORT=streamable-http MCP_HOST=0.0.0.0 MCP_PORT=8080 uv run learn-fastmcp
```

## Implementation Details

### Configuration Parsing

The server uses the `parse_config()` function to read environment variables:

```python
import os

VALID_TRANSPORTS = {"stdio", "sse", "streamable-http"}
DEFAULT_TRANSPORT = "sse"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000

def parse_config() -> dict:
    transport = os.getenv("MCP_TRANSPORT", DEFAULT_TRANSPORT)

    if transport not in VALID_TRANSPORTS:
        raise ValueError(f"Invalid transport: '{transport}'")

    port = int(os.getenv("MCP_PORT", str(DEFAULT_PORT)))
    if port < 1 or port > 65535:
        raise ValueError(f"Port must be between 1 and 65535, got {port}")

    config = {
        "transport": transport,
        "host": os.getenv("MCP_HOST", DEFAULT_HOST),
        "port": port,
    }
    return config
```

### Running the Server

The `main()` function uses `app.run(**config)` to start the server:

```python
def main():
    try:
        config = parse_config()
        print(f"Starting MCP server with transport: {config['transport']}")
        print(f"Host: {config['host']}, Port: {config['port']}")
        app.run(**config)
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        exit(1)
```

## Testing

A test script is provided to verify configuration parsing:

```bash
uv run python test_config.py
```

This runs all test cases including:
- Default configuration
- All transport types
- Custom host and port settings
- Invalid transport validation
- Invalid port handling

## Best Practices

1. **Use STDIO for local development and testing**
   - No network configuration needed
   - Faster for CLI tools

2. **Use SSE for real-time streaming**
   - Default transport for new projects
   - Good for continuous updates and live data

3. **Use Streamable-HTTP for production deployments**
   - Better for large data transfers
   - Supports stateless HTTP mode
   - More efficient for chunked data

4. **Set environment variables in production**
   - Use deployment platform's environment variable support
   - Keep sensitive config out of code

5. **Validate configuration early**
   - Server exits immediately with clear error messages
   - No partial startup with invalid config

## Troubleshooting

### Port Already in Use

If you get a "port already in use" error:

```bash
# Try a different port
MCP_TRANSPORT=sse MCP_PORT=8080 uv run learn-fastmcp
```

### Connection Refused

If clients can't connect:

```bash
# Check server is running and bound to correct interface
MCP_TRANSPORT=sse MCP_HOST=0.0.0.0 MCP_PORT=8000 uv run learn-fastmcp

# Verify firewall settings
# Ensure port 8000 is accessible
```

### STDIO Mode Issues

If STDIO transport doesn't work as expected:

- Ensure client supports STDIO MCP
- Check that the server is being spawned as a subprocess
- Verify no network code paths are being used

## Additional Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Server-Sent Events (SSE)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [HTTP Chunked Transfer Encoding](https://en.wikipedia.org/wiki/Chunked_transfer_encoding)
