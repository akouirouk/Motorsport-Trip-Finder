from enum import Enum
from typing import ClassVar, Self

from pendulum import datetime
from pydantic import BaseModel, Field, model_validator, validate_call

from data_ingestion.models.custom_dtypes import HttpUrlString
from data_ingestion.models.geography import Coordinates
from helpers.general import convert_datetime_to_int_timestamp


class TemperatureUnits(str, Enum):
    SI = "SI"
    CA = "CA"
    UK = "UK"
    US = "US"


class ExcludeDataOptions(str, Enum):
    CURRENTLY = "currently"
    MINUTELY = "minutely"
    HOURLY = "hourly"
    DAILY = "daily"
    ALERTS = "alerts"
    FLAGS = "flags"


class ForecastEndpointParms(BaseModel):
    # the base endpoint for the forecast API
    FORECAST_BASE_ENDPOINT: ClassVar[HttpUrlString] = (
        "https://api.pirateweather.net/forecast/"
    )
    # the base data to exclude from the forecast API response
    # these data points are not needed for the current use case
    BASE_DATA_EXCLUSIONS: ClassVar[list[ExcludeDataOptions]] = [
        ExcludeDataOptions.MINUTELY,
        ExcludeDataOptions.HOURLY,
        ExcludeDataOptions.FLAGS,
    ]

    coordinates: Coordinates
    time: datetime | None = Field(
        default=None,
        description="The forecast at the specified datetime (will be converted to a unix timestamp in API request).",
    )
    units: TemperatureUnits | None = Field(
        default=TemperatureUnits.US.value,
        description="The temperature units to use.",
        examples=["SI", "CA", "UK", "US"],
    )
    exclude: list[ExcludeDataOptions] | None = Field(
        default=None,
        description="The data to exclude from the forecast API response.",
    )

    @model_validator(mode="after")
    def add_to_exclusions(self) -> Self:
        """
        Add any additional exlusions to the base list of exclusions.

        Returns:
            Self: The updated model with the additional exclusions (if any).
        """

        # extend the list of data exclusions
        # ensuring there are no duplicates by casting to set -> list
        if self.exclude:
            self.exclude = list(set(self.BASE_DATA_EXCLUSIONS.extend(self.exclude)))

        # return the instance with any possible updates
        return self

    @validate_call(validate_return=True)
    def create_endpoint_str(self, api_key: str) -> HttpUrlString:
        # the API endpoint to get the forecast for a given location
        api_endpoint = self.FORECAST_BASE_ENDPOINT + (
            f"{api_key}/{self.coordinates.latitude},{self.coordinates.longitude}"
        )

        # append any other query parameters to the endpoint
        if self.time:
            # convert the datetime to a unix timestamp
            dt_int_timestamp = convert_datetime_to_int_timestamp(self.time)
            # append to the endpoint
            api_endpoint += f",{dt_int_timestamp}"

        if self.units:
            # determine which character to use to prefix new param
            api_endpoint = self.__endpoint_param_checker(api_endpoint)

            # append the units query parameter to the endpoint
            api_endpoint += f"units={self.units}"

    @classmethod
    @validate_call(validate_return=True)
    def __endpoint_param_checker(cls, api_endpoint: str) -> str:
        """
        Determine whether to append a "?" or "&" to the API endpoint.

        Args:
            api_endpoint (str): The API endpoint to check.

        Returns:
            str: The updated API endpoint with the proper query parameter separator.
        """

        # determine if there are already query parameters in the endpoint
        if "?" not in api_endpoint:
            api_endpoint += "?"
        else:
            api_endpoint += "&"

        # return the updated endpoint string
        return api_endpoint
