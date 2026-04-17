"""Integration tests for MongoCounterRepository."""

import pytest

from src.repositories.mongodb.mongo_counter_repository import (
    MongoCounterRepository,
)


@pytest.mark.asyncio
class TestCounterRepository:
    """Tests for MongoCounterRepository against real MongoDB."""

    async def test_sequence_starts_at_one(self) -> None:
        """First call to get_next_sequence returns 1."""
        repo = MongoCounterRepository()
        value = await repo.get_next_sequence("test_seq")
        assert value == 1

    async def test_sequence_increments(self) -> None:
        """Subsequent calls increment the sequence."""
        repo = MongoCounterRepository()
        first = await repo.get_next_sequence("increment_seq")
        second = await repo.get_next_sequence("increment_seq")
        assert second == first + 1

    async def test_different_sequences_are_independent(self) -> None:
        """Two different sequences are tracked independently."""
        repo = MongoCounterRepository()
        a1 = await repo.get_next_sequence("seq_a")
        b1 = await repo.get_next_sequence("seq_b")
        a2 = await repo.get_next_sequence("seq_a")
        assert a1 == 1
        assert b1 == 1
        assert a2 == 2
