from enum import Enum, StrEnum
from typing import Self

from pydantic import BaseModel, model_validator


class BrowserEnum(str, Enum):
    Chrome = "Chrome"
    Safari = "Safari"
    Firefox = "Firefox"
    ChromeMobile = "Chrome Mobile"
    SafariMobile = "Mobile Safari UI/WKWebView"


class OsEnum(StrEnum):
    MacOs = "Mac OS X"
    Windows = "Windows"
    Linux = "Linux"
    Ubuntu = "Ubuntu"
    Ios = "iOS"
    Android = "Android"


class PlatformEnum(StrEnum):
    mobile = "mobile"
    desktop = "desktop"


class UserAgentFilters(BaseModel):
    """
    The filters for a desired User-Agent string.
    """

    browser: BrowserEnum
    os: OsEnum
    platform: PlatformEnum

    @model_validator(mode="after")
    def ensure_compatability(self) -> Self:
        """
        Ensure that the browser and the platform are compatible.
        """

        # conditionals to check when the platform is "Mobile"
        if self.platform == PlatformEnum.mobile:
            # only allow Android and iOS as the OS when the platform is mobile
            if self.os not in [OsEnum.Android, OsEnum.Ios]:
                raise ValueError(
                    "Only Android and iOS are allowed when the platform is mobile."
                )

            # only allow mobile browsers when the platform is mobile
            if "mobile" not in self.browser.value.lower():
                raise ValueError(
                    "Only mobile browser are allowed when the platform is mobile."
                )

            if self.os == OsEnum.Android and self.browser == BrowserEnum.SafariMobile:
                raise ValueError("Safari Mobile is not allowed when the OS is Android.")

        # conditionals to check when the platform is "Desktop"
        if self.platform == PlatformEnum.desktop:
            # only allow desktop browsers when the platform is desktop
            if "mobile" in self.browser.value.lower():
                raise ValueError(
                    "Mobile browsers are not allowed when the platform is desktop."
                )

            # Android and iOS are mobile platforms and are NOT allowed when the platform is desktop
            if self.os in [OsEnum.Android, OsEnum.Ios]:
                raise ValueError(
                    "Android and iOS are not allowed when the platform is desktop."
                )

            # only allow MacOs as the browser when the browser is Safari
            if self.browser == BrowserEnum.Safari:
                if self.os != OsEnum.MacOs:
                    raise ValueError(
                        "Only Mac OS is allowed when the browser is Safari."
                    )

        # return the instance
        return self
