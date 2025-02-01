import io
import json
from contextlib import AsyncExitStack
from typing import Literal

import botocore.config
import stamina
from aiobotocore.client import AioBaseClient
from aiobotocore.session import AioSession
from botocore.exceptions import ClientError
from pydantic import ConfigDict, validate_call

from configs import load_secrets

# specify aws regions available
aws_regions = Literal["us-east-1"]


class Manager:
    "Needed for aiobotocore to use with an existing context manager."

    def __init__(self):
        self._exit_stack = AsyncExitStack()

        self._s3_client = None

    async def __aenter__(self, access_key: str, secret_key: str):
        """
        Creating an S3 client to interact with S3 buckets when entering an asynchronous context manager.

        Args:
            access_key (str): AWS Access Key ID.
            secret_key (str): AWS Secret Access Key.
        """

        # load AWS credentials from Prefect Cloud
        auth = await load_secrets()

        # create the async S3 session
        session = AioSession()

        # create the async context manager for the S3 client using the newly created session
        self._s3_client = await self._exit_stack.enter_async_context(
            session.create_client(
                "s3",
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=auth.aws_creds.region_name,
            )
        )

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exiting the asynchronous context manager, therefore, closing the S3 client connection.
        """

        await self._exit_stack.__aexit__(exc_type, exc_val, exc_tb)


@validate_call(config=ConfigDict(arbitrary_types_allowed=True), validate_return=True)
async def create_s3_client(
    session: AioSession, exit_stack: AsyncExitStack
) -> AioBaseClient:
    """
    Create an S3 client to interact with S3 buckets.

    Args:
        session (AioSession): Async AWS S3 session.
        exit_stack (AsyncExitStack): Async context manager.

    Returns:
        AioBaseClient: Async S3 client.
    """

    # load AWS credentials from Prefect Cloud
    auth = await load_secrets()

    # create client and add cleanup
    client = await exit_stack.enter_async_context(
        session.create_client(
            service_name="s3",
            aws_access_key_id=auth.aws_creds.aws_access_key_id,
            aws_secret_access_key=auth.aws_creds.aws_secret_access_key,
            region_name=auth.aws_creds.region_name,
        )
    )
    return client


@validate_call(config=ConfigDict(arbitrary_types_allowed=True), validate_return=True)
async def upload_to_s3(
    s3_client: AioBaseClient,
    data: dict,
    bucket: str,
    upload_key: str,
) -> str:
    """
    Upload a JSON object to an S3 bucket.

    Args:
        s3_client (AioBaseClient): Async S3 client.
        data (dict): JSON data to upload.
        bucket_name (str): S3 bucket name.
        upload_key (str): S3 key to upload the data to.

    Raises:
        TypeError, ValueError: Error serializing data to JSON.
        botocore.excpetions.ClientError: Error uploading file to S3.

    Returns:
        str: S3 key of the uploaded file.
    """

    try:
        # convert the dictionary to a JSON object
        json_data = json.dumps(data)
        # create a file-like object from the JSON string
        file_obj = io.BytesIO(json_data.encode("utf-8"))
    except (TypeError, ValueError) as err:
        # log and raise error if data can't be JSON-serialized or can't be encoded
        print(
            f"ERROR: serializing data to JSON on S3 upload of file '{upload_key}': {err}"
        )
        raise err

    try:
        # try to upload the file object to S3
        await s3_client.put_object(Bucket=bucket, Key=upload_key, Body=file_obj)
    except botocore.exceptions.ClientError as err:
        # log the error
        print(
            f"ERROR: Failed to upload {upload_key} to the S3 Bucket '{bucket}'. Error Message: {err}"
        )
        raise err

    # return the key of the upload
    return upload_key


@validate_call(config=ConfigDict(arbitrary_types_allowed=True), validate_return=True)
@stamina.retry(on=ClientError, wait_initial=3, wait_jitter=3, attempts=3)
async def download_json_from_s3(
    s3_client: AioBaseClient, bucket_name: str, key: str
) -> dict:
    """
    Download a JSON file from an S3 bucket and parse it into a dictionary.

    Args:
        s3_client (AioBaseClient): Async S3 client.
        bucket_name (str): S3 bucket name.
        key (str): S3 key of the file to download.

    Raises:
        botocore.exceptions.ClientError: Error downloading file from S3.

    Returns:
        dict: JSON data from the downloaded file.
    """

    try:
        # download the JSON file from S3
        response = await s3_client.get_object(Bucket=bucket_name, Key=key)
    except botocore.exceptions.ClientError as err:
        # log and raise the error
        print(f"Error downloading key:  {err}")
        raise err

    try:
        # read and parse file into dict
        obj = await response["Body"].read()
        json_data = json.loads(obj)
    except json.JSONDecodeError as e:
        # log and raise JSON parsing errors
        print(f"Error parsing JSON: {e}")
        raise

    # log and return JSON data
    return json_data
