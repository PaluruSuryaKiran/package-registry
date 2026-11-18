from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class PackageCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

    name: str = Field(
        ..., min_length=2, max_length=100, pattern=r"^[a-z][a-z0-9-]*$"
    )
    description: str = Field(default="", max_length=500)

class PackageOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    name: str
    description: str
    created_at: datetime
    latest_version: str | None = None
    

