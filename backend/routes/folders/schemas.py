from typing import Optional
from pydantic import BaseModel, field_validator


class CreateFolderRequest(BaseModel):
    name: str
    parent_id: Optional[int] = None

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, v: str) -> str:
        v = v.strip()
        if not v or len(v) > 255:
            raise ValueError("Folder name must be between 1 and 255 characters")
        return v


# Poprawka: przeniesiono klasę na górę pliku, zamiast definiować ją w środku, po routerach
class RenameFolderRequest(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, v: str) -> str:
        v = v.strip()
        if not v or len(v) > 255:
            raise ValueError("Folder name must be between 1 and 255 characters")
        return v

class MoveFolderRequest(BaseModel):
    parent_id: Optional[int] = None