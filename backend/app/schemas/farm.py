from pydantic import BaseModel, Field, field_validator
from typing import Optional

VALID_ROLES = {"owner", "veterinarian", "farmhand", "data_analyst"}

class FarmBase(BaseModel):
    name: str = Field(..., max_length=200)
    location: Optional[str] = Field(None, max_length=300)

class FarmCreate(FarmBase):
    pass

class FarmUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=300)

class FarmResponse(FarmBase):
    id: int
    role: Optional[str] = None

    class Config:
        from_attributes = True

class FarmMemberAdd(BaseModel):
    username: str = Field(..., max_length=150)
    role: str = Field(..., max_length=50)

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v not in VALID_ROLES:
            raise ValueError(f"Invalid role '{v}'. Must be one of: {', '.join(sorted(VALID_ROLES))}")
        return v

class FarmMemberUpdate(BaseModel):
    role: str = Field(..., max_length=50)

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v not in VALID_ROLES:
            raise ValueError(f"Invalid role '{v}'. Must be one of: {', '.join(sorted(VALID_ROLES))}")
        return v

class FarmMemberResponse(BaseModel):
    user_id: int
    username: str
    full_name: Optional[str] = None
    role: str

    class Config:
        from_attributes = True
