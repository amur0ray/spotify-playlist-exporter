import json
import logging
from pathlib import Path
from typing import Dict, Any
from .base_exporter import BaseExporter

logger = logging.getLogger(__name__)


class JSONExporter(BaseExporter):
    """Exports playlist data to JSON format."""

    def export(self, data: Dict[str, Any], file_path: str) -> None:
        """Export data to a JSON file.
        
        Args:
            data: Dictionary containing playlist data.
            file_path: Path where the JSON file should be written.
            
        Raises:
            ValueError: If data is invalid.
            IOError: If file write fails.
        """
        if not data:
            raise ValueError("Data cannot be empty")
        
        try:
            # Ensure parent directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, indent=4, ensure_ascii=False)
            
            logger.info(f"Successfully exported data to JSON: {file_path}")
        except IOError as e:
            logger.error(f"Failed to write JSON file {file_path}: {e}")
            raise
