"""Tests for SpotifyClient module."""

import pytest
from unittest.mock import MagicMock, patch

from spotify_playlist_exporter.models.playlist import Playlist, Track
from spotify_playlist_exporter.spotify_client import (
    SpotifyAPIError,
    SpotifyAuthenticationError,
    SpotifyClient,
)


@pytest.fixture
def spotify_client():
    """Create a SpotifyClient instance for testing."""
    return SpotifyClient(client_id="test_id", client_secret="test_secret")


class TestSpotifyClientInitialization:
    """Tests for SpotifyClient initialization."""

    def test_initialization_with_credentials(self, spotify_client):
        """SpotifyClient should initialize with provided credentials."""
        assert spotify_client.client_id == "test_id"
        assert spotify_client.client_secret == "test_secret"
        assert spotify_client.access_token is None

    def test_initialization_without_explicit_credentials_requires_env_vars(self, monkeypatch):
        """SpotifyClient should raise ValueError if no credentials are available."""
        # Remove environment variables if they exist
        monkeypatch.delenv("SPOTIFY_CLIENT_ID", raising=False)
        monkeypatch.delenv("SPOTIFY_CLIENT_SECRET", raising=False)

        with pytest.raises(ValueError, match="credentials"):
            SpotifyClient()


class TestSpotifyClientAuthentication:
    """Tests for authentication functionality."""

    @patch("spotify_playlist_exporter.spotify_client.requests.post")
    def test_successful_authentication(self, mock_post, spotify_client):
        """Authentication should succeed with valid credentials."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_token_123",
            "token_type": "Bearer",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_response

        result = spotify_client.authenticate()

        assert result is True
        assert spotify_client.access_token == "test_token_123"
        mock_post.assert_called_once()

    @patch("spotify_playlist_exporter.spotify_client.requests.post")
    def test_authentication_with_invalid_credentials(self, mock_post):
        """Authentication should raise SpotifyAuthenticationError with invalid credentials."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        client = SpotifyClient(client_id="test_id", client_secret="test_secret")

        with pytest.raises(SpotifyAuthenticationError, match="Invalid Spotify credentials"):
            client.authenticate()

    @patch("spotify_playlist_exporter.spotify_client.requests.post")
    def test_authentication_with_network_error(self, mock_post):
        """Authentication should raise SpotifyAuthenticationError on network errors."""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError("Network error")

        client = SpotifyClient(client_id="test_id", client_secret="test_secret")

        with pytest.raises(SpotifyAuthenticationError, match="Network error"):
            client.authenticate()


class TestSpotifyClientPlaylistFetching:
    """Tests for playlist fetching functionality."""

    @patch("spotify_playlist_exporter.spotify_client.requests.get")
    @patch("spotify_playlist_exporter.spotify_client.requests.post")
    def test_get_playlist_success(self, mock_post, mock_get, spotify_client):
        """get_playlist should return Playlist with correct data."""
        auth_response = MagicMock()
        auth_response.status_code = 200
        auth_response.json.return_value = {"access_token": "test_token"}
        mock_post.return_value = auth_response

        playlist_response = MagicMock()
        playlist_response.status_code = 200
        playlist_response.json.return_value = {
            "name": "My Playlist",
            "description": "A great playlist",
        }

        tracks_response = MagicMock()
        tracks_response.status_code = 200
        tracks_response.json.return_value = {
            "items": [
                {
                    "track": {
                        "name": "Song 1",
                        "artists": [{"name": "Artist 1"}],
                        "album": {"name": "Album 1"},
                        "duration_ms": 180000,
                    }
                }
            ],
            "next": None,
        }

        mock_get.side_effect = [playlist_response, tracks_response]

        playlist = spotify_client.get_playlist("playlist123")

        assert isinstance(playlist, Playlist)
        assert playlist.name == "My Playlist"
        assert playlist.description == "A great playlist"
        assert len(playlist.tracks) == 1
        assert playlist.tracks[0].title == "Song 1"

    @patch("spotify_playlist_exporter.spotify_client.requests.get")
    def test_get_playlist_not_found(self, mock_get):
        """get_playlist should raise SpotifyAPIError when playlist not found."""
        client = SpotifyClient(client_id="test_id", client_secret="test_secret")
        client.access_token = "test_token"

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with pytest.raises(SpotifyAPIError, match="Playlist not found"):
            client.get_playlist("nonexistent")

    def test_get_playlist_with_invalid_id(self, spotify_client):
        """get_playlist should raise ValueError with empty playlist ID."""
        spotify_client.access_token = "test_token"

        with pytest.raises(ValueError, match="Playlist ID"):
            spotify_client.get_playlist("")


class TestSpotifyClientTrackFetching:
    """Tests for track fetching functionality."""

    @patch("spotify_playlist_exporter.spotify_client.requests.get")
    def test_get_tracks_success(self, mock_get):
        """get_tracks should return list of Track objects."""
        client = SpotifyClient(client_id="test_id", client_secret="test_secret")
        client.access_token = "test_token"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "track": {
                        "name": "Track 1",
                        "artists": [{"name": "Artist 1"}],
                        "album": {"name": "Album 1"},
                        "duration_ms": 200000,
                    }
                },
                {
                    "track": {
                        "name": "Track 2",
                        "artists": [{"name": "Artist 2"}],
                        "album": {"name": "Album 2"},
                        "duration_ms": 250000,
                    }
                },
            ],
            "next": None,
        }
        mock_get.return_value = mock_response

        tracks = client.get_tracks("playlist123")

        assert len(tracks) == 2
        assert all(isinstance(track, Track) for track in tracks)
        assert tracks[0].title == "Track 1"
        assert tracks[1].artist == "Artist 2"

    @patch("spotify_playlist_exporter.spotify_client.requests.get")
    def test_get_tracks_with_pagination(self, mock_get):
        """get_tracks should handle paginated responses."""
        client = SpotifyClient(client_id="test_id", client_secret="test_secret")
        client.access_token = "test_token"

        first_response = MagicMock()
        first_response.status_code = 200
        first_response.json.return_value = {
            "items": [
                {
                    "track": {
                        "name": "Track 1",
                        "artists": [{"name": "Artist 1"}],
                        "album": {"name": "Album 1"},
                        "duration_ms": 200000,
                    }
                }
            ],
            "next": "https://api.spotify.com/v1/playlists/123/tracks?offset=1",
        }

        second_response = MagicMock()
        second_response.status_code = 200
        second_response.json.return_value = {
            "items": [
                {
                    "track": {
                        "name": "Track 2",
                        "artists": [{"name": "Artist 2"}],
                        "album": {"name": "Album 2"},
                        "duration_ms": 250000,
                    }
                }
            ],
            "next": None,
        }

        mock_get.side_effect = [first_response, second_response]

        tracks = client.get_tracks("playlist123")

        assert len(tracks) == 2
        assert mock_get.call_count == 2

    @patch("spotify_playlist_exporter.spotify_client.requests.get")
    def test_get_tracks_with_invalid_data(self, mock_get):
        """get_tracks should skip invalid track data."""
        client = SpotifyClient(client_id="test_id", client_secret="test_secret")
        client.access_token = "test_token"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "track": {
                        "name": "Valid Track",
                        "artists": [{"name": "Artist"}],
                        "album": {"name": "Album"},
                        "duration_ms": 200000,
                    }
                },
                {"track": None},  # Invalid track
            ],
            "next": None,
        }
        mock_get.return_value = mock_response

        tracks = client.get_tracks("playlist123")

        # Should only include the valid track
        assert len(tracks) == 1
        assert tracks[0].title == "Valid Track"