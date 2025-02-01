from pydantic import SecretStr
from pydantic_settings import BaseSettings
from prefect_aws import AwsCredentials


class MySecrets(BaseSettings):
    aws_creds: AwsCredentials
    pirate_weather: SecretStr
