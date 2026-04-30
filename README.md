# genai-taskq

`genai-taskq` は、生成 AI ワークロードを「再開可能・監査可能・永続化可能」に運用するためのタスクキューです。  
Task の状態遷移、lease ベースの実行制御、Worker 実行、Provider 抽象化、REST API / CLI / SDK / MCP 連携を 1 つのプロジェクトで提供します。

## Features

- 永続化 Task 管理（create / list / show / cancel）
- 状態遷移管理（`pending` / `scheduled` / `running` / `succeeded` / `failed` / `canceled`）
- idempotency key による重複 submit 防止
- lease ベース dequeue と retry 再投入
- Provider 抽象化（mock / OpenAI 互換 / Anthropic / Ollama / llama.cpp）
- FastAPI / Typer CLI / Python SDK / MCP エンドポイント
- Prometheus metrics エンドポイント（`/metrics`）

## Architecture (high-level)

```text
Client (CLI / SDK / API / MCP)
            |
         FastAPI
            |
  Core (state machine / lease / retry)
            |
 Storage (SQLite / PostgreSQL-ready)
            |
         Worker(s)
            |
        Provider(s)
```

## Requirements

- Python 3.12+
- macOS / Linux

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# DB 初期化
gtq init

# Task 登録
gtq submit "hello from genai-taskq"

# Worker 起動（別ターミナル推奨）
gtq-worker
```

## Run API Server

```bash
source .venv/bin/activate
uvicorn genai_taskq.api.app:app --reload
```

主要エンドポイント:

- `POST /tasks`
- `GET /tasks`
- `GET /tasks/{task_id}`
- `POST /tasks/{task_id}/cancel`
- `GET /tasks/{task_id}/logs`
- `GET /metrics`

## CLI

```bash
gtq init
gtq submit "summarize docs" --provider mock
gtq list
gtq show <task_id>
gtq logs <task_id>
gtq cancel <task_id>
```

## Python SDK

```python
from genai_taskq.sdk import GTQClient

client = GTQClient("http://127.0.0.1:8000")
task = client.submit("write release notes", provider="mock")
print(task["id"])
```

## Development

```bash
source .venv/bin/activate
make ci
```

利用可能な主要コマンド:

- `make lint`
- `make typecheck`
- `make unit`
- `make integration`
- `make e2e`
- `make test`
- `make ci`

## Project Layout

```text
src/genai_taskq/
  api/            FastAPI app
  cli/            Typer CLI
  core/           domain model and state machine
  storage/        SQLAlchemy repository
  worker/         worker runtime
  providers/      provider adapters
  sdk/            sync/async clients
  mcp/            MCP-facing routes
```

## Status

このリポジトリは初期実装フェーズです。  
API/スキーマ/運用ガードレールは継続的に改善されます。
