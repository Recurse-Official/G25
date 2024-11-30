import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time

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

def mermaid_template(json_intermediate):
    '''
    Generate Mermaid template from the JSON intermediate
    '''
    prompt = f"""

This is the input json: {json_intermediate}
    "input_format": {{
        "description": "Given a JSON array containing API details with 'functions' and 'routes' arrays",
        "expected_structure": "Functions array should have function details (name, parameters, return type, decorators) and Routes array should have API endpoint details (method, path, request/response schemas)"
    }},
    "output_requirements": {{
        "format": "Return only the Mermaid graph code as a single line string",
        "syntax": "Use graph TD for top-down diagram",
        "must_include": [
            "All routes with HTTP methods",
            "All functions",
            "All request/response schemas",
            "All service dependencies",
            "Data flow between components",
            "Proper styling for nodes"
        ]
    }},
    "node_naming_convention": {{
        "routes": "R[HTTP_METHOD /path]",
        "functions": "F[function_name]",
        "services": "S[ServiceName]",
        "schemas": "Schema[name<br/>field1: type<br/>field2: type]"
    }},
    "relationship_rules": [
        "Connect routes to functions using -->",
        "Show service dependencies using ==>",
        "Show data flow using -.->",
        "Connect request/response schemas using -->"
    ],
    "style_definitions":{ {
        "routes": "fill:#bbf,stroke:#333,stroke-width:1px",
        "functions": "fill:#dfd,stroke:#333,stroke-width:1px",
        "services": "fill:#fdd,stroke:#333,stroke-width:1px",
        "schemas": "fill:#fff,stroke:#333,stroke-width:1px"
    }},
    This is an example output for your reference:
    {{"code": "graph TD; A[API] --> B[Route1]; B --> C[Function1]; C --> D[Schema1]"}}
    """
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
        time.sleep(1)
        
    with open("functions_routes.json", "w") as file:
        json.dump(intermediate_content, file)

def mermaid_code(json_intermediate):
    '''
    Generate Mermaid code from the intermediate JSON
    '''
    mermaid_prompt=mermaid_template(json_intermediate)
    model = genai.GenerativeModel(
        "gemini-1.5-flash-latest",
        generation_config={"response_mime_type": "application/json"},
    )
    response = model.generate_content(mermaid_prompt)
    response = json.loads(response.text)
    with open("mermaid_code.json", "w") as file:
        json.dump(response, file)

if __name__ == "__main__":
    # file_path = "/Users/rachitdas/Desktop/doccie/backend/backup/repo_contents.json"
    # with open(file_path, "r") as file:
    #     data = json.load(file)
    # get_functions_routes(data)

    with open("/Users/rachitdas/Desktop/G25/backup/functions_routes.json", "r") as file:
        json_intermediate = json.load(file)
        mermaid_code(json_intermediate)
