from pydantic import BaseModel


class FilterCreate(BaseModel):
    is_has_logo: bool
    logo: str
    is_has_brand: bool
    brand: str
    is_bigger_then_date: bool
    date: int

class FilterUpdate(BaseModel):
    is_has_logo: bool | None = None
    logo: str | None = None
    is_has_brand: bool | None = None
    brand: str | None = None
    is_bigger_then_date: bool | None = None
    date: int | None = None