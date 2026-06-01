import os
from pathlib import Path
from typing import Final

BASE_URL: Final[str] = os.getenv("EVAL_BASE_URL", "http://localhost:8000")
PROMPTS_PATH: Final[Path] = Path(__file__).with_name("prompts.json")
REPORTS_DIR: Final[Path] = Path(__file__).with_name("reports")
