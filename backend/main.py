"""
ClauseGuard API – Application Entry Point

A slim main module that creates the FastAPI app, applies middleware,
initialises the database, and includes all routers from the api package.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.core.config import UPLOAD_DIR
from backend.core.database import init_db
from backend.api import api_router

# ── Application factory ───────────────────────────────────────────────────────

app = FastAPI(
    title="ClauseGuard API",
    description="AI-powered contract risk analysis engine.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure the uploads directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialise the SQLite database (creates tables if missing)
init_db()

# Register every API router
app.include_router(api_router)

# ── Static file serving (production build) ────────────────────────────────────

if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
elif os.path.exists("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")