"""REST client handling, including ReadTheDocsStream base class."""

from typing import Any, Dict, Iterable, Optional

import requests
import requests_cache
from singer_sdk.authenticators import APIKeyAuthenticator
from singer_sdk.exceptions import RetriableAPIError
from singer_sdk.streams import RESTStream

from tap_readthedocs.pagination import APIPaginator, OffsetPaginator

requests_cache.install_cache()


class CustomPaginator(APIPaginator):
    """Paginator that works with REST streams as they exist today."""

    def get_next(self, response: requests.Response, stream: RESTStream):
        """Get next page value by calling the stream method."""
        return stream.get_next_page_token(response, self.current_value)


class ReadTheDocsPaginator(OffsetPaginator):
    """Paginator that stops when a page with 0 items is returned."""

    def has_more(self, response: requests.Response) -> bool:
        """Check if response has any items.

        Args:
            response: API response object.

        Returns:
            True if response contains at least one item.
        """
        return len(response.json()["results"]) > 0


class ReadTheDocsStream(RESTStream):
    """ReadTheDocs stream class."""

    url_base = "https://readthedocs.org"
    records_jsonpath = "$.results[*]"
    page_size = 50

    @property
    def authenticator(self) -> APIKeyAuthenticator:
        """Return a new authenticator object.

        Returns:
            An API authenticator.
        """
        return APIKeyAuthenticator.create_for_stream(
            self,
            key="Authorization",
            value="Token {token}".format(**self.config),
            location="header",
        )

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        headers = {}
        headers["User-Agent"] = f"{self.tap_name}/{self._tap.plugin_version}"
        return headers

    def validate_response(self, response: requests.Response) -> None:
        """Validate HTTP response.

        Args:
            response: A `requests.Response`_ object.

        Raises:
            RetriableAPIError: If the rate limit is hit.
        """
        if response.status_code == 429:
            raise RetriableAPIError(response.reason)
        super().validate_response(response)

    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Optional[Any],
    ) -> Dict[str, Any]:
        """Get URL query parameters.

        Args:
            context: Stream sync context.
            next_page_token: Next offset.

        Returns:
            Mapping of URL query parameters.
        """
        return {
            "limit": self.page_size,
            "offset": next_page_token,
            "expand": "config",
        }

    def get_new_paginator(self) -> ReadTheDocsPaginator:
        """Get a fresh paginator for this API endpoint.

        Returns:
            A paginator instance.
        """
        return ReadTheDocsPaginator(start_value=0, page_size=self.page_size)

    def request_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Request records from REST endpoint(s), returning response records.

        If pagination is detected, pages will be recursed automatically.

        Args:
            context: Stream partition or context dictionary.

        Yields:
            An item for every record in the response.
        """
        paginator = self.get_new_paginator()
        decorated_request = self.request_decorator(self._request)

        while not paginator.finished:
            prepared_request = self.prepare_request(
                context,
                next_page_token=paginator.current_value,
            )
            resp = decorated_request(prepared_request, context)
            for row in self.parse_response(resp):
                yield row

            paginator.advance(resp)
