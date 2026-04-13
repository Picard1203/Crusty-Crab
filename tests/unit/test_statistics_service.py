"""Unit tests for StatisticsService."""

from unittest.mock import AsyncMock

import pytest

from src.enums import OrderStatus
from src.services.statistics_service import StatisticsService


@pytest.mark.asyncio
class TestGetTotalProfits:
    """Tests for StatisticsService.get_total_profits."""

    async def test_returns_zero_when_no_orders(
        self,
        mock_order_repo: AsyncMock,
        mock_menu_item_repo: AsyncMock,
    ) -> None:
        """Returns 0.0 when there are no orders.

        Args:
            mock_order_repo (AsyncMock): Mocked order repository.
            mock_menu_item_repo (AsyncMock): Mocked menu item repository.
        """
        mock_order_repo.sum_total_price.return_value = 0.0
        service = StatisticsService(mock_order_repo, mock_menu_item_repo)
        result = await service.get_total_profits()
        assert result.value == 0.0

    async def test_returns_correct_total(
        self,
        mock_order_repo: AsyncMock,
        mock_menu_item_repo: AsyncMock,
    ) -> None:
        """Returns the correct summed total.

        Args:
            mock_order_repo (AsyncMock): Mocked order repository.
            mock_menu_item_repo (AsyncMock): Mocked menu item repository.
        """
        mock_order_repo.sum_total_price.return_value = 150.0
        service = StatisticsService(mock_order_repo, mock_menu_item_repo)
        result = await service.get_total_profits()
        assert result.value == 150.0


@pytest.mark.asyncio
class TestGetDailyAverage:
    """Tests for StatisticsService.get_daily_average_profits."""

    async def test_returns_zero_average_when_no_orders(
        self,
        mock_order_repo: AsyncMock,
        mock_menu_item_repo: AsyncMock,
    ) -> None:
        """Returns 0.0 average when no orders or days exist.

        Args:
            mock_order_repo (AsyncMock): Mocked order repository.
            mock_menu_item_repo (AsyncMock): Mocked menu item repository.
        """
        mock_order_repo.sum_total_price.return_value = 0.0
        mock_order_repo.count_distinct_order_days.return_value = 0
        service = StatisticsService(mock_order_repo, mock_menu_item_repo)
        result = await service.get_daily_average_profits()
        assert result.total == 0.0
        assert result.daily_average == 0.0

    async def test_calculates_average_correctly(
        self,
        mock_order_repo: AsyncMock,
        mock_menu_item_repo: AsyncMock,
    ) -> None:
        """Correctly divides total by distinct days.

        Args:
            mock_order_repo (AsyncMock): Mocked order repository.
            mock_menu_item_repo (AsyncMock): Mocked menu item repository.
        """
        mock_order_repo.sum_total_price.return_value = 300.0
        mock_order_repo.count_distinct_order_days.return_value = 3
        service = StatisticsService(mock_order_repo, mock_menu_item_repo)
        result = await service.get_daily_average_profits()
        assert result.total == 300.0
        assert result.daily_average == 100.0


@pytest.mark.asyncio
class TestGetOrdersByStatus:
    """Tests for StatisticsService.get_orders_by_status."""

    async def test_returns_status_breakdown(
        self,
        mock_order_repo: AsyncMock,
        mock_menu_item_repo: AsyncMock,
    ) -> None:
        """Returns per-status order counts.

        Args:
            mock_order_repo (AsyncMock): Mocked order repository.
            mock_menu_item_repo (AsyncMock): Mocked menu item repository.
        """
        mock_order_repo.aggregate_by_status.return_value = [
            {"status": OrderStatus.ORDER_RECEIVED, "count": 5},
            {"status": OrderStatus.ORDER_CONFIRMED, "count": 3},
        ]
        service = StatisticsService(mock_order_repo, mock_menu_item_repo)
        results = await service.get_orders_by_status()
        assert len(results) == 2
        assert results[0].count == 5

    async def test_returns_empty_list_when_no_orders(
        self,
        mock_order_repo: AsyncMock,
        mock_menu_item_repo: AsyncMock,
    ) -> None:
        """Returns empty list when no orders exist.

        Args:
            mock_order_repo (AsyncMock): Mocked order repository.
            mock_menu_item_repo (AsyncMock): Mocked menu item repository.
        """
        mock_order_repo.aggregate_by_status.return_value = []
        service = StatisticsService(mock_order_repo, mock_menu_item_repo)
        results = await service.get_orders_by_status()
        assert results == []


@pytest.mark.asyncio
class TestGetMostProfitableItem:
    """Tests for StatisticsService.get_most_profitable_item."""

    async def test_returns_na_when_no_orders(
        self,
        mock_order_repo: AsyncMock,
        mock_menu_item_repo: AsyncMock,
    ) -> None:
        """Returns N/A label when no orders exist.

        Args:
            mock_order_repo (AsyncMock): Mocked order repository.
            mock_menu_item_repo (AsyncMock): Mocked menu item repository.
        """
        mock_order_repo.aggregate_item_profitability.return_value = []
        service = StatisticsService(mock_order_repo, mock_menu_item_repo)
        result = await service.get_most_profitable_item()
        assert result.label == "N/A"
        assert result.value == 0.0

    async def test_returns_highest_revenue_item(
        self,
        mock_order_repo: AsyncMock,
        mock_menu_item_repo: AsyncMock,
    ) -> None:
        """Returns the item with the highest total revenue.

        Args:
            mock_order_repo (AsyncMock): Mocked order repository.
            mock_menu_item_repo (AsyncMock): Mocked menu item repository.
        """
        mock_order_repo.aggregate_item_profitability.return_value = [
            {"name": "Schnitzel Alef", "total_revenue": 660.0},
            {"name": "Lazanja", "total_revenue": 252.0},
        ]
        service = StatisticsService(mock_order_repo, mock_menu_item_repo)
        result = await service.get_most_profitable_item()
        assert result.label == "Schnitzel Alef"
        assert result.value == 660.0
