"""REST client handling, including ReadTheDocsStream base class."""

from typing import Any, Dict, Optional

import requests
import requests_cache
from singer_sdk.authenticators import APIKeyAuthenticator
from singer_sdk.streams import RESTStream

requests_cache.install_cache()


class ReadTheDocsStream(RESTStream):
    """ReadTheDocs stream class."""

    url_base = "https://readthedocs.org"
    records_jsonpath = "$.results[*]"

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
            "limit": 50,
            "offset": next_page_token,
            "expand": "config",
        }

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Optional[Any],
    ) -> Any:
        """Get next page offset.

        Args:
            response: API response.
            previous_token: Previous offset.

        Returns:
            Page offset.
        """
        if not len(response.json()["results"]):
            return None

        return 50 if previous_token is None else previous_token + 50
