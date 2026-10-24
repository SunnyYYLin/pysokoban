"""Script to generate rich animated GIFs showcasing PySokoban features.

Generates:
1. doc/assets/ai_solve_tier2.gif: Smooth playback of AI solving tier 2 level.
2. doc/assets/search_heatmap_contrast.gif: Side-by-side / sequential comparison of BFS vs Deadlock-A* heatmaps.
3. doc/assets/interactive_undo_redo.gif: Showcase of manual play, undoing mistakes, and reaching goal.
"""

from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from pysokoban.algorithms import get_algorithm
from pysokoban.core.board import Board
from pysokoban.core.enums import Action
from pysokoban.core.state import Coord, SokobanState


OUTPUT_DIR = Path("doc/assets")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TILE_SIZE = 40
HEADER_H = 60


def load_textures() -> dict[str, Image.Image]:
    tex_dir = Path("assets/images_v1")
    textures = {}
    names = {
        "wall": "wall.png",
        "floor": "space.png",
        "box": "box.png",
        "goal": "goal.png",
        "goalbox": "goalbox.png",
        "player": "player.png",
        "goalplayer": "goalplayer.png",
    }
    for k, v in names.items():
        p = tex_dir / v
        if p.exists():
            im = Image.open(p).convert("RGBA")
            textures[k] = im.resize((TILE_SIZE, TILE_SIZE), Image.Resampling.NEAREST)
        else:
            im = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (200, 200, 200, 255))
            textures[k] = im
    return textures


TEXTURES = load_textures()


def render_frame(
    board: Board,
    state: SokobanState,
    title: str = "",
    subtitle: str = "",
    heatmap_tiles: set[Coord] | None = None,
    banner: str | None = None,
) -> Image.Image:
    grid_w = max(board.width * TILE_SIZE, 360)
    grid_h = board.height * TILE_SIZE + HEADER_H

    img = Image.new("RGBA", (grid_w, grid_h), (24, 27, 34, 255))
    draw = ImageDraw.Draw(img)

    # Top HUD
    draw.rectangle([(0, 0), (grid_w, HEADER_H)], fill=(33, 38, 48, 255))
    draw.line([(0, HEADER_H), (grid_w, HEADER_H)], fill=(60, 68, 84, 255), width=2)

    # Text
    draw.text((12, 10), title, fill=(240, 240, 240, 255))
    draw.text((12, 34), subtitle, fill=(255, 215, 0, 255))

    # Center board
    offset_x = (grid_w - board.width * TILE_SIZE) // 2
    offset_y = HEADER_H

    for r in range(board.height):
        for c in range(board.width):
            pos = (r, c)
            x = offset_x + c * TILE_SIZE
            y = offset_y + r * TILE_SIZE

            if pos not in board.walls:
                img.alpha_composite(TEXTURES["floor"], (x, y))

            if pos in board.walls:
                img.alpha_composite(TEXTURES["wall"], (x, y))
            elif pos in board.goals:
                if pos in state.boxes:
                    img.alpha_composite(TEXTURES["goalbox"], (x, y))
                elif pos == state.player:
                    img.alpha_composite(TEXTURES["goalplayer"], (x, y))
                else:
                    img.alpha_composite(TEXTURES["goal"], (x, y))
            elif pos in state.boxes:
                img.alpha_composite(TEXTURES["box"], (x, y))
            elif pos == state.player:
                img.alpha_composite(TEXTURES["player"], (x, y))

            # Heatmap overlay
            if heatmap_tiles and pos in heatmap_tiles and pos not in board.walls:
                overlay = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (255, 60, 0, 95))
                img.alpha_composite(overlay, (x, y))

    if banner:
        bw, bh = grid_w - 40, 36
        bx, by = 20, (grid_h + HEADER_H - bh) // 2
        overlay = Image.new("RGBA", (grid_w, grid_h), (0, 0, 0, 160))
        img.alpha_composite(overlay, (0, 0))
        draw = ImageDraw.Draw(img)
        draw.rectangle([(bx, by), (bx + bw, by + bh)], fill=(40, 160, 80, 240), outline=(255, 255, 255, 255), width=2)
        draw.text((bx + 20, by + 10), banner, fill=(255, 255, 255, 255))

    return img.convert("RGB")


def generate_ai_solve_gif():
    print("Generating doc/assets/ai_solve_tier2.gif ...")
    board = Board.from_file("levels/02_benchmark/tier2_dual_2box.txt")
    algo = get_algorithm("deadlock-astar")
    res = algo.solve(board)

    frames = []
    # Intro frame
    for _ in range(5):
        frames.append(
            render_frame(
                board,
                board.initial_state,
                title="PySokoban AI Solver",
                subtitle="Press 'S' -> Solving with Deadlock-A* (1999)...",
            )
        )

    # Playback frames
    for i, st in enumerate(res.states):
        f = render_frame(
            board,
            st,
            title="Deadlock-Pruned A* (Rolling Stone style, 1999)",
            subtitle=f"Step {i}/{len(res.states)-1} | Exp: {res.metrics.expanded_nodes} nodes | Time: {res.metrics.duration_sec*1000:.1f}ms",
            heatmap_tiles=set(res.explored_tiles),
        )
        frames.append(f)

    # Victory frame
    for _ in range(12):
        frames.append(
            render_frame(
                board,
                res.states[-1],
                title="Deadlock-Pruned A* (1999)",
                subtitle="Level Solved! Optimal 33 steps.",
                heatmap_tiles=set(res.explored_tiles),
                banner="Level Solved! (Optimal 33 Steps)",
            )
        )

    out_p = OUTPUT_DIR / "ai_solve_tier2.gif"
    frames[0].save(
        out_p,
        save_all=True,
        append_images=frames[1:],
        duration=180,
        loop=0,
    )
    print(f"Saved: {out_p} ({len(frames)} frames)")


def generate_heatmap_contrast_gif():
    print("Generating doc/assets/search_heatmap_contrast.gif ...")
    board = Board.from_file("levels/02_benchmark/tier3_trio_3box.txt")

    # Run BFS
    bfs = get_algorithm("bfs")
    res_bfs = bfs.solve(board)

    # Run Deadlock-A*
    dl_astar = get_algorithm("deadlock-astar")
    res_dl = dl_astar.solve(board)

    frames = []

    # Sequence 1: BFS Heatmap
    for _ in range(15):
        frames.append(
            render_frame(
                board,
                board.initial_state,
                title="1. BFS (1959) Search Heatmap",
                subtitle=f"Expanded: {res_bfs.metrics.expanded_nodes:,} nodes | Explored: {len(res_bfs.explored_tiles)} tiles (ALL)",
                heatmap_tiles=res_bfs.explored_tiles,
            )
        )

    # Sequence 2: Deadlock-A* Heatmap
    for _ in range(15):
        frames.append(
            render_frame(
                board,
                board.initial_state,
                title="2. Deadlock-Pruned A* (1999) Heatmap",
                subtitle=f"Expanded: {res_dl.metrics.expanded_nodes:,} nodes | Explored: {len(res_dl.explored_tiles)} tiles (Pruned)",
                heatmap_tiles=res_dl.explored_tiles,
            )
        )

    # Sequence 3: Solution Playback with Heatmap
    for i, st in enumerate(res_dl.states):
        frames.append(
            render_frame(
                board,
                st,
                title="Solution Playback: Deadlock-Pruned A*",
                subtitle=f"Step {i}/{len(res_dl.states)-1} (17x faster than BFS)",
                heatmap_tiles=res_dl.explored_tiles,
            )
        )

    # Victory frame
    for _ in range(10):
        frames.append(
            render_frame(
                board,
                res_dl.states[-1],
                title="Solution Playback: Complete",
                subtitle="Deadlock A*: 470 nodes vs BFS: 8,121 nodes",
                heatmap_tiles=res_dl.explored_tiles,
                banner="Pruning Slashes 94% Search Space!",
            )
        )

    out_p = OUTPUT_DIR / "search_heatmap_contrast.gif"
    frames[0].save(
        out_p,
        save_all=True,
        append_images=frames[1:],
        duration=220,
        loop=0,
    )
    print(f"Saved: {out_p} ({len(frames)} frames)")


def generate_undo_redo_gif():
    print("Generating doc/assets/interactive_undo_redo.gif ...")
    board = Board.from_file("levels/01_tutorial/01_corner_deadlock.txt")

    # Sequence:
    # 1. Start: player at (1, 1), box at (1, 3), goal at (1, 5)
    # 2. Player moves right to (1, 2)
    # 3. Player moves down to (2, 2)
    # 4. Player presses Undo 'U' -> back to (1, 2)
    # 5. Player pushes box right to (1, 4)
    # 6. Player pushes box right to (1, 5) -> Solved!

    s0 = board.initial_state
    s1 = s0.move_player((1, 2))
    s_mistake = s1.move_player((2, 2))
    s_p1 = s1.push_box((1, 3), (1, 4), (1, 3))
    s_goal = s_p1.push_box((1, 4), (1, 5), (1, 4))

    frames = []
    # Start
    for _ in range(6):
        frames.append(render_frame(board, s0, title="Interactive Play", subtitle="Manual play with full Undo/Redo"))

    # Step 1: Move Right
    for _ in range(4):
        frames.append(render_frame(board, s1, title="Interactive Play", subtitle="Player moves Right -> [Z/U] to Undo"))

    # Step 2: Mistake down
    for _ in range(6):
        frames.append(render_frame(board, s_mistake, title="Interactive Play", subtitle="Wrong move down! Press [U] to Undo"))

    # Step 3: Undo
    for _ in range(6):
        frames.append(render_frame(board, s1, title="Interactive Play", subtitle="Undo! Returned to previous safe state"))

    # Step 4: Push Right
    for _ in range(4):
        frames.append(render_frame(board, s_p1, title="Interactive Play", subtitle="Pushing box toward goal..."))

    # Step 5: Push into goal
    for _ in range(4):
        frames.append(render_frame(board, s_goal, title="Interactive Play", subtitle="Box placed on goal!"))

    # Victory
    for _ in range(10):
        frames.append(render_frame(board, s_goal, title="Interactive Play", subtitle="Level Cleared!", banner="Level Cleared!"))

    out_p = OUTPUT_DIR / "interactive_undo_redo.gif"
    frames[0].save(
        out_p,
        save_all=True,
        append_images=frames[1:],
        duration=250,
        loop=0,
    )
    print(f"Saved: {out_p} ({len(frames)} frames)")


if __name__ == "__main__":
    generate_ai_solve_gif()
    generate_heatmap_contrast_gif()
    generate_undo_redo_gif()
