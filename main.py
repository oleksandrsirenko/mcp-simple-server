#!/usr/bin/env python3
"""Minimal MCP Server with FastMCP - Railway Compatible"""

import os
from mcp.server.fastmcp import FastMCP

# Force set environment variables before creating FastMCP instance
os.environ["HOST"] = os.getenv("HOST", "0.0.0.0")
os.environ["PORT"] = os.getenv("PORT", "8000")

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
    port = os.getenv("PORT", "8000")

    print("Starting MCP server...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print("MCP endpoint will be available at the server URL + /mcp")
    print(f"Health check endpoint: http://{host}:{port}/mcp/")

    # Run the server
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
