import requests
import os
import logging
from typing import List, Optional
from dotenv import load_dotenv
from .models.playlist import Playlist, Track

load_dotenv()
logger = logging.getLogger(__name__)


class SpotifyAuthenticationError(Exception):
    """Raised when Spotify authentication fails."""
    pass


class SpotifyAPIError(Exception):
    """Raised when Spotify API request fails."""
    pass


class SpotifyClient:
    """Client for interacting with the Spotify API."""

    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None, 
                 redirect_uri: Optional[str] = None) -> None:
        """Initialize SpotifyClient with credentials.
        
        Args:
            client_id: Spotify API client ID. If None, uses SPOTIFY_CLIENT_ID env var.
            client_secret: Spotify API client secret. If None, uses SPOTIFY_CLIENT_SECRET env var.
            redirect_uri: OAuth redirect URI. If None, uses SPOTIFY_REDIRECT_URI env var.
            
        Raises:
            ValueError: If required credentials are missing.
        """
        self.client_id = client_id or os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = redirect_uri or os.getenv("SPOTIFY_REDIRECT_URI")
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Spotify credentials (client_id and client_secret) are required")
        
        self.access_token: Optional[str] = None
        self.base_url = "https://api.spotify.com/v1"
        logger.info("SpotifyClient initialized")

    def authenticate(self) -> bool:
        """Authenticate with Spotify API using Client Credentials flow.
        
        Returns:
            True if authentication successful.
            
        Raises:
            SpotifyAuthenticationError: If authentication fails.
        """
        auth_url = "https://accounts.spotify.com/api/token"
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        
        try:
            response = requests.post(auth_url, data=auth_data, timeout=10)
            if response.status_code == 200:
                self.access_token = response.json()["access_token"]
                logger.info("Successfully authenticated with Spotify")
                return True
            elif response.status_code == 401:
                logger.error("Authentication failed: Invalid credentials")
                raise SpotifyAuthenticationError("Invalid Spotify credentials")
            else:
                logger.error(f"Authentication failed with status {response.status_code}")
                raise SpotifyAuthenticationError(f"Authentication failed: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during authentication: {e}")
            raise SpotifyAuthenticationError(f"Network error during authentication: {e}")

    def _validate_playlist_id(self, playlist_id: str) -> None:
        """Validate playlist ID format.
        
        Args:
            playlist_id: The playlist ID to validate.
            
        Raises:
            ValueError: If playlist ID is invalid.
        """
        if not playlist_id or not isinstance(playlist_id, str) or len(playlist_id.strip()) == 0:
            raise ValueError("Playlist ID cannot be empty")

    def _get_headers(self) -> dict:
        """Get authorization headers for API requests.
        
        Returns:
            Dictionary with authorization headers.
        """
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def get_playlist(self, playlist_id: str) -> Playlist:
        """Fetch playlist data from Spotify API.
        
        Args:
            playlist_id: The Spotify playlist ID.
            
        Returns:
            Playlist object containing playlist data and tracks.
            
        Raises:
            ValueError: If playlist_id is invalid.
            SpotifyAuthenticationError: If not authenticated.
            SpotifyAPIError: If API request fails.
        """
        self._validate_playlist_id(playlist_id)
        
        if not self.access_token:
            self.authenticate()
        
        url = f"{self.base_url}/playlists/{playlist_id}"
        
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully fetched playlist: {playlist_id}")
                tracks = self.get_tracks(playlist_id)
                return Playlist(
                    name=data.get("name", "Untitled"),
                    description=data.get("description"),
                    tracks=tracks
                )
            elif response.status_code == 404:
                logger.error(f"Playlist not found: {playlist_id}")
                raise SpotifyAPIError(f"Playlist not found: {playlist_id}")
            elif response.status_code == 401:
                logger.error("Unauthorized: Invalid or expired token")
                raise SpotifyAuthenticationError("Invalid or expired authentication token")
            else:
                logger.error(f"Failed to fetch playlist: {response.status_code}")
                raise SpotifyAPIError(f"Failed to fetch playlist: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching playlist: {e}")
            raise SpotifyAPIError(f"Network error fetching playlist: {e}")

    def get_tracks(self, playlist_id: str) -> List[Track]:
        """Fetch all tracks from a specific playlist.
        
        Args:
            playlist_id: The Spotify playlist ID.
            
        Returns:
            List of Track objects.
            
        Raises:
            ValueError: If playlist_id is invalid.
            SpotifyAuthenticationError: If not authenticated.
            SpotifyAPIError: If API request fails.
        """
        self._validate_playlist_id(playlist_id)
        
        if not self.access_token:
            self.authenticate()
        
        tracks: List[Track] = []
        url = f"{self.base_url}/playlists/{playlist_id}/tracks"
        
        try:
            while url:
                response = requests.get(url, headers=self._get_headers(), timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("items", []):
                        track_data = item.get("track")
                        if track_data:
                            try:
                                tracks.append(Track(
                                    title=track_data.get("name", "Unknown Track"),
                                    artist=track_data.get("artists", [{}])[0].get("name"),
                                    album=track_data.get("album", {}).get("name"),
                                    duration=track_data.get("duration_ms", 0)
                                ))
                            except ValueError as e:
                                logger.warning(f"Skipping invalid track: {e}")
                                continue
                    
                    url = data.get("next")
                    logger.debug(f"Fetched batch of tracks. Total so far: {len(tracks)}")
                else:
                    logger.error(f"Failed to fetch tracks: {response.status_code}")
                    raise SpotifyAPIError(f"Failed to fetch tracks: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching tracks: {e}")
            raise SpotifyAPIError(f"Network error fetching tracks: {e}")
        
        logger.info(f"Successfully fetched {len(tracks)} tracks from playlist {playlist_id}")
        return tracks
