#!/usr/bin/env python3
"""
Simple test script for MCP server.

Tests the complete MCP protocol flow:
1. Server startup
2. Initialize session
3. Send initialized notification
4. List tools
5. Call tools
"""

import asyncio
import json
import subprocess
import sys
import time
from typing import Optional

import httpx


class MCPServerTest:
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.mcp_endpoint = f"{server_url}/mcp/"
        self.session_id: Optional[str] = None
        self.client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def _get_headers(self, include_session: bool = True) -> dict:
        """Get standard MCP headers."""
        headers = {
            "Content-Type": "application/json",
            "MCP-Protocol-Version": "2025-06-18",
            "Accept": "application/json, text/event-stream",
        }

        if include_session and self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        return headers

    async def _send_request(self, data: dict, expect_session: bool = False) -> dict:
        """Send a request to the MCP server."""
        response = await self.client.post(
            self.mcp_endpoint,
            json=data,
            headers=self._get_headers(include_session=not expect_session),
        )

        if expect_session:
            session_header = response.headers.get("Mcp-Session-Id")
            if session_header:
                self.session_id = session_header
                print(f"✅ Got session ID: {self.session_id}")

        response.raise_for_status()

        # Handle SSE responses
        if response.headers.get("content-type", "").startswith("text/event-stream"):
            # Parse SSE format: "event: message\ndata: {...}"
            content = response.text.strip()
            lines = content.split("\n")

            # Find the data line
            for line in lines:
                if line.startswith("data: "):
                    json_data = line[6:]  # Remove "data: " prefix
                    return json.loads(json_data)

            # If no data line found, return empty
            return {}

        # Handle JSON responses
        if response.text.strip():
            return response.json()
        else:
            return {}

    async def test_initialize(self) -> bool:
        """Test the initialize request."""
        print("🔄 Testing initialize...")

        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        }

        try:
            result = await self._send_request(request, expect_session=True)

            if result.get("jsonrpc") == "2.0" and "result" in result:
                server_info = result["result"].get("serverInfo", {})
                print(
                    f"✅ Initialize successful - Server: {server_info.get('name', 'Unknown')}"
                )
                return True
            else:
                print(f"❌ Initialize failed: {result}")
                return False

        except Exception as e:
            print(f"❌ Initialize error: {e}")
            return False

    async def test_initialized_notification(self) -> bool:
        """Send the initialized notification."""
        print("🔄 Sending initialized notification...")

        request = {"jsonrpc": "2.0", "method": "notifications/initialized"}

        try:
            response = await self.client.post(
                self.mcp_endpoint, json=request, headers=self._get_headers()
            )

            # Should return 202 Accepted for notifications
            if response.status_code == 202:
                print("✅ Initialized notification sent")
                return True
            else:
                print(f"❌ Initialized notification failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Initialized notification error: {e}")
            return False

    async def test_list_tools(self) -> bool:
        """Test listing available tools."""
        print("🔄 Testing tools/list...")

        request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}

        try:
            result = await self._send_request(request)

            if result.get("jsonrpc") == "2.0" and "result" in result:
                tools = result["result"].get("tools", [])
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"   - {tool['name']}: {tool['description']}")
                return len(tools) > 0
            else:
                print(f"❌ List tools failed: {result}")
                return False

        except Exception as e:
            print(f"❌ List tools error: {e}")
            return False

    async def test_call_add_tool(self) -> bool:
        """Test calling the add tool."""
        print("🔄 Testing add tool...")

        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "add", "arguments": {"a": 25, "b": 17}},
        }

        try:
            result = await self._send_request(request)

            if result.get("jsonrpc") == "2.0" and "result" in result:
                content = result["result"].get("content", [])
                if content:
                    response_text = content[0].get("text", "")
                    if "42" in response_text:  # 25 + 17 = 42
                        print("✅ Add tool returned correct result")
                        return True

                print(f"❌ Add tool unexpected result: {result}")
                return False

        except Exception as e:
            print(f"❌ Add tool error: {e}")
            return False

    async def test_call_multiply_tool(self) -> bool:
        """Test calling the multiply tool."""
        print("🔄 Testing multiply tool...")

        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "multiply", "arguments": {"a": 8, "b": 6}},
        }

        try:
            result = await self._send_request(request)

            if result.get("jsonrpc") == "2.0" and "result" in result:
                content = result["result"].get("content", [])
                if content:
                    response_text = content[0].get("text", "")
                    if "48" in response_text:  # 8 * 6 = 48
                        print("✅ Multiply tool returned correct result")
                        return True

                print(f"❌ Multiply tool unexpected result: {result}")
                return False

        except Exception as e:
            print(f"❌ Multiply tool error: {e}")
            return False

    async def run_all_tests(self) -> bool:
        """Run all tests in sequence."""
        print("🧪 Starting MCP Server Tests")
        print("=" * 50)

        tests = [
            ("Initialize", self.test_initialize),
            ("Initialized Notification", self.test_initialized_notification),
            ("List Tools", self.test_list_tools),
            ("Add Tool", self.test_call_add_tool),
            ("Multiply Tool", self.test_call_multiply_tool),
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            print(f"\n📋 Running {test_name} test...")
            if await test_func():
                passed += 1
            else:
                print(f"💥 {test_name} test failed")
                break  # Stop on first failure for MCP protocol

        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed! Your MCP server is working correctly.")
            return True
        else:
            print("💥 Some tests failed. Check the server logs.")
            return False


async def wait_for_server(url: str, timeout: int = 30) -> bool:
    """Wait for server to be ready."""
    print(f"⏳ Waiting for server at {url}...")

    async with httpx.AsyncClient() as client:
        for _ in range(timeout):
            try:
                response = await client.get(url)
                if response.status_code in [
                    200,
                    404,
                    405,
                ]:  # Any response means server is up
                    print("✅ Server is responding")
                    return True
            except:
                pass
            await asyncio.sleep(1)

    print("❌ Server not responding")
    return False


async def main():
    """Main test runner."""
    server_url = "http://localhost:8000"

    # Check if server is already running
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.get(server_url)
        print("✅ Server already running")
        server_process = None
    except:
        print("🚀 Starting server...")
        # Start the server
        server_process = subprocess.Popen(
            [sys.executable, "main.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        # Wait for server to start
        if not await wait_for_server(server_url):
            if server_process:
                server_process.terminate()
            print("❌ Could not start server")
            return False

    try:
        # Run tests
        async with MCPServerTest(server_url) as tester:
            success = await tester.run_all_tests()
            return success

    finally:
        # Clean up
        if server_process:
            print("🛑 Stopping server...")
            server_process.terminate()
            server_process.wait()


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Tests interrupted")
        sys.exit(1)
