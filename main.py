import asyncio
from contextlib import AsyncExitStack

from aiobotocore.session import AioSession
from prefect import flow, get_run_logger, task
from pydantic import ConfigDict, validate_call

from aws_ops.s3 import create_s3_client
from helpers.network.bot_detection import (
    get_random_proxy,
    get_random_user_agent,
    ua_filters,
)


@task(retries=2, persist_result=False)
@validate_call(config=ConfigDict(arbitrary_types_allowed=True), validate_return=True)
async def ingest_data():
    # create the async S3 session
    session = AioSession()

    async with AsyncExitStack() as exit_stack:
        # create the S3 client to interact with buckets in S3
        s3_client = await create_s3_client(session, exit_stack)

        # explicity close the S3 client
        await s3_client.close()


@flow(name="Motorsport Trip Finder", log_prints=True, persist_result=False)
async def run_mtf_data_processor():
    # get the Prefect logger
    logger = get_run_logger()

    # specify the filters for a User-Agent
    ua_filter = ua_filters.UserAgentFilters(
        browser=ua_filters.BrowserEnum.SafariMobile,
        os=ua_filters.OsEnum.Ios,
        platform=ua_filters.PlatformEnum.mobile,
    )
    # get a random user agent based on the filters
    user_agent = get_random_user_agent(ua_filter=ua_filter)
    logger.info(f"Random user agent: {user_agent}")

    # get a random proxy from the pool
    random_proxy = get_random_proxy()
    logger.info(f"Random proxy: {random_proxy}")


if __name__ == "__main__":
    # run the flow
    asyncio.run(run_mtf_data_processor())
