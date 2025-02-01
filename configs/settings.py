from prefect.blocks.system import Secret
from prefect_aws import AwsCredentials

from configs.models import MySecrets

# initialize the global variable
my_secrets = None


def load_secrets() -> MySecrets:
    """
    Load the secrets from Prefect Cloud blocks and validate the secret values with the pydantic-settings model.

    Returns:
        MySecrets: The validated secrets.
    """

    # load the secrets from Prefect Cloud blocks
    pirate_weather = Secret.load("pirate-weather")
    aws_creds = AwsCredentials.load("aws-creds")

    # validate the secret values with the Block model
    my_secrets = MySecrets(aws_creds=aws_creds, pirate_weather=pirate_weather)

    # return the validated secrets
    return my_secrets
