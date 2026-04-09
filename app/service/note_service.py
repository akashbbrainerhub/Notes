from app.models.note_model import Note
from app.schemas.note_schema import NoteCreate, NoteUpdate
from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination.limit_offset import LimitOffsetPage, LimitOffsetParams
from sqlalchemy import asc, desc

class NoteService:
    @staticmethod
    def get_all(
        db: Session, 
        user_id: UUID, 
        params: LimitOffsetParams, 
        sort_by: str, 
        order: str,
        search: str = None,
        status: str = None, 
    ) -> LimitOffsetPage[Note]:
        
        query = db.query(Note).filter(Note.user_id == user_id)
        if search:
            query = query.filter(Note.title.ilike(f"%{search}%"))
        if status:
            if status == "done":
                query = query.filter(Note.is_done == True)
            elif status == "pending":
                query = query.filter(Note.is_done == False)
        sort_column = getattr(Note, sort_by, Note.created_at)

        if order.lower() == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))
        return paginate(db, query, params)
    
    
    @staticmethod
    def create(db: Session, data: NoteCreate, user_id: UUID) -> Note:
        note = Note(**data.model_dump(), user_id=user_id)
        db.add(note)
        db.commit()
        db.refresh(note)
        return note
    
    @staticmethod
    def update(db: Session, data: NoteUpdate, user_id: UUID, note_id: UUID) -> Note:
        note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
        if not note:
            raise HTTPException(status_code=404, detail="note not found")
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(note, key, value)

        db.commit()
        db.refresh(note)
        return note

    @staticmethod
    def delete(db: Session, note_id: UUID, user_id: UUID) -> dict:
        note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        db.delete(note)
        db.commit()
        return {"message": "note deleted"}
    
    