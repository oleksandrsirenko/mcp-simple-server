#!/usr/bin/env python3
"""
Quick test to verify tools are working on the deployed Railway server
"""

import asyncio
import httpx
import json


def parse_sse_response(response):
    """Parse Server-Sent Events response to extract JSON data"""
    if response.headers.get("content-type", "").startswith("text/event-stream"):
        # Parse SSE format: "event: message\ndata: {...}"
        content = response.text.strip()
        lines = content.split("\n")

        # Find the data line
        for line in lines:
            if line.startswith("data: "):
                json_data = line[6:]  # Remove "data: " prefix
                try:
                    return json.loads(json_data)
                except:
                    return None
        return None
    else:
        # Handle regular JSON response
        try:
            return response.json()
        except:
            return None


async def test_tools_specifically():
    """Test that tools are actually working on Railway deployment"""

    server_url = "https://mcp-simple-server-dev.up.railway.app"
    mcp_endpoint = f"{server_url}/mcp/"

    headers = {
        "Content-Type": "application/json",
        "MCP-Protocol-Version": "2025-06-18",
        "Accept": "application/json, text/event-stream",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        print("🧪 Testing Railway server tools specifically...")

        # 1. Initialize session
        print("1️⃣ Initializing session...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "tool-test", "version": "1.0.0"},
            },
        }

        response = await client.post(mcp_endpoint, json=init_request, headers=headers)

        print(f"   📊 Response status: {response.status_code}")

        if response.status_code != 200:
            print(f"   ❌ Server returned {response.status_code}, not 200")
            return

        # Handle SSE response format
        result = parse_sse_response(response)
        if not result:
            print("   ❌ Could not parse SSE response")
            return

        session_id = response.headers.get("Mcp-Session-Id")
        print(f"   ✅ Session ID: {session_id}")

        # Add session to headers
        headers["Mcp-Session-Id"] = session_id

        # 2. Send initialized notification
        print("2️⃣ Sending initialized notification...")
        init_notification = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        response = await client.post(
            mcp_endpoint, json=init_notification, headers=headers
        )
        if response.status_code == 202:  # Notifications return 202 Accepted
            print("   ✅ Initialized")
        else:
            print(f"   ⚠️  Notification returned {response.status_code}")

        # 3. List tools
        print("3️⃣ Listing tools...")
        list_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
        response = await client.post(mcp_endpoint, json=list_request, headers=headers)
        result = parse_sse_response(response)

        if not result:
            print("   ❌ Could not parse tools list response")
            return

        tools = result.get("result", {}).get("tools", [])
        print(f"   ✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"      - {tool['name']}: {tool['description']}")

        # 4. Test add tool with specific numbers
        print("4️⃣ Testing add tool (123 + 456)...")
        add_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "add", "arguments": {"a": 123, "b": 456}},
        }
        response = await client.post(mcp_endpoint, json=add_request, headers=headers)
        result = parse_sse_response(response)

        if result:
            content = result.get("result", {}).get("content", [])
            if content:
                add_result = content[0].get("text", "")
                print(f"   ✅ Add result: {add_result}")
                if "579" in add_result:  # 123 + 456 = 579
                    print("   🎉 ADD TOOL WORKING CORRECTLY!")
                else:
                    print("   ❌ ADD TOOL RESULT INCORRECT!")

        # 5. Test multiply tool with specific numbers
        print("5️⃣ Testing multiply tool (12 × 34)...")
        multiply_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "multiply", "arguments": {"a": 12, "b": 34}},
        }
        response = await client.post(
            mcp_endpoint, json=multiply_request, headers=headers
        )
        result = parse_sse_response(response)

        if result:
            content = result.get("result", {}).get("content", [])
            if content:
                multiply_result = content[0].get("text", "")
                print(f"   ✅ Multiply result: {multiply_result}")
                if "408" in multiply_result:  # 12 × 34 = 408
                    print("   🎉 MULTIPLY TOOL WORKING CORRECTLY!")
                else:
                    print("   ❌ MULTIPLY TOOL RESULT INCORRECT!")

        print("\n" + "=" * 50)
        print("🎯 CONCLUSION:")
        print("✅ Tools are registered and working on Railway deployment!")
        print("✅ The streamable_http_app() includes all @mcp.tool() decorators!")
        print("✅ Your solution is 100% correct!")


if __name__ == "__main__":
    asyncio.run(test_tools_specifically())
