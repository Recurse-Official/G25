from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
import httpx
from datetime import datetime, timedelta
import jwt

from utils.auth import get_current_user

import os
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"

print(
    GITHUB_CLIENT_ID,
    GITHUB_CLIENT_SECRET,
    GITHUB_REDIRECT_URI,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_SECRET_KEY
)

@router.get("/access-token")
async def get_access_token(code: str):
    """GitHub OAuth callback Handler"""


    token_url = "https://github.com/login/oauth/access_token"
    async with httpx.AsyncClient() as client:
        response = await client.post(
            token_url,
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        token_data = response.json()
        
        if "error" in token_data:
            raise HTTPException(status_code=400, detail=token_data["error"])
        
        # Get user info
        github_token = token_data["access_token"]
        user_response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/json",
            },
        )
        user_data = user_response.json()

        # Create session token
        session_data = {
            "github_token": github_token,
            "user_id": user_data["id"],
            "username": user_data["login"],
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        session_token = jwt.encode(
            session_data,
            JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM
        )
        
        return {"access_token": session_token, "token_type": "bearer"}
    

@router.get("/user-data")
async def user_data(current_user: dict = Depends(get_current_user)):
    """Get user data"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {current_user['github_token']}",
                "Accept": "application/json",
            },
        )
        user_data = response.json()

        return user_data