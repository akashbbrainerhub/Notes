from fastapi import APIRouter , Depends
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserCreate, UserResponse
from app.service.user_service import get_user_by_id, get_all_users, create_user
from app.database.connection import get_db
from uuid import UUID

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

@router.get("/", response_model=list[UserResponse])
def get_all_user(db: Session = Depends(get_db)):
    return get_all_users(db)

    
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    return user
