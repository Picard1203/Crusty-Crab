"""Abstract counter repository — interface for auto-increment ID generation."""

from abc import ABC, abstractmethod


class CounterRepository(ABC):
    """Generates auto-increment business IDs via atomic sequences."""

    @abstractmethod
    async def get_next_sequence(self, sequence_name: str) -> int:
        """Atomically increment and return the next value in a named sequence.

        Args:
            sequence_name (str): The sequence identifier
                (e.g., 'order_number', 'menu_item_number').

        Returns:
            int: The next unique value in the sequence.
        """
        raise NotImplementedError
