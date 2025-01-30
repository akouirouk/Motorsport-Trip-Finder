from helpers.network.bot_detection import ua_filters, get_random_user_agent

from swiftshadow.classes import ProxyInterface

from helpers.network.bot_detection import get_random_proxy


def main():
    # specify the filters for a User-Agent
    ua_filter = ua_filters.UserAgentFilters(
        browser=ua_filters.BrowserEnum.SafariMobile,
        os=ua_filters.OsEnum.Ios,
        platform=ua_filters.PlatformEnum.mobile,
    )
    # get a random user agent based on the filters
    user_agent = get_random_user_agent(ua_filter=ua_filter)
    print(f"Random user agent: {user_agent}")

    # this proxy manager will create a pool of valid proxies
    proxy_manager = ProxyInterface(
        countries=["US"],  # only US proxies
        cachePeriod=1,  # cache the proxies for 5 minutes
        maxProxies=30,  # get a maximum of 50 proxies
        autoRotate=True,  # auto rotate the proxies
    )
    # get a random proxy from the pool
    random_proxy = get_random_proxy(proxy_manager=proxy_manager)
    print(f"Random proxy: {random_proxy}")


main()
