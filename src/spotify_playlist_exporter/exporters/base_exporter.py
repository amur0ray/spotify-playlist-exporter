from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseExporter(ABC):
    """Abstract base class for data exporters."""

    @abstractmethod
    def export(self, data: Dict[str, Any], file_path: str) -> None:
        """Export data to a file.
        
        Args:
            data: Dictionary containing playlist data with 'name', 'description', and 'tracks'.
            file_path: Path where the file should be written.
        """
        pass
