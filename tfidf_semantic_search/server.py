import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .engine import build_index, search

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "docs.json"
WEB_DIR = BASE_DIR / "web"


def load_docs():
    if not DATA_PATH.exists():
        return []
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def save_docs(docs):
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(docs, indent=2), encoding="utf-8")


def seed_docs():
    docs = [
        {
            "id": 1,
            "title": "Retrieval roadmap",
            "body": "Plan vector indexing, hybrid search, and ranking calibration.",
        },
        {
            "id": 2,
            "title": "Model monitoring",
            "body": "Track drift, log metrics, and capture feedback loops.",
        },
        {
            "id": 3,
            "title": "Prompt library",
            "body": "Create reusable prompt patterns for summarization and QA.",
        },
        {
            "id": 4,
            "title": "Evaluation strategy",
            "body": "Define golden sets, automate BLEU and ROUGE scoring.",
        },
        {
            "id": 5,
            "title": "Infra checklist",
            "body": "GPU sizing, caching, and batch inference pipelines.",
        },
        {
            "id": 6,
            "title": "Security review",
            "body": "Threat modeling, prompt injection prevention, and red teaming.",
        },
    ]
    save_docs(docs)
    return docs


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def log_message(self, format, *args):
        return

    def _send_json(self, payload, status=HTTPStatus.OK):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        if not length:
            return {}
        body = self.rfile.read(length)
        return json.loads(body.decode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/docs":
            docs = load_docs()
            self._send_json({"docs": docs})
            return
        if parsed.path.startswith("/api/"):
            self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return
        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/search":
            payload = self._read_json()
            query = payload.get("query", "")
            top_k = int(payload.get("top_k", 5))
            docs = load_docs()
            index = build_index(docs)
            results = search(query, docs, index, top_k=top_k)
            self._send_json({"results": results})
            return
        if parsed.path == "/api/seed":
            docs = seed_docs()
            self._send_json({"count": len(docs)})
            return
        self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)


def run(host="127.0.0.1", port=5173):
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Tfidf Semantic Search running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the Tfidf Semantic Search server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5173)
    args = parser.parse_args()

    run(host=args.host, port=args.port)
