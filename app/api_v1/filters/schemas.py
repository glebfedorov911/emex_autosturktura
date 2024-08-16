from pydantic import BaseModel


class FilterCreate(BaseModel):
    deep_filter: int | None = 10
    deep_analog: int | None = 10
    analog: bool
    is_bigger: bool | None = None
    date: int | None = None
    logo: str | None = None


class FilterUpdate(BaseModel):
    deep_filter: int | None = None
    deep_analog: int | None = None
    analog: bool | None = None
    is_bigger: bool | None = None
    date: int | None = None
    logo: str | None = None