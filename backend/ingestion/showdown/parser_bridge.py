"""Python wrapper around the Node-side Showdown parser.

Invokes ``parser/parse.mjs`` as a subprocess and returns the parsed
result as a Python dict. Keeps the parsed JSON on disk (inside the
dataset dir) as the RAW SNAPSHOT, per architecture requirements.
"""
from __future__ import annotations
import json
import subprocess
from pathlib import Path

_PARSER = Path(__file__).parent / "parser" / "parse.mjs"


def parse_repo(repo_dir: str, dataset_dir: str) -> tuple[dict, dict]:
    """Parse a cloned Showdown repo. Returns ``(result, errors)``.

    ``result`` is a dict keyed by category (pokedex, moves, ...).
    ``errors`` maps categories that failed to their error string.
    """
    out_path = Path(dataset_dir) / "parsed.json"
    proc = subprocess.run(
        ["node", str(_PARSER), repo_dir, str(out_path)],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"parser failed: {proc.stderr or proc.stdout}")
    data = json.loads(out_path.read_text())
    return data.get("result", {}), data.get("errors", {})
