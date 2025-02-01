from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field, condecimal


class Coordinates(BaseModel):
    latitude: Annotated[Decimal, condecimal(max_digits=7, decimal_places=5)] = Field(
        description="Latitude, with a maximum of 7 digits and 5 decimal places."
    )
    longitude: Annotated[Decimal, condecimal(max_digits=8, decimal_places=5)] = Field(
        description="Latitude, with a maximum of 8 digits and 5 decimal places."
    )
