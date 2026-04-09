"""
tools/file_writer.py
Utility for parsing <file name="...">...</file> blocks from text
and writing them to disk. Used as a fallback when OpenCode
doesn't write files itself (e.g. in dry-run / test mode).
"""

import re
from pathlib import Path


def parse_file_blocks(text: str) -> dict[str, str]:
    """
    Parse <file name="...">...</file> blocks from text.
    Returns { filename: content }.
    """
    pattern = re.compile(
        r'<file\s+name=["\']([^"\']+)["\']>(.*?)</file>',
        re.DOTALL | re.IGNORECASE,
    )
    return {m.group(1).strip(): m.group(2).strip() for m in pattern.finditer(text)}


def write_files(files: dict[str, str], output_dir: str) -> list[str]:
    """Write files dict to output_dir. Returns list of written paths."""
    written = []
    base = Path(output_dir)
    base.mkdir(parents=True, exist_ok=True)
    for filename, content in files.items():
        filepath = base / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content, encoding="utf-8")
        written.append(str(filepath))
        print(f"  [FileWriter] Wrote: {filepath}")
    return written


def write_raw(content: str, output_dir: str, filename: str) -> str:
    """Write a single file. Returns path."""
    base = Path(output_dir)
    base.mkdir(parents=True, exist_ok=True)
    filepath = base / filename
    filepath.write_text(content, encoding="utf-8")
    print(f"  [FileWriter] Wrote: {filepath}")
    return str(filepath)
