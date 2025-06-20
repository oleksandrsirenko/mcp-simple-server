# MCP Simple Server

Minimal Model Context Protocol server with streamable HTTP transport. Built with FastMCP following the official Anthropic MCP specification 2025-06-18.

## Features

- ✅ **Two Math Tools**: `add` and `multiply` functions
- ✅ **Streamable HTTP Transport**: Modern MCP protocol with SSE support
- ✅ **Session Management**: Proper MCP initialization flow
- ✅ **Production Ready**: Docker, Railway, Heroku, Render deployment configs
- ✅ **Automated Testing**: Complete protocol validation
- ✅ **Claude Desktop Integration**: Ready for AI assistant integration

## Quick Start

### Local Development

```bash
git clone https://github.com/oleksandrsirenko/mcp-simple-server.git
cd mcp-simple-server
uv sync
source .venv/bin/activate
python main.py
```

Server starts at: `http://localhost:8000/mcp/`

### Test the Server

```bash
python test_server.py
```

Expected output:
```
🧪 Starting MCP Server Tests
✅ Initialize successful - Server: Simple Server
✅ Initialized notification sent
✅ Found 2 tools: add, multiply  
✅ Add tool returned correct result
✅ Multiply tool returned correct result
🎉 All tests passed!
```

## Available Tools

### `add(a, b)`
Adds two numbers together.

**Example:**
```json
{"name": "add", "arguments": {"a": 25, "b": 17}}
→ Returns: 42
```

### `multiply(a, b)`
Multiplies two numbers together.

**Example:**
```json
{"name": "multiply", "arguments": {"a": 8, "b": 6}}
→ Returns: 48
```

## Manual Testing with curl

### 1. Initialize Session
```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "MCP-Protocol-Version: 2025-06-18" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{"tools":{}},"clientInfo":{"name":"test-client","version":"1.0.0"}}}'
```

### 2. Send Initialized Notification
```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "MCP-Protocol-Version: 2025-06-18" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: YOUR_SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}'
```

### 3. List Tools
```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "MCP-Protocol-Version: 2025-06-18" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: YOUR_SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'
```

### 4. Call Add Tool
```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "MCP-Protocol-Version: 2025-06-18" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: YOUR_SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"add","arguments":{"a":25,"b":17}}}'
```

## Deployment

### Railway (Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "ready for deployment"
   git push origin main
   ```

2. **Deploy to Railway**:
   - Go to [railway.app](https://railway.app)
   - Click "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects Dockerfile and deploys

3. **Your MCP URL**: `https://your-app.railway.app/mcp/`

### Heroku

```bash
heroku create your-mcp-server
git push heroku main
```

**Your MCP URL**: `https://your-mcp-server.herokuapp.com/mcp/`

### Render

1. Connect GitHub repository to Render
2. Render auto-detects `render.yaml` and Dockerfile
3. Deploys automatically

**Your MCP URL**: `https://your-service.onrender.com/mcp/`

### Docker

```bash
docker build -t mcp-simple-server .
docker run -p 8000:8000 mcp-simple-server
```

## Claude Desktop Integration

### Local Server
```json
{
  "mcpServers": {
    "simple-server": {
      "command": "python",
      "args": ["main.py"],
      "cwd": "/path/to/mcp-simple-server"
    }
  }
}
```

### Remote Server (after deployment)
```json
{
  "mcpServers": {
    "simple-server-remote": {
      "command": "curl",
      "args": [
        "-X", "POST",
        "https://your-app.railway.app/mcp/",
        "-H", "Content-Type: application/json",
        "-H", "MCP-Protocol-Version: 2025-06-18",
        "-H", "Accept: application/json, text/event-stream"
      ]
    }
  }
}
```

**Configuration Location:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

## Test with Claude

After integration, ask Claude:
- "Can you add 42 and 18 for me?"
- "What's 7 times 9?"
- "What tools do you have available?"

Claude will use your MCP server to perform calculations! 🎉

## Development

### Adding New Tools

```python
@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract two numbers"""
    return a - b

@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide two numbers"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

### Environment Variables

- `HOST`: Server host (default: 127.0.0.1)
- `PORT`: Server port (default: 8000, set by FastMCP)

```bash
HOST=0.0.0.0 PORT=3000 python main.py
```

Note: FastMCP uses port 8000 by default, but you can override with the PORT environment variable.

## Project Structure

```
mcp-simple-server/
├── main.py              # MCP server (~25 lines)
├── test_server.py       # Automated tests (~300 lines)
├── pyproject.toml       # Project configuration
├── README.md            # This documentation
├── uv.lock              # Dependency lock file
├── Dockerfile           # Docker deployment
├── railway.toml         # Railway configuration
├── Procfile             # Heroku configuration
└── render.yaml          # Render configuration
```

## Architecture

- **FastMCP**: High-level MCP implementation from Anthropic
- **Streamable HTTP**: Modern transport with SSE streaming support
- **Session Management**: Stateful connections with session IDs
- **JSON-RPC 2.0**: Standard protocol for message exchange
- **Protocol 2025-06-18**: Latest MCP specification
- **Port 8000**: Default FastMCP server port (configurable via PORT env var)

## Technical Details

### Server Implementation
- **Framework**: FastMCP (official Anthropic library)
- **Transport**: Streamable HTTP with Server-Sent Events
- **Protocol**: MCP 2025-06-18 specification
- **Dependencies**: `httpx>=0.28.1`, `mcp>=1.9.4`

### MCP Protocol Flow
1. Client sends `initialize` request
2. Server responds with capabilities and session ID
3. Client sends `initialized` notification
4. Normal operations begin (tools/list, tools/call, etc.)

### Tool Response Format
Tools return simple Python values (float, int, str) which FastMCP automatically wraps in the proper MCP response format.

## Troubleshooting

### Server Won't Start
```bash
# Check if port is in use
lsof -i :8000

# Try different port
PORT=3000 python main.py
```

### MCP Protocol Errors
```bash
# Run automated test
python test_server.py

# Check server logs for detailed errors
```

### Claude Desktop Not Connecting
1. Verify JSON configuration syntax
2. Check server URL accessibility
3. Restart Claude Desktop after config changes
4. Ensure proper MCP endpoint path (`/mcp/` with trailing slash)

### Test Remote Deployment
```bash
# Test your deployed server (replace with your URL)
python -c "
import asyncio
from test_server import MCPServerTest

async def test():
    async with MCPServerTest('https://your-app.railway.app') as tester:
        await tester.run_all_tests()

asyncio.run(test())
"
```

### Common Issues
- **Wrong endpoint**: Use `/mcp/` (with trailing slash)
- **Missing headers**: Include all required MCP headers
- **Session management**: Must send `initialized` notification after `initialize`
- **Port confusion**: FastMCP defaults to 8000, not 3000

## Dependencies

```toml
dependencies = [
    "httpx>=0.28.1",   # HTTP client for testing
    "mcp>=1.9.4",      # Official Anthropic MCP library
]
```

The project uses:
- **mcp**: Official Anthropic MCP Python SDK
- **httpx**: Modern HTTP client for automated testing
- **Python**: Requires Python >=3.10

## Contributing

1. Fork the repository
2. Make your changes
3. Run tests: `python test_server.py`
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License

## Resources

- [MCP Specification 2025-06-18](https://modelcontextprotocol.io/specification/2025-06-18/)
- [FastMCP Documentation](https://mcp.so/docs)
- [Claude Desktop](https://claude.ai/download)
- [Railway Deployment](https://railway.app)
- [Render Deployment](https://render.com)