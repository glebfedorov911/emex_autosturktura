from pydantic import BaseModel


class ParserCreate(BaseModel):
    article: str
    number_of_goods: str
    logo: str
    delivery: str
    best_price: str
    user_id: int