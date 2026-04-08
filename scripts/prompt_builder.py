"""Prompt assembly and style management."""

from __future__ import annotations

import sys
from pathlib import Path

VALID_ASPECT_RATIOS = ["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3"]

_FALLBACK_STYLE = (
    "Style: Clean minimalist infographic in the style of IDEO or McKinsey consulting frameworks.\n"
    "Light warm background (#FAFAF8 or off-white). Bold sans-serif typography.\n"
    "Limited color palette: one accent color + neutral grays.\n"
    "Generous whitespace. No gradients or 3D effects. Flat geometric shapes only.\n"
    "Hand-drawn style arrows and connectors. Professional but approachable.\n"
    "High resolution."
)


def load_default_style(styles_dir: Path) -> str:
    """Load the default style prefix from file, with inline fallback."""
    style_file = styles_dir / "default.txt"
    if style_file.is_file():
        return style_file.read_text(encoding="utf-8").strip()
    return _FALLBACK_STYLE


def resolve_style(
    *,
    style_prefix: str | None = None,
    style_file: str | None = None,
    use_default: bool = False,
    styles_dir: Path | None = None,
) -> str:
    """Determine style text from the various style options."""
    if style_prefix:
        return style_prefix
    if style_file:
        sf = Path(style_file)
        if sf.is_file():
            return sf.read_text(encoding="utf-8").strip()
        print(f"Warning: Style file not found: {sf}", file=sys.stderr)
        return ""
    if use_default and styles_dir:
        return load_default_style(styles_dir)
    return ""


def build_prompt(
    *,
    prompt_text: str | None = None,
    prompt_file: str | None = None,
    style: str = "",
    aspect: str | None = None,
) -> str:
    """Assemble the final prompt from components.

    Args:
        prompt_text: Direct prompt string.
        prompt_file: Path to a file containing the prompt.
        style: Style prefix to prepend (empty string = no style).
        aspect: Aspect ratio string (e.g. "16:9"). Appended to prompt.

    Returns:
        Complete prompt string ready for the API.
    """
    if prompt_text:
        base = prompt_text
    elif prompt_file:
        p = Path(prompt_file)
        if not p.is_file():
            print(f"Error: Prompt file not found: {p}", file=sys.stderr)
            sys.exit(1)
        base = p.read_text(encoding="utf-8").strip()
    else:
        print("Error: Either prompt text or prompt file is required.", file=sys.stderr)
        sys.exit(1)

    if aspect:
        base = f"{base}\nAspect ratio {aspect}."

    if style:
        return f"{style}\n\n{base}"
    return base
