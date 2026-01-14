# EchoLens

EchoLens is a local semantic search engine for knowledge bases. It builds TF-IDF vectors from notes, scores them with cosine similarity, and serves a clean web UI plus a JSON API.

## Features

- TF-IDF vectorization with cosine similarity
- Local JSON knowledge base
- API for search + document listing
- Lightweight web interface

## Quick start

```bash
python -m app.server --port 5173
```

Open http://localhost:5173

## API

- GET `/api/docs`
- POST `/api/search` `{ "query": "text", "top_k": 5 }`
- POST `/api/seed`

