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
    """Rewrite ``/mcp`` → ``/mcp/`` at the ASGI level so Starlette's router
    never emits a 307 redirect.  This is required because many reverse
    proxies (Railway, AWS ALB, GCP Cloud Run …) terminate TLS and the
    redirect's ``Location`` header can end up using ``http://`` or trigger
    a redirect loop.

    See https://github.com/modelcontextprotocol/python-sdk/issues/1168
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope["path"] == "/mcp":
            scope["path"] = "/mcp/"
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
