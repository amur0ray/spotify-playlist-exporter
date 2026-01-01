"""Tests for exporter classes."""

import json
from pathlib import Path

import pytest

from spotify_playlist_exporter.exporters.csv_exporter import CSVExporter
from spotify_playlist_exporter.exporters.json_exporter import JSONExporter
from spotify_playlist_exporter.exporters.xml_exporter import XMLExporter
from spotify_playlist_exporter.models.playlist import Playlist, Track


@pytest.fixture
def sample_tracks():
    """Fixture providing sample track data."""
    return [
        Track(title="Song 1", artist="Artist 1", album="Album 1", duration=180000),
        Track(title="Song 2", artist="Artist 2", album="Album 2", duration=200000),
    ]


@pytest.fixture
def sample_playlist(sample_tracks):
    """Fixture providing a sample playlist."""
    return Playlist(
        name="Test Playlist",
        description="A playlist for testing",
        tracks=sample_tracks,
    )


@pytest.fixture
def sample_data(sample_playlist):
    """Fixture providing sample data dictionary."""
    return {
        "name": sample_playlist.name,
        "description": sample_playlist.description,
        "tracks": [track.to_dict() for track in sample_playlist.tracks],
    }


class TestJSONExporter:
    """Tests for JSONExporter."""

    def test_instantiation(self):
        """JSONExporter should instantiate without errors."""
        exporter = JSONExporter()
        assert isinstance(exporter, JSONExporter)

    def test_export_creates_file(self, tmp_path, sample_data):
        """Export should create a JSON file with correct content."""
        exporter = JSONExporter()
        file_path = tmp_path / "playlist.json"

        exporter.export(sample_data, str(file_path))

        assert file_path.exists()
        with open(file_path) as f:
            exported_data = json.load(f)

        assert exported_data["name"] == "Test Playlist"
        assert exported_data["description"] == "A playlist for testing"
        assert len(exported_data["tracks"]) == 2

    def test_export_creates_nested_directories(self, tmp_path, sample_data):
        """Export should create missing parent directories."""
        exporter = JSONExporter()
        file_path = tmp_path / "nested" / "dirs" / "playlist.json"

        exporter.export(sample_data, str(file_path))

        assert file_path.exists()
        assert file_path.parent.exists()

    @pytest.mark.parametrize("data", [{}, None])
    def test_export_with_empty_data_raises_error(self, tmp_path, data):
        """Export should raise ValueError for empty data."""
        exporter = JSONExporter()
        file_path = tmp_path / "test.json"

        with pytest.raises(ValueError, match="Data cannot be empty"):
            exporter.export(data, str(file_path))


class TestCSVExporter:
    """Tests for CSVExporter."""

    def test_instantiation(self):
        """CSVExporter should instantiate without errors."""
        exporter = CSVExporter()
        assert isinstance(exporter, CSVExporter)

    def test_export_creates_file_with_header(self, tmp_path, sample_data):
        """Export should create a CSV file with header and data."""
        exporter = CSVExporter()
        file_path = tmp_path / "playlist.csv"

        exporter.export(sample_data, str(file_path))

        assert file_path.exists()
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        assert len(lines) == 3  # Header + 2 tracks
        assert "Track Title" in lines[0]
        assert "Song 1" in lines[1]
        assert "Song 2" in lines[2]

    def test_export_without_tracks_key_raises_error(self, tmp_path):
        """Export should raise ValueError if 'tracks' key is missing."""
        exporter = CSVExporter()
        file_path = tmp_path / "test.csv"
        data = {"name": "Test", "description": "Test"}

        with pytest.raises(ValueError, match="'tracks' key"):
            exporter.export(data, str(file_path))

    def test_export_with_empty_tracks(self, tmp_path):
        """Export should succeed with empty tracks list."""
        exporter = CSVExporter()
        file_path = tmp_path / "test.csv"
        data = {"name": "Empty", "description": "No tracks", "tracks": []}

        exporter.export(data, str(file_path))

        assert file_path.exists()


class TestXMLExporter:
    """Tests for XMLExporter."""

    def test_instantiation(self):
        """XMLExporter should instantiate without errors."""
        exporter = XMLExporter()
        assert isinstance(exporter, XMLExporter)

    def test_export_creates_valid_xml_file(self, tmp_path, sample_data):
        """Export should create a valid XML file with correct content."""
        exporter = XMLExporter()
        file_path = tmp_path / "playlist.xml"

        exporter.export(sample_data, str(file_path))

        assert file_path.exists()
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        assert "xml version" in content
        assert "Test Playlist" in content
        assert "Song 1" in content

    def test_export_without_tracks_key_raises_error(self, tmp_path):
        """Export should raise ValueError if 'tracks' key is missing."""
        exporter = XMLExporter()
        file_path = tmp_path / "test.xml"
        data = {"name": "Test"}

        with pytest.raises(ValueError, match="'tracks' key"):
            exporter.export(data, str(file_path))

    def test_export_with_special_characters(self, tmp_path):
        """Export should handle special characters correctly."""
        exporter = XMLExporter()
        file_path = tmp_path / "test.xml"
        data = {
            "name": "Test & Special <Chars>",
            "description": 'Description with "quotes"',
            "tracks": [
                {
                    "title": "Song with & chars",
                    "artist": "Artist <name>",
                    "album": "Album",
                    "duration": 180000,
                }
            ],
        }

        exporter.export(data, str(file_path))

        assert file_path.exists()


class TestExporterIntegration:
    """Integration tests for all exporters."""

    @pytest.mark.parametrize(
        "exporter_class,extension",
        [
            (JSONExporter, "json"),
            (CSVExporter, "csv"),
            (XMLExporter, "xml"),
        ],
    )
    def test_export_all_formats(self, tmp_path, sample_data, exporter_class, extension):
        """All exporters should create files with correct extensions."""
        exporter = exporter_class()
        file_path = tmp_path / f"playlist.{extension}"

        exporter.export(sample_data, str(file_path))

        assert file_path.exists()
        assert file_path.suffix == f".{extension}"
