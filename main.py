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
    print("Starting MCP server...")
    print("MCP endpoint will be available at the server URL + /mcp")

    # Set HOST to 0.0.0.0 for Railway deployment if not already set
    # This allows external connections to reach the server
    if not os.getenv("HOST"):
        os.environ["HOST"] = "0.0.0.0"

    # Ensure PORT is set (Railway will provide this)
    port = os.getenv("PORT", "8000")
    os.environ["PORT"] = port

    host = os.getenv("HOST", "0.0.0.0")

    print(f"Server will bind to {host}:{port}")
    print(f"Health check endpoint: http://{host}:{port}/mcp/")

    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
