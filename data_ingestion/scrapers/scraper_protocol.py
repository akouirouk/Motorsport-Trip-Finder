from typing_extensions import Protocol, runtime_checkable

from pydantic import validate_call


@runtime_checkable
class Scraper(Protocol):

    @validate_call(validate_return=True)
    async def make_request(
        self,
        url: str,
    ) -> dict:
        """Make an asynchronous HTTP request to a URL or API endpoint."""
        ...
