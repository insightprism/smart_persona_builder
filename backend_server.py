#!/usr/bin/env python3
"""FastAPI backend server for Smart Persona Builder"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import sys

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our API router
from spb_api.persona_endpoints import router as persona_router

# Create FastAPI app
app = FastAPI(
    title="Smart Persona Builder API",
    description="API for creating and managing AI personas with flexible trait blocks",
    version="1.0.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:36665",
        "http://localhost:3000",
        "http://127.0.0.1:36665",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create personas directory if it doesn't exist
PERSONAS_DIR = os.path.join(os.path.dirname(__file__), "personas")
os.makedirs(PERSONAS_DIR, exist_ok=True)

# Set the personas directory in environment
os.environ["SPB_PERSONAS_DIR"] = PERSONAS_DIR

# Include the persona routes
app.include_router(persona_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Smart Persona Builder API",
        "version": "1.0.0",
        "docs": "/docs",
        "personas_directory": PERSONAS_DIR
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Get server info
@app.get("/api/info")
async def get_info():
    # Count personas
    persona_count = 0
    if os.path.exists(PERSONAS_DIR):
        persona_count = len([f for f in os.listdir(PERSONAS_DIR) if f.endswith('.json')])
    
    return {
        "server": "Smart Persona Builder",
        "version": "1.0.0",
        "personas_directory": PERSONAS_DIR,
        "persona_count": persona_count,
        "api_endpoints": [
            "/api/personas",
            "/api/personas/{id}",
            "/api/personas/{id}/generate",
            "/api/personas/{id}/traits",
            "/api/personas/categories",
            "/api/personas/validate",
            "/api/personas/search",
            "/api/personas/{id}/export",
            "/api/personas/import"
        ]
    }

if __name__ == "__main__":
    print("="*60)
    print("Smart Persona Builder Backend Server")
    print("="*60)
    print(f"Personas directory: {PERSONAS_DIR}")
    print(f"Starting server on http://localhost:36664")
    print(f"API documentation: http://localhost:36664/docs")
    print("="*60)
    
    # Run the server
    uvicorn.run(
        "backend_server:app",
        host="0.0.0.0",
        port=36664,
        reload=True,
        reload_dirs=[os.path.dirname(__file__)]
    )