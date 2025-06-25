#!/usr/bin/env python3
"""
FastMCP Proxy Server combining local and remote MCP servers
Uses FastMCP's built-in proxy functionality
"""

import asyncio
import logging
from fastmcp import FastMCP, Client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_unified_proxy():
    """Create a unified proxy combining local and remote servers"""

    # Configuration for multiple servers
    config = {
        "mcpServers": {
            "local": {
                "url": "http://localhost:8001/mcp",
                "transport": "http"
            },
            "remote": {
                "url": "https://0d49-34-211-143-25.ngrok-free.app/mcp",
                "transport": "http",
                "headers": {
                    "ngrok-skip-browser-warning": "true"
                }
            }
        }
    }

    # Create proxy using FastMCP's built-in functionality
    proxy = FastMCP.as_proxy(
        config,
        name="AutoGluon Unified MCP Proxy"
    )

    # Add some proxy-level documentation
    @proxy.prompt()
    def unified_workflow() -> str:
        """Complete AutoGluon workflow using unified proxy"""
        return """
        Unified AutoGluon Workflow:
        
        This proxy combines local file operations with remote AutoGluon processing.
        
        Available tools:
        - Local tools (prefix: local_): File operations on your Mac
          - local_prepare_local_folder: Prepare folders for upload
          - local_explore_directory: Browse local directories
          - local_validate_dataset: Validate CSV/JSON files
          - local_read_credentials: Read credential files
          
        - Remote tools (prefix: remote_): AutoGluon operations on EC2
          - remote_upload_input_folder: Upload data to server
          - remote_start_task: Start AutoGluon tasks
          - remote_check_status: Monitor task progress
          - remote_download_file: Download results
          
        Workflow:
        1. Use local_prepare_local_folder to prepare your data
        2. Use local_get_cached_data to retrieve the prepared data
        3. Use remote_upload_input_folder to upload to EC2
        4. Use remote_start_task to begin processing
        5. Monitor with remote_check_status
        6. Download results with remote_download_file
        """

    return proxy


# Alternative: Direct client-based proxy for more control
def create_proxy_with_clients():
    """Create proxy using explicit clients for more control"""

    # Create local client
    local_client = Client(
        command=["python", "local_server.py"],
        transport="stdio",
        env={"PYTHONPATH": "/Users/huawen.shen/Documents/autogluon-mcp-client"}
    )

    # Create remote client with retry configuration
    remote_client = Client(
        url="https://0d49-34-211-143-25.ngrok-free.app/mcp",
        transport="http",
        headers={"ngrok-skip-browser-warning": "true"},
        # Add any retry configuration here if supported
    )

    # Create a composite proxy
    composite_proxy = FastMCP(name="AutoGluon Composite Proxy")

    # Mount the clients with prefixes
    @composite_proxy.prompt()
    async def setup_proxies():
        """Setup proxy connections"""
        # This would be done internally by FastMCP.as_proxy
        # but shown here for clarity
        return "Proxy configured with local and remote servers"

    # For now, use the config-based approach as it's cleaner
    return create_unified_proxy()


if __name__ == "__main__":
    # Create and run the proxy
    proxy = create_unified_proxy()

    # Run on port 8003 as specified in your setup
    proxy.run(
        transport="http",
        host="0.0.0.0",
        port=8003
    )
