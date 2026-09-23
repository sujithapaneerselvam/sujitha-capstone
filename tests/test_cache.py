from src.rag import cache


def test_cache_round_trip_and_clear(tmp_path):
    db = str(tmp_path / "cache.db")
    vector = [1.0, 0.0, 0.0]

    assert cache.lookup(vector, db_path=db) is None
    assert cache.stats(db)["n_entries"] == 0

    cache.put(
        "How much annual leave is provided?",
        vector,
        "Twenty days.",
        db_path=db,
    )

    hit = cache.lookup(vector, db_path=db)
    assert hit is not None
    assert hit["answer"] == "Twenty days."
    assert hit["similarity"] >= 0.95
    assert cache.stats(db) == {"n_entries": 1, "total_hits": 1}

    assert cache.clear(db) == 1
    assert cache.lookup(vector, db_path=db) is None
    assert cache.stats(db)["n_entries"] == 0


def test_dissimilar_question_is_cache_miss(tmp_path):
    db = str(tmp_path / "cache.db")
    cache.put("Leave policy?", [1.0, 0.0], "Twenty days.", db_path=db)

    assert cache.lookup([0.0, 1.0], db_path=db) is None
    assert cache.stats(db)["total_hits"] == 0