from pydantic import field_validator, BaseModel


class RenameFileRequest(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, v: str) -> str:
        v = v.strip()
        if not v or len(v) > 255:
            raise ValueError("File name must be between 1 and 255 characters")
        return v