#!/usr/bin/env python3
"""
Debug client to simulate OpenAI's MCP tool call
This directly calls the pipeline server for debugging purposes
"""

import asyncio
import json
import logging
from datetime import datetime
from fastmcp import Client

# Enable detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration - EXACT SAME as OpenAI would use
PIPELINE_SERVER_URL = 'https://victorian-handbags-empirical-deals.trycloudflare.com'
# PIPELINE_SERVER_URL = 'http://localhost:8005'  # Uncomment for local testing

# Parameters - EXACT SAME as your command line
PARAMS = {
    "input_folder": "/Users/huawen.shen/Documents/autogluon-mcp-client/test_data",
    "output_folder": "/Users/huawen.shen/Documents/autogluon-mcp-client/output",
    "server_url": "https://44a9-34-211-143-25.ngrok-free.app",
    "config_file": "/Users/huawen.shen/Documents/autogluon-mcp-client/config.yaml",
    "max_iterations": 1,
    "provider": "bedrock",
    "model": "anthropic.claude-3-haiku-20240307-v1:0",
    "creds_path": "/Users/huawen.shen/.aws/autogluon_creds.txt",
    "verbosity": "info",
    "need_user_input": False,
    "cleanup_server": True
}


def parse_mcp_response(response):
    """Parse FastMCP response format - same as OpenAI would receive"""
    if isinstance(response, list) and len(response) > 0:
        # Extract text content from TextContent object
        text_content = response[0].text
        try:
            return json.loads(text_content)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON: {text_content}")
            return {"raw_text": text_content}
    return response


async def test_pipeline_direct():
    """Test the pipeline server directly, simulating OpenAI's behavior"""

    # Add /mcp to URL if not present (like OpenAI does)
    server_url = PIPELINE_SERVER_URL
    if not server_url.endswith('/mcp'):
        server_url = server_url.rstrip('/') + '/mcp'

    print(f"=== AutoGluon Pipeline Debug Test ===")
    print(f"Time: {datetime.now()}")
    print(f"Server URL: {server_url}")
    print(f"Parameters:")
    for key, value in PARAMS.items():
        print(f"  {key}: {value}")
    print("=" * 50)

    try:
        # Create client - this simulates OpenAI's MCP client
        logger.info(f"Creating MCP client to {server_url}")
        client = Client(server_url)

        async with client:
            logger.info("Client connected successfully")
            print("\n1. Testing connection...")
            print("   ✓ Connected to MCP server")

            # Call the tool - EXACTLY as OpenAI would
            print("\n2. Calling run_autogluon_pipeline tool...")
            start_time = datetime.now()

            try:
                logger.debug(
                    f"Calling tool with params: {json.dumps(PARAMS, indent=2)}")

                result = await client.call_tool("run_autogluon_pipeline", PARAMS)

                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                logger.debug(f"Raw result type: {type(result)}")
                logger.debug(f"Raw result: {result}")

                # Parse the response
                parsed_result = parse_mcp_response(result)

                print(
                    f"\n3. Tool execution completed in {duration:.1f} seconds")
                print("\n4. Results:")
                print("-" * 50)

                if isinstance(parsed_result, dict):
                    # Pretty print the result
                    print(json.dumps(parsed_result, indent=2))

                    # Analyze the result
                    print("\n5. Result Analysis:")
                    print(
                        f"   - Success: {parsed_result.get('success', 'Unknown')}")
                    print(
                        f"   - Task ID: {parsed_result.get('task_id', 'None')}")
                    print(
                        f"   - Output Directory: {parsed_result.get('output_directory', 'None')}")
                    print(
                        f"   - Number of output files: {len(parsed_result.get('output_files', []))}")
                    print(
                        f"   - Number of log entries: {len(parsed_result.get('logs', []))}")

                    # Print brief logs if any
                    logs = parsed_result.get('logs', [])
                    if logs:
                        print("\n6. Brief Logs:")
                        for log in logs[:10]:  # First 10 logs
                            level = log.get('level', 'INFO')
                            text = log.get('text', '')
                            print(f"   [{level}] {text}")
                        if len(logs) > 10:
                            print(
                                f"   ... and {len(logs) - 10} more log entries")

                    # Check for errors
                    if not parsed_result.get('success'):
                        print(
                            f"\n⚠️  ERROR: {parsed_result.get('error', 'Unknown error')}")
                else:
                    print(f"Unexpected result format: {parsed_result}")

            except asyncio.TimeoutError:
                print("\n❌ ERROR: Tool call timed out")
                print("This might happen if the pipeline takes too long to execute")

            except Exception as e:
                print(
                    f"\n❌ ERROR during tool call: {type(e).__name__}: {str(e)}")
                logger.exception("Detailed error:")

    except Exception as e:
        print(f"\n❌ ERROR: Failed to connect to MCP server")
        print(f"   {type(e).__name__}: {str(e)}")
        logger.exception("Connection error details:")

        print("\nTroubleshooting:")
        print("1. Check if pipeline_server.py is running")
        print("2. Verify the server URL is correct")
        print("3. For local testing, use http://localhost:8005")
        print("4. Check server logs for errors")


async def test_connection_only():
    """Just test if we can connect to the server"""
    server_url = PIPELINE_SERVER_URL
    if not server_url.endswith('/mcp'):
        server_url = server_url.rstrip('/') + '/mcp'

    print(f"\n=== Testing Connection Only ===")
    print(f"Server URL: {server_url}")

    try:
        client = Client(server_url)
        async with client:
            print("✓ Successfully connected to MCP server")

            # Try to list tools if possible
            # Note: This might not work depending on the MCP implementation
            try:
                # This is a common MCP pattern but might not be supported
                print("\nAttempting to discover available tools...")
                # FastMCP doesn't expose tool listing directly to clients
                print("Note: Tool discovery not available in FastMCP")
            except:
                pass

    except Exception as e:
        print(f"❌ Connection failed: {type(e).__name__}: {str(e)}")


async def test_with_timeout():
    """Test with explicit timeout to catch hanging operations"""
    print("\n=== Testing with 30-second timeout ===")

    try:
        # Run with timeout
        await asyncio.wait_for(test_pipeline_direct(), timeout=30.0)
    except asyncio.TimeoutError:
        print("\n❌ Test timed out after 30 seconds")
        print("This suggests the pipeline is taking too long to execute")
        print("Consider:")
        print("1. Using smaller test data")
        print("2. Reducing max_iterations to 1")
        print("3. Implementing async/polling pattern instead")


def main():
    """Main entry point with menu"""
    print("AutoGluon Pipeline Debug Client")
    print("==============================\n")

    print("Options:")
    print("1. Full pipeline test (simulates OpenAI)")
    print("2. Connection test only")
    print("3. Pipeline test with 30s timeout")
    print("4. Run all tests")

    choice = input("\nSelect option (1-4): ").strip()

    if choice == "1":
        asyncio.run(test_pipeline_direct())
    elif choice == "2":
        asyncio.run(test_connection_only())
    elif choice == "3":
        asyncio.run(test_with_timeout())
    elif choice == "4":
        asyncio.run(test_connection_only())
        asyncio.run(test_with_timeout())
    else:
        print("Invalid choice. Running full test...")
        asyncio.run(test_pipeline_direct())


if __name__ == "__main__":
    # For direct execution without menu
    # asyncio.run(test_pipeline_direct())

    # With menu
    main()
