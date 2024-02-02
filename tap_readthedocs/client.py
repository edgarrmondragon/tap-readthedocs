"""REST client handling, including ReadTheDocsStream base class."""

from __future__ import annotations

import typing as t
from http import HTTPStatus

import requests_cache
from singer_sdk.authenticators import APIKeyAuthenticator
from singer_sdk.exceptions import RetriableAPIError
from singer_sdk.pagination import BaseOffsetPaginator
from singer_sdk.streams import RESTStream

if t.TYPE_CHECKING:
    import requests

requests_cache.install_cache()
TStream = t.TypeVar("TStream", bound=RESTStream[int])


class ReadTheDocsStream(RESTStream[int]):
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
    def http_headers(self) -> dict[str, str]:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        return {"User-Agent": f"{self.tap_name}/{self._tap.plugin_version}"}

    def validate_response(self, response: requests.Response) -> None:
        """Validate HTTP response.

        Args:
            response: A `requests.Response`_ object.

        Raises:
            RetriableAPIError: If the rate limit is hit.
        """
        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            raise RetriableAPIError(response.reason)
        super().validate_response(response)

    def get_url_params(
        self,
        context: dict[str, t.Any] | None,  # noqa: ARG002
        next_page_token: int | None,
    ) -> dict[str, t.Any]:
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

    def get_new_paginator(self) -> BaseOffsetPaginator:
        """Get a fresh paginator for this API endpoint.

        Returns:
            A paginator instance.
        """
        return BaseOffsetPaginator(
            start_value=0,
            page_size=self.page_size,
        )
