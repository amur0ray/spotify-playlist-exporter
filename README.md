# Spotify Playlist Exporter

## Overview
The Spotify Playlist Exporter is a Python application that allows users to export their Spotify playlists to various file formats, including JSON, CSV, and XML. This project utilizes the Spotify API to fetch playlist data and provides a simple interface for exporting it.

## Features
- ✓ Authenticate with the Spotify API using Client Credentials flow
- ✓ Retrieve playlists and their tracks (with pagination support)
- ✓ Export playlists to JSON, CSV, and XML formats
- ✓ Command-line interface with flexible arguments
- ✓ Comprehensive logging and error handling
- ✓ Type hints throughout the codebase
- ✓ Full test coverage with mocked HTTP responses

## Project Structure
```
spotify-playlist-exporter
├── src
│   └── spotify_playlist_exporter   # Main package
│       ├── __init__.py
│       ├── main.py                 # Entry point with CLI interface
│       ├── spotify_client.py       # Spotify API client with error handling
│       ├── exporters               # Exporter classes for different formats
│       │   ├── __init__.py
│       │   ├── base_exporter.py    # Abstract base class (ABC)
│       │   ├── json_exporter.py    # JSON format exporter
│       │   ├── csv_exporter.py     # CSV format exporter
│       │   └── xml_exporter.py     # XML format exporter
│       └── models                  # Data models
│           ├── __init__.py
│           └── playlist.py         # Playlist and Track classes
├── tests                           # Unit tests
│   ├── __init__.py
│   ├── test_spotify_client.py      # Tests for SpotifyClient
│   └── test_exporters.py           # Tests for all exporters
├── pyproject.toml                  # Build configuration
├── setup.py                        # Setup script
├── requirements.txt                # Python dependencies
├── .env.example                    # Example environment configuration
└── README.md                       # This file
```

## Installation

### Prerequisites
- Python 3.8+
- Spotify API credentials (Client ID and Client Secret)

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/amur0ray/spotify-playlist-exporter.git
   cd spotify-playlist-exporter
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install the package in development mode:**
   ```bash
   pip install -e .
   ```

4. **Configure Spotify API credentials:**
   - Copy `.env.example` to `.env`
   - Get your credentials from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Update `.env` with your Client ID and Client Secret:
     ```
     SPOTIFY_CLIENT_ID=your_client_id
     SPOTIFY_CLIENT_SECRET=your_client_secret
     ```

## Usage

### Command-Line Interface

```bash
# Basic usage - export to JSON (default)
spotify-playlist-exporter <playlist_id>

# Specify export format
spotify-playlist-exporter <playlist_id> -f csv

# Specify output directory
spotify-playlist-exporter <playlist_id> -f xml -o ./exports

# Enable verbose logging
spotify-playlist-exporter <playlist_id> -v

# Full example
spotify-playlist-exporter 37i9dQZEVXbNG2KDcFcKOF -f csv -o ./exports -v
```

### Options
- `playlist_id`: Spotify playlist ID (required)
- `-f, --format`: Export format: `json`, `csv`, or `xml` (default: `json`)
- `-o, --output`: Output directory (default: current directory)
- `-v, --verbose`: Enable debug logging

### Finding Playlist IDs
1. Open a Spotify playlist in the web player
2. Right-click → "Share" → "Copy link to playlist"
3. Extract the ID from the URL: `spotify:playlist:<PLAYLIST_ID>`

## Architecture

### SpotifyClient
Handles Spotify API authentication and data retrieval with:
- Automatic re-authentication when needed
- Pagination support for large playlists
- Comprehensive error handling with custom exceptions
- Detailed logging for debugging

### Exporters
All exporters inherit from `BaseExporter` abstract base class and provide:
- Automatic parent directory creation
- UTF-8 encoding for all formats
- Input validation and error handling
- Detailed logging

### Models
- **Playlist**: Represents a playlist with name, description, and tracks
- **Track**: Represents a track with title, artist, album, and duration
- Both include validation and dictionary conversion methods

## Error Handling

The application uses custom exceptions for better error handling:
- `SpotifyAuthenticationError`: Authentication failures
- `SpotifyAPIError`: API request failures
- `ValueError`: Invalid input data
- `IOError`: File write operations

## Testing

Run all tests:
```bash
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_spotify_client.py -v
```

Run with coverage:
```bash
pytest tests/ --cov=spotify_playlist_exporter --cov-report=html
```

### Test Coverage
- SpotifyClient: Authentication, playlist fetching, tracks fetching, error cases
- Exporters: File creation, data validation, directory creation, all formats
- Models: Initialization, validation, dictionary conversion

## Dependencies

- **requests**: HTTP library for Spotify API calls
- **python-dotenv**: Environment variable management
- **pytest**: Testing framework
- **pandas**: Data manipulation (for future enhancements)
- **xmltodict**: XML handling utilities

See `requirements.txt` for version specifications.

## Logging

Logging is configured in main.py and outputs to console:
- INFO: General informational messages
- WARNING: Non-critical issues (e.g., skipped invalid tracks)
- ERROR: Critical errors requiring user attention
- DEBUG: Detailed debug information (use `-v` flag)

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Add or update tests as needed
5. Submit a pull request

## Known Limitations

- Client Credentials flow doesn't have user context (uses app context)
- Cannot access private playlists without user authentication
- Rate limiting depends on Spotify API quotas

## Future Enhancements

- [ ] OAuth 2.0 user authentication flow
- [ ] Support for private playlists
- [ ] Batch playlist export
- [ ] Playlist comparison and merging
- [ ] Web UI interface
- [ ] Database storage of playlist metadata

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.