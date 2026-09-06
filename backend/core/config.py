import os
from dotenv import load_dotenv

load_dotenv()

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
MODEL_DIR = os.path.join(DATA_DIR, "onnx_model")
DB_PATH = os.path.join(DATA_DIR, "clauseguard.db")

# Ensure required runtime directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Security & API credentials
SECRET_KEY = os.getenv("SECRET_KEY", "clauseguard-super-secret-jwt-key-2026-secure-auth")
TOKEN_EXPIRATION_SECONDS = 60 * 60 * 24 * 7  # 7 days
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Supported file formats
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
