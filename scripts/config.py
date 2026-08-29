"""Shared, portable project-path configuration for all analysis scripts."""

import os
from pathlib import Path


# By default, the project root is the parent of this scripts folder.
# Advanced users may set EV_CHARGING_PROJECT_DIR to use another location.
PROJECT_DIR = Path(
    os.environ.get(
        "EV_CHARGING_PROJECT_DIR",
        Path(__file__).resolve().parents[1]
    )
).resolve()
