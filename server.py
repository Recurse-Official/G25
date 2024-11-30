from fastapi import FastAPI, Request, HTTPException
import json
import hmac
import hashlib
import uvicorn

app = FastAPI()

# GITHUB_SECRET = "your_github_secret"

# def verify_signature(request: Request, payload: bytes) -> bool:
#     signature = request.headers.get("X-Hub-Signature-256")
#     if signature is None:
#         return False

#     sha_name, signature = signature.split('=')
#     if sha_name != 'sha256':
#         return False

#     mac = hmac.new(GITHUB_SECRET.encode(), msg=payload, digestmod=hashlib.sha256)
#     return hmac.compare_digest(mac.hexdigest(), signature)

@app.get("/")
def health_check():
    return "🚀🚀🚀The server is up"

@app.post("/github-webhook")
async def github_webhook(request: Request):
    # if not verify_signature(request, payload):
    #     raise HTTPException(status_code=400, detail="Invalid signature")
    #print content of the payload
    payload = request.headers
    print(json.dumps(await request.json(), indent=2))
    # print("Payload received from GitHub:", payload)
    # print(json.loads(payload))
    #print the response payload from github



    event = request.headers.get("X-GitHub-Event")
    if event == "push":
        # Handle push event
        return {"message": "Push event received"}
    else:
        return {"message": f"Unhandled event: {event}"}

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=80, reload=True)# restart on file change
