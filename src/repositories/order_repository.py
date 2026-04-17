"""Abstract order repository with domain-specific query methods."""

from abc import abstractmethod
from typing import Any, Dict, List, Optional

from src.models.order_document import OrderDocument
from src.repositories.base_repository import BaseRepository


class OrderRepository(BaseRepository):
    """Extends BaseRepository with order-specific access patterns."""

    @abstractmethod
    async def get_by_order_number(
        self, order_number: int
    ) -> Optional[OrderDocument]:
        """Retrieve an order by its auto-increment business number.

        Args:
            order_number (int): The unique order identifier.

        Returns:
            Optional[OrderDocument]: The order if found, None otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    async def sum_total_price(self, filters: Dict[str, Any]) -> float:
        """Sum the total_price across all matching orders.

        Args:
            filters (Dict[str, Any]): MongoDB match criteria.

        Returns:
            float: The aggregate sum of total_price.
        """
        raise NotImplementedError

    @abstractmethod
    async def aggregate_by_status(self) -> List[Dict[str, Any]]:
        """Count orders grouped by status.

        Returns:
            List[Dict[str, Any]]: List of {status, count} dicts.
        """
        raise NotImplementedError

    @abstractmethod
    async def aggregate_by_hour(
        self, date_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Count orders grouped by hour of creation.

        Args:
            date_filter (Optional[Dict[str, Any]]): Optional date range filter.

        Returns:
            List[Dict[str, Any]]: List of {hour, order_count} dicts.
        """
        raise NotImplementedError

    @abstractmethod
    async def aggregate_top_customers(self, limit: int) -> List[Dict[str, Any]]:
        """Return top customers ranked by total spend.

        Args:
            limit (int): Maximum number of customers to return.

        Returns:
            List[Dict[str, Any]]: List of
                {orderer_name, order_count, total_spent} dicts.
        """
        raise NotImplementedError

    @abstractmethod
    async def aggregate_item_profitability(self) -> List[Dict[str, Any]]:
        """Return all menu items ranked by total revenue generated.

        Returns:
            List[Dict[str, Any]]: List of {name, total_revenue} dicts.
        """
        raise NotImplementedError

    @abstractmethod
    async def count_distinct_order_days(self) -> int:
        """Count the number of distinct calendar days with at least one order.

        Returns:
            int: Number of distinct days that have orders.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_average_items_per_order(self) -> float:
        """Calculate the average number of items across all orders.

        Returns:
            float: Average item count per order, or 0.0 if no orders.
        """
        raise NotImplementedError
