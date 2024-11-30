from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
import httpx
import sqlite3
import logging
import os
from pydantic import BaseModel
from utils.auth import get_current_user
from models.data_models import ReadDocsRequest
import yaml
import jwt

router = APIRouter()

class Repository(BaseModel):
    id: int
    name: str
    full_name: str
    is_active: bool = False
    backend_path: Optional[str] = None

class RepoActivation(BaseModel):
    backend_path: str

class createDb(BaseModel):
    name: str

@router.get("/list")
async def list_repositories(current_user: dict = Depends(get_current_user)):
    """List all repositories the user has access to with their database status"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user/repos",
            headers={
                "Authorization": f"Bearer {current_user['github_token']}",
                "Accept": "application/json",
            },
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch repositories")
            
        repos = response.json()
        
        # try:
        db_path = os.path.join("backend/database", f"repos.db")
        print(db_path)
        with sqlite3.connect(db_path) as db:
            cursor = db.cursor()
            
            result = []
            for repo in repos:
                # Query database for each repository
                cursor.execute("SELECT is_active, backend_path FROM repos WHERE id = ?", (repo["id"],))
                db_data = cursor.fetchone()
                
                # Use database values if available, otherwise use defaults
                is_active = db_data[0] if db_data else False
                backend_path = db_data[1] if db_data else None
                
                result.append(
                    Repository(
                        id=repo["id"],
                        name=repo["name"],
                        full_name=repo["full_name"],
                        is_active=is_active,
                        backend_path=backend_path
                    )
                )
            return result
                
        # except sqlite3.Error as e:
        #     logging.error(f"Database error while fetching repository details: {e}")
        #     raise HTTPException(status_code=500, detail="Database error occurred")
        # except Exception as e:
        #     logging.error(f"Unexpected error while processing repositories: {e}")
        #     raise HTTPException(status_code=500, detail="An unexpected error occurred")
    
@router.get("/{repo_id}")
async def get_repository_details(repo_id: int, current_user: dict = Depends(get_current_user)):
    """Get detailed information about a specific repository"""
    async with httpx.AsyncClient() as client:
        # Get repo details
        response = await client.get(
            f"https://api.github.com/repositories/{repo_id}",
            headers={
                "Authorization": f"Bearer {current_user['github_token']}",
                "Accept": "application/json",
            },
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Repository not found")
            
        repo_data = response.json()
        
        # Get repository contents
        contents_response = await client.get(
            f"https://api.github.com/repos/{repo_data['full_name']}/contents",
            headers={
                "Authorization": f"Bearer {current_user['github_token']}",
                "Accept": "application/json",
            },
        )
        
        if contents_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch repository contents")
            
        contents = contents_response.json()
        
        # Extract directory structure
        async def get_directory_contents(path=""):
            dir_response = await client.get(
                f"https://api.github.com/repos/{repo_data['full_name']}/contents/{path}",
                headers={
                    "Authorization": f"Bearer {current_user['github_token']}",
                    "Accept": "application/json",
                },
            )
            
            if dir_response.status_code != 200:
                return []
                
            items = dir_response.json()
            structure = []
            
            for item in items:
                if item["type"] == "dir":
                    children = await get_directory_contents(item["path"])
                    structure.append({
                        "name": item["name"],
                        "path": item["path"],
                        "type": "directory",
                        "children": children
                    })
                else:
                    structure.append({
                        "name": item["name"],
                        "path": item["path"],
                        "type": "file"
                    })
                    
            return structure

        directory_structure = await get_directory_contents()
        
        return {
            "id": repo_data["id"],
            "name": repo_data["name"],
            "full_name": repo_data["full_name"],
            "default_branch": repo_data["default_branch"],
            "visibility": repo_data["private"] and "private" or "public",
            "directory_structure": directory_structure
        }
@router.post("/read_docs")
async def read_documentation(request: ReadDocsRequest):
    try:
        # Decode JWT to get GitHub token
        try:
            decoded_token = jwt.decode(request.access_token, options={"verify_signature": False})
            github_token = decoded_token.get('github_token')
            if not github_token:
                return {"Message": "GitHub token not found in JWT"}
        except jwt.InvalidTokenError:
            return {"Message": "Invalid JWT token"}

        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github.v3.raw",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            
            # Fetch documentation.yaml
            docs_url = f"https://api.github.com/repos/{request.full_name}/contents/documentation.yaml?ref=doccie"
            docs_response = await client.get(docs_url, headers=headers)
            
            # Fetch dependency.mermaid
            mermaid_url = f"https://api.github.com/repos/{request.full_name}/contents/dependency.mermaid?ref=doccie"
            mermaid_response = await client.get(mermaid_url, headers=headers)
            
            # Check for authentication errors
            if docs_response.status_code == 401 or mermaid_response.status_code == 401:
                return {
                    "Message": "GitHub authentication failed. Please check your token.",
                    "details": docs_response.text if docs_response.status_code == 401 else mermaid_response.text
                }
            
            # Check if files exist
            if docs_response.status_code == 404 and mermaid_response.status_code == 404:
                return {"Message": "Documentation files not found in doccie branch"}
            
            # Handle other error responses
            if docs_response.status_code != 200 or mermaid_response.status_code != 200:
                return {
                    "Message": "Failed to fetch documentation files",
                    "yaml_status": docs_response.status_code,
                    "mermaid_status": mermaid_response.status_code,
                    "yaml_response": docs_response.text if docs_response.status_code != 200 else None,
                    "mermaid_response": mermaid_response.text if mermaid_response.status_code != 200 else None
                }
                
            try:
                yaml_content = yaml.safe_load(docs_response.text) if docs_response.status_code == 200 else None
                mermaid_content = mermaid_response.text if mermaid_response.status_code == 200 else None
            except yaml.YAMLError as e:
                return {"Message": f"Invalid YAML format: {str(e)}"}
                
            return {
                "Message": "Documentation fetched successfully",
                "data": yaml_content,
                "dependency": mermaid_content
            }
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")