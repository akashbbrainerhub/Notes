from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

class PasswordHandler:

    @staticmethod
    def hash(password: str):
        password = password[:72]
        return pwd_context.hash(password)
    
    @staticmethod
    def verify(plain_password: str, hashed_password: str):
        plain_password = plain_password[:72]
        return pwd_context.verify(plain_password, hashed_password)