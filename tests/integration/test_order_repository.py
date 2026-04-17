"""Integration tests for MongoOrderRepository."""

from datetime import datetime, timezone

import pytest

from src.enums import OrderStatus
from src.models.order_document import OrderDocument
from src.repositories.mongodb.mongo_order_repository import (
    MongoOrderRepository,
)


async def _insert_order(
    repo: MongoOrderRepository,
    order_number: int = 1,
    orderer_name: str = "testuser",
    items: list | None = None,
    prices: list | None = None,
    status: OrderStatus = OrderStatus.ORDER_RECEIVED,
) -> OrderDocument:
    """Insert an order document directly into the repository.

    Args:
        repo (MongoOrderRepository): The repository.
        order_number (int): The order number.
        orderer_name (str): The username who placed the order.
        items (list): Item names.
        prices (list): Price snapshot.
        status (OrderStatus): The order status.

    Returns:
        OrderDocument: The inserted document.
    """
    if items is None:
        items = ["Schnitzel Alef"]
    if prices is None:
        prices = [66.0]
    total = sum(prices)
    now = datetime.now(timezone.utc)
    order = OrderDocument(
        order_number=order_number,
        orderer_name=orderer_name,
        items=items,
        item_price_snapshot=prices,
        total_price=total,
        status=status,
        created_at=now,
        updated_at=now,
    )
    return await repo.create(order)


@pytest.mark.asyncio
class TestOrderRepository:
    """Tests for MongoOrderRepository against real MongoDB."""

    async def test_create_and_get_by_id(self) -> None:
        """Created order is retrievable by ObjectId."""
        repo = MongoOrderRepository()
        order = await _insert_order(repo)
        found = await repo.get_by_id(order.id)
        assert found is not None
        assert found.order_number == 1

    async def test_get_by_order_number(self) -> None:
        """Order is retrievable by business order number."""
        repo = MongoOrderRepository()
        await _insert_order(repo, order_number=42)
        found = await repo.get_by_order_number(42)
        assert found is not None
        assert found.order_number == 42

    async def test_get_all_with_pagination(self) -> None:
        """Pagination limits results correctly."""
        repo = MongoOrderRepository()
        for i in range(5):
            await _insert_order(repo, order_number=i + 1)
        page = await repo.get_all(skip=0, limit=2, filters={})
        assert len(page) == 2

    async def test_get_all_with_status_filter(self) -> None:
        """Status filter returns matching orders."""
        repo = MongoOrderRepository()
        await _insert_order(
            repo, order_number=1, status=OrderStatus.ORDER_RECEIVED
        )
        await _insert_order(
            repo, order_number=2, status=OrderStatus.ORDER_CONFIRMED
        )
        results = await repo.get_all(
            0, 10, {"status": OrderStatus.ORDER_CONFIRMED}
        )
        assert len(results) == 1
        assert results[0].status == OrderStatus.ORDER_CONFIRMED

    async def test_get_all_with_orderer_filter(self) -> None:
        """Orderer name filter returns matching orders."""
        repo = MongoOrderRepository()
        await _insert_order(repo, order_number=1, orderer_name="alice")
        await _insert_order(repo, order_number=2, orderer_name="bob")
        results = await repo.get_all(0, 10, {"orderer_name": "alice"})
        assert len(results) == 1
        assert results[0].orderer_name == "alice"

    async def test_update(self) -> None:
        """Update modifies the specified fields."""
        repo = MongoOrderRepository()
        order = await _insert_order(repo)
        updated = await repo.update(
            order.id, {"status": OrderStatus.ORDER_CONFIRMED}
        )
        assert updated is not None
        assert updated.status == OrderStatus.ORDER_CONFIRMED

    async def test_delete(self) -> None:
        """Delete removes the order."""
        repo = MongoOrderRepository()
        order = await _insert_order(repo)
        result = await repo.delete(order.id)
        assert result is True
        found = await repo.get_by_id(order.id)
        assert found is None

    async def test_sum_total_price(self) -> None:
        """sum_total_price aggregates correctly."""
        repo = MongoOrderRepository()
        await _insert_order(repo, order_number=1, prices=[66.0, 42.0])
        await _insert_order(
            repo, order_number=2, items=["Yellow Rice"], prices=[18.0]
        )
        total = await repo.sum_total_price({})
        assert total == pytest.approx(126.0)

    async def test_aggregate_by_status(self) -> None:
        """aggregate_by_status groups orders by their status."""
        repo = MongoOrderRepository()
        await _insert_order(
            repo, order_number=1, status=OrderStatus.ORDER_RECEIVED
        )
        await _insert_order(
            repo, order_number=2, status=OrderStatus.ORDER_RECEIVED
        )
        await _insert_order(
            repo, order_number=3, status=OrderStatus.ORDER_CONFIRMED
        )
        results = await repo.aggregate_by_status()
        counts = {r["status"]: r["count"] for r in results}
        assert counts[OrderStatus.ORDER_RECEIVED] == 2
        assert counts[OrderStatus.ORDER_CONFIRMED] == 1

    async def test_count(self) -> None:
        """Count returns correct number of orders."""
        repo = MongoOrderRepository()
        for i in range(3):
            await _insert_order(repo, order_number=i + 1)
        assert await repo.count({}) == 3
