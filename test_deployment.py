#!/usr/bin/env python3
"""
Test deployed MCP server on Railway.

Usage:
    python test_deployment.py mcp-simple-server-dev.up.railway.app
    python test_deployment.py https://mcp-simple-server-production.up.railway.app
"""

import asyncio
import sys
from test_server import MCPServerTest


async def test_deployed_server(server_url: str) -> bool:
    """Test the deployed MCP server."""
    print(f"🌐 Testing deployed server at: {server_url}")
    print("=" * 60)

    try:
        async with MCPServerTest(server_url) as tester:
            success = await tester.run_all_tests()
            return success
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("💡 Make sure the server is deployed and accessible")
        return False


def main():
    """Main test runner for deployed server."""
    if len(sys.argv) != 2:
        print("Usage: python test_deployment.py <server_url>")
        print(
            "Example: python test_deployment.py https://mcp-simple-server-production.up.railway.app"
        )
        print("Example: python test_deployment.py mcp-simple-server-dev.up.railway.app")
        sys.exit(1)

    server_url = sys.argv[1].rstrip("/")  # Remove trailing slash

    # Add https:// if not present
    if not server_url.startswith(("http://", "https://")):
        server_url = f"https://{server_url}"
        print(f"🔗 Added https protocol: {server_url}")

    try:
        success = asyncio.run(test_deployed_server(server_url))
        if success:
            print("\n🎉 Deployment test successful!")
            print(f"✅ Your MCP server is live at: {server_url}/mcp/")
            print("\n🔧 Next steps:")
            print("1. Use this URL in Claude Desktop configuration")
            print("2. Set up GitHub Actions for auto-deployment")
            print("3. Test with Claude AI assistant")
        else:
            print("\n❌ Deployment test failed!")

        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")
        sys.exit(1)


if __name__ == "__main__":
    main()
