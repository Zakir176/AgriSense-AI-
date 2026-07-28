from pydantic import BaseModel, field_validator
from typing import Optional

VALID_ROLES = {"owner", "veterinarian", "farmhand", "data_analyst"}

class FarmBase(BaseModel):
    name: str
    location: Optional[str] = None

class FarmCreate(FarmBase):
    pass

class FarmUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None

class FarmResponse(FarmBase):
    id: int
    role: Optional[str] = None

    class Config:
        from_attributes = True

class FarmMemberAdd(BaseModel):
    username: str
    role: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v not in VALID_ROLES:
            raise ValueError(f"Invalid role '{v}'. Must be one of: {', '.join(sorted(VALID_ROLES))}")
        return v

class FarmMemberUpdate(BaseModel):
    role: str

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
