import json
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY_RACHIT"))

def prompt_template(content):
    prompt = f"""
    You are an advanced documentation generator designed to systematically extract and analyze code artifacts. Your primary objective is to comprehensively document functions and API routes from the provided source code.

        Input Requirements:
        - Supports multiple programming languages (Python, JavaScript, TypeScript, Java, etc.)
        - Handles different code formats and project structures
        - Extracts detailed information about functions and routes

        Documentation Generation Guidelines:

        1. Function Documentation:
        - Extract full function name
        - Capture function description (if available in comments, docstrings or try to understand the function definition if present)
        - Identify function parameters and their types
        - Note return types and potential exceptions
        - Include any decorators or special annotations
        - Only give parameter types if you are completely sure about the type, otherwise, leave it as "any"

        2. API Route Documentation:
        - Identify HTTP method (GET, POST, PUT, DELETE, etc.)
        - Extract complete route path
        - Note path parameters, query parameters
        - Capture request and response body schemas
        - List potential status codes
        - Include any authentication or middleware requirements

        Output Format:
        {{
        "functions": [
            {{
            "name": "string",
            "description": "string",
            "parameters": [
                {{
                "name": "string",
                "type": "string",
                "required": "boolean",
                "description": "string"
                }}
            ],
            "returnType": "string",
            "decorators": ["string"],
            "exceptions": ["string"]
            }}
        ],
        "routes": [
            {{
            "method": "string",
            "path": "string",
            "pathParams": ["string"],
            "queryParams": ["string"],
            "requestBody": {{
                "type": "string",
                "schema": "object"
            }},
            "responseBody": {{
                "type": "string",
                "schema": "object"
            }}
            }}
        ]
        }}

        This is the code you need to document:{content}"""
    return prompt

def get_functions_routes(data):
    '''
    Get functions and API routes from the repo contents
    '''
    intermediate_content = []
    for file in data:
        content=data[file]["content"]
        prompt = prompt_template(content)
        model = genai.GenerativeModel(
            "gemini-1.5-flash-latest",
            generation_config={"response_mime_type": "application/json"},
        )
        response = model.generate_content(prompt)
        response = json.loads(response.text)
        intermediate_content.append(response)
        break
    with open("functions_routes.json", "w") as file:
        json.dump(intermediate_content, file)



if __name__ == "__main__":
    file_path = "/Users/rachitdas/Desktop/doccie/backend/backup/repo_contents.json"
    with open(file_path, "r") as file:
        data = json.load(file)
    get_functions_routes(data)
