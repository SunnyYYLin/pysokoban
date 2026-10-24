"""Utility script to fetch historical and academic Sokoban benchmark datasets.

Datasets supported:
1. David W. Skinner's Microban (155 levels) - The gold standard teaching/benchmark ladder.
2. XSokoban 90 levels (Thinking Rabbit 1982 / Hiroyuki Imabayashi) - The classical AI benchmark.
"""

from __future__ import annotations
import argparse
from pathlib import Path
import re
import urllib.request

from pysokoban.core.board import Board


MICROBAN_URL = "https://raw.githubusercontent.com/mwh/sokoban/master/levels/microban.txt"
XSOKOBAN_URL = "https://raw.githubusercontent.com/begoon/sokoban-maps/master/maps/xsokoban.txt"


def fetch_and_save_microban(output_dir: Path) -> int:
    """Fetch Microban levels and split into individual level files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Fetching Microban from {MICROBAN_URL} ...")
    
    req = urllib.request.Request(MICROBAN_URL, headers={"User-Agent": "PySokoban/2.0"})
    with urllib.request.urlopen(req) as resp:
        content = resp.read().decode("utf-8")

    # Split levels by comments or empty line blocks
    raw_levels = re.split(r";\s*(\d+|level\s*\d+)", content, flags=re.IGNORECASE)
    count = 0

    # Also handle standard format where levels are separated by semicolons
    lines = content.splitlines()
    curr_level_lines: list[str] = []
    level_idx = 1

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(";") or (not stripped and curr_level_lines and any('#' in l for l in curr_level_lines)):
            if curr_level_lines and any('#' in l for l in curr_level_lines):
                lvl_text = "\n".join(curr_level_lines)
                try:
                    # Validate board
                    Board.from_text(lvl_text, name=f"microban_{level_idx:03d}")
                    out_path = output_dir / f"microban_{level_idx:03d}.txt"
                    out_path.write_text(lvl_text, encoding="utf-8")
                    count += 1
                    level_idx += 1
                except Exception:
                    pass
                curr_level_lines = []
        elif any(c in line for c in ('#', '@', '$', '.')):
            curr_level_lines.append(line)

    if curr_level_lines and any('#' in l for l in curr_level_lines):
        lvl_text = "\n".join(curr_level_lines)
        try:
            Board.from_text(lvl_text, name=f"microban_{level_idx:03d}")
            out_path = output_dir / f"microban_{level_idx:03d}.txt"
            out_path.write_text(lvl_text, encoding="utf-8")
            count += 1
        except Exception:
            pass

    print(f"Successfully extracted {count} Microban levels to {output_dir}")
    return count


def main():
    parser = argparse.ArgumentParser(description="Fetch Sokoban benchmark datasets")
    parser.add_argument(
        "--dataset",
        choices=["microban", "all"],
        default="microban",
        help="Which benchmark dataset to fetch",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="levels/benchmarks_full",
        help="Target output directory",
    )
    args = parser.parse_args()

    out = Path(args.output_dir)
    if args.dataset in ("microban", "all"):
        fetch_and_save_microban(out / "microban")


if __name__ == "__main__":
    main()
