from pydantic import BaseModel 
from typing import Optional
from passlib.context import CryptContext


# Authentication
class User(BaseModel):
    username: str
    email: str
    hashed_password: str

class UserInDB(User):
    id: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str 


# Password hashing
class Hashing:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)
