#!/usr/bin/env python3
"""
Debug script for FastMCP proxy setup
Helps diagnose connection and configuration issues
"""

import asyncio
import subprocess
import time
import json
from pathlib import Path
import httpx
from fastmcp import FastMCP, Client


async def test_local_server():
    """Test if local server is running correctly"""
    print("1. Testing local server (port 8001)...")

    try:
        # Test HTTP endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001", timeout=5.0)
            print(f"   HTTP response: {response.status_code}")

        # Test as MCP client
        local_client = Client("http://localhost:8001/mcp")
        async with local_client:
            print("   ✓ Local server is accessible via MCP")
            # Try to call a simple tool if possible

    except Exception as e:
        print(f"   ✗ Local server error: {e}")
        print("   Checking if it's running as stdio instead...")

        # Try stdio transport
        try:
            proc = subprocess.Popen(
                ["python", "local_server.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # Send initialization
            proc.stdin.write(
                '{"jsonrpc": "2.0", "method": "initialize", "params": {}, "id": 1}\n')
            proc.stdin.flush()

            # Read response (with timeout)
            import select
            readable, _, _ = select.select([proc.stdout], [], [], 2.0)
            if readable:
                response = proc.stdout.readline()
                print(f"   Stdio response: {response[:50]}...")
                print("   ℹ️  Local server is running in stdio mode")
            proc.terminate()

        except Exception as e2:
            print(f"   ✗ Stdio test failed: {e2}")

        return False

    return True


async def test_remote_server():
    """Test if remote server is accessible"""
    print("\n2. Testing remote server...")

    remote_url = "https://0d49-34-211-143-25.ngrok-free.app/mcp"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                remote_url,
                headers={"ngrok-skip-browser-warning": "true"},
                timeout=10.0
            )
            print(f"   Remote server response: {response.status_code}")
            print("   ✓ Remote server is accessible")
            return True

    except Exception as e:
        print(f"   ✗ Remote server error: {e}")
        return False


def create_simple_proxy():
    """Create a simple test proxy"""
    print("\n3. Creating simple test proxy...")

    try:
        # Simple HTTP-to-HTTP proxy
        remote_url = "https://0d49-34-211-143-25.ngrok-free.app/mcp"

        proxy = FastMCP.as_proxy(
            remote_url,
            name="Simple Test Proxy"
        )

        print("   ✓ Simple proxy created successfully")
        return proxy

    except Exception as e:
        print(f"   ✗ Failed to create proxy: {e}")
        return None


async def test_stdio_proxy():
    """Test creating a stdio-based proxy"""
    print("\n4. Testing stdio-based proxy configuration...")

    config = {
        "mcpServers": {
            "test": {
                "command": ["python", "local_server.py"],
                "transport": "stdio"
            }
        }
    }

    try:
        proxy = FastMCP.as_proxy(config, name="Stdio Test Proxy")
        print("   ✓ Stdio proxy configuration is valid")
        return proxy
    except Exception as e:
        print(f"   ✗ Stdio proxy failed: {e}")
        return None


async def check_logs():
    """Check recent log files for errors"""
    print("\n5. Checking log files...")

    log_files = {
        "Local server": "logs/local_server.log",
        "Proxy": "logs/proxy.log"
    }

    for name, path in log_files.items():
        if Path(path).exists():
            print(f"\n   {name} logs (last 10 lines):")
            with open(path, 'r') as f:
                lines = f.readlines()
                for line in lines[-10:]:
                    print(f"     {line.rstrip()}")
        else:
            print(f"   No {name} log file found")


async def run_diagnostics():
    """Run all diagnostic tests"""
    print("=== FastMCP Proxy Diagnostics ===\n")

    # Test components
    local_ok = await test_local_server()
    remote_ok = await test_remote_server()

    # Try creating proxies
    simple_proxy = create_simple_proxy()
    stdio_proxy = await test_stdio_proxy()

    # Check logs
    await check_logs()

    # Recommendations
    print("\n=== Recommendations ===")

    if not local_ok:
        print("• Fix local server first:")
        print("  - Check if local_server.py uses correct transport (http vs stdio)")
        print("  - For http: mcp.run(transport='http', host='127.0.0.1', port=8001)")
        print("  - For stdio: mcp.run(transport='stdio')")

    if not remote_ok:
        print("• Remote server issues:")
        print("  - Check if ngrok URL is correct")
        print("  - Verify EC2 server is running")

    if simple_proxy and not stdio_proxy:
        print("• Use HTTP transport for local server instead of stdio")
        print("  - Modify local_server.py to use: mcp.run(transport='http', port=8001)")

    print("\nTo test a minimal setup:")
    print("1. Start only the remote proxy: python -c \"from fastmcp import FastMCP; FastMCP.as_proxy('https://0d49-34-211-143-25.ngrok-free.app/mcp').run(transport='http', port=8003)\"")
    print("2. Test with: curl http://localhost:8003")


if __name__ == "__main__":
    asyncio.run(run_diagnostics())
