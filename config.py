import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env if present
load_dotenv(BASE_DIR / ".env")

# Detect serverless environment (e.g. Vercel)
IS_SERVERLESS = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
DEFAULT_STORAGE = Path("/tmp") if IS_SERVERLESS else BASE_DIR

# If running on serverless, copy pre-bundled db to /tmp for write access
if IS_SERVERLESS:
    bundled_db = BASE_DIR / "resume_enhancer.db"
    tmp_db = DEFAULT_STORAGE / "resume_enhancer.db"
    if bundled_db.exists() and not tmp_db.exists():
        try:
            shutil.copyfile(str(bundled_db), str(tmp_db))
        except Exception:
            pass


class Config:
    """Application configuration parameters."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-ai-resume-enhancer-2026")
    
    # Storage paths (serverless safe)
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", str(DEFAULT_STORAGE / "uploads"))
    GENERATED_FOLDER = os.environ.get("GENERATED_FOLDER", str(DEFAULT_STORAGE / "generated_resumes"))
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(DEFAULT_STORAGE / "resume_enhancer.db"))
    
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
try:
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.GENERATED_FOLDER, exist_ok=True)
except Exception:
    pass
