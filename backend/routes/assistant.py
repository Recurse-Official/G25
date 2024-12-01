from utils.repo import get_github_repo_contents
from dotenv import load_dotenv
import os
import json
import google.generativeai as genai
import asyncio
import aiohttp
import time
from fastapi import APIRouter
from pydantic import BaseModel
import base64

router = APIRouter()

class DocsRequest(BaseModel):
    owner: str
    repo: str
    token: str

load_dotenv()

def determine_file_type(file_path):
    """Determine if a file is server-side or user-side based on extension"""
    server_extensions = {'.py', '.php', '.rb', '.java', '.go', '.rs', '.cs', '.js'}
    user_extensions = {'.html', '.css', '.jsx', '.tsx', '.vue', '.svelte'}
    
    ext = os.path.splitext(file_path)[1].lower()
    if ext in server_extensions:
        return "server"
    elif ext in user_extensions:
        return "user"
    return "other"

async def process_with_ollama(session, content):
    """Process file content through Ollama API asynchronously with improved prompt"""
    async with session.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2:latest",
            "format": "json",
            "stream": False,
            "prompt": f"""You are an expert API documentation generator. Analyze the following code and extract detailed API endpoint information. Focus on:
            1. Complete endpoint paths
            2. HTTP methods (GET, POST, PUT, DELETE, etc.)
            3. Request parameters (query params, path params, request body)
            4. Response structure
            5. Authentication requirements
            6. Purpose/description of each endpoint

            Code to analyze:
            {content}

            Return a valid JSON object with the following structure:
            {{
                "endpoints": [
                    {{
                        "path": "/example",
                        "method": "GET",
                        "parameters": [],
                        "description": "Description of endpoint",
                    }}
                ],
            }}

            Important:
            - Extract only actual API endpoints from the code
            - Include all parameters, whether they're in the URL, query string, or request body
            - Provide accurate response structures based on the code
            - Include authentication requirements if specified
            - Group related endpoints with tags
            - Ensure the description clearly explains the endpoint's purpose
            - If you can't determine certain details, use reasonable defaults based on the code context

            Analyze every aspect of the code carefully to ensure accurate endpoint documentation."""
        }
    ) as response:
        response_data = await response.json()
        return response_data.get("response", "")
    
async def process_files(repo_contents):
    """Process files concurrently with a semaphore to limit concurrent requests"""
    semaphore = asyncio.Semaphore(2)  # Limit to 2 concurrent requests
    async with aiohttp.ClientSession() as session:
        tasks = []
        for file_path, file_info in repo_contents.items():
            if file_info["file_type"] == "server":
                tasks.append(process_file(session, semaphore, file_path, file_info))
        return await asyncio.gather(*tasks)

async def process_file(session, semaphore, file_path, file_info):
    """Process a single file with semaphore control"""
    async with semaphore:
        try:
            print(f"Processing {file_path}...")
            print(f"Content: {file_info['content'][:100]}...")  # Truncate content for display
            api_info = await process_with_ollama(session, file_info["content"])
            return file_path, json.loads(api_info)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return file_path, None

def generate_yaml_with_gemini(api_data):
    """Generate YAML documentation using Gemini"""
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    
    prompt = f"""You are an OpenAPI YAML generator. Convert this JSON to OpenAPI 3.0 specification YAML format. Output only the YAML content with no additional text, markdown, or code blocks. Do not include any explanations or notes.

    Requirements:
    - Use OpenAPI 3.0 format
    - Include only the YAML content
    - Start with 'openapi: 3.0.0'
    - Include proper paths, methods, parameters, request bodies, and responses
    - Exclude any commentary or explanations
    - Do not wrap the output in code blocks or markdown

    Input JSON:
    {json.dumps(api_data, indent=2)}"""
        
    response = model.generate_content(prompt)
    return response.text

