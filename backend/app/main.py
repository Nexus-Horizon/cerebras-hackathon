import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routers import example, analyze, tasks, metrics, leaderboard, qwen_api

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(metrics.router)
app.include_router(example.router)
app.include_router(analyze.router)
app.include_router(tasks.router)
app.include_router(leaderboard.router)
app.include_router(qwen_api.router)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    file_path = os.path.join("app", "static", "favicon.ico")
    return FileResponse(file_path)
