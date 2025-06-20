#!/usr/bin/env python3
"""
Test script to verify that the server is actually binding to 0.0.0.0
This helps us confirm the fix works before deploying to Railway
"""

import asyncio
import os
import subprocess
import sys
import time
import signal
import httpx
from typing import Optional


class HostBindingTest:
    def __init__(self):
        self.server_process: Optional[subprocess.Popen] = None

    async def start_server(self, use_startup_script: bool = True) -> bool:
        """Start the server using either startup script or direct python"""
        print("🚀 Starting server for host binding test...")

        if use_startup_script:
            print("Using startup script (./start.sh)...")
            cmd = ["./start.sh"]
        else:
            print("Using direct python (python main.py)...")
            cmd = ["python", "main.py"]

        try:
            self.server_process = subprocess.Popen(
                cmd,
                env={"HOST": "0.0.0.0", "PORT": "8000"},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid if hasattr(os, "setsid") else None,
            )

            # Wait for server to start
            await asyncio.sleep(3)

            # Check if process is still running
            if self.server_process.poll() is not None:
                stdout, stderr = self.server_process.communicate()
                print(f"❌ Server process exited early")
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                return False

            return True

        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False

    async def test_binding(self) -> bool:
        """Test if server is accessible from external IP (0.0.0.0)"""
        print("🔍 Testing server accessibility...")

        # Test localhost (should always work)
        localhost_ok = await self.test_endpoint("http://127.0.0.1:8000/mcp/")

        # Test 0.0.0.0 (this is what Railway needs)
        external_ok = await self.test_endpoint("http://0.0.0.0:8000/mcp/")

        print(f"📊 Results:")
        print(f"  • Localhost (127.0.0.1): {'✅ OK' if localhost_ok else '❌ FAIL'}")
        print(f"  • External (0.0.0.0): {'✅ OK' if external_ok else '❌ FAIL'}")

        if external_ok:
            print("🎉 SUCCESS: Server is properly binding to 0.0.0.0!")
            print("🚂 This should work on Railway!")
            return True
        else:
            print("❌ PROBLEM: Server is not accessible from 0.0.0.0")
            print("🚨 This will fail on Railway!")
            return False

    async def test_endpoint(self, url: str) -> bool:
        """Test if a specific endpoint is accessible"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    url,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "initialize",
                        "params": {
                            "protocolVersion": "2025-06-18",
                            "capabilities": {"tools": {}},
                            "clientInfo": {"name": "binding-test", "version": "1.0.0"},
                        },
                    },
                    headers={
                        "Content-Type": "application/json",
                        "MCP-Protocol-Version": "2025-06-18",
                        "Accept": "application/json, text/event-stream",
                    },
                )
                return response.status_code == 200
        except Exception as e:
            print(f"    Connection failed: {e}")
            return False

    def stop_server(self):
        """Stop the server process"""
        if self.server_process:
            try:
                if hasattr(os, "killpg"):
                    os.killpg(os.getpgid(self.server_process.pid), signal.SIGTERM)
                else:
                    self.server_process.terminate()

                # Wait for process to terminate
                try:
                    self.server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.server_process.kill()
                    self.server_process.wait()

                print("🛑 Server stopped")
            except Exception as e:
                print(f"⚠️  Error stopping server: {e}")


async def main():
    """Run the host binding test"""
    print("🧪 Host Binding Test for Railway Deployment")
    print("=" * 60)

    tester = HostBindingTest()

    try:
        # Test with startup script
        print("\n📋 Test 1: Using startup script (./start.sh)")
        if await tester.start_server(use_startup_script=True):
            success = await tester.test_binding()
            tester.stop_server()

            if success:
                print("\n🎉 HOST BINDING TEST PASSED!")
                print("✅ Your server should work on Railway!")
                return True
        else:
            print("❌ Could not start server with startup script")

        # If startup script fails, test direct python
        print("\n📋 Test 2: Using direct python (python main.py)")
        if await tester.start_server(use_startup_script=False):
            success = await tester.test_binding()
            tester.stop_server()

            if success:
                print("\n🎉 HOST BINDING TEST PASSED!")
                print("✅ Your server should work on Railway!")
                return True
        else:
            print("❌ Could not start server with direct python")

        print("\n💥 HOST BINDING TEST FAILED!")
        print("❌ The server is not binding to 0.0.0.0")
        print("🚨 This will cause Railway deployment to fail!")
        return False

    except KeyboardInterrupt:
        print("\n👋 Test interrupted")
        return False
    finally:
        tester.stop_server()


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)
