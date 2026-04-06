from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user_model import User
from app.schemas.user_schema import UserCreate
from uuid import UUID

def get_user_by_id(db: Session, user_id: UUID) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def get_all_users(db: Session) -> list[User]:
    return db.query(User).all()

def create_user(db: Session, user_data: UserCreate) -> User:
    existing = get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        is_active=user_data.is_active,
        password=user_data.password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def delete_user(db: Session, user_id: UUID) -> dict:
    user = get_user_by_id(db, user_id)
    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} deleted"}