"""Tests generic paginator classes."""

import json
from typing import Optional

from requests import Response

from tap_readthedocs.pagination import (
    BaseHATEOASPaginator,
    HeaderLinkPaginator,
    JSONPathPaginator,
    OffsetPaginator,
    PageNumberPaginator,
)


def test_paginator_offset():
    """Validate paginator that uses the page offset."""

    class _TestOffsetPaginator(OffsetPaginator):
        def has_more(self, response: Response) -> bool:
            return response.json()["hasMore"]

    response = Response()
    paginator = _TestOffsetPaginator(0, 2)
    assert not paginator.finished
    assert paginator.current_value == 0
    assert paginator.count == 0

    response._content = b'{"hasMore": true}'
    paginator.advance(response)
    assert not paginator.finished
    assert paginator.current_value == 2
    assert paginator.count == 1

    response._content = b'{"hasMore": false}'
    paginator.advance(response)
    assert paginator.finished
    assert paginator.count == 2


def test_paginator_page_number():
    """Validate paginator that uses the page number."""

    class _TestPageNumberPaginator(PageNumberPaginator):
        def has_more(self, response: Response) -> bool:
            return response.json()["hasMore"]

    has_more_response = b'{"hasMore": true}'
    no_more_response = b'{"hasMore": false}'

    response = Response()
    paginator = _TestPageNumberPaginator(0)
    assert not paginator.finished
    assert paginator.current_value == 0
    assert paginator.count == 0

    response._content = has_more_response
    paginator.advance(response)
    assert not paginator.finished
    assert paginator.current_value == 1
    assert paginator.count == 1

    response._content = has_more_response
    paginator.advance(response)
    assert not paginator.finished
    assert paginator.current_value == 2
    assert paginator.count == 2

    response._content = no_more_response
    paginator.advance(response)
    assert paginator.finished
    assert paginator.count == 3


def test_paginator_jsonpath():
    """Validate paginator that uses JSONPath."""

    response = Response()
    paginator = JSONPathPaginator(None, jsonpath="$.nextPageToken")
    assert not paginator.finished
    assert paginator.current_value is None
    assert paginator.count == 0

    response._content = b'{"nextPageToken": "abc"}'
    paginator.advance(response)
    assert not paginator.finished
    assert paginator.current_value == "abc"
    assert paginator.count == 1

    response._content = b'{"nextPageToken": null}'
    paginator.advance(response)
    assert paginator.finished
    assert paginator.count == 2


def test_paginator_header_links():
    """Validate paginator that uses HATEOS links."""

    api_hostname = "myapi.test"
    resource_path = "/path/to/resource"

    response = Response()
    paginator = HeaderLinkPaginator(None)
    assert not paginator.finished
    assert paginator.current_value is None
    assert paginator.count == 0

    response.headers.update(
        {"Link": f"<https://{api_hostname}{resource_path}?page=2&limit=100>; rel=next"},
    )
    paginator.advance(response)
    assert not paginator.finished
    assert paginator.current_value.hostname == api_hostname
    assert paginator.current_value.path == resource_path
    assert paginator.current_value.query == "page=2&limit=100"
    assert paginator.count == 1

    response.headers.update(
        {
            "Link": (
                f"<https://{api_hostname}{resource_path}?page=3&limit=100>;rel=next,"
                f"<https://{api_hostname}{resource_path}?page=2&limit=100>;rel=back"
            )
        },
    )
    paginator.advance(response)
    assert not paginator.finished
    assert paginator.current_value.hostname == api_hostname
    assert paginator.current_value.path == resource_path
    assert paginator.current_value.query == "page=3&limit=100"
    assert paginator.count == 2

    response.headers.update(
        {"Link": "<https://myapi.test/path/to/resource?page=3&limit=100>;rel=back"},
    )
    paginator.advance(response)
    assert paginator.finished
    assert paginator.count == 3


def test_paginator_custom_hateos():
    """Validate paginator that uses HATEOS links."""

    class _CustomHATEOSPaginator(BaseHATEOASPaginator):
        def get_next_url(self, response: Response) -> Optional[str]:
            """Get a parsed HATEOS link for the next, if the response has one."""
            links = response.json().get("links", [])
            next_path = next((l["href"] for l in links if l["rel"] == "next"), None)
            return next_path

    resource_path = "/path/to/resource"

    response = Response()
    paginator = _CustomHATEOSPaginator(None)
    assert not paginator.finished
    assert paginator.current_value is None
    assert paginator.count == 0

    response._content = json.dumps(
        {
            "links": [
                {
                    "rel": "next",
                    "href": f"{resource_path}?page=2&limit=100",
                }
            ]
        }
    ).encode()
    paginator.advance(response)
    assert not paginator.finished
    assert paginator.current_value.path == resource_path
    assert paginator.current_value.query == "page=2&limit=100"
    assert paginator.count == 1

    response._content = json.dumps(
        {
            "links": [
                {
                    "rel": "next",
                    "href": f"{resource_path}?page=3&limit=100",
                }
            ]
        }
    ).encode()
    paginator.advance(response)
    assert not paginator.finished
    assert paginator.current_value.path == resource_path
    assert paginator.current_value.query == "page=3&limit=100"
    assert paginator.count == 2

    response._content = json.dumps({"links": []}).encode()
    paginator.advance(response)
    assert paginator.finished
    assert paginator.count == 3
