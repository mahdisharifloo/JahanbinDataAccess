import os
import sys
from datetime import timedelta
from fastapi import Depends, HTTPException
from fastapi import APIRouter

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_path)

from models.auth import *
from controllers.auth import *
from models.app import *
from utils.logger import Logger

log = Logger("access_api")


router = APIRouter()
ACCESS_TOKEN_EXPIRE_MINUTES = 300000
tags_metadata = [
    {"name": "Instagram", "description": "Endpoints related to instagram"},
    {"name": "Twitter", "description": "Endpoints related to twitter"},
    {"name": "NewsAgency", "description": "Endpoints related to news_agency"},
    {"name": "TelegramChannels", "description": "Endpoints related to telegram_channels"},
    {"name": "TelegramGroups", "description": "Endpoints related to telegram_groups"},
    {"name": "B2B", "description": "Endpoints related to worker-related functionality."},
    {"name": "Login", "description": "Endpoints related to loging functionality."},
]


@router.post("/token", tags=["Login"], response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if not user or not verify_user_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", tags=["Login"], response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.post("/register", tags=["Login"])
async def register_user(username: str, email: str, password: str):
    user_model = userModel()
    # Check if the user already exists in the database
    existing_user = get_user(username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    # Hash the password
    hashed_password = hashing.get_password_hash(password)
    # Create a new user document
    new_user = {
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
    }
    # Insert the user document into the database
    user_model.insert_one(new_user)
    return {"message": "User registered successfully"}

