import csv
import logging
from pathlib import Path
from typing import Dict, Any
from .base_exporter import BaseExporter

logger = logging.getLogger(__name__)


class CSVExporter(BaseExporter):
    """Exports playlist data to CSV format."""

    def export(self, data: Dict[str, Any], file_path: str) -> None:
        """Export data to a CSV file.
        
        Args:
            data: Dictionary containing playlist data with 'tracks' list.
            file_path: Path where the CSV file should be written.
            
        Raises:
            ValueError: If data structure is invalid.
            IOError: If file write fails.
        """
        if not data or "tracks" not in data:
            raise ValueError("Data must contain 'tracks' key")
        
        tracks = data.get("tracks", [])
        if not tracks:
            logger.warning("No tracks to export")
        
        try:
            # Ensure parent directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Track Title', 'Artist', 'Album', 'Duration (ms)'])
                
                for track in tracks:
                    writer.writerow([
                        track.get('title', 'Unknown'),
                        track.get('artist', 'Unknown'),
                        track.get('album', 'Unknown'),
                        track.get('duration', 0)
                    ])
            
            logger.info(f"Successfully exported {len(tracks)} tracks to CSV: {file_path}")
        except IOError as e:
            logger.error(f"Failed to write CSV file {file_path}: {e}")
            raise
