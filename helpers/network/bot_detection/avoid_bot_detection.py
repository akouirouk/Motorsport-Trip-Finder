from fake_useragent import UserAgent
from swiftshadow.classes import ProxyInterface

from helpers.network.bot_detection.models import request_proxy, ua_filters


def get_random_user_agent(ua_filter: ua_filters.UserAgentFilters) -> str:
    """
    Fetch a random User-Agent string based on the filters provided.

    Args:
        ua_filter (ua_filters.UserAgentFilters): The filters to apply to the User-Agent retriever object.

    Returns:
        str: The random User-Agent string.
    """

    # create the user agent retriever object based on the filters
    ua = UserAgent(
        browsers=ua_filter.browser, os=ua_filter.os, platforms=ua_filter.platform
    )

    # return the random user agent
    return ua.random


def get_random_proxy(proxy_manager: ProxyInterface) -> str:
    """
    Get a random proxy from the rotating proxy manager.

    Args:
        proxy_manager (ProxyInterface): The rotating proxy manager, that checks the validity of the proxy.

    Returns:
        str: The random proxy string.
    """

    # get a random proxy
    proxy = proxy_manager.get().as_requests_dict()

    # validate the proxy to ensure it is in the proper format
    validated_proxy = request_proxy.RequestProxy.model_validate(proxy)

    # format the proxy for the HTTPX client
    return format_proxy_httpx(proxy=validated_proxy)


def format_proxy_httpx(proxy: request_proxy.RequestProxy) -> str:
    """
    Format the proxy for the HTTPX client.

    Args:
        proxy (request_proxy.RequestProxy): The proxy to be formatted.

    Returns:
        str: The formatted proxy string.
    """

    # if the HTTP proxy is provided
    if proxy.http:
        return f"http://{proxy.http}"

    # if the HTTPS proxy is provided
    elif proxy.https:
        return f"https://{proxy.https}"
