"""Tests standard tap features using the built-in SDK tests library."""

from __future__ import annotations

from typing import Any

from requests import Response
from singer_sdk.testing import get_standard_tap_tests

from tap_readthedocs.client import ReadTheDocsPaginator
from tap_readthedocs.streams import ReadTheDocsStream
from tap_readthedocs.tap import TapReadTheDocs

SAMPLE_CONFIG: dict[str, Any] = {}


def test_standard_tap_tests():
    """Run standard tap tests from the SDK."""
    tests = get_standard_tap_tests(TapReadTheDocs, config=SAMPLE_CONFIG)
    for test in tests:
        test()


def test_paginator():
    """Validate paginator that uses the page offset."""

    response = Response()
    paginator = ReadTheDocsPaginator(
        start_value=0,
        page_size=2,
        records_jsonpath=ReadTheDocsStream.records_jsonpath,
    )

    assert not paginator.finished
    assert paginator.current_value == 0

    response._content = b'{"results": [{}, {}]}'
    paginator.advance(response)
    assert not paginator.finished
    assert paginator.current_value == 2
    assert paginator.count == 1

    response._content = b'{"results": [{}, {}]}'
    paginator.advance(response)
    assert not paginator.finished
    assert paginator.current_value == 4
    assert paginator.count == 2

    response._content = b'{"results": []}'
    paginator.advance(response)
    assert paginator.finished
    assert paginator.count == 3
