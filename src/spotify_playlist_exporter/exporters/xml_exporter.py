import xml.etree.ElementTree as ET
import logging
from pathlib import Path
from typing import Dict, Any
from .base_exporter import BaseExporter

logger = logging.getLogger(__name__)


class XMLExporter(BaseExporter):
    """Exports playlist data to XML format."""

    def export(self, data: Dict[str, Any], file_path: str) -> None:
        """Export data to an XML file.
        
        Args:
            data: Dictionary containing playlist data with 'name', 'description', and 'tracks'.
            file_path: Path where the XML file should be written.
            
        Raises:
            ValueError: If data structure is invalid.
            IOError: If file write fails.
        """
        if not data:
            raise ValueError("Data cannot be empty")
        
        if "tracks" not in data:
            raise ValueError("Data must contain 'tracks' key")
        
        try:
            # Ensure parent directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            root = ET.Element("playlist")
            root.set("name", str(data.get('name', 'Untitled')))
            root.set("description", str(data.get('description', '')))
            
            tracks_element = ET.SubElement(root, "tracks")
            for track in data.get('tracks', []):
                track_element = ET.SubElement(tracks_element, "track")
                ET.SubElement(track_element, "title").text = str(track.get('title', 'Unknown'))
                ET.SubElement(track_element, "artist").text = str(track.get('artist', 'Unknown'))
                ET.SubElement(track_element, "album").text = str(track.get('album', 'Unknown'))
                ET.SubElement(track_element, "duration").text = str(track.get('duration', 0))
            
            tree = ET.ElementTree(root)
            tree.write(file_path, encoding='utf-8', xml_declaration=True)
            
            logger.info(f"Successfully exported {len(data.get('tracks', []))} tracks to XML: {file_path}")
        except IOError as e:
            logger.error(f"Failed to write XML file {file_path}: {e}")
            raise
