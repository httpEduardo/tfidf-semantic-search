import math
import re
from collections import Counter

TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text):
    return TOKEN_RE.findall(text.lower())


def build_index(docs):
    doc_tokens = [tokenize(doc["body"]) for doc in docs]
    doc_freq = Counter()
    for tokens in doc_tokens:
        doc_freq.update(set(tokens))

    total_docs = len(docs)
    idf = {term: math.log((1 + total_docs) / (1 + freq)) + 1 for term, freq in doc_freq.items()}

    vectors = []
    norms = []
    for tokens in doc_tokens:
        tf = Counter(tokens)
        vec = {term: (tf[term] / len(tokens)) * idf.get(term, 0.0) for term in tf}
        norm = math.sqrt(sum(value * value for value in vec.values()))
        vectors.append(vec)
        norms.append(norm)

    return {"idf": idf, "vectors": vectors, "norms": norms}


def _vectorize_query(query, idf):
    tokens = tokenize(query)
    if not tokens:
        return {}, 0.0
    tf = Counter(tokens)
    vec = {term: (tf[term] / len(tokens)) * idf.get(term, 0.0) for term in tf}
    norm = math.sqrt(sum(value * value for value in vec.values()))
    return vec, norm


def search(query, docs, index, top_k=5):
    query_vec, query_norm = _vectorize_query(query, index["idf"])
    if not query_vec or query_norm == 0.0:
        return []

    results = []
    for doc, doc_vec, doc_norm in zip(docs, index["vectors"], index["norms"]):
        if doc_norm == 0.0:
            continue
        dot = sum(query_vec.get(term, 0.0) * doc_vec.get(term, 0.0) for term in query_vec)
        score = dot / (query_norm * doc_norm)
        if score > 0:
            results.append({"id": doc["id"], "title": doc["title"], "score": round(score, 4)})

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]
