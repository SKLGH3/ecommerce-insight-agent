from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.repositories.es.value_es_repository import ValueESRepository


@pytest.mark.asyncio
async def test_ensure_index_uses_single_node_replica_setting():
    indices = SimpleNamespace(
        exists=AsyncMock(return_value=False),
        create=AsyncMock(),
    )
    repository = ValueESRepository(SimpleNamespace(indices=indices))

    await repository.ensure_index()

    indices.create.assert_awaited_once_with(
        index="value_index",
        mappings=repository.index_mappings,
        settings={"number_of_replicas": 0},
    )


@pytest.mark.asyncio
async def test_ensure_index_does_not_recreate_existing_index():
    indices = SimpleNamespace(
        exists=AsyncMock(return_value=True),
        create=AsyncMock(),
    )
    repository = ValueESRepository(SimpleNamespace(indices=indices))

    await repository.ensure_index()

    indices.create.assert_not_awaited()
