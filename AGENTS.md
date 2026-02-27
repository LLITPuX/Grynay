# AGENTS.md

## Cursor Cloud specific instructions

### Overview

Grynya is an AI agent orchestration platform with graph-based long-term memory. It consists of Docker-containerized microservices orchestrated via `falkordb-service/docker-compose.yml`.

### Services

| Service | Container | Port | Description |
|---|---|---|---|
| FalkorDB | `falkordb` | 6379, 3000 (UI) | Graph database (Redis-compatible). Core data store. |
| MCP Server | `grynya-mcp-server` | 8000 | FastAPI + MCP server exposing graph CRUD tools via SSE. |
| LLM Provider | `llm-provider-mcp` | 8001 | MCP server proxying LLM calls (Gemini/OpenAI). Optional — needs API keys. |

### Starting services

```bash
cd /workspace/falkordb-service
# Core (required):
docker compose up -d --build falkordb mcp_server
# Optional (needs OPENAI_API_KEY or Gemini credentials):
docker compose up -d --build llm_provider_mcp
```

### Verifying services

- FalkorDB: `docker exec falkordb redis-cli PING` → `PONG`
- MCP Server health: `curl -s http://localhost:8000/health` → `{"status":"ok","falkordb_connected":true}`
- FalkorDB Browser UI: `http://localhost:3000`
- MCP SSE endpoint: `http://localhost:8000/sse`
- LLM Provider SSE: `http://localhost:8001/sse`

### Docker in Cloud VM (gotcha)

Docker must be started manually: `sudo dockerd &>/tmp/dockerd.log &` (wait ~5s). The VM uses `fuse-overlayfs` storage driver and `iptables-legacy` due to nested container constraints (Docker-in-Docker inside Firecracker VM).

### No linting or automated test suite

This project has no `pyproject.toml`, no linter config, and no formal test framework. The `llm_provider_mcp/src/test_*.py` files are manual integration test scripts, not pytest-based automated tests. Validation is done via running the services and querying the MCP tools.

### Interacting with MCP tools from Python

Install the MCP client library (`pip install mcp httpx-sse`) and use `mcp.client.sse.sse_client` + `mcp.client.session.ClientSession` to connect to `http://localhost:8000/sse`. Available tools: `query_graph`, `create_session`, `add_node`, `link_nodes`, `update_last_event`, `batch_add_nodes`, `batch_link_nodes`, `delete_node`, `delete_link`.

### docker-compose.yml `version` key

The `version: '3.8'` key in `docker-compose.yml` is obsolete and triggers a warning. It is harmless and can be ignored.
