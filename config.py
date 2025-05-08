# config.py
from pathlib import Path

# Core paths
PROJECT_ROOT = Path(__file__).parent
RESULTS_ROOT = PROJECT_ROOT / "results"
TEMPLATE_PATH = PROJECT_ROOT / "prompt_template.j2"
DB_PATH = PROJECT_ROOT / "experiments.db"

# Defaults
DEFAULT_K = 3
DEFAULT_NUM_FACTS = 6

