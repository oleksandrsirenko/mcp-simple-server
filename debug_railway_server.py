#!/usr/bin/env python3
"""
Debug script to see what's happening with Railway server responses
"""

import asyncio
import httpx


async def debug_railway_server():
    """Debug what the Railway server is actually returning"""

    server_url = "https://mcp-simple-server-dev.up.railway.app"

    print(f"🔍 Debugging Railway server: {server_url}")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=30.0) as client:

        # Test 1: Basic connectivity
        print("1️⃣ Testing basic connectivity...")
        try:
            response = await client.get(server_url)
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            print(f"   Content: {response.text[:200]}...")
        except Exception as e:
            print(f"   ❌ Connection error: {e}")
            return

        # Test 2: MCP endpoint basic check
        print("\n2️⃣ Testing MCP endpoint...")
        mcp_endpoint = f"{server_url}/mcp/"
        try:
            response = await client.get(mcp_endpoint)
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            print(f"   Content: {response.text[:200]}...")
        except Exception as e:
            print(f"   ❌ Connection error: {e}")
            return

        # Test 3: MCP initialize request
        print("\n3️⃣ Testing MCP initialize request...")
        headers = {
            "Content-Type": "application/json",
            "MCP-Protocol-Version": "2025-06-18",
            "Accept": "application/json, text/event-stream",
        }

        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "debug-test", "version": "1.0.0"},
            },
        }

        try:
            response = await client.post(
                mcp_endpoint, json=init_request, headers=headers
            )
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            print(f"   Content Type: {response.headers.get('content-type')}")
            print(f"   Raw Content: {response.text[:1000]}...")

            if response.status_code == 200:
                try:
                    json_result = response.json()
                    print(f"   ✅ JSON parsed successfully!")
                    print(f"   JSON result: {json_result}")

                    session_id = response.headers.get("Mcp-Session-Id")
                    print(f"   Session ID: {session_id}")

                    if session_id:
                        print("\n🎉 MCP PROTOCOL IS WORKING!")
                        print("✅ Server is responding correctly to MCP requests")
                        print("✅ Tools should be available")
                    else:
                        print("\n⚠️  No session ID in response headers")

                except Exception as json_error:
                    print(f"   ❌ JSON parsing failed: {json_error}")
                    print(f"   📊 This suggests server returned non-JSON content")
            else:
                print(f"   ❌ Server returned status {response.status_code}")

        except Exception as e:
            print(f"   ❌ Request failed: {e}")

        # Test 4: Check if server supports SSE
        print("\n4️⃣ Testing Server-Sent Events support...")
        sse_headers = headers.copy()
        sse_headers["Accept"] = "text/event-stream"

        try:
            response = await client.post(
                mcp_endpoint, json=init_request, headers=sse_headers
            )
            print(f"   SSE Status: {response.status_code}")
            print(f"   SSE Content Type: {response.headers.get('content-type')}")
            print(f"   SSE Content: {response.text[:500]}...")
        except Exception as e:
            print(f"   ❌ SSE test failed: {e}")


if __name__ == "__main__":
    asyncio.run(debug_railway_server())
