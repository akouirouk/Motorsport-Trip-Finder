from typing import Annotated

from pydantic import BeforeValidator, HttpUrl, TypeAdapter

# configure adapter for HTTP URLs
http_url_adapter = TypeAdapter(HttpUrl)

# create this annotated type to convert the pydantic URL type to a string
HttpUrlString = Annotated[
    str, BeforeValidator(lambda value: str(http_url_adapter.validate_python(value)))
]
