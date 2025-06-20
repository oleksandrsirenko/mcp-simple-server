#!/usr/bin/env python3
"""Minimal MCP Server with FastMCP"""

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

    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
