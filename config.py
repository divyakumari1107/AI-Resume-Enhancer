import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env if present
load_dotenv(BASE_DIR / ".env")


class Config:
    """Application configuration parameters."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-ai-resume-enhancer-2026")
    
    # Storage paths
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", str(BASE_DIR / "uploads"))
    GENERATED_FOLDER = os.environ.get("GENERATED_FOLDER", str(BASE_DIR / "generated_resumes"))
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(BASE_DIR / "resume_enhancer.db"))
    
    # File upload restrictions
    ALLOWED_EXTENSIONS = {"pdf", "docx"}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size
    
    # Gemini API configuration
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Application settings
    APP_NAME = "AI Resume Enhancer & ATS Analyzer"
    VERSION = "2.0.0"


# Ensure necessary runtime directories exist
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.GENERATED_FOLDER, exist_ok=True)
