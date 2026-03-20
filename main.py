#!/usr/bin/env python3
"""Minimal MCP Server with FastMCP"""

import os
import uvicorn
from mcp.server.fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.applications import Starlette
from starlette.routing import Mount

mcp = FastMCP("Simple Server")


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers"""
    return a + b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers"""
    return a * b


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    print(f"Starting MCP server on {host}:{port}")
    print(f"MCP endpoint: /mcp")

    mcp_app = mcp.streamable_http_app()

    # Wrap to disable trailing slash redirects that break behind reverse proxies
    app = Starlette(
        routes=[Mount("/", app=mcp_app)],
        redirect_slashes=False,
    )

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
