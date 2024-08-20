from pydantic import BaseModel


class ParserCreate(BaseModel):
    article: str
    number_of_goods: str
    logo: str
    delivery: str
    best_price: str
    quantity_goods: str
    price_with_logo: str | None = None
    user_id: int