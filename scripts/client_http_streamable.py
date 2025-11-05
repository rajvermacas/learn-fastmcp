import asyncio
from fastmcp import Client

async def progress_handler(progress: float, total: float | None, message: str | None) -> None:
    """Handle progress notifications from the server."""
    if total is not None:
        percentage = (progress / total) * 100
        print(f"Progress: {percentage:.1f}% ({progress}/{total}) - {message or 'Processing...'}")
    else:
        print(f"Progress: {progress} - {message or 'Processing...'}")

async def main():
    print("Connecting to MCP server and calling stream_sum tool...\n")

    # Create client with progress handler
    async with Client("http://127.0.0.1:8000/mcp", progress_handler=progress_handler) as client:
        result = await client.call_tool(
            name="stream_sum",
            arguments={"n": 5}
        )

    print("\n=== Final Result ===")
    print(f"Data: {result.data}")
    print(f"Content: {result.content}")

asyncio.run(main())