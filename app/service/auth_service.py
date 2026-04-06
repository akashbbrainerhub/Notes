from app.schemas.user_schema import UserCreate
from app.models.user_model import User
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.auth.jwt_handler import JWTHandler
from app.auth.password_handler import PasswordHandler

class AuthService:
    @staticmethod
    def registration(db:Session,user_data:UserCreate)->User:
        exiting=db.query(User).filter(User.email==user_data.email).first()
        if exiting:
            raise HTTPException(status_code=400,detail="email already exist")
        
        hashed_pw=PasswordHandler.hash(user_data.password)
        user=User(
            name=user_data.name,
            email=user_data.email,
            password=hashed_pw
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def login(db: Session, email: str, password: str) -> str:
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # verify() checks plain password against stored hash
        if not PasswordHandler.verify(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Create JWT token with user's id as subject
        token = JWTHandler.create_access_token({"sub": str(user.id), "email": user.email})
        return token