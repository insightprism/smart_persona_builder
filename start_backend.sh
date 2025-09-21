#!/bin/bash

# Smart Persona Builder - Backend Startup Script
# Runs FastAPI backend server on port 36664

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Smart Persona Builder - Backend${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

# Display Python version
echo -e "${GREEN}Python version: $(python3 --version)${NC}"
echo ""

# Start the backend server
echo -e "${GREEN}Starting FastAPI backend server...${NC}"
echo -e "${GREEN}Server will be available at: http://localhost:36664${NC}"
echo -e "${GREEN}API documentation at: http://localhost:36664/docs${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Run the FastAPI server with uvicorn
python3 -m uvicorn backend_server:app \
    --host 0.0.0.0 \
    --port 36664 \
    --reload \
    --log-level info