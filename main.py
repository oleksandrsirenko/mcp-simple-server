#!/usr/bin/env python3
"""
Minimal MCP Server with FastMCP — production-ready boilerplate.

Uses Streamable HTTP transport with stateless mode and JSON responses
as recommended by the official MCP Python SDK for scalable deployments.

Works behind any reverse proxy (Railway, AWS ALB, Nginx, Cloudflare, etc.)
thanks to uvicorn proxy-header support and a lightweight ASGI middleware
that prevents Starlette's trailing-slash 307 redirect from breaking
TLS-terminating proxies.

Ref: https://github.com/modelcontextprotocol/python-sdk
Ref: https://github.com/modelcontextprotocol/python-sdk/issues/1168
"""

import os
import uvicorn
from mcp.server.fastmcp import FastMCP
from starlette.types import ASGIApp, Receive, Scope, Send


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------


class TrailingSlashMiddleware:
    """Normalize MCP endpoint path to avoid Starlette's 307 redirect.

    With stateless_http=True the route is registered at ``/mcp`` (no slash).
    With stateful mode the route is at ``/mcp/`` (with slash).
    This middleware accepts both variants so the server works regardless
    of how the client or reverse proxy formats the URL.

    See https://github.com/modelcontextprotocol/python-sdk/issues/1168
    """

    def __init__(self, app: ASGIApp, mcp_path: str = "/mcp") -> None:
        self.app = app
        self.mcp_path = mcp_path

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            path = scope["path"]
            # Accept both /mcp and /mcp/ — try the canonical form first,
            # and if that would 307 just rewrite to the other variant.
            if path in (self.mcp_path, self.mcp_path + "/"):
                scope["path"] = self.mcp_path
        await self.app(scope, receive, send)


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "Simple Server",
    stateless_http=True,  # No server-side session state → horizontally scalable
    json_response=True,  # Plain JSON responses instead of SSE streams
)


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers"""
    return a + b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers"""
    return a * b


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

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
        proxy_headers=True,  # Trust X-Forwarded-Proto / X-Forwarded-For
        forwarded_allow_ips="*",  # Allow any proxy (Railway, ALB, Nginx …)
    )
