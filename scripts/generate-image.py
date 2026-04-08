#!/usr/bin/env python3
"""
generate-image.py — Gemini API を使ったインフォグラフィック画像生成スクリプト

Usage:
    python scripts/generate-image.py --prompt "Your prompt here" --output output/slide.png
    python scripts/generate-image.py --prompt-file prompts/slide1.txt --default-style --aspect 16:9 --output output/slide.png
    python scripts/generate-image.py --prompt "..." --num 3 --output-dir output/ --name slide

Environment:
    Google_Image_API — Gemini API key (.env or environment variable)

Requires: Python 3.9+
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

# Project root = parent of the scripts/ directory this file lives in
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"

# Ensure scripts/ is on the import path regardless of cwd
sys.path.insert(0, str(SCRIPTS_DIR))

from gemini_client import DEFAULT_MODEL, generate_image, get_api_key
from prompt_builder import VALID_ASPECT_RATIOS, build_prompt, resolve_style


# ---------------------------------------------------------------------------
# Output path resolution
# ---------------------------------------------------------------------------

def resolve_output_path(args: argparse.Namespace, index: int = 0, total: int = 1) -> Path:
    """Determine the output file path from CLI arguments."""
    if args.output and total == 1:
        return Path(args.output)

    out_dir = Path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    base_name = args.name or datetime.now().strftime("image-%Y%m%d-%H%M%S")

    if total > 1:
        return out_dir / f"{base_name}-{index + 1:02d}.png"
    return out_dir / f"{base_name}.png"


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate infographic images using the Google Gemini API.",
    )

    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", "-p", help="Direct prompt text.")
    prompt_group.add_argument("--prompt-file", "-f", help="Path to a prompt file.")

    parser.add_argument("--output", "-o", help="Output file path (ignored when --num > 1).")
    parser.add_argument("--output-dir", "-d", help=f"Output directory (default: {DEFAULT_OUTPUT_DIR}).")
    parser.add_argument("--name", "-n", help="Base filename without extension.")

    parser.add_argument("--style-prefix", help="Style instruction text to prepend.")
    parser.add_argument("--style-file", help="Path to a style instructions file.")
    parser.add_argument("--default-style", action="store_true", help="Use the built-in IDEO/McKinsey style.")

    parser.add_argument("--aspect", "-a", choices=VALID_ASPECT_RATIOS, help="Aspect ratio (e.g. 16:9, 1:1).")
    parser.add_argument("--num", "-N", type=int, default=1, help="Number of images to generate (default: 1).")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, help=f"Gemini model (default: {DEFAULT_MODEL}).")

    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()
    api_key = get_api_key(PROJECT_ROOT)

    style = resolve_style(
        style_prefix=args.style_prefix,
        style_file=args.style_file,
        use_default=args.default_style,
        styles_dir=SCRIPTS_DIR / "styles",
    )

    prompt = build_prompt(
        prompt_text=args.prompt,
        prompt_file=args.prompt_file,
        style=style,
        aspect=args.aspect,
    )

    num = max(1, args.num)

    print(f"Model: {args.model}", file=sys.stderr)
    print(f"Generating {num} image(s)...", file=sys.stderr)

    for i in range(num):
        out_path = resolve_output_path(args, index=i, total=num)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if num > 1:
            print(f"\n[{i + 1}/{num}] Generating...", file=sys.stderr)

        try:
            image_bytes = generate_image(prompt, api_key, model=args.model)
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        out_path.write_bytes(image_bytes)
        print(str(out_path))
        print(f"Saved: {out_path}", file=sys.stderr)

        if num > 1 and i < num - 1:
            time.sleep(1)

    print("\nDone.", file=sys.stderr)


if __name__ == "__main__":
    main()
