#!/usr/bin/env python3
"""
Quick test for the Claude MCP proxy script
"""

import asyncio
import json
from claude_mcp_proxy import MCPProxy


async def test_proxy():
    """Test the proxy script functionality"""
    print("🧪 Testing Claude MCP Proxy Script...")
    print("=" * 50)

    proxy = MCPProxy("https://mcp-simple-server-dev.up.railway.app")

    # Test 1: Initialize
    print("1️⃣ Testing initialize...")
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {"tools": {}},
            "clientInfo": {"name": "claude-proxy-test", "version": "1.0.0"},
        },
    }

    result = await proxy.handle_request(init_request)
    if result and "result" in result:
        print(f"   ✅ Initialize successful")
        print(f"   Server: {result['result']['serverInfo']['name']}")
    else:
        print(f"   ❌ Initialize failed: {result}")
        return False

    # Test 1.5: Send initialized notification (REQUIRED!)
    print("\n1️⃣.5 Sending initialized notification...")
    init_notification = {"jsonrpc": "2.0", "method": "notifications/initialized"}

    result = await proxy.handle_request(init_notification)
    print("   ✅ Initialized notification sent")

    # Test 2: List tools (now it should work)
    print("\n2️⃣ Testing tools list...")
    list_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}

    result = await proxy.handle_request(list_request)
    if result and "result" in result:
        tools = result["result"]["tools"]
        print(f"   ✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"      - {tool['name']}")
    else:
        print(f"   ❌ Tools list failed: {result}")
        return False

    # Test 3: Call add tool
    print("\n3️⃣ Testing add tool...")
    add_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": "add", "arguments": {"a": 99, "b": 1}},
    }

    result = await proxy.handle_request(add_request)
    if result and "result" in result:
        content = result["result"]["content"][0]["text"]
        print(f"   ✅ Add result: {content}")
        if "100" in content:
            print("   🎉 Proxy working correctly!")
        else:
            print("   ⚠️  Unexpected result")
    else:
        print(f"   ❌ Add tool failed: {result}")
        return False

    await proxy.client.aclose()

    print("\n" + "=" * 50)
    print("🎉 PROXY TEST SUCCESSFUL!")
    print("✅ Ready for Claude Desktop integration!")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_proxy())
    if not success:
        print("❌ Proxy test failed!")
        exit(1)
