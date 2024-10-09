from pydantic import BaseModel


class FilterCreate(BaseModel):
    deep_filter: int | None = 10
    deep_analog: int | None = 10
    analog: bool
    replacement : bool
    title: str
    is_bigger: bool | None = None
    date: int | None = None
    logo: str | None = None
    pickup_point: int | None = 38760


class FilterUpdate(BaseModel):
    deep_filter: int | None = None
    deep_analog: int | None = None
    analog: bool | None = None
    replacement: bool | None = None
    title: str | None = None
    is_bigger: bool | None = None
    date: int | None = None
    logo: str | None = None
    pickup_point: int | None = 38760
