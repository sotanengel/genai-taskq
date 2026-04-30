# Architecture

- FastAPI が submit/list/get/cancel と metrics を公開する。
- Worker は DB から dequeue して Provider に渡し、結果を保存する。
- Storage は SQLAlchemy により SQLite/PostgreSQL を切替可能にする。
