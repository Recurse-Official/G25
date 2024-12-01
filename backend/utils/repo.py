import os
import re
import requests
import tempfile
import zipfile
import shutil
import json
from urllib.parse import urlparse

def get_github_repo_contents(owner, repo, token, branch="main", output_file=None):
    """
    Download and extract a GitHub repository with improved error handling and validation
    
    :param owner: GitHub repository owner
    :param repo: Repository name
    :param token: GitHub Personal Access Token
    :param branch: Repository branch (default is 'main')
    :param output_file: Optional path to save repository contents as JSON
    :return: Dictionary of repository contents with file paths and contents
    """
    temp_dir = None
    try:
        # Validate token format
        if not token.startswith(('ghp_', 'gho_', 'github_pat_')):
            raise ValueError("Invalid GitHub token format")

        # Create a temporary directory
        temp_dir = tempfile.mkdtemp(prefix='doccie_')
        os.chmod(temp_dir, 0o755)

        # Create temporary file for ZIP download
        temp_zip = os.path.join(temp_dir, "repo.zip")
        
        # GitHub API headers
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        # First verify repository access
        verify_url = f"https://api.github.com/repos/{owner}/{repo}"
        verify_response = requests.get(verify_url, headers=headers)
        if verify_response.status_code != 200:
            raise Exception(f"Repository access failed: {verify_response.json().get('message', 'Unknown error')}")

        # Download URL for the repository
        download_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{branch}"
        
        # Download the repository
        print(f"Downloading repository {owner}/{repo}...")
        with requests.get(download_url, headers=headers, stream=True) as response:
            response.raise_for_status()
            with open(temp_zip, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        # Verify the downloaded file is a valid ZIP
        if not zipfile.is_zipfile(temp_zip):
            raise Exception("Downloaded file is not a valid ZIP file")

        # Create extraction directory
        extract_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)

        # Extract the repository
        print("Extracting repository contents...")
        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # Get the extracted directory name (GitHub adds a unique prefix)
        extracted_dirs = [d for d in os.listdir(extract_dir) 
                        if os.path.isdir(os.path.join(extract_dir, d))]
        if not extracted_dirs:
            raise Exception("No directory found after extraction")

        repo_path = os.path.join(extract_dir, extracted_dirs[0])
        
        # Parse repository contents
        print("Parsing repository files...")
        repo_contents = parse_directory(repo_path)

        # Save to JSON if requested
        if output_file and repo_contents:
            save_to_json(repo_contents, output_file)

        return repo_contents

    except requests.exceptions.RequestException as e:
        print(f"Network error: {str(e)}")
        return {}
    except zipfile.BadZipFile:
        print("Error: Invalid or corrupted ZIP file")
        return {}
    except Exception as e:
        print(f"Error processing repository: {str(e)}")
        return {}
    finally:
        # Clean up temporary directory
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


def parse_directory(directory):
    """
    Recursively parse directory contents with improved binary file handling
    """
    IGNORE_PATTERNS = [
        r"^(node_modules|bower_components|jspm_packages|vendor|dist|build|out|target)",
        r"^(\.(git|svn|hg)|__pycache__|\.vscode|\.idea|\.eclipse)",
        r"(\.pyc|\.pyo|\.pyd|\.class|\.log|\.sqlite3)$",
        r"\.(gif|jpg|jpeg|png|bmp|webp|mp4|avi|mov|mp3|wav|zip|tar|gz|7z|ipynb)$",
        r"package-lock.json",
    ]

    ignore_regex = re.compile("|".join(IGNORE_PATTERNS), re.IGNORECASE)
    contents = {}

    for root, dirs, files in os.walk(directory):
        # Filter directories
        dirs[:] = [d for d in dirs if not ignore_regex.search(d)]

        for file in files:
            relative_path = os.path.relpath(os.path.join(root, file), directory)
            
            # Skip ignored files
            if ignore_regex.search(relative_path):
                continue

            full_path = os.path.join(root, file)
            try:
                file_size = os.path.getsize(full_path)
                
                # Try to detect if file is binary
                is_binary = False
                try:
                    with open(full_path, 'tr') as check_file:
                        check_file.read(1024)
                except UnicodeDecodeError:
                    is_binary = True

                if is_binary:
                    contents[relative_path] = {
                        "path": relative_path,
                        "content": "[Binary File]",
                        "size": file_size,
                    }
                else:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        contents[relative_path] = {
                            "path": relative_path,
                            "content": f.read(),
                            "size": file_size,
                        }

            except Exception as e:
                print(f"Error reading file {relative_path}: {str(e)}")

    return contents


def save_to_json(contents, output_file):
    """Save repository contents to JSON with error handling"""
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(contents, f, indent=2, ensure_ascii=False)
        print(f"Repository contents saved to {output_file}")
    except Exception as e:
        print(f"Error saving to JSON: {str(e)}")