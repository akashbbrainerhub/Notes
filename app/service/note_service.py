from app.models.note_model import Note
from app.schemas.note_schema import NoteCreate, NoteUpdate
from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

class NoteService:
    @staticmethod
    def get_all(db: Session, user_id: UUID, limit: int, offset: int) -> tuple[list[Note], int, bool]:
        query = db.query(Note).filter(Note.user_id == user_id)
        total_notes = query.count()
        notes = query.offset(offset).limit(limit).all()
        has_next = (offset + limit) < total_notes
        return notes, total_notes, has_next
    
    
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
    
    