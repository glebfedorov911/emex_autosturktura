from pydantic import BaseModel


class ParserCreate(BaseModel):
    article: str
    name: str
    brand: str
    article1: str
    quantity: str
    price: str
    batch: str
    nds: str
    best_price: str
    logo: str
    delivery_time: str
    new_price: str | None = None
    quantity1: str
    user_id: int
    file_id: int 