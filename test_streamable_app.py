#!/usr/bin/env python3
"""Test script to verify we can get and use FastMCP's streamable_http_app"""

import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Test Server")


@mcp.tool()
def test_tool() -> str:
    """Test tool"""
    return "test"


print("🧪 Testing FastMCP's streamable_http_app...")

try:
    app = mcp.streamable_http_app
    print(f"✅ Got streamable_http_app: {type(app)}")
    print(f"App object: {app}")

    if app is not None:
        print("🎉 SUCCESS: streamable_http_app is available!")
        print("This means we can run it with uvicorn directly!")

        # Check if it's a proper ASGI app
        if hasattr(app, "__call__"):
            print("✅ App is callable (ASGI compatible)")
        else:
            print("❌ App is not callable - might not be ASGI")

    else:
        print("❌ streamable_http_app is None")

except Exception as e:
    print(f"❌ Error accessing streamable_http_app: {e}")

print(f"\n🔍 All app-related attributes:")
for attr in dir(mcp):
    if "app" in attr.lower():
        value = getattr(mcp, attr)
        print(f"  {attr}: {type(value)} = {value}")
