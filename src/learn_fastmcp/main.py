# server.py
import asyncio
import os
import sys
from dotenv import load_dotenv
from fastmcp import FastMCP, Context

load_dotenv()

# --------------------------------------------------------------------
# FastMCP is a framework for building MCP (Model Context Protocol) apps.
# It supports different communication channels (transports):
#   - stdio (standard input/output)
#   - SSE (Server-Sent Events) - Legacy
#   - HTTP streamable (chunked responses) - Recommended
#
# The choice depends on how your MCP client connects and whether
# you need streaming output (and what type of streaming).
# --------------------------------------------------------------------

app = FastMCP("mcp-protocol-demo")

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
    # Configuration constants
    VALID_TRANSPORTS = {"stdio", "streamable-http"}
    DEFAULT_TRANSPORT = "streamable-http"
    DEFAULT_HOST = "0.0.0.0"
    DEFAULT_PORT = 8000

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


@app.tool("add", description="Add two numbers (plain HTTP)")
def add_tool(a: float, b: float) -> dict:
    return {"a": a, "b": b, "sum": a + b}


@app.tool("stream_sum", description="Calculate sum with progress notifications")
async def stream_sum_tool(n: int, ctx: Context):
    total = 0
    for i in range(1, n + 1):
        total += i
        # Report progress to client
        await ctx.report_progress(
            progress=i,
            total=n,
            message=f"Computed sum up to {i}: {total}"
        )
        await asyncio.sleep(0.5)
    return {"final_sum": total, "steps": n}


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
