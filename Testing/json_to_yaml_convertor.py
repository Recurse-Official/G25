import yaml

def convert_to_openapi_yaml(json_data):
    """
    Convert the JSON API documentation to OpenAPI 3.0.0 YAML format
    """
    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "API Documentation",
            "version": "1.0.0",
            "description": "Automatically generated API documentation"
        },
        "paths": {}
    }
    
    # Extract routes from JSON data
    routes = json_data[0]["routes"]
    
    # Process each route
    for route in routes:
        path = route["path"]
        method = route["method"].lower()
        
        # Initialize path if it doesn't exist
        if path not in openapi_spec["paths"]:
            openapi_spec["paths"][path] = {}
            
        # Create method specification
        method_spec = {
            "summary": f"{method.upper()} {path}",
            "parameters": [],
            "responses": {
                "200": {
                    "description": "Successful response",
                    "content": {}
                }
            }
        }
        
        # Add path parameters
        for param in route["pathParams"]:
            method_spec["parameters"].append({
                "name": param,
                "in": "path",
                "required": True,
                "schema": {
                    "type": "string"
                }
            })
            
        # Add query parameters
        for param in route["queryParams"]:
            method_spec["parameters"].append({
                "name": param,
                "in": "query",
                "schema": {
                    "type": "string"
                }
            })
            
        # Add request body if it exists
        if route["requestBody"]["type"] != "null":
            method_spec["requestBody"] = {
                "required": True,
                "content": {
                    route["requestBody"]["type"]: {
                        "schema": parse_schema(route["requestBody"]["schema"])
                    }
                }
            }
            
        # Add response body
        if route["responseBody"]["type"] != "null":
            method_spec["responses"]["200"]["content"] = {
                "application/json": {
                    "schema": parse_schema(route["responseBody"]["schema"])
                }
            }
            
        # Add method specification to path
        openapi_spec["paths"][path][method] = method_spec
    
    # Convert to YAML
    return yaml.dump(openapi_spec, sort_keys=False, allow_unicode=True)

def parse_schema(schema_str):
    """
    Parse schema string into OpenAPI schema object
    """
    if schema_str == "null":
        return {"type": "null"}
    
    # Remove single quotes and convert to dict
    schema_str = schema_str.replace("'", '"')
    
    # Handle simple types
    if schema_str in ["str", "string"]:
        return {"type": "string"}
    elif schema_str in ["int", "integer"]:
        return {"type": "integer"}
    elif schema_str in ["bool", "boolean"]:
        return {"type": "boolean"}
    
    # Parse complex schema strings
    try:
        import json
        schema_dict = json.loads(schema_str)
        
        # Convert to OpenAPI schema format
        properties = {}
        for key, value in schema_dict.items():
            if value == "str":
                properties[key] = {"type": "string"}
            elif value == "boolean":
                properties[key] = {"type": "boolean"}
            elif value == "UploadFile":
                properties[key] = {"type": "string", "format": "binary"}
            else:
                properties[key] = {"type": "string"}
                
        return {
            "type": "object",
            "properties": properties
        }
    except:
        return {"type": "object"}

if __name__ == "__main__":
    import json
    
    with open(r"D:\Workspace\Hackathons\doccie\G25\Testing\functions_routes.json", "r") as f:
        json_data = json.load(f)
    
    yaml_output = convert_to_openapi_yaml(json_data)
    
    with open("openapi_spec.yaml", "w") as f:
        f.write(yaml_output)