#!/bin/bash

# Setup script for AutoGluon MCP Proxy using FastMCP's built-in proxy
# This combines local file operations with remote AutoGluon processing

set -e

echo "=== AutoGluon MCP Proxy Setup (FastMCP) ==="
echo

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check current directory
CLIENT_DIR="/Users/huawen.shen/Documents/autogluon-mcp-client"
if [ "$PWD" != "$CLIENT_DIR" ]; then
    echo -e "${YELLOW}Changing to client directory: $CLIENT_DIR${NC}"
    cd "$CLIENT_DIR"
fi

# Step 1: Install dependencies
echo "1. Checking dependencies..."

# Check Python dependencies
echo -n "Checking Python dependencies... "
if python -c "import fastmcp" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}Installing fastmcp...${NC}"
    pip install fastmcp aiohttp httpx
fi

# Step 2: Create necessary directories
echo
echo "2. Creating directories..."
mkdir -p logs
mkdir -p cache
echo -e "${GREEN}✓ Directories created${NC}"

# Step 3: Check required files
echo
echo "3. Checking required files..."
REQUIRED_FILES=("local_server.py" "proxy_server.py" "file_handler.py")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}✗ Missing required file: $file${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✓ All required files present${NC}"

# Step 4: Test remote server connection
echo
echo "4. Testing remote server connection..."
REMOTE_URL="https://0d49-34-211-143-25.ngrok-free.app"

if curl -s -H "ngrok-skip-browser-warning: true" "$REMOTE_URL/mcp" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Remote server is accessible${NC}"
else
    echo -e "${YELLOW}⚠ Remote server may not be accessible. Check your ngrok URL.${NC}"
    echo "Update the URL in proxy_server.py if needed."
fi

# Step 5: Kill existing processes
echo
echo "5. Cleaning up existing processes..."

# Kill local server if running
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}Stopping existing local server on port 8001...${NC}"
    lsof -ti:8001 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# Kill proxy if running
if lsof -Pi :8003 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}Stopping existing proxy on port 8003...${NC}"
    lsof -ti:8003 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# Step 6: Start local server
echo
echo "6. Starting local MCP server..."

echo "Starting local server on port 8001..."
nohup python local_server.py >logs/local_server.log 2>&1 &
LOCAL_PID=$!
echo "Local server PID: $LOCAL_PID"

# Wait for local server to start
sleep 3

# Check if local server is running
if curl -s http://localhost:8001 >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Local server started successfully${NC}"
else
    echo -e "${RED}✗ Failed to start local server${NC}"
    echo "Check logs/local_server.log for details:"
    tail -n 20 logs/local_server.log
    exit 1
fi

# Step 7: Start FastMCP Proxy
echo
echo "7. Starting FastMCP Proxy..."

echo "Starting proxy server on port 8003..."
nohup python proxy_server.py >logs/proxy.log 2>&1 &
PROXY_PID=$!
echo "Proxy PID: $PROXY_PID"

# Save PIDs for stop script
echo $LOCAL_PID >.local_server.pid
echo $PROXY_PID >.proxy.pid

# Wait for proxy to start
echo "Waiting for proxy to initialize..."
sleep 5

# Check if proxy is running
PROXY_CHECK_ATTEMPTS=0
PROXY_RUNNING=false

while [ $PROXY_CHECK_ATTEMPTS -lt 10 ]; do
    if curl -s http://localhost:8003 >/dev/null 2>&1; then
        PROXY_RUNNING=true
        break
    fi
    sleep 1
    PROXY_CHECK_ATTEMPTS=$((PROXY_CHECK_ATTEMPTS + 1))
done

if [ "$PROXY_RUNNING" = true ]; then
    echo -e "${GREEN}✓ Proxy started successfully${NC}"
else
    echo -e "${RED}✗ Failed to start proxy server${NC}"
    echo "Check logs/proxy.log for details:"
    tail -n 20 logs/proxy.log

    # Clean up
    kill $LOCAL_PID 2>/dev/null || true
    kill $PROXY_PID 2>/dev/null || true
    exit 1
fi

# Final status
echo
echo "=== Setup Complete ==="
echo
echo -e "${GREEN}Services running:${NC}"
echo "  - Local MCP Server: http://localhost:8001"
echo "  - FastMCP Proxy: http://localhost:8003"
echo "  - Remote Server: $REMOTE_URL"
echo
echo "Available tools:"
echo "  - Local: local_* (file operations)"
echo "  - Remote: remote_* (AutoGluon operations)"
echo
echo "To view logs:"
echo "  - Local server: tail -f logs/local_server.log"
echo "  - Proxy server: tail -f logs/proxy.log"
echo
echo "To stop all services: ./stop_proxy.sh"
echo
echo "Test with: python test_proxy_client.py"
