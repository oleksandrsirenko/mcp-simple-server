#!/usr/bin/env python3
"""
MCP Proxy for Claude Desktop to connect to Railway-deployed server
Save this as: claude_mcp_proxy.py
"""

import asyncio
import json
import sys
import httpx


class MCPProxy:
    def __init__(self, server_url):
        self.server_url = server_url
        self.client = httpx.AsyncClient(timeout=60.0)
        self.session_id = None

    async def handle_request(self, request_data):
        """Forward MCP request to Railway server"""
        headers = {
            "Content-Type": "application/json",
            "MCP-Protocol-Version": "2025-06-18",
            "Accept": "application/json, text/event-stream",
        }

        # Add session ID if we have one
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        try:
            response = await self.client.post(
                f"{self.server_url}/mcp/", json=request_data, headers=headers
            )

            # Store session ID from response
            if "Mcp-Session-Id" in response.headers:
                self.session_id = response.headers["Mcp-Session-Id"]

            # Parse SSE response if needed
            if response.headers.get("content-type", "").startswith("text/event-stream"):
                content = response.text.strip()
                lines = content.split("\n")
                for line in lines:
                    if line.startswith("data: "):
                        return json.loads(line[6:])
            else:
                return response.json()

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "error": {"code": -32603, "message": f"Proxy error: {str(e)}"},
            }

    async def run(self):
        """Main proxy loop"""
        try:
            while True:
                # Read JSON-RPC request from stdin
                line = sys.stdin.readline()
                if not line:
                    break

                try:
                    request_data = json.loads(line.strip())
                    response_data = await self.handle_request(request_data)

                    # Write JSON-RPC response to stdout
                    print(json.dumps(response_data), flush=True)

                except json.JSONDecodeError:
                    continue

        except KeyboardInterrupt:
            pass
        finally:
            await self.client.aclose()


if __name__ == "__main__":
    proxy = MCPProxy("https://mcp-simple-server-dev.up.railway.app")
    asyncio.run(proxy.run())
