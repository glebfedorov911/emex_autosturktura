from pydantic import BaseModel


class FilesCreate(BaseModel):
    before_parsing_filename: str
    user_id: int
    filename_after_parsing: str
    filename_after_parsing_without_nds: str 
    filename_after_parsing_with_nds: str