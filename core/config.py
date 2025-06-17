import os
from pathlib import Path

# Base directory for all Inquiro data storage based on the operating system
if os.name == 'nt':  # Windows
    INQUIRO_BASE_DIR = Path("C:/inquiro")
elif os.name == 'posix':
    INQUIRO_BASE_DIR = Path("/inquiro")

# Data storage directories
DATA_PATH = str(INQUIRO_BASE_DIR / "data")
FAISS_PATH = str(INQUIRO_BASE_DIR / "database" / "faiss_index")