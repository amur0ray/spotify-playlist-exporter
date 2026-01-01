from typing import List, Dict, Any, Optional


class Track:
    """Represents a track in a Spotify playlist."""

    def __init__(self, title: str, artist: Optional[str], album: Optional[str], duration: int) -> None:
        """Initialize a Track.
        
        Args:
            title: The track's title.
            artist: The primary artist's name.
            album: The album name.
            duration: Duration in milliseconds.
            
        Raises:
            ValueError: If title is empty.
        """
        if not title:
            raise ValueError("Track title cannot be empty")
        self.title = title
        self.artist = artist or "Unknown Artist"
        self.album = album or "Unknown Album"
        self.duration = duration

    def to_dict(self) -> Dict[str, Any]:
        """Convert track to dictionary.
        
        Returns:
            Dictionary representation of the track.
        """
        return {
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "duration": self.duration
        }


class Playlist:
    """Represents a Spotify playlist."""

    def __init__(self, name: str, description: Optional[str], tracks: List[Track]) -> None:
        """Initialize a Playlist.
        
        Args:
            name: The playlist's name.
            description: Optional description of the playlist.
            tracks: List of Track objects.
            
        Raises:
            ValueError: If name is empty.
        """
        if not name:
            raise ValueError("Playlist name cannot be empty")
        self.name = name
        self.description = description or ""
        self.tracks = tracks or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert playlist to dictionary.
        
        Returns:
            Dictionary representation of the playlist.
        """
        return {
            "name": self.name,
            "description": self.description,
            "tracks": [track.to_dict() for track in self.tracks]
        }