async def save_to_github_branch(owner: str, repo: str, token: str, content: str,
                              branch: str = "doccie", filename: str = "documentation.yaml"):
    """
    Save content to a specific branch using GitHub REST API
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    base_url = "https://api.github.com"

    async with aiohttp.ClientSession() as session:
        try:
            # Step 1: Get the default branch's SHA
            url = f"{base_url}/repos/{owner}/{repo}/git/refs/heads"
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"Failed to get refs: {await response.text()}")
                refs = await response.json()
                default_ref = next((ref for ref in refs if ref["ref"].endswith("/main") or ref["ref"].endswith("/master")), None)
                if not default_ref:
                    raise Exception("Could not find default branch")
                default_sha = default_ref["object"]["sha"]

            # Step 2: Check if doccie branch exists
            url = f"{base_url}/repos/{owner}/{repo}/git/refs/heads/{branch}"
            async with session.get(url, headers=headers) as response:
                if response.status == 404:
                    # Create doccie branch
                    create_branch_data = {
                        "ref": f"refs/heads/{branch}",
                        "sha": default_sha
                    }
                    url = f"{base_url}/repos/{owner}/{repo}/git/refs"
                    async with session.post(url, headers=headers, json=create_branch_data) as response:
                        if response.status not in [201, 200]:
                            raise Exception(f"Failed to create branch: {await response.text()}")
                elif response.status != 200:
                    raise Exception(f"Failed to check branch: {await response.text()}")

            # Step 3: Check if file exists
            url = f"{base_url}/repos/{owner}/{repo}/contents/{filename}"
            params = {"ref": branch}
            async with session.get(url, headers=headers, params=params) as response:
                file_exists = response.status == 200
                if file_exists:
                    file_data = await response.json()
                    file_sha = file_data["sha"]
                else:
                    file_sha = None

            # Step 4: Create or update file
            url = f"{base_url}/repos/{owner}/{repo}/contents/{filename}"
            file_content_encoded = base64.b64encode(content.encode()).decode()
            
            update_data = {
                "message": f"{'Update' if file_exists else 'Create'} {filename}",
                "content": file_content_encoded,
                "branch": branch
            }
            
            if file_sha:
                update_data["sha"] = file_sha

            async with session.put(url, headers=headers, json=update_data) as response:
                if response.status not in [200, 201]:
                    raise Exception(f"Failed to {'update' if file_exists else 'create'} file: {await response.text()}")

            print(f"Successfully {'updated' if file_exists else 'created'} {filename} in {branch} branch")
            return True

        except Exception as e:
            print(f"Error saving to GitHub: {str(e)}")
            return False
    
@router.post("/generate-api-docs")
async def async_main(request: DocsRequest):
    start_time = time.time()

    print("Starting API documentation generation...")
    
    owner = request.owner
    repo = request.repo
    token = request.token
    
    # Try to get repository contents, fall back to sample file if it fails
    repo_contents = get_github_repo_contents(owner, repo, token)
    if not repo_contents:
        return {"Message": "Failed to retrieve repository contents"}    
    
    # Add file_type classification
    file_count = 0
    for file_path in repo_contents:
        repo_contents[file_path]["file_type"] = determine_file_type(file_path)
        if repo_contents[file_path]["file_type"] == "server":
            file_count += 1
    
    print(f"Found {file_count} server-side files to process")
    
    # Process server files with Ollama concurrently
    process_start = time.time()
    results = await process_files(repo_contents)
    process_end = time.time()
    
    # Convert results to dictionary
    api_routes = {file_path: result for file_path, result in results if result is not None}
    
    # Save API routes to file
    with open("api_routes.json", "w") as f:
        json.dump(api_routes, f, indent=2)
    
    # Generate YAML documentation
    yaml_content = generate_yaml_with_gemini(api_routes)
    
    #! Save yaml content to doccie branch
    upload_success = await save_to_github_branch(
        owner=owner,
        repo=repo,
        token=token,
        content=yaml_content
    )
    
    if not upload_success:
        return {"Message": "Failed to upload documentation to GitHub"}
    
    end_time = time.time()
    
    return {
        "Message": "API documentation generated and uploaded successfully",
        "Statistics": {
            "files_processed": file_count,
            "processing_time": process_end - process_start,
            "total_time": end_time - start_time
        }
    }