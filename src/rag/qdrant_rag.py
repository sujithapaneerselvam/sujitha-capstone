"""Qdrant-backed RAG for the capstone — W7 upgrade of W6's naive_rag.

Same public interface as W6's ask_rag: (question, store, k) → dict.
Storage layer swapped from JSON+numpy to Qdrant.
"""
from __future__ import annotations

from typing import Any

from openai import OpenAI
from pathlib import Path
from src.pipeline.settings import Settings
from src.rag.qdrant_store import QdrantStore, load_store
from src.rag.qdrant_store import _get_client
from src.rag import cache
from pathlib import Path
from dotenv import load_dotenv
from qdrant_client.models import Filter, IsEmptyCondition, PayloadField

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=True)

CHAT_MODEL = "gpt-4o-mini"
EMBED_MODEL = "text-embedding-3-small"
# EMBED_MODEL = "text-embedding-3-large"
_client = None
def _openai() -> OpenAI:
    """Lazy-init the OpenAI client (unit tests can import without a key)."""
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def embed_query(text: str) -> list[float]:
    """Single-string embedding. Used at query time."""
    resp = _openai().embeddings.create(model=EMBED_MODEL, input=[text])
    return resp.data[0].embedding


def retrieve(
    store: QdrantStore,
    query: str,
    k: int = 10,
    include_deleted: bool = False,
) -> list[dict[str, Any]]:
    q_vec = embed_query(query)

    live_filter = Filter(
        must=[
            IsEmptyCondition(
                is_empty=PayloadField(key="deleted_at")
            )
        ]
    )

    results = store.client.query_points(
        collection_name=store.collection,
        query=q_vec,
        query_filter=None if include_deleted else live_filter,
        limit=k,
    ).points

    return [
        {
            "chunk_id": hit.payload["chunk_id"],
            "source_id": (
                hit.payload.get("source_id")
                or Path(hit.payload.get("source", "unknown")).stem
            ),
            "text": hit.payload["text"],
            "score": hit.score,
        }
        for hit in results
    ]


SYSTEM = (
    "You are a helpful assistant. Answer the user's question using ONLY the "
    "provided context. If the context does not contain the answer, say so "
    "plainly. Cite the source_id in square brackets after any fact you use."
)

def ask_rag(
    question: str,
    store: QdrantStore | None = None,
    settings: Settings | None = None,
    k: int = 3,
    cache_threshold: float = 0.95,
    use_cache: bool = True,
) -> dict[str, Any]:
    """Cache-first RAG pipeline.

    Flow:
    1. Embed the question.
    2. Return a semantic-cache answer when similarity >= threshold.
    3. Otherwise retrieve live chunks, call the LLM, and cache the answer.
    """
    if store is None:
        store = load_store()

    client = _openai()
    question_embedding = None

    # Layer 1: semantic cache
    if use_cache:
        question_embedding = client.embeddings.create(
            model="text-embedding-3-small",
            input=[question],
        ).data[0].embedding

        hit = cache.lookup(
            question_embedding,
            threshold=cache_threshold,
        )

        if hit:
            return {
                "answer": hit["answer"],
                "sources": [],
                "chunk_ids": [],
                "tokens_in": 0,
                "tokens_out": 0,
                "n_input_tokens": 0,
                "n_output_tokens": 0,
                "n_cached_input_tokens": 0,
                "cache_hit": True,
                "similarity": hit["similarity"],
                "matched": hit["matched_question"],
            }

    # Cache miss: execute the existing RAG pipeline
    retrieved = retrieve(store, question, k=k)

    context = "\n\n".join(
        f"[{hit['chunk_id']}] (source: {hit['source_id']})\n{hit['text']}"
        for hit in retrieved
    )

    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0.0,
        messages=[
            {
                "role": "system",
                "content": SYSTEM,
            },
            {
                "role": "user",
                "content": (
                    f"Context:\n{context}\n\n"
                    f"---\n\n"
                    f"Question: {question}"
                ),
            },
        ],
    )

    answer = resp.choices[0].message.content or ""

    prompt_details = getattr(
        resp.usage,
        "prompt_tokens_details",
        None,
    )
    cached_input_tokens = (
        getattr(prompt_details, "cached_tokens", 0)
        if prompt_details
        else 0
    )

    # Store fresh answer for the next semantically similar question
    if use_cache:
        if question_embedding is None:
            question_embedding = client.embeddings.create(
                model="text-embedding-3-small",
                input=[question],
            ).data[0].embedding

        cache.put(
            question=question,
            embedding=question_embedding,
            answer=answer,
        )

    return {
        "answer": answer,
        "sources": [hit["source_id"] for hit in retrieved],
        "chunk_ids": [hit["chunk_id"] for hit in retrieved],
        "tokens_in": resp.usage.prompt_tokens,
        "tokens_out": resp.usage.completion_tokens,
        "n_input_tokens": resp.usage.prompt_tokens,
        "n_output_tokens": resp.usage.completion_tokens,
        "n_cached_input_tokens": cached_input_tokens,
        "cache_hit": False,
        "similarity": None,
        "matched": None,
        "retrieved": retrieved,
    }
# def load_store():
#     """Load a store pointing at the v2 collection."""
#     from src.rag.qdrant_store import QdrantStore
#     return QdrantStore(client=_get_client(), collection="capstone_chunks_v2")