"""
FastMCP Server - Main Entry Point

This module provides the main entry point for the FastMCP server application.
It demonstrates different transport mechanisms for MCP (Model Context Protocol).
"""

import asyncio
import logging
import sys

from fastmcp import FastMCP, Context

from learn_fastmcp.config import load_config


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

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


@app.tool("add", description="Add two numbers (plain HTTP)")
def add_tool(a: float, b: float) -> dict:
    """
    Add two numbers and return the result.

    Args:
        a: First number
        b: Second number

    Returns:
        dict: Dictionary containing inputs and sum
    """
    logger.info(f"Adding {a} + {b}")
    return {"a": a, "b": b, "sum": a + b}


@app.tool("stream_sum", description="Calculate sum with progress notifications")
async def stream_sum_tool(n: int, ctx: Context):
    """
    Calculate sum of numbers from 1 to n with progress reporting.

    This demonstrates streaming capabilities with progress notifications.

    Args:
        n: Upper limit for sum calculation
        ctx: FastMCP context for progress reporting

    Returns:
        dict: Final sum and number of steps
    """
    logger.info(f"Starting stream_sum calculation for n={n}")
    total = 0
    for i in range(1, n + 1):
        total += i
        # Report progress to client
        await ctx.report_progress(
            progress=i,
            total=n,
            message=f"Computed sum up to {i}: {total}"
        )
        logger.debug(f"Progress: {i}/{n}, current total: {total}")
        await asyncio.sleep(0.5)

    logger.info(f"Completed stream_sum: final_sum={total}, steps={n}")
    return {"final_sum": total, "steps": n}


def main():
    """
    Main entry point for the CLI.

    Loads configuration from environment variables and starts the MCP server
    with the specified transport type.

    Exit codes:
        0: Success
        1: Configuration error
    """
    try:
        # Load configuration
        config = load_config()

        # Log configuration
        logger.info("=" * 60)
        logger.info("Starting MCP Server")
        logger.info("=" * 60)
        config.log_config()
        logger.info("=" * 60)

        # Get run configuration
        run_config = config.to_run_config()

        # Start server
        logger.info(f"Server starting on {config.mcp_host}:{config.mcp_port}")
        app.run(**run_config)

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
