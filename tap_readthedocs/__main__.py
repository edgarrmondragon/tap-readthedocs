"""Entrypoint module for tap-readthedocs."""

from __future__ import annotations

from tap_readthedocs.tap import TapReadTheDocs

TapReadTheDocs.cli()
