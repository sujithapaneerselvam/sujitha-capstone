"""api/main.py — REFERENCE for Week 3 Lab Step 1.

The completed version. Wraps the W2 async pipeline behind a stable HTTP
contract (Question/Answer with field names question/content) while delegating
to the W2 pipeline internally.

Run with:
    uvicorn api.main:app --reload --port 8000

Hit with curl:
    curl -X POST http://localhost:8000/ask_batched \
         -H "Content-Type: application/json" \
         -d '{"question": "What is RAG?"}'
"""
import asyncio
import logging

from fastapi import FastAPI,Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# W2 pipeline — the underlying engine
from src.pipeline.pipeline import ask_llm as _pipeline_ask_llm
from src.pipeline.pipeline import stream_answer as _pipeline_stream
from src.pipeline.pipeline import Question as _PipelineQuestion
from dotenv import load_dotenv
from src.rag.qdrant_store import load_store,collection_size
from src.rag.qdrant_rag import retrieve
import os

load_dotenv(
    "/voc/work/Demo Files/AI-RAG_W7_TrackAB_Bundle/.env"
)

_RAG_STORE = load_store()
point_count = collection_size(_RAG_STORE)
if point_count == 0:
    raise RuntimeError("qdrant collection is empty. Run the migration first.")
print(f"Qdrant collection loaded: {point_count} points")
# # W6: naive RAG retrieval. Load the index once at startup; if it's missing
# # (not built yet), fall back to answering from training data.
# try:
#     from src.rag.naive_rag import load_index, retrieve
#     RAG_INDEX_PATH = os.getenv("RAG_INDEX_PATH","data/embeddings_small.json")
#    # _RAG_INDEX = load_index(RAG_INDEX_PATH)--PART of week6
#     #print(f"Loaded {len(_RAG_INDEX)} chunks")
#    # logging.getLogger(__name__).info("RAG index loaded: %d chunks", len(_RAG_INDEX))
# except (FileNotFoundError, ImportError) as error:  # index not built yet -> app still works, just ungrounded
#     print(f"RAG index unavailable: {error}")
#     #_RAG_INDEX = None

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger(__name__)



# ─────────────────────────────────────────────────────────────────────────────
# Public W3 API models — locked in ADR 0002
# These are intentionally separate from the W2 internal models (which use
# `text` field names). The endpoint handlers translate between the two.
# ─────────────────────────────────────────────────────────────────────────────
class Question(BaseModel):
    """Public request shape — locked in ADR 0002."""
    question: str


class Answer(BaseModel):
    """Public response shape — locked in ADR 0002 (grown additively in W4)."""
    content: str
    cost_usd: float
    retries: int
    confidence: float = 1.0
    sources: list[str] = []


app = FastAPI(
    title="Capstone API",
    description="Wraps the W2 async pipeline. Contract locked in ADR 0002 (W3); internals upgraded W4+.",
    version="1.0.0",
)

request_counts:dict[str,int] = {}

@app.middleware("http")
async def count_requests(request: Request, call_next):
    path = request.url.path
    request_counts[path] = request_counts.get(path, 0) + 1
    response = await call_next(request)
    return response

# ─────────────────────────────────────────────────────────────────────────────
# /ask_batched — non-streaming reference endpoint
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/ask_batched", response_model=Answer)
async def ask_batched(q: Question) -> Answer:
    """Non-streaming. Returns the full Answer in a single JSON body."""
    log.info("ask_batched  question=%r", q.question[:80])
    pipeline_q = _PipelineQuestion(text=q.question)

    # context, sources = None, None
    # if _RAG_INDEX:                                    # W6: retrieve before answering
    #     hits = retrieve(q.question, _RAG_INDEX, k=3)
    #     context = "\n\n".join(f"[{h['chunk_id']}]\n{h['text']}" for h in hits)
    #     sources = [h["chunk_id"] for h in hits]
    hits = await asyncio.to_thread(
        retrieve,_RAG_STORE,q.question,k=10,
    )
    context = "\n\n".join(f"[{hit['chunk_id']}]\n{hit['text']}" for hit in hits)
    sources = [hit["chunk_id"] for hit in hits]
    pipeline_ans = await _pipeline_ask_llm(pipeline_q, context=context, sources=sources)
    return Answer(
        content=pipeline_ans.text,
        cost_usd=pipeline_ans.cost_usd,
        retries=pipeline_ans.retries,
        confidence=pipeline_ans.confidence,
        sources=pipeline_ans.sources,
    )


# ─────────────────────────────────────────────────────────────────────────────
# /health — liveness probe
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok"}


# ─────────────────────────────────────────────────────────────────────────────
# /ask — streaming endpoint (the contracted one)
# ─────────────────────────────────────────────────────────────────────────────
async def stream_answer(question_text: str):
    """Async generator yielding the answer word-by-word.

    W3 streams from FastAPI to the client; the pipeline call itself is still
    non-streaming. In W4 the LLM call becomes a real stream end-to-end — this
    generator's shape doesn't change, only what fills it.
    """
    pipeline_q = _PipelineQuestion(text=question_text)
    pipeline_ans = await _pipeline_ask_llm(pipeline_q)
    for word in pipeline_ans.text.split(" "):
        yield word + " "
        await asyncio.sleep(0.05)


@app.post("/ask")
async def ask(q: Question):
    """Streaming /ask — now backed by the pipeline's REAL token stream (W4)."""
    log.info("ask  question=%r", q.question[:80])
    return StreamingResponse(
        _pipeline_stream(q.question),
        media_type="text/plain",
    )



@app.get("/metrics")
async def metrics():
    return {
        "endpoints": request_counts,
        "total": sum(request_counts.values()),
    }