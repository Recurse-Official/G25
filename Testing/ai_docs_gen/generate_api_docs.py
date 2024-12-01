from get_repo_contents import get_github_repo_contents
from dotenv import load_dotenv
import os
import json
import requests
import google.generativeai as genai
import asyncio
import aiohttp
import time

load_dotenv()
SAMPLE_FILE = r"D:\Workspace\Hackathons\doccie\G25\Testing\ai_docs_gen\repo_contents.json"

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
    """Process file content through Ollama API asynchronously"""
    async with session.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5-coder:3b",
            "format": "json",
            "stream": False,
            "prompt": f"""Analyze this code and extract API Endpoints information in JSON format. Only API Endpoints are needed, no other information:
            {content}
            Return only valid JSON with this structure:
            {{
                "endpoints": [
                    {{
                        "path": "/example",
                        "method": "GET",
                        "parameters": [],
                        "description": "Description of endpoint",
                    }}
                ],
            }}"""
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
            api_info = await process_with_ollama(session, file_info["content"])
            return file_path, json.loads(api_info)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return file_path, None

def generate_yaml_with_gemini(api_data):
    """Generate YAML documentation using Gemini"""
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    
    prompt = f"""This JSON contains information about API endpoints. I need you to convert this JSON to YAML format. Ensure it is compatible with OpenAPI 3.0 specification format and it renders with no issues:
    {json.dumps(api_data, indent=2)}
    
    Use OpenAPI 3.0 specification format."""
    
    response = model.generate_content(prompt)
    return response.text

async def async_main():
    start_time = time.time()
    
    token = os.getenv("GITHUB_TOKEN")
    owner = "srujan-landeri"
    repo = "doccie"

    print("Starting API documentation generation...")
    
    # Try to get repository contents, fall back to sample file if it fails
    repo_contents = get_github_repo_contents(owner, repo, token)
    if not repo_contents:
        print("Using sample JSON file instead...")
        with open(SAMPLE_FILE, "r") as f:
            repo_contents = json.load(f)
    
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
    
    # Save YAML documentation
    with open("api_documentation.yaml", "w") as f:
        f.write(yaml_content)
    
    end_time = time.time()
    
    print(f"\nProcessing Statistics:")
    print(f"Total files processed: {file_count}")
    print(f"Ollama processing time: {process_end - process_start:.2f} seconds")
    print(f"Total execution time: {end_time - start_time:.2f} seconds")

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()