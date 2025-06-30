# mcp_client.py - 修改为 HTTP 连接
from fastmcp import Client
from typing import Any, List
import json


class MCPClient:
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.client = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def connect(self):
        """Establishes connection to MCP server"""
        try:
            self.client = Client(self.server_url)
            await self.client.__aenter__()
        except Exception as e:
            raise RuntimeError(
                f"Failed to connect to MCP server at {self.server_url}: {e}")

    async def get_available_tools(self) -> List[Any]:
        """List available tools - for pipeline server, this is just run_autogluon_pipeline"""
        if not self.client:
            raise RuntimeError("Not connected to MCP server")

        # Pipeline server has one tool: run_autogluon_pipeline
        # You might need to adjust this based on actual tool discovery
        return [{
            'name': 'run_autogluon_pipeline',
            'description': 'Run complete AutoGluon pipeline from data upload to results download',
            'inputSchema': {
                "type": "object",
                "properties": {
                    "input_folder": {"type": "string"},
                    "output_folder": {"type": "string"},
                    "server_url": {"type": "string"},
                    "config_file": {"type": "string"},
                    "max_iterations": {"type": "integer"},
                    "need_user_input": {"type": "boolean"},
                    "provider": {"type": "string"},
                    "model": {"type": "string"},
                    "creds_path": {"type": "string"},
                    "verbosity": {"type": "string"},
                    "cleanup_server": {"type": "boolean"}
                },
                "required": ["input_folder", "output_folder", "server_url"]
            }
        }]

    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """Call a tool with given arguments"""
        if not self.client:
            raise RuntimeError("Not connected to MCP server")

        result = await self.client.call_tool(tool_name, arguments)

        # Parse the response based on fastmcp format
        if isinstance(result, list) and len(result) > 0:
            return json.loads(result[0].text)
        return result
