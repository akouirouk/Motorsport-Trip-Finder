import pendulum
from pydantic import validate_call


@validate_call(validate_return=True)
def current_int_timestamp() -> int:
    """
    Get the current timestamp as an integer.

    Returns:
        int: The current timestamp as an integer.
    """

    return pendulum.now().int_timestamp


@validate_call(validate_return=True)
def convert_datetime_to_int_timestamp(dt: pendulum.DateTime) -> int:
    """
    Convert a datetime to an integer timestamp.

    Args:
        dt (pendulum.DateTime): The datetime to convert.

    Returns:
        int: The integer timestamp.
    """

    return dt.int_timestamp
