from pydantic import BaseModel, Field


class Color(BaseModel):
    r: int = Field(description="Red part of a color", default=0)
    g: int = Field(description="Green part of a color", default=0)
    b: int = Field(description="Blue part of a color", default=0)
