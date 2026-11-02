#!/usr/bin/env python3
"""Validate the public profile README and bundled EVALQUOR visual assets.

No third-party services, network requests, or packages are required.
"""
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
PALETTE = {"#111411", "#D5FB74", "#F4F6F0", "#9CA89B", "#2A3A2E"}

def check() -> list[str]:
    errors: list[str] = []
    markdown = README.read_text(encoding="utf-8")
    if "README.ar.md" in markdown or (ROOT / "README.ar.md").exists():
        errors.append("Unexpected Arabic profile version.")
    if "evalquor-website.vercel.app" not in markdown:
        errors.append("Official EVALQUOR website link missing.")
    if "assets/evalquor-profile.svg" not in markdown:
        errors.append("Branded banner reference missing.")

    sources = re.findall(r'<img[^>]*?src=["\']([^"\']+)["\']', markdown)
    if not sources:
        errors.append("No profile imagery found.")
    for source in sources:
        if source.startswith(("http:", "https:", "//")):
            errors.append(f"External image dependency is disallowed: {source}")
            continue
        asset = (ROOT / source).resolve()
        if not asset.is_relative_to(ROOT):
            errors.append(f"Unsafe image reference: {source}")
        elif not asset.is_file():
            errors.append(f"Missing image: {source}")

    for name in ("evalquor-profile.svg", "evalquor-official-logo.svg"):
        path = ROOT / "assets" / name
        if not path.is_file():
            errors.append(f"Required official brand asset missing: {name}")
            continue
        try:
            root = ET.parse(path).getroot()
            if not root.tag.endswith("svg"):
                errors.append(f"Not an SVG: {name}")
            svg_text = path.read_text(encoding="utf-8")
            if name == "evalquor-profile.svg":
                for color in PALETTE:
                    if color not in svg_text:
                        errors.append(f"Brand color {color} is missing in the banner.")
        except ET.ParseError as exc:
            errors.append(f"Invalid SVG {name}: {exc}")
    return errors

if __name__ == "__main__":
    problems = check()
    for problem in problems:
        print(f"ERROR: {problem}", file=sys.stderr)
    if problems:
        raise SystemExit(1)
    print("PASS — branded profile assets and README references are valid.")
