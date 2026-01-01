import logging
import argparse
import re
from pathlib import Path
from .spotify_client import SpotifyClient, SpotifyAuthenticationError, SpotifyAPIError
from .exporters.json_exporter import JSONExporter
from .exporters.csv_exporter import CSVExporter
from .exporters.xml_exporter import XMLExporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Exporter mapping
EXPORTERS = {
    'json': JSONExporter,
    'csv': CSVExporter,
    'xml': XMLExporter,
}


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and invalid characters.
    
    Args:
        filename: The filename to sanitize.
        
    Returns:
        Sanitized filename.
    """
    # Remove path separators and traversal attempts
    filename = filename.replace('/', '').replace('\\', '').replace('..', '')
    # Remove invalid characters but keep basic ones
    filename = re.sub(r'[<>:"|?*]', '', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    return filename or 'playlist'


def parse_arguments():
    """Parse command-line arguments.
    
    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description='Export Spotify playlists to various file formats.'
    )
    parser.add_argument(
        'playlist_id',
        help='Spotify playlist ID to export'
    )
    parser.add_argument(
        '-f', '--format',
        default='json',
        choices=list(EXPORTERS.keys()),
        help='Export format (default: json)'
    )
    parser.add_argument(
        '-o', '--output',
        default='.',
        help='Output directory (default: current directory)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    return parser.parse_args()


def main():
    """Main entry point for the playlist exporter."""
    try:
        args = parse_arguments()
        
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        logger.info("Starting Spotify Playlist Exporter")
        
        # Initialize Spotify client
        logger.debug("Initializing Spotify client...")
        client = SpotifyClient()
        
        # Authenticate with Spotify
        logger.info("Authenticating with Spotify...")
        client.authenticate()
        logger.info("Authentication successful!")
        
        # Retrieve the playlist
        logger.info(f"Fetching playlist {args.playlist_id}...")
        playlist = client.get_playlist(args.playlist_id)
        logger.info(f"Successfully fetched playlist: {playlist.name}")
        
        # Prepare data for export
        data = {
            "name": playlist.name,
            "description": playlist.description,
            "tracks": [track.to_dict() for track in playlist.tracks]
        }
        
        # Create exporter instance
        exporter_class = EXPORTERS[args.format]
        exporter = exporter_class()
        logger.debug(f"Using {exporter_class.__name__} for export")
        
        # Determine output path
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        safe_name = sanitize_filename(playlist.name)
        file_name = output_dir / f"{safe_name}.{args.format}"
        
        # Export the playlist data
        logger.info(f"Exporting playlist to {args.format.upper()} format...")
        exporter.export(data, str(file_name))
        
        logger.info(f"Playlist successfully exported to {file_name}")
        print(f"✓ Playlist exported successfully to {file_name}")
        
    except SpotifyAuthenticationError as e:
        logger.error(f"Authentication error: {e}")
        print(f"✗ Authentication failed: {e}", flush=True)
        return 1
    except SpotifyAPIError as e:
        logger.error(f"API error: {e}")
        print(f"✗ API error: {e}", flush=True)
        return 1
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        print(f"✗ Invalid input: {e}", flush=True)
        return 1
    except IOError as e:
        logger.error(f"File I/O error: {e}")
        print(f"✗ File write failed: {e}", flush=True)
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"✗ Unexpected error: {e}", flush=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
