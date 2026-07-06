from pydantic import BaseModel
from typing import Optional

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

class FarmMemberUpdate(BaseModel):
    role: str

class FarmMemberResponse(BaseModel):
    user_id: int
    username: str
    full_name: Optional[str] = None
    role: str

    class Config:
        from_attributes = True
