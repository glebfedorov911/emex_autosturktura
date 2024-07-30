from pydantic import BaseModel


class FilesCreate(BaseModel):
    filename: str
    user_id: int