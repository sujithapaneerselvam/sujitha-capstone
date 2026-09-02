"""Local embeddings using all-MiniLM-L6-v2."""

_model = None


def _get_model():
    global _model

    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("all-MiniLM-L6-v2")

    return _model


def embed_local(texts: list[str]) -> list[list[float]]:
    """Return one normalized, 384-dimensional vector per text."""
    vectors = _get_model().encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    return vectors.tolist()