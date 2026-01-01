"""Spotify Playlist Exporter - Export playlists to JSON, CSV, and XML formats."""

__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "Export Spotify playlists to various file formats"

from .spotify_client import SpotifyClient, SpotifyAuthenticationError, SpotifyAPIError
from .models.playlist import Playlist, Track

__all__ = [
    "SpotifyClient",
    "SpotifyAuthenticationError",
    "SpotifyAPIError",
    "Playlist",
    "Track",
]
