#!/usr/bin/env python3
"""
Simple connection test for EC2 MCP server
"""

import requests
import asyncio
import httpx
from fastmcp import Client

# 替换为你的 EC2 公网 IP
EC2_IP = "34.211.143.25"
SERVER_URL = f"http://{EC2_IP}:8000"


def test_basic_connection():
    """Test basic HTTP connection"""
    print("=== Testing Basic Connection ===")
    
    # Test root endpoint
    try:
        response = requests.get(SERVER_URL, timeout=5)
        print(f"GET {SERVER_URL}: Status {response.status_code}")
    except Exception as e:
        print(f"GET {SERVER_URL}: Failed - {e}")
        return False
    
    # Test MCP endpoint
    try:
        response = requests.get(f"{SERVER_URL}/mcp", timeout=5)
        print(f"GET {SERVER_URL}/mcp: Status {response.status_code}")
    except Exception as e:
        print(f"GET {SERVER_URL}/mcp: Failed - {e}")
    
    return True


async def test_mcp_client():
    """Test MCP client connection"""
    print("\n=== Testing MCP Client ===")
    
    mcp_url = f"{SERVER_URL}/mcp"
    print(f"Connecting to: {mcp_url}")
    
    try:
        # Create client with explicit configuration
        client = Client(mcp_url)
        
        async with client:
            print("✓ Client connected successfully")
            
            # Try to list tools
            print("Attempting to call a simple tool...")
            result = await client.call_tool("get_progress", {})
            print(f"Tool call result: {result}")
            
    except Exception as e:
        print(f"✗ MCP client error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


async def test_httpx_direct():
    """Test direct httpx connection"""
    print("\n=== Testing Direct httpx ===")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test base URL
            response = await client.get(SERVER_URL)
            print(f"httpx GET {SERVER_URL}: Status {response.status_code}")
            
            # Test MCP endpoint
            response = await client.get(f"{SERVER_URL}/mcp")
            print(f"httpx GET {SERVER_URL}/mcp: Status {response.status_code}")
            
            # Test POST to MCP
            headers = {"Content-Type": "application/json"}
            data = {"jsonrpc": "2.0", "method": "tools/list", "id": 1}
            
            response = await client.post(
                f"{SERVER_URL}/mcp",
                json=data,
                headers=headers
            )
            print(f"httpx POST {SERVER_URL}/mcp: Status {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"httpx error: {e}")


def main():
    print(f"Testing connection to EC2 MCP Server at {EC2_IP}")
    print("=" * 50)
    
    # Test basic connection
    if not test_basic_connection():
        print("\n❌ Basic connection failed!")
        print("\nPossible issues:")
        print("1. EC2 security group doesn't allow port 8000 from your IP")
        print("2. MCP server is not running on EC2")
        print("3. EC2 instance is not reachable")
        return
    
    # Test httpx
    print("\nBasic connection OK. Testing advanced connections...")
    asyncio.run(test_httpx_direct())
    
    # Test MCP client
    asyncio.run(test_mcp_client())
    
    print("\n" + "=" * 50)
    print("Test completed.")


if __name__ == "__main__":
    main()
