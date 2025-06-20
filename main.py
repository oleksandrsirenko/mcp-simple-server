#!/usr/bin/env python3
"""Minimal MCP Server with FastMCP - Railway Compatible"""

import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Simple Server")


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers"""
    return a + b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers"""
    return a * b


def main():
    """Run the server"""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    print("Starting MCP server...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print("MCP endpoint will be available at the server URL + /mcp")
    print(f"Health check endpoint: http://{host}:{port}/mcp/")

    # For Railway/production deployment, we need to ensure 0.0.0.0 binding
    if host == "0.0.0.0":
        print("🚀 Production mode: Ensuring proper host binding")

        # Set environment variables that uvicorn will definitely read
        os.environ["UVICORN_HOST"] = host
        os.environ["UVICORN_PORT"] = str(port)
        os.environ["HOST"] = host
        os.environ["PORT"] = str(port)

        # Also try setting common server environment variables
        os.environ["SERVER_HOST"] = host
        os.environ["BIND_HOST"] = host
        os.environ["LISTEN_HOST"] = host

        print(f"✅ Set multiple environment variables to force {host}:{port} binding")

    print("🏃 Starting FastMCP server...")

    # Run the server - FastMCP should now pick up the environment variables
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
