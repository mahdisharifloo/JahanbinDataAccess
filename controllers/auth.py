import os
import sys
import jwt
from fastapi import Depends, HTTPException 
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime ,timedelta

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_path)

from models.auth import * 
from models.app import * 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
hashing = Hashing()

# Configuration
SECRET_KEY = "secret-key"  # Replace with your secret key
ALGORITHM = "HS256"

# Authentication functions
def get_user(username: str):
    db = userModel()
    user_data = db.find_one({"username": username})
    if user_data:
        user_data['id'] = str(user_data['_id'])
        return UserInDB(**user_data)
    
# Dependency for getting the current user
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=400, detail="Could not validate credentials")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    user = get_user(username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user

def verify_user_password(plain_password, hashed_password):
    return hashing.verify_password(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
