from datetime import datetime,UTC

from pydantic import BaseConfig, BaseModel


def convert_datetime_to_realworld(dt: datetime) -> str | None:
    return dt.replace(tzinfo=UTC).isoformat().replace("+00:00", "Z")


def convert_field_to_camel_case(string: str) -> str:
    return "".join(
        word if index == 0 else word.capitalize()
        for index, word in enumerate(string.split("_"))
    )


class RWModel(BaseModel):
    class Config(BaseConfig):
        validate_by_name = True
        json_encoders = {datetime: convert_datetime_to_realworld}
        alias_generator = convert_field_to_camel_case
