#!/bin/bash

# Stop script for AutoGluon MCP Proxy

echo "=== Stopping AutoGluon MCP Proxy Services ==="
echo

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Stop proxy
if [ -f .proxy.pid ]; then
    PROXY_PID=$(cat .proxy.pid)
    echo -n "Stopping MCP Proxy (PID: $PROXY_PID)... "
    if kill $PROXY_PID 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}Process not found${NC}"
    fi
    rm .proxy.pid
else
    echo "No proxy PID file found, checking port 8003..."
    if lsof -Pi :8003 -sTCP:LISTEN -t >/dev/null 2>&1; then
        lsof -ti:8003 | xargs kill -9 2>/dev/null
        echo -e "${GREEN}✓ Stopped process on port 8003${NC}"
    fi
fi

# Stop local server
if [ -f .local_server.pid ]; then
    LOCAL_PID=$(cat .local_server.pid)
    echo -n "Stopping Local Server (PID: $LOCAL_PID)... "
    if kill $LOCAL_PID 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}Process not found${NC}"
    fi
    rm .local_server.pid
else
    echo "No local server PID file found, checking port 8001..."
    if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1; then
        lsof -ti:8001 | xargs kill -9 2>/dev/null
        echo -e "${GREEN}✓ Stopped process on port 8001${NC}"
    fi
fi

# Final port check
echo
echo "Checking ports..."
PORTS_CLEAR=true

if lsof -Pi :8003 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}⚠ Port 8003 still in use${NC}"
    PORTS_CLEAR=false
else
    echo -e "${GREEN}✓ Port 8003 is free${NC}"
fi

if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}⚠ Port 8001 still in use${NC}"
    PORTS_CLEAR=false
else
    echo -e "${GREEN}✓ Port 8001 is free${NC}"
fi

echo
if [ "$PORTS_CLEAR" = true ]; then
    echo -e "${GREEN}All services stopped successfully.${NC}"
else
    echo -e "${YELLOW}Some ports may still be in use. Use 'lsof -ti:PORT | xargs kill -9' to force stop.${NC}"
fi
