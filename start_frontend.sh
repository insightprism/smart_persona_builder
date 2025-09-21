#!/bin/bash

# Smart Persona Builder - Frontend Startup Script
# Runs React development server on port 36665

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/spb_ui"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Smart Persona Builder - Frontend${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    echo -e "${YELLOW}Please install Node.js from https://nodejs.org/${NC}"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm is not installed${NC}"
    exit 1
fi

# Display Node and npm versions
echo -e "${BLUE}Node version: $(node --version)${NC}"
echo -e "${BLUE}npm version: $(npm --version)${NC}"
echo ""

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
    echo ""
else
    echo -e "${GREEN}Dependencies already installed${NC}"
    # Skip update check for faster startup
    # Uncomment the next line if you want to check for updates
    # npm update 2>/dev/null || true
    echo ""
fi

# Update the backend API URL to use port 36664
echo -e "${GREEN}Configuring API endpoint for port 36664...${NC}"

# Start the frontend development server
echo ""
echo -e "${GREEN}Starting React development server...${NC}"
echo -e "${GREEN}Frontend will be available at: http://localhost:36665${NC}"
echo -e "${BLUE}Backend API expected at: http://localhost:36664${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Run the React development server on port 36665
# Note: Using npm start which is configured in package.json
PORT=36665 npm start