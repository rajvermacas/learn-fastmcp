# server.py
import asyncio
import os
import sys
from fastmcp import FastMCP

# --------------------------------------------------------------------
# FastMCP is a framework for building MCP (Model Context Protocol) apps.
# It supports different communication channels (transports):
#   - stdio (standard input/output)
#   - SSE (Server-Sent Events)
#   - HTTP streamable (chunked responses)
#
# The choice depends on how your MCP client connects and whether
# you need streaming output (and what type of streaming).
# --------------------------------------------------------------------

app = FastMCP("mcp-protocol-demo")

# Configuration constants
VALID_TRANSPORTS = {"stdio", "sse", "streamable-http"}
DEFAULT_TRANSPORT = "sse"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000


def parse_config() -> dict:
    """
    Parse configuration from environment variables.

    Environment variables:
    - MCP_TRANSPORT: Transport type (stdio, sse, streamable-http)
    - MCP_HOST: Server host (default: 127.0.0.1)
    - MCP_PORT: Server port (default: 8000)

    Returns:
        dict: Configuration dictionary for app.run(**config)
    """
    # Parse transport type
    transport = os.getenv("MCP_TRANSPORT", DEFAULT_TRANSPORT)

    # Validate transport type
    if transport not in VALID_TRANSPORTS:
        raise ValueError(
            f"Invalid transport: '{transport}'. "
            f"Must be one of {VALID_TRANSPORTS}"
        )

    # Parse and validate port
    try:
        port = int(os.getenv("MCP_PORT", str(DEFAULT_PORT)))
        if port < 1 or port > 65535:
            raise ValueError(f"Port must be between 1 and 65535, got {port}")
    except ValueError as e:
        raise ValueError(f"Invalid port: {e}")

    # Build configuration dictionary
    config = {
        "transport": transport,
        "host": os.getenv("MCP_HOST", DEFAULT_HOST),
        "port": port,
    }

    return config


# ====================================================================
# 🧱 1️⃣ PLAIN HTTP TOOL (default)
# ====================================================================
# - This is the simplest mode — normal HTTP request/response.
# - Use this when:
#     * You want immediate, single-shot responses (no streaming).
#     * The operation is fast and returns a complete result.
# - Works best for synchronous logic or small computations.
#
# Example: classic REST API style usage.
#
# curl example:
#   curl -X POST http://localhost:8000/tools/add \
#        -H "Content-Type: application/json" \
#        -d '{"a": 3, "b": 4}'
#   → {"a": 3, "b": 4, "sum": 7}
# ====================================================================
@app.tool("add", description="Add two numbers (plain HTTP)")
def add_tool(a: float, b: float) -> dict:
    return {"a": a, "b": b, "sum": a + b}



# ====================================================================
# 🔁 2️⃣ SERVER-SENT EVENTS (SSE)
# ====================================================================
# - SSE keeps a persistent connection open between client and server.
# - The server pushes *events* (JSON objects) as they occur.
# - Each event is delivered as a separate message over the connection.
#
# When to use SSE:
#   ✅ You need to send real-time updates (progress, logs, live data)
#   ✅ The client supports "EventSource" (e.g., browsers)
#   ✅ The data flow is naturally event-like (like chat or countdown)
#
# Internally:
#   - Uses HTTP with "Content-Type: text/event-stream"
#   - Each message is prefixed with "data: ...\n\n"
#   - Connection stays open until done
#
# Difference from HTTP streamable:
#   * SSE is *event-based*, meant for continuous updates.
#   * HTTP streamable is *chunk-based*, meant for partial result chunks.
#   * SSE is great for live UI updates; streamable is for incremental API data.
#
# curl example (you'll see events arriving live):
#   curl -N http://localhost:8000/tools/countdown?start=5
#   → data: {"count":5}
#     data: {"count":4}
#     ...
#     data: {"done":true}
# ====================================================================
@app.tool("countdown", description="Stream countdown numbers")
async def countdown_tool(start: int):
    for i in range(start, 0, -1):
        yield {"count": i}   # Each yield is a new SSE event
        await asyncio.sleep(1)
    yield {"done": True}



# ====================================================================
# 🌊 3️⃣ HTTP STREAMABLE TOOL (chunked transfer)
# ====================================================================
# - This sends progressive data chunks in the *HTTP response body*.
# - The client receives the data as it’s generated, before completion.
#
# When to use HTTP streamable:
#   ✅ You’re generating a large dataset or long computation result.
#   ✅ You want the client to process partial results as they arrive.
#   ✅ Your client doesn’t support SSE (CLI tools, SDKs, etc.)
#
# Internally:
#   - Uses "Transfer-Encoding: chunked"
#   - No "data:" prefix; just sequential chunks of JSON/text.
#   - Closes the connection once all chunks are sent.
#
# Difference from SSE:
#   * SSE sends discrete JSON *events* via "text/event-stream".
#   * HTTP streamable sends a continuous *byte stream*.
#   * SSE is structured for push-based event updates;
#     HTTP streamable is structured for incremental data transfer.
#
# curl example (shows chunks as they arrive):
#   curl -N http://localhost:8000/tools/stream_sum?n=5
#   → {"partial_sum":1}
#     {"partial_sum":3}
#     {"partial_sum":6}
#     {"partial_sum":10}
#     {"partial_sum":15}
#     {"final_sum":15}
# ====================================================================
@app.tool("stream_sum", description="Stream progressive sum")
async def stream_sum_tool(n: int):
    total = 0
    for i in range(1, n + 1):
        total += i
        yield {"partial_sum": total}
        await asyncio.sleep(0.5)
    yield {"final_sum": total}



# ====================================================================
# 🖥️ 4️⃣ STDIO (not shown in this script)
# ====================================================================
# - Used when running as a subprocess (e.g., ChatGPT tools or CLI)
# - Communication happens via standard input/output pipes (not HTTP)
# - Ideal for local or embedded scenarios where network servers
#   are unnecessary.
#
# You’d typically use:
#   fastmcp run server.py --transport stdio
#
# When to use stdio:
#   ✅ Integrating with other MCP apps via local pipes
#   ✅ You don’t want to expose an HTTP port
# ====================================================================


# --------------------------------------------------------------------
# Start the MCP server with configurable transport.
# The transport type is determined by environment variables:
#   - MCP_TRANSPORT: stdio, sse, or streamable-http (default: sse)
#   - MCP_HOST: Server host (default: 127.0.0.1)
#   - MCP_PORT: Server port (default: 8000)
# --------------------------------------------------------------------
def main():
    """
    Main entry point for the CLI.

    Parses configuration from environment variables and starts the MCP server
    with the specified transport type. Defaults to SSE transport if no
    environment variables are set.
    """
    try:
        config = parse_config()
        print(f"Starting MCP server with transport: {config['transport']}")
        print(f"Host: {config['host']}, Port: {config['port']}")
        app.run(**config)
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        exit(1)


if __name__ == "__main__":
    main()
