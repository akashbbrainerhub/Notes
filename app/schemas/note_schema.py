from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: Optional[str] = Field(None, max_length=500)

class NoteResponse(BaseModel):
    id: UUID
    title: str
    content: Optional[str]
    is_done: bool
    created_at: datetime
    user_id: UUID

    class Config:
        from_attributes = True

class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = None
    is_done: Optional[bool] = None