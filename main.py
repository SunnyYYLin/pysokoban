"""Main entrypoint for PySokoban: The Chronicle of AI Search Algorithms.

Supports both modern subcommands:
    pysokoban play
    pysokoban bench
    pysokoban solve
    pysokoban list-algorithms

And legacy options:
    python main.py --level 1 --icon-style images_v1
    python main.py --test
"""

import sys
from pathlib import Path

# Ensure 'src' is on sys.path if running directly from repository root without pip install
src_dir = Path(__file__).parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from pysokoban.cli import main

if __name__ == "__main__":
    # If called with legacy flags like --level or --test directly without subcommands
    args = sys.argv[1:]
    if not args:
        # Default action: launch play
        sys.argv = [sys.argv[0], "play"]
    elif args[0] not in ("play", "bench", "solve", "list-algorithms", "-h", "--help"):
        if "--test" in args:
            sys.argv = [sys.argv[0], "bench"]
        else:
            # Map legacy args to 'play'
            lvl = "levels/02_benchmark/tier1_micro_1box.txt"
            style = "images_v1"
            if "--level" in args:
                idx = args.index("--level")
                if idx + 1 < len(args):
                    lvl_num = args[idx + 1]
                    # Check if numeric
                    if lvl_num.isdigit():
                        lvl = f"levels/level{lvl_num}.txt"
                    else:
                        lvl = lvl_num
            if "--icon-style" in args:
                idx = args.index("--icon-style")
                if idx + 1 < len(args):
                    style = args[idx + 1]
            sys.argv = [sys.argv[0], "play", "--level", lvl, "--icon-style", style]

    main()
