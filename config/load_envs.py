from dotenv import load_dotenv
import os
from pathlib import Path

project_root = Path(__file__).parent
load_dotenv(project_root / ".env")