"""Gemini API client and .env loader.

No external dependencies — uses only Python standard library.
"""

from __future__ import annotations

import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
DEFAULT_MODEL = "gemini-3-pro-image-preview"


# ---------------------------------------------------------------------------
# .env loader
# ---------------------------------------------------------------------------

def load_dotenv(env_path: Path) -> dict[str, str]:
    """Parse a .env file and return key-value pairs.

    Supports:
        KEY=value
        KEY="value"
        KEY='value'
        # comments
        empty lines
    """
    env_vars: dict[str, str] = {}
    if not env_path.is_file():
        return env_vars
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            env_vars[key] = value
    return env_vars


def get_api_key(project_root: Path) -> str:
    """Retrieve the Gemini API key from environment or .env file.

    Search order:
        1. Environment variable ``Google_Image_API``
        2. ``.env`` in the current working directory (user's project)
        3. ``.env`` in the script's project root (plugin install location)
    """
    key = os.environ.get("Google_Image_API")
    if key:
        return key

    # Search order: cwd (user's project) → home dir → plugin root
    search_paths = []
    cwd = Path.cwd()
    home_env = Path.home() / ".env"
    if cwd != project_root:
        search_paths.append(cwd / ".env")
    search_paths.append(home_env)
    search_paths.append(project_root / ".env")

    for env_path in search_paths:
        env_vars = load_dotenv(env_path)
        key = env_vars.get("Google_Image_API")
        if key:
            return key

    print(
        "Error: API key not found.\n"
        "Set the 'Google_Image_API' environment variable or add it to .env\n"
        f"Searched: {', '.join(str(p) for p in search_paths)}",
        file=sys.stderr,
    )
    sys.exit(1)


# ---------------------------------------------------------------------------
# Image generation
# ---------------------------------------------------------------------------

def generate_image(
    prompt: str,
    api_key: str,
    model: str = DEFAULT_MODEL,
) -> bytes:
    """Call the Gemini API to generate an image from a text prompt.

    Returns raw PNG image bytes.
    Raises RuntimeError on API or network errors.
    """
    url = f"{API_BASE}/{model}:generateContent?key={api_key}"

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
        },
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = ""
        try:
            error_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        raise RuntimeError(
            f"API request failed (HTTP {e.code}): {e.reason}\n{error_body}"
        ) from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error: {e.reason}") from e

    candidates = body.get("candidates", [])
    if not candidates:
        block_reason = body.get("promptFeedback", {}).get("blockReason", "")
        if block_reason:
            raise RuntimeError(f"Content blocked by API: {block_reason}")
        raise RuntimeError(
            f"No candidates in API response:\n{json.dumps(body, indent=2)}"
        )

    parts = candidates[0].get("content", {}).get("parts", [])
    for part in parts:
        inline_data = part.get("inlineData")
        if inline_data and inline_data.get("data"):
            return base64.b64decode(inline_data["data"])

    raise RuntimeError(
        f"No image data found in API response:\n"
        f"{json.dumps(body, indent=2, ensure_ascii=False)}"
    )
