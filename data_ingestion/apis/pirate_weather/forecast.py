import httpx

from configs.settings import load_secrets
from data_ingestion.apis.pirate_weather.models.forecast_models import (
    ForecastEndpointParms,
)


class WeatherForecost:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

        # load the secrets from Prefect Cloud blocks
        self.secrets = load_secrets()
        # get the value of the Pirate Weather API key
        self.PIRATE_API_KEY = self.secrets.pirate_weather.get_secret_value()

    async def get_forecast(self, params: ForecastEndpointParms):
        # create the endpoint with the query string parameters appended to the base URL
        api_endpoint = params.create_endpoint_str(api_key=self.PIRATE_API_KEY)

        # make the request to the API
        response = self.client.get(url=api_endpoint)

        # UPDATE - validate the response against the respective model

        # return the validated response
        return response
