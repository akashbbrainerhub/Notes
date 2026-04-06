from fastapi import HTTPException ,Request
from dotenv import load_dotenv
from datetime import datetime , timedelta
from jose import JWTError, jwt
import os
from uuid import UUID

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
ALGORITHM = os.getenv("ALGORITHM")

class JWTHandler:
    @staticmethod
    def create_access_token(data:dict)->str:
        to_encode=data.copy()
        expire = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES or 30))
        to_encode.update({"exp":expire})
        
        token=jwt.encode(to_encode , SECRET_KEY ,algorithm= ALGORITHM) 
        return token
    
    @staticmethod
    def verify_token(token: str) -> dict | None:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
        
    @staticmethod
    def get_current_user_id(request: Request) -> UUID | None:
        token = request.cookies.get("access_token")

        if not token:
            return None

        payload = JWTHandler.verify_token(token)

        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        try:
            return UUID(user_id)
        except ValueError:
            return None
        
    