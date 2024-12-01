from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
import json
import os 
from dotenv import load_dotenv

from database_models.token_store import delete_record
load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Validate JWT token and return user info
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token, 
            os.getenv("JWT_SECRET_KEY"), 
            algorithms=os.getenv("JWT_ALGORITHM")
        )
        
        # Extract user data from payload
        user_data = {
            "github_token": payload.get("github_token"),
            "user_id": payload.get("user_id"),
            "username": payload.get("username")
        }
        if not all(user_data.values()):
            print("user data error")
            raise credentials_exception
            
        # print("user data:\n",json.dumps(user_data, indent=2))
        return user_data
        
    except (jwt.PyJWTError, HTTPException):
        print("user data error jwt")
        # delete_record() #TODO: delete the record from the database
        raise credentials_exception