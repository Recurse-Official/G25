from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
import httpx
from datetime import datetime, timedelta
import jwt
import json

from utils.auth import get_current_user
from .assistant import async_main
from database_models.token_store import save_token, read_token
from models.data_models import addRepo
from .database import add_user, get_data, remove_repo

import os
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()

GITHUB_API_URL = "https://api.github.com"
GITHUB_CALLBACK_URL = os.getenv("GITHUB_CALLBACK_URL")
DOC_BRANCH = "doccie"

@router.post("/create-webhook")
async def create_github_webhook(addRepoRequest:addRepo, current_user: dict = Depends(get_current_user)):
    headers={
                "Authorization": f"Bearer {current_user['github_token']}",
                "Accept": "application/json",
    }

    data = {
        "name": "web",
        "active": True,
        "events": ["push"], #TODO: add for pr as well, also make the app raise a pr to the doc branch
        "config": {
            "url": GITHUB_CALLBACK_URL,
            "content_type": "json"
        }
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{GITHUB_API_URL}/repos/{current_user['username']}/{addRepoRequest.name}/hooks", headers=headers, json=data) #! maybe full_name instead of name
        response_json = response.json()
        print("webhook create response: ", json.dumps(response_json,indent=2))
        if response.status_code == 201:
            print({"message": "Webhook created successfully"})
            addRepoRequest.webhook_id = response_json["id"]
            return add_user(addRepoRequest)
        else:
            raise HTTPException(status_code=response.status_code, detail=response.json())


@router.post("/webhook")
async def github_webhook(request:Request):
    payload_headers = request.headers
    print("Github webhook headers: ",request.headers.get("X-GitHub-Event"))
    payload = await request.json()
    print("Github webhook callback: \n",json.dumps(payload, indent=2))
    # print("Payload received from GitHub:", payload)
    # print(json.loads(payload))
    #print the response payload from github


    event = request.headers.get("X-GitHub-Event")
    if (event == "push" or event == "ping") and (DOC_BRANCH not in payload.get("ref","")):
        token = read_token(payload["repository"]["owner"]["id"])
        if token is None:
            raise HTTPException(status_code=404, detail="Token not found during webhook event")
        print("Calling api documentation generation")
        generate_api_docs = await async_main({
            "owner":payload["repository"]["owner"]["login"],
            "repo": payload["repository"]["name"],
            "token":  token.token
        })

        print("API documentation generation completed", generate_api_docs)
        # Handle push event
        return {"message": "Push event received"}
    else:
        return {"message": f"Unhandled event: {event}"}
    

@router.delete("/delete-webhook")
async def delete_github_webhook(addRepoRequest:addRepo, current_user: dict = Depends(get_current_user)):
    headers = {
        "Authorization": f"Bearer {current_user['github_token']}",
        "Accept": "application/json",
    }

    get_data_response = get_data(addRepoRequest.id)
    print("Get data response: ", get_data_response)

    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{GITHUB_API_URL}/repos/{current_user['username']}/{addRepoRequest.name}/hooks/{get_data_response.webhook_id}", headers=headers)
        if response.status_code == 204:
            print("Web hook deleted successfully")
            return remove_repo(addRepoRequest.id)
            # return {"message": "Webhook deleted successfully"}
        else:
            raise HTTPException(status_code=response.status_code, detail=response.json())
