from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
import httpx
from datetime import datetime, timedelta
import jwt
import json

from utils.auth import get_current_user
from database_models.token_store import save_token

import os
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()

@router.post("/webhook")
async def github_webhook(request:Request):
    payload_headers = request.headers
    payload = await request.json()
    print("Github webhook: \n",json.dumps(payload, indent=2))
    # print("Payload received from GitHub:", payload)
    # print(json.loads(payload))
    #print the response payload from github

    event = request.headers.get("X-GitHub-Event")
    if event == "push":
        # Handle push event
        return {"message": "Push event received"}
    else:
        return {"message": f"Unhandled event: {event}"}
    