from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from routes.authentication import router as auth_router
from routes.repository import router as repo_router
from routes.repository import router as db_router
from routes.github import router as github_router
from routes.assistant import router as assistant_router

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(repo_router, prefix="/api/repo", tags=["repo"])
app.include_router(db_router, prefix="/api/db", tags=["db"])
app.include_router(github_router, prefix="/api/github", tags=["github"])
app.include_router(assistant_router, prefix="/api/assistant", tags=["assistant"])

# Root endpoint
@app.get("/")
async def root():
    return {"message": "API is running"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)