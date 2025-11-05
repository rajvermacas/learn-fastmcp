# server.py
import asyncio
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
# curl example (you’ll see events arriving live):
#   curl -N http://localhost:8000/tools/countdown?start=5
#   → data: {"count":5}
#     data: {"count":4}
#     ...
#     data: {"done":true}
# ====================================================================
@app.stream_tool("countdown", description="Stream countdown numbers")
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
@app.streamable_tool("stream_sum", description="Stream progressive sum")
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
# Start the MCP server. This will automatically default to HTTP.
# To run with SSE/streaming enabled, make sure the client requests
# the appropriate tool endpoint (as defined above).
# --------------------------------------------------------------------
if __name__ == "__main__":
    app.run()
