import os
import re
import requests
import tempfile
import zipfile
import shutil
import json


def get_github_repo_contents(owner, repo, token, branch="main", output_file=None):
    """
    Download and extract a GitHub repository

    :param owner: GitHub repository owner
    :param repo: Repository name
    :param token: GitHub Personal Access Token
    :param branch: Repository branch (default is 'main')
    :param output_file: Optional path to save repository contents as JSON
    :return: Dictionary of repository contents with file paths and contents
    """
    # Create a temporary directory with elevated permissions
    try:
        temp_dir = tempfile.mkdtemp(prefix='doccie_')
        os.chmod(temp_dir, 0o755)  # Set read/write/execute permissions
        
        try:
            # Create temporary file for ZIP download
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".zip", dir=temp_dir, mode='wb'
            ) as temp_zip:
                # Set permissions for the temp file
                os.chmod(temp_zip.name, 0o644)
                
                # GitHub API URL for downloading repository ZIP
                base_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{branch}"

                # Prepare headers for authentication
                headers = {
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"token {token}",
                }

                # Download the repository ZIP
                response = requests.get(base_url, headers=headers, stream=True)
                response.raise_for_status()

                # Save the ZIP file
                for chunk in response.iter_content(chunk_size=8192):
                    temp_zip.write(chunk)

                temp_zip_path = temp_zip.name

                # Create a directory for extraction
                extract_dir = os.path.join(temp_dir, "extracted_repo")
                os.makedirs(extract_dir, exist_ok=True)

                # Unzip the repository
                with zipfile.ZipFile(temp_zip_path, "r") as zip_ref:
                    zip_ref.extractall(extract_dir)

                # Get the name of the extracted directory (GitHub ZIP has a unique prefix)
                extracted_dirs = [
                    d
                    for d in os.listdir(extract_dir)
                    if os.path.isdir(os.path.join(extract_dir, d))
                ]

                if not extracted_dirs:
                    raise ValueError("No directory found after extraction")

                # Full path to the extracted repository
                repo_path = os.path.join(extract_dir, extracted_dirs[0])

                # Parse repository contents
                repo_contents = parse_directory(repo_path)

                # Optionally save to JSON file
                if output_file and repo_contents:
                    save_to_json(repo_contents, output_file)

                return repo_contents
                
        except Exception as e:
            print(f"Error processing repository: {e}")
            return {}  # Return empty dict instead of None
            
        finally:
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except Exception as e:
        print(f"Error creating temporary directory: {e}")
        return {}  # Return empty dict instead of None


def parse_directory(directory):
    """
    Recursively parse directory contents with advanced filtering

    :param directory: Path to the directory
    :return: Dictionary of file paths and contents
    """
    # Comprehensive list of directories and patterns to ignore
    IGNORE_PATTERNS = [
        # Dependency and build directories
        r"^(node_modules|bower_components|jspm_packages|vendor|dist|build|out|target)",
        # Version control and IDE directories
        r"^(\.(git|svn|hg)|__pycache__|\.vscode|\.idea|\.eclipse)",
        # Compiled and cached files
        r"(\.pyc|\.pyo|\.pyd|\.class|\.log|\.sqlite3)$",
        # Large binary and media files
        r"\.(gif|jpg|jpeg|png|bmp|webp|mp4|avi|mov|mp3|wav|zip|tar|gz|7z|ipynb)$",
        # ignore package_lock.json
        r"package-lock.json",
    ]

    # Compile ignore patterns
    ignore_regex = re.compile("|".join(IGNORE_PATTERNS), re.IGNORECASE)

    contents = {}

    for root, dirs, files in os.walk(directory):
        # Remove ignored directories
        dirs[:] = [d for d in dirs if not ignore_regex.search(d)]

        for file in files:
            # Get full file path
            full_path = os.path.join(root, file)

            # Get relative path from repository root
            relative_path = os.path.relpath(full_path, directory)

            # Skip files matching ignore patterns
            if ignore_regex.search(relative_path):
                continue

            try:
                # Determine file size
                file_size = os.path.getsize(full_path)

                # Read file contents
                with open(full_path, "r", encoding="utf-8") as f:
                    file_content = f.read()

                contents[relative_path] = {
                    "path": relative_path,
                    "content": file_content,
                    "size": file_size,
                }

            except UnicodeDecodeError:
                # Handle binary files
                contents[relative_path] = {
                    "path": relative_path,
                    "content": "[Binary File]",
                    "size": file_size,
                }

            except Exception as e:
                contents[relative_path] = {
                    "path": relative_path,
                    "content": f"[Error reading file: {str(e)}]",
                    "size": 0,
                }

    return contents


def save_to_json(contents, output_file):
    """
    Save repository contents to a JSON file

    :param contents: Dictionary of repository contents
    :param output_file: Path to save the JSON file
    """
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(contents, f, indent=2, ensure_ascii=False)
        print(f"Repository contents saved to {output_file}")
    except Exception as e:
        print(f"Error saving to JSON: {e}")


# Example usage
if __name__ == "__main__":
    # Replace with your GitHub token, owner, and repo
    token = "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"
    owner = "Exterminator11"
    repo = "solvus_assignment"

    # Get repository contents
    repo_contents = get_github_repo_contents(
        owner, repo, token, output_file="repo_contents.json"  # Optional: save to JSON
    )

    if repo_contents:
        # Print some basic information
        print(f"Total files parsed: {len(repo_contents)}")

        # Example: Print first few file paths
        for path in list(repo_contents.keys())[:5]:
            print(f"File: {path}")