"""ReadTheDocs tap class."""
from __future__ import annotations

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_readthedocs import streams


class TapReadTheDocs(Tap):
    """Singer tap for readthedocs.io."""

    name = "tap-readthedocs"

    config_jsonschema = th.PropertiesList(
        th.Property("token", th.StringType, required=True),
    ).to_dict()

    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams.

        Returns:
            A list of ReadTheDocs streams.
        """
        return [
            streams.Builds(tap=self),
            streams.Projects(tap=self),
            streams.Redirects(tap=self),
            streams.Subprojects(tap=self),
            streams.Translations(tap=self),
            streams.Versions(tap=self),
        ]
