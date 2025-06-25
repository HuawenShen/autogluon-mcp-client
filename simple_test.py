#!/usr/bin/env python3
"""
Simple test to verify FastMCP proxy is working
"""

import asyncio
from fastmcp import Client


async def test_proxy():
    """Simple proxy test"""
    proxy_url = "http://localhost:8003/mcp"
    
    print("Testing FastMCP Proxy...")
    print(f"Connecting to: {proxy_url}")
    
    try:
        async with Client(proxy_url) as client:
            print("✓ Connected successfully!")
            
            # Test a simple local tool
            print("\nTesting local tool...")
            result = await client.call_tool("local_explore_directory", {
                "directory_path": "/Users/huawen.shen/Documents/autogluon-mcp-client/test_data",
                "max_depth": 1
            })
            
            if isinstance(result, list) and len(result) > 0:
                import json
                parsed = json.loads(result[0].text)
                if parsed.get("success"):
                    print(f"✓ Local tool works! Found tree with {parsed['tree'].get('count', 'some')} items")
                else:
                    print(f"✗ Local tool error: {parsed.get('error')}")
            
            # Test a simple remote tool
            print("\nTesting remote tool...")
            result = await client.call_tool("remote_check_status", {})
            
            if isinstance(result, list) and len(result) > 0:
                import json
                parsed = json.loads(result[0].text)
                print(f"✓ Remote tool works! Status: {parsed.get('state', 'connected')}")
            
            print("\n✅ Proxy is working correctly!")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure local server is running: curl http://localhost:8001")
        print("2. Check proxy logs: tail -f logs/proxy.log")
        print("3. Run debug script: python debug_proxy.py")


if __name__ == "__main__":
    asyncio.run(test_proxy())
