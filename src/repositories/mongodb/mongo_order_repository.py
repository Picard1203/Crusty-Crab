"""Concrete MongoDB implementation of the order repository."""

import logging
from typing import Any, Dict, List, Optional

from bson import ObjectId

from src.models import OrderDocument
from src.repositories import OrderRepository

logger = logging.getLogger(__name__)


class MongoOrderRepository(OrderRepository):
    """Beanie-based implementation of OrderRepository."""

    async def get_by_id(
        self, entity_id: ObjectId
    ) -> Optional[OrderDocument]:
        """Retrieve an order by MongoDB ObjectId.

        Args:
            entity_id (ObjectId): The MongoDB document ID.

        Returns:
            Optional[OrderDocument]: The order if found, None otherwise.
        """
        logger.debug(f"Fetching order by ObjectId {entity_id}")
        return await OrderDocument.get(entity_id)

    async def get_by_order_number(
        self, order_number: int
    ) -> Optional[OrderDocument]:
        """Retrieve an order by its auto-increment business number.

        Args:
            order_number (int): The unique order identifier.

        Returns:
            Optional[OrderDocument]: The order if found, None otherwise.
        """
        logger.debug(f"Fetching order by order_number {order_number}")
        return await OrderDocument.find_one(
            OrderDocument.order_number == order_number
        )

    async def get_all(
        self, skip: int, limit: int, filters: Dict[str, Any]
    ) -> List[OrderDocument]:
        """Retrieve orders with pagination and filtering.

        Args:
            skip (int): Number of documents to skip.
            limit (int): Maximum number of documents to return.
            filters (Dict[str, Any]): Key-value pairs for query filtering.

        Returns:
            List[OrderDocument]: The matching orders.
        """
        query = self._build_query(filters)
        logger.debug(
            f"Querying orders with filters {filters}, "
            f"skip={skip}, limit={limit}"
        )
        return (
            await OrderDocument.find(query).skip(skip).limit(limit).to_list()
        )

    async def create(self, entity: OrderDocument) -> OrderDocument:
        """Persist a new order document to MongoDB.

        Args:
            entity (OrderDocument): The document to insert.

        Returns:
            OrderDocument: The inserted document with _id populated.
        """
        logger.info(
            f"Creating order with order_number {entity.order_number}"
        )
        await entity.insert()
        return entity

    async def update(
        self, entity_id: ObjectId, data: Dict[str, Any]
    ) -> Optional[OrderDocument]:
        """Update an existing order by ObjectId.

        Args:
            entity_id (ObjectId): The MongoDB document ID.
            data (Dict[str, Any]): Fields to update with their new values.

        Returns:
            Optional[OrderDocument]: The updated order, None if not found.
        """
        logger.info(
            f"Updating order {entity_id} with fields {list(data.keys())}"
        )
        order = await OrderDocument.get(entity_id)
        if order is None:
            return None
        await order.set(data)
        return order

    async def delete(self, entity_id: ObjectId) -> bool:
        """Delete an order by ObjectId.

        Args:
            entity_id (ObjectId): The MongoDB document ID.

        Returns:
            bool: True if deleted, False if not found.
        """
        logger.info(f"Deleting order {entity_id}")
        order = await OrderDocument.get(entity_id)
        if order is None:
            return False
        await order.delete()
        return True

    async def count(self, filters: Dict[str, Any]) -> int:
        """Count orders matching the given filters.

        Args:
            filters (Dict[str, Any]): Key-value pairs for query filtering.

        Returns:
            int: Number of matching orders.
        """
        query = self._build_query(filters)
        return await OrderDocument.find(query).count()

    async def sum_total_price(self, filters: Dict[str, Any]) -> float:
        """Sum total_price across all matching orders using aggregation.

        Args:
            filters (Dict[str, Any]): MongoDB match criteria.

        Returns:
            float: The aggregate sum of total_price.
        """
        pipeline = []
        if filters:
            pipeline.append({"$match": filters})
        pipeline.append(
            {"$group": {"_id": None, "total": {"$sum": "$total_price"}}}
        )
        collection = OrderDocument.get_pymongo_collection()
        results = await collection.aggregate(pipeline).to_list(length=1)
        if len(results) == 0:
            return 0.0
        return results[0].get("total", 0.0)

    async def aggregate_by_status(self) -> List[Dict[str, Any]]:
        """Count orders grouped by lifecycle status.

        Returns:
            List[Dict[str, Any]]: List of {status, count} dicts.
        """
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}},
        ]
        collection = OrderDocument.get_pymongo_collection()
        results = await collection.aggregate(pipeline).to_list(length=None)
        status_breakdown = []
        for result in results:
            status_breakdown.append(
                {"status": result["_id"], "count": result["count"]}
            )
        return status_breakdown

    async def aggregate_by_hour(
        self, date_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Count orders grouped by hour of creation.

        Args:
            date_filter (Optional[Dict[str, Any]]): Optional date range filter
                applied before grouping.

        Returns:
            List[Dict[str, Any]]: List of {hour, order_count} dicts
                sorted by hour.
        """
        pipeline = []
        if date_filter:
            pipeline.append({"$match": date_filter})
        pipeline += [
            {
                "$group": {
                    "_id": {"$hour": "$created_at"},
                    "order_count": {"$sum": 1},
                }
            },
            {"$sort": {"_id": 1}},
        ]
        collection = OrderDocument.get_pymongo_collection()
        results = await collection.aggregate(pipeline).to_list(length=None)
        hourly_breakdown = []
        for result in results:
            hourly_breakdown.append(
                {"hour": result["_id"], "order_count": result["order_count"]}
            )
        return hourly_breakdown

    async def aggregate_top_customers(
        self, limit: int
    ) -> List[Dict[str, Any]]:
        """Return top customers ranked by cumulative spend.

        Args:
            limit (int): Maximum number of customers to return.

        Returns:
            List[Dict[str, Any]]: List of
                {orderer_name, order_count, total_spent} dicts.
        """
        pipeline = [
            {
                "$group": {
                    "_id": "$orderer_name",
                    "order_count": {"$sum": 1},
                    "total_spent": {"$sum": "$total_price"},
                }
            },
            {"$sort": {"total_spent": -1}},
            {"$limit": limit},
        ]
        collection = OrderDocument.get_pymongo_collection()
        results = await collection.aggregate(pipeline).to_list(length=None)
        top_customers = []
        for result in results:
            top_customers.append(
                {
                    "orderer_name": result["_id"],
                    "order_count": result["order_count"],
                    "total_spent": result["total_spent"],
                }
            )
        return top_customers

    async def aggregate_item_profitability(self) -> List[Dict[str, Any]]:
        """Return menu items ranked by total revenue generated.

        Returns:
            List[Dict[str, Any]]: List of {name, total_revenue} dicts
                sorted by total_revenue descending.
        """
        pipeline = [
            {
                "$project": {
                    "zipped": {
                        "$zip": {
                            "inputs": ["$items", "$item_price_snapshot"]
                        }
                    }
                }
            },
            {"$unwind": "$zipped"},
            {
                "$group": {
                    "_id": {"$arrayElemAt": ["$zipped", 0]},
                    "total_revenue": {
                        "$sum": {"$arrayElemAt": ["$zipped", 1]}
                    },
                }
            },
            {"$sort": {"total_revenue": -1}},
        ]
        collection = OrderDocument.get_pymongo_collection()
        results = await collection.aggregate(pipeline).to_list(length=None)
        item_profitability = []
        for result in results:
            item_profitability.append(
                {"name": result["_id"], "total_revenue": result["total_revenue"]}
            )
        return item_profitability

    async def get_average_items_per_order(self) -> float:
        """Calculate the average number of items across all orders.

        Returns:
            float: Average item count per order, or 0.0 if no orders exist.
        """
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_items": {"$sum": {"$size": "$items"}},
                    "total_orders": {"$sum": 1},
                }
            }
        ]
        collection = OrderDocument.get_pymongo_collection()
        results = await collection.aggregate(pipeline).to_list(length=1)
        if len(results) == 0:
            return 0.0
        row = results[0]
        total_orders = row.get("total_orders", 0)
        if total_orders == 0:
            return 0.0
        return row.get("total_items", 0) / total_orders

    async def count_distinct_order_days(self) -> int:
        """Count distinct calendar days that have at least one order.

        Returns:
            int: Number of distinct days with orders.
        """
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$created_at"},
                        "month": {"$month": "$created_at"},
                        "day": {"$dayOfMonth": "$created_at"},
                    }
                }
            },
            {"$count": "distinct_days"},
        ]
        collection = OrderDocument.get_pymongo_collection()
        results = await collection.aggregate(pipeline).to_list(length=1)
        if len(results) == 0:
            return 0
        return results[0].get("distinct_days", 0)

    @staticmethod
    def _build_query(filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build a MongoDB query dict from filter parameters.

        Args:
            filters (Dict[str, Any]): Raw filter key-value pairs.

        Returns:
            Dict[str, Any]: MongoDB-compatible query dictionary.
        """
        query: Dict[str, Any] = {}
        if filters.get("status") is not None:
            query["status"] = filters["status"]
        orderer_name = filters.get("orderer_name")
        if orderer_name is not None:
            query["orderer_name"] = {
                "$regex": orderer_name,
                "$options": "i",
            }
        return query
