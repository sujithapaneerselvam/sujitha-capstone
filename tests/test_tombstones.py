from types import SimpleNamespace
from unittest.mock import MagicMock

from qdrant_client.models import IsEmptyCondition

from src.pipeline.pipeline import tombstone_source


def test_tombstone_source_filters_live_points_and_preserves_collection():
    client = MagicMock()
    client.count.return_value.count = 26
    store = SimpleNamespace(
        client=client,
        collection="capstone_chunks_v2",
    )

    result = tombstone_source(
        store,
        "HR_02_Annual_Leave_Policy.txt",
    )

    assert result == 26

    count_kwargs = client.count.call_args.kwargs
    assert count_kwargs["collection_name"] == "capstone_chunks_v2"
    assert count_kwargs["exact"] is True

    conditions = count_kwargs["count_filter"].must
    assert any(
        isinstance(condition, IsEmptyCondition)
        and condition.is_empty.key == "deleted_at"
        for condition in conditions
    )

    update_kwargs = client.set_payload.call_args.kwargs
    assert update_kwargs["collection_name"] == "capstone_chunks_v2"
    assert update_kwargs["wait"] is True
    assert isinstance(update_kwargs["payload"]["deleted_at"], float)
    assert update_kwargs["points"] == count_kwargs["count_filter"]