import asyncio
from fastmcp import Client


async def cancel_stuck_task():
    client = Client("https://ff31-34-211-143-25.ngrok-free.app/mcp")
    async with client:
        result = await client.call_tool("cancel_task", {})
        print(result)

asyncio.run(cancel_stuck_task())
