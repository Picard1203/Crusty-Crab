"""Concrete MongoDB implementation of the counter repository."""

import logging

from pymongo import ReturnDocument

from src.models import CounterDocument
from src.repositories import CounterRepository

logger = logging.getLogger(__name__)


class MongoCounterRepository(CounterRepository):
    """MongoDB implementation using atomic find_one_and_update with $inc."""

    async def get_next_sequence(self, sequence_name: str) -> int:
        """Atomically increment and return the next sequence value.

        Args:
            sequence_name (str): The sequence identifier
                (e.g., 'order_number', 'menu_item_number').

        Returns:
            int: The next unique value in the sequence.
        """
        collection = CounterDocument.get_pymongo_collection()
        result = await collection.find_one_and_update(
            {"_id": sequence_name},
            {"$inc": {"sequence_value": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        next_value = result["sequence_value"]
        logger.info(
            f"Generated next sequence for {sequence_name}: {next_value}"
        )
        return next_value
