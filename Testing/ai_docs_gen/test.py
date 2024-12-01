from dotenv import load_dotenv
import os
import json
import requests
import base64
import google.generativeai as genai
import asyncio
import aiohttp
import time
from typing import Dict, Optional

load_dotenv()

class GitHubRepoAccess:
    def __init__(self, token: str, owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.base_url = "https://api.github.com"
    
    async def get_repo_contents(self, path: str = "") -> Optional[Dict]:
        """
        Recursively fetch repository contents using GitHub's REST API
        Returns a dictionary of file paths and their contents
        """
        contents = {}
        try:
            url = f"{self.base_url}/repos/{self.owner}/{self.repo}/contents/{path}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status != 200:
                        raise Exception(f"GitHub API error: {response.status} - {await response.text()}")
                    
                    items = await response.json()
                    
                    tasks = []
                    for item in items:
                        if item["type"] == "file":
                            tasks.append(self.fetch_file_content(session, item["path"], item["download_url"]))
                        elif item["type"] == "dir":
                            tasks.append(self.get_repo_contents(item["path"]))
                    
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for result in results:
                        if isinstance(result, dict):
                            contents.update(result)
            
            return contents
        
        except Exception as e:
            print(f"Error accessing repository: {str(e)}")
            return None
    
    async def fetch_file_content(self, session: aiohttp.ClientSession, path: str, download_url: str) -> Dict:
        """Fetch individual file content"""
        try:
            async with session.get(download_url, headers=self.headers) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch file {path}: {response.status}")
                content = await response.text()
                return {path: {
                    "content": content,
                    "file_type": self.determine_file_type(path)
                }}
        except Exception as e:
            print(f"Error fetching file {path}: {str(e)}")
            return {}

    @staticmethod
    def determine_file_type(file_path: str) -> str:
        """Determine if a file is server-side or user-side based on extension"""
        server_extensions = {'.py', '.php', '.rb', '.java', '.go', '.rs', '.cs', '.js'}
        user_extensions = {'.html', '.css', '.jsx', '.tsx', '.vue', '.svelte'}
        
        ext = os.path.splitext(file_path)[1].lower()
        if ext in server_extensions:
            return "server"
        elif ext in user_extensions:
            return "user"
        return "other"

async def main():
    # Load configuration from environment variables
    token = os.getenv("GITHUB_TOKEN")
    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO")
    
    if not all([token, owner, repo]):
        raise ValueError("Missing required environment variables: GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO")
    
    # Initialize GitHub repo access
    github = GitHubRepoAccess(token, owner, repo)
    
    print("Starting API documentation generation...")
    
    # Get repository contents
    repo_contents = await github.get_repo_contents()
    
    if not repo_contents:
        print("Failed to fetch repository contents. Check your credentials and repository access.")
        return
    
    # Count server-side files
    server_files = {path: info for path, info in repo_contents.items() 
                   if info["file_type"] == "server"}
    
    print(f"Found {len(server_files)} server-side files to process")
    
    # Continue with the rest of your processing logic...

if __name__ == "__main__":
    asyncio.run(main())