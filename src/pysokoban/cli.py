"""Command Line Interface (CLI) for PySokoban: Chronicle of AI Search Algorithms."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from pysokoban.algorithms import get_algorithm, list_algorithms
from pysokoban.core.board import Board

console = Console()


def cmd_list_algorithms(args: argparse.Namespace) -> None:
    """List all available search algorithms in chronological order."""
    table = Table(title="The Chronicle of AI Search Algorithms (1950s - Present)")
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("Year", style="magenta")
    table.add_column("Algorithm", style="green")
    table.add_column("Family", style="yellow")
    table.add_column("Optimality", style="blue")

    for key, _, _ in list_algorithms():
        algo = get_algorithm(key)
        opt_str = (
            "[bold green]Optimal[/]" if algo.optimality_guaranteed else "[dim yellow]Suboptimal[/]"
        )
        table.add_row(
            key,
            str(algo.historical_year),
            algo.name,
            algo.family,
            opt_str,
        )

    console.print(table)


def cmd_solve(args: argparse.Namespace) -> None:
    """Solve a level with a chosen algorithm."""
    level_path = Path(args.level)
    if not level_path.exists():
        console.print(f"[bold red]Level file not found:[/] {args.level}")
        sys.exit(1)

    board = Board.from_file(level_path)
    algo = get_algorithm(args.algo)

    console.print(
        Panel(
            f"[bold]Level:[/] {board.name} ({board.width}x{board.height}) | "
            f"[bold]Boxes:[/] {len(board.initial_state.boxes)} | "
            f"[bold]Algorithm:[/] {algo.name} ({algo.historical_year})",
            title="Sokoban AI Solver",
            border_style="cyan",
        )
    )

    with console.status("[bold green]Executing search..."):
        start = time.perf_counter()
        result = algo.solve(board, timeout_sec=args.timeout)
        duration = time.perf_counter() - start

    if result.solved:
        console.print(f"[bold green]✓ SOLVED in {duration:.4f}s![/]")
        m = result.metrics
        console.print(
            f"  • [cyan]Solution steps:[/] {m.solution_steps} (Pushes: {m.solution_pushes})"
        )
        console.print(f"  • [cyan]Nodes expanded:[/] {m.expanded_nodes:,}")
        console.print(f"  • [cyan]Nodes generated:[/] {m.generated_nodes:,}")
        console.print(f"  • [cyan]Peak frontier:[/]  {m.peak_frontier:,}")

        action_str = "".join(a.char for a in result.actions)
        if len(action_str) > 80:
            action_str = action_str[:77] + "..."
        console.print(f"  • [cyan]Action sequence:[/] [dim]{action_str}[/]")

        if args.animate:
            console.print("\n[bold]Replaying Solution:[/]")
            for i, st in enumerate(result.states):
                console.clear()
                console.print(f"[bold cyan]Step {i}/{len(result.states) - 1}[/]")
                console.print(board.render_ascii(st))
                time.sleep(args.delay)
    else:
        console.print(
            f"[bold red]✗ Search failed to find a solution.[/] Reason: {result.metrics.notes}"
        )


def cmd_bench(args: argparse.Namespace) -> None:
    """Run comparative benchmark across algorithms and levels."""
    levels: List[Path] = []
    level_arg = Path(args.levels)

    if level_arg.is_dir():
        levels = sorted(list(level_arg.glob("*.txt")))
    elif level_arg.is_file():
        levels = [level_arg]
    else:
        # Check default benchmark directory
        bench_dir = Path("levels/02_benchmark")
        if bench_dir.exists():
            levels = sorted(list(bench_dir.glob("*.txt")))

    if not levels:
        console.print(f"[bold red]No levels found at:[/] {args.levels}")
        sys.exit(1)

    algo_keys = (
        [k.strip() for k in args.algorithms.split(",") if k.strip()]
        if args.algorithms != "all"
        else [
            "bfs",
            "gbfs",
            "astar",
            "astar-hungarian",
            "weighted-astar",
            "deadlock-astar",
            "bidirectional",
        ]
    )

    table = Table(title="PySokoban Historical Benchmark Matrix")
    table.add_column("Level", style="cyan", no_wrap=True)
    table.add_column("Boxes", justify="right")
    table.add_column("Algorithm", style="green")
    table.add_column("Year", justify="right", style="magenta")
    table.add_column("Solved", justify="center")
    table.add_column("Steps", justify="right")
    table.add_column("Expanded", justify="right", style="yellow")
    table.add_column("Frontier", justify="right")
    table.add_column("Time (ms)", justify="right", style="bold blue")

    for lvl_p in levels:
        board = Board.from_file(lvl_p)
        n_boxes = len(board.initial_state.boxes)

        for a_key in algo_keys:
            try:
                algo = get_algorithm(a_key)
            except ValueError:
                continue

            result = algo.solve(board, timeout_sec=args.timeout)
            m = result.metrics

            solved_icon = "[bold green]YES[/]" if result.solved else "[bold red]NO[/]"
            steps_str = str(m.solution_steps) if result.solved else "-"
            exp_str = f"{m.expanded_nodes:,}"
            front_str = f"{m.peak_frontier:,}"
            time_ms = f"{m.duration_sec * 1000:.2f}"

            table.add_row(
                board.name,
                str(n_boxes),
                algo.name,
                str(algo.historical_year),
                solved_icon,
                steps_str,
                exp_str,
                front_str,
                time_ms,
            )

    console.print(table)


def cmd_play(args: argparse.Namespace) -> None:
    """Launch the interactive Pygame Sokoban GUI."""
    from pysokoban.visualizer.pygame_gui import run_gui

    run_gui(level_path=args.level, icon_style=args.icon_style)


def main():
    parser = argparse.ArgumentParser(
        prog="pysokoban",
        description="PySokoban: Chronicle of AI Search Algorithms",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # list-algorithms
    subparsers.add_parser("list-algorithms", help="List all algorithms chronologically")

    # solve
    p_solve = subparsers.add_parser("solve", help="Solve a level with an AI algorithm")
    p_solve.add_argument(
        "--level",
        type=str,
        default="levels/02_benchmark/tier1_micro_1box.txt",
        help="Path to level text file",
    )
    p_solve.add_argument(
        "--algo",
        type=str,
        default="deadlock-astar",
        help="Algorithm key (e.g. bfs, astar, deadlock-astar)",
    )
    p_solve.add_argument("--timeout", type=float, default=30.0, help="Search timeout in seconds")
    p_solve.add_argument("--animate", action="store_true", help="Animate solution in terminal")
    p_solve.add_argument(
        "--delay", type=float, default=0.15, help="Step delay for terminal animation"
    )

    # bench
    p_bench = subparsers.add_parser("bench", help="Run historical benchmark across algorithms")
    p_bench.add_argument(
        "--levels", type=str, default="levels/02_benchmark", help="Directory or file path of levels"
    )
    p_bench.add_argument(
        "--algorithms",
        type=str,
        default="bfs,astar,astar-hungarian,deadlock-astar,bidirectional",
        help="Comma-separated algorithm keys or 'all'",
    )
    p_bench.add_argument("--timeout", type=float, default=10.0, help="Timeout per run in seconds")

    # play
    p_play = subparsers.add_parser("play", help="Launch interactive Pygame GUI")
    p_play.add_argument(
        "--level",
        type=str,
        default="levels/02_benchmark/tier1_micro_1box.txt",
        help="Path to level text file",
    )
    p_play.add_argument(
        "--icon-style",
        type=str,
        default="images_v1",
        help="Icon style: images_v1, images_v2, tiny_images",
    )

    args = parser.parse_args()

    if args.command == "list-algorithms":
        cmd_list_algorithms(args)
    elif args.command == "solve":
        cmd_solve(args)
    elif args.command == "bench":
        cmd_bench(args)
    elif args.command == "play":
        cmd_play(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
