#!/usr/bin/env python3
"""Minimal MCP Server with FastMCP"""

import os
import uvicorn
from mcp.server.fastmcp import FastMCP
from starlette.types import ASGIApp, Receive, Scope, Send


class TrailingSlashMiddleware:
    """Add trailing slash to /mcp requests to avoid 307 redirects.

    Starlette's Router redirects /mcp -> /mcp/ with a 307, which breaks
    behind reverse proxies (Railway, AWS ALB, etc.) that terminate TLS.
    This middleware normalizes the path before it reaches the router.
    See: https://github.com/modelcontextprotocol/python-sdk/issues/1168
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope["path"] == "/mcp":
            scope["path"] = "/mcp/"
        await self.app(scope, receive, send)


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
    app = TrailingSlashMiddleware(mcp_app)

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
