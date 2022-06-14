"""Generic paginator classes."""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Any, Generator, Generic, Iterable, Optional, TypeVar
from urllib.parse import ParseResult, urlparse

from requests import Response
from singer_sdk.helpers.jsonpath import extract_jsonpath

T = TypeVar("T")
TPageToken = TypeVar("TPageToken")


def first(iterable: Iterable[T]) -> T:
    """Return the first element of an iterable or raise an exception.

    Args:
        iterable: An iterable.

    Returns:
        The first element of the iterable.

    >>> first('ABC')
    'A'
    """
    return next(iter(iterable))


class BaseAPIPaginator(Generic[TPageToken], metaclass=ABCMeta):
    """An API paginator object."""

    def __init__(
        self,
        start_value: TPageToken,
        records_jsonpath: str = "$[*]",
    ) -> None:
        """Create a new paginator.

        Args:
            start_value: Initial value.
            records_jsonpath: JSONPath expression to extract records from the response.
        """
        self._value: TPageToken = start_value
        self._page_count = 0
        self._finished = False
        self._last_seen_record: dict | None = None
        self._records_jsonpath = records_jsonpath

    @property
    def current_value(self) -> TPageToken:
        """Get the current pagination value.

        Returns:
            Current page value.
        """
        return self._value

    @property
    def finished(self) -> bool:
        """Get a flag that indicates if the last page of data has been reached.

        Returns:
            True if there are no more pages.
        """
        return self._finished

    @property
    def count(self) -> int:
        """Count the number of pages traversed so far.

        Returns:
            Number of pages.
        """
        return self._page_count

    @property
    def last_seen_record(self) -> dict | None:
        """Get the last seen record.

        Returns:
            The last seen record.
        """
        return self._last_seen_record

    @last_seen_record.setter
    def last_seen_record(self, record: dict | None) -> None:
        """Set the last seen record.

        Args:
            record: The last seen record.
        """
        self._last_seen_record = record

    def __str__(self) -> str:
        """Stringify this object.

        Returns:
            String representation.
        """
        return f"{self.__class__.__name__}<{self.current_value}>"

    def __repr__(self) -> str:
        """Stringify this object.

        Returns:
            String representation.
        """
        return str(self)

    def advance(self, response: Response) -> None:
        """Get a new page value and advance the current one.

        Args:
            response: API response object.

        Raises:
            RuntimeError: If a loop in pagination is detected. That is, when two
                consecutive pagination tokens are identical.
        """
        self._page_count += 1

        if not self.has_more(response):
            self._finished = True
            return

        new_value = self.get_next(response)

        if new_value and new_value == self._value:
            raise RuntimeError(
                f"Loop detected in pagination. "
                f"Pagination token {new_value} is identical to prior token."
            )

        if new_value is None:
            self._finished = True
        else:
            self._value = new_value

    def iter_records(self, response: Response) -> Generator[dict, None, None]:
        """Override this method to iterate over records in the response.

        Args:
            response: API response object.

        Yields:
            Records.
        """
        for record in self.parse_records(response):
            self.last_seen_record = record
            yield record

        self.advance(response)

    def has_more(self, response: Response) -> bool:
        """Override this method to check if the endpoint has any pages left.

        Args:
            response: API response object.

        Returns:
            Boolean flag used to indicate if the endpoint has more pages.
        """
        return True

    def parse_records(self, response: Response) -> Generator[dict, None, None]:
        """Parse records from the response.

        Args:
            response: API response object.

        Yields:
            Page records.
        """
        yield from extract_jsonpath(self._records_jsonpath, input=response.json())

    @abstractmethod
    def get_next(self, response: Response) -> TPageToken | None:
        """Get the next pagination token or index from the API response.

        Args:
            response: API response object.

        Returns:
            The next page token or index. Return `None` from this method to indicate
                the end of pagination.
        """
        ...


class SinglePagePaginator(BaseAPIPaginator[None]):
    """A paginator that does works with single-page endpoints."""

    def __init__(self) -> None:
        """Create a new paginator."""
        super().__init__(None)

    def get_next(self, response: Response) -> None:
        """Get the next pagination token or index from the API response.

        Args:
            response: API response object.

        Returns:
            The next page token or index. Return `None` from this method to indicate
                the end of pagination.
        """
        return None


class BaseHATEOASPaginator(BaseAPIPaginator[Optional[ParseResult]], metaclass=ABCMeta):
    """Paginator class for APIs supporting HATEOAS links in their responses."""

    @abstractmethod
    def get_next_url(self, response: Response) -> str | None:
        """Override this method to extract a HATEOAS link from the response.

        Args:
            response: API response object.
        """
        ...

    def get_next(self, response: Response) -> ParseResult | None:
        """Get the next pagination token or index from the API response.

        Args:
            response: API response object.

        Returns:
            A parsed HATEOAS link if the response has one, otherwise `None`.
        """
        next_url = self.get_next_url(response)
        return urlparse(next_url) if next_url else None


class HeaderLinkPaginator(BaseHATEOASPaginator):
    """Paginator class for APIs supporting HATEOAS links in their headers.

    Links:
        - https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Link
        - https://datatracker.ietf.org/doc/html/rfc8288#section-3
    """

    def get_next_url(self, response: Response) -> str | None:
        """Override this method to extract a HATEOAS link from the response.

        Args:
            response: API response object.

        Returns:
            A HATEOAS link parsed from the response headers.
        """
        return response.links.get("next", {}).get("url")


class JSONPathPaginator(BaseAPIPaginator[Optional[str]]):
    """Paginator class for APIs returning a pagination token in the response body."""

    def __init__(
        self,
        start_value: str | None,
        jsonpath: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Create a new paginator.

        Args:
            start_value: Initial value.
            jsonpath: A JSONPath expression.
            args: Paginator positional arguments.
            kwargs: Paginator keyword arguments.
        """
        super().__init__(start_value, *args, **kwargs)
        self._jsonpath = jsonpath

    def get_next(self, response: Response) -> str | None:
        """Get the next page token.

        Args:
            response: API response object.

        Returns:
            The next page token.
        """
        all_matches = extract_jsonpath(self._jsonpath, response.json())
        return next(all_matches, None)


class BasePageNumberPaginator(BaseAPIPaginator[int], metaclass=ABCMeta):
    """Paginator class for APIs that use page number."""

    @abstractmethod
    def has_more(self, response: Response) -> bool:
        """Override this method to check if the endpoint has any pages left.

        Args:
            response: API response object.

        Returns:
            Boolean flag used to indicate if the endpoint has more pages.

        """
        ...

    def get_next(self, response: Response) -> int | None:
        """Get the next page number.

        Args:
            response: API response object.

        Returns:
            The next page number.
        """
        return self._value + 1


class BaseOffsetPaginator(BaseAPIPaginator[int], metaclass=ABCMeta):
    """Paginator class for APIs that use page offset."""

    def __init__(
        self,
        start_value: int,
        page_size: int,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Create a new paginator.

        Args:
            start_value: Initial value.
            page_size: Constant page size.
            args: Paginator positional arguments.
            kwargs: Paginator keyword arguments.
        """
        super().__init__(start_value, *args, **kwargs)
        self._page_size = page_size

    @abstractmethod
    def has_more(self, response: Response) -> bool:
        """Override this method to check if the endpoint has any pages left.

        Args:
            response: API response object.

        Returns:
            Boolean flag used to indicate if the endpoint has more pages.
        """
        ...

    def get_next(self, response: Response) -> int | None:
        """Get the next page offset.

        Args:
            response: API response object.

        Returns:
            The next page offset.
        """
        return self._value + self._page_size
