"""Static configuration read from environment (never hardcoded).

Env vars (with fallback defaults so tests run without extra setup):
- SHOWDOWN_REPO_URL  (default: public smogon/pokemon-showdown)
- SHOWDOWN_BRANCH    (default: master)
- SHOWDOWN_DATASETS_DIR  (default: /app/backend/.showdown_datasets)
- SHOWDOWN_ENABLE_CLONE  (default: "0" — sync records commit without cloning)
- IMPORTER_VERSION   (default: 0.1.0)
- APP_VERSION        (default: 0.1.0)
"""
from __future__ import annotations
import os


def repo_url() -> str:
    return os.environ.get(
        "SHOWDOWN_REPO_URL",
        "https://github.com/smogon/pokemon-showdown.git",
    )


def branch() -> str:
    return os.environ.get("SHOWDOWN_BRANCH", "master")


def datasets_dir() -> str:
    return os.environ.get(
        "SHOWDOWN_DATASETS_DIR",
        "/app/backend/.showdown_datasets",
    )


def clone_enabled() -> bool:
    return os.environ.get("SHOWDOWN_ENABLE_CLONE", "0") == "1"


def importer_version() -> str:
    return os.environ.get("IMPORTER_VERSION", "0.1.0")


def app_version() -> str:
    return os.environ.get("APP_VERSION", "0.1.0")
