"""ReadTheDocs tap class."""

from typing import List

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_readthedocs.streams import (
    Builds,
    Projects,
    Redirects,
    Subprojects,
    Translations,
    Versions,
)

STREAM_TYPES = [
    Builds,
    Projects,
    Redirects,
    Subprojects,
    Translations,
    Versions,
]


class TapReadTheDocs(Tap):
    """Singer tap for readthedocs.io."""

    name = "tap-readthedocs"

    config_jsonschema = th.PropertiesList(
        th.Property("token", th.StringType, required=True),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams.

        Returns:
            A list of ReadTheDocs streams.
        """
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
