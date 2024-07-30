from pydantic import BaseModel


class FilesCreate(BaseModel):
    before_parsing_filename: str
    user_id: int