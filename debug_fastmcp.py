#!/usr/bin/env python3
"""Debug script to understand FastMCP's behavior"""

import os
from mcp.server.fastmcp import FastMCP

# Set environment variables
os.environ["HOST"] = "0.0.0.0"
os.environ["PORT"] = "8000"
os.environ["UVICORN_HOST"] = "0.0.0.0"
os.environ["UVICORN_PORT"] = "8000"

print("🔍 Debugging FastMCP...")
print(f"Environment variables set:")
print(f"  HOST: {os.environ.get('HOST')}")
print(f"  PORT: {os.environ.get('PORT')}")
print(f"  UVICORN_HOST: {os.environ.get('UVICORN_HOST')}")
print(f"  UVICORN_PORT: {os.environ.get('UVICORN_PORT')}")

mcp = FastMCP("Debug Server")

print(f"\n🔍 FastMCP instance attributes:")
for attr in dir(mcp):
    if not attr.startswith("_"):
        print(f"  {attr}: {type(getattr(mcp, attr))}")

print(f"\n🔍 Looking for app-related attributes:")
for attr in dir(mcp):
    if "app" in attr.lower() or "server" in attr.lower():
        print(f"  {attr}: {getattr(mcp, attr)}")

print(f"\n🔍 FastMCP methods:")
for attr in dir(mcp):
    if callable(getattr(mcp, attr)) and not attr.startswith("_"):
        print(f"  {attr}()")

# Try to see what FastMCP imports
print(f"\n🔍 FastMCP module info:")
import mcp.server.fastmcp

print(f"FastMCP module: {mcp.server.fastmcp}")
print(f"FastMCP file: {mcp.server.fastmcp.__file__}")

# Check for uvicorn usage
try:
    import uvicorn

    print(f"\nUvicorn version: {uvicorn.__version__}")
    print(f"Uvicorn config defaults:")
    config = uvicorn.Config("dummy:app")
    print(f"  host: {config.host}")
    print(f"  port: {config.port}")
except Exception as e:
    print(f"Uvicorn error: {e}")

print("\n" + "=" * 50)
print("Now let's see what happens when we run FastMCP...")
print("=" * 50)
