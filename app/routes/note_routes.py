from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.auth.jwt_handler import JWTHandler
from app.service.note_service import NoteService
from app.models.user_model import User
from app.models.note_model import Note
from uuid import UUID
from fastapi import HTTPException

router = APIRouter(tags=["Notes"])
templates = Jinja2Templates(directory="app/template")

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = JWTHandler.get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user

@router.get("/dashboard")
def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = JWTHandler.get_current_user_id(request)
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)

    current_user = db.query(User).filter(User.id == user_id).first()
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    notes = NoteService.get_all(db, current_user.id)
    return templates.TemplateResponse(request, "dashboard.html", {
        "request": request,
        "user": current_user,
        "notes": notes
    })

@router.post("/notes/create")
def create_note(
    request: Request,
    title: str = Form(...),
    content: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.schemas.note_schema import NoteCreate
    NoteService.create(db, NoteCreate(title=title, content=content), current_user.id)
    return RedirectResponse(url="/dashboard", status_code=302)

@router.post("/notes/{note_id}/toggle")
def toggle_note(
    note_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.schemas.note_schema import NoteUpdate
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        return RedirectResponse(url="/dashboard", status_code=302)
    NoteService.update(db, NoteUpdate(is_done=not note.is_done), current_user.id, note_id)
    return RedirectResponse(url="/dashboard", status_code=302)

@router.post("/notes/{note_id}/delete")
def delete_note(
    note_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    NoteService.delete(db, note_id, current_user.id)
    return RedirectResponse(url="/dashboard", status_code=302)