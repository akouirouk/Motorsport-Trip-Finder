import re

from pydantic import BaseModel, model_validator

# regex pattern for a valid proxy "IP:PORT"
PROXY_PATTERN = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$")


class RequestProxy(BaseModel):
    """
    The model for proxies in HTTP requests, supporting `http` and `https` protocols.
    """

    http: str | None = None
    https: str | None = None

    @model_validator(mode="after")
    def validate_proxy(self):
        """
        Validate the proxy values for the "http" and "https" protocols.
        """

        # iterate over the proxy values (for both "http" and "https")
        for protocol, proxy in self.__dict__.items():
            # skip if the proxy is None
            if proxy is None:
                continue

            # set the proxy for the given protocol to None if does not match the pattern
            # failing to match the PROXY_PATTERN means the proxy is not properly formatted
            elif not PROXY_PATTERN.match(proxy):
                setattr(self, protocol, None)

        # raise ValueError if both http and https proxies are None
        if self.http is None and self.https is None:
            raise ValueError("At least one of the proxy types must be provided.")

        # return the instance
        return self
