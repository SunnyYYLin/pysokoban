"""Interactive Educational Pygame GUI for PySokoban with Search Heatmap & Timeline."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Set

import pygame

from pysokoban.algorithms import get_algorithm
from pysokoban.core.board import Board
from pysokoban.core.enums import Action
from pysokoban.core.state import Coord, SokobanState


class SokobanGUI:
    """Modernized interactive Sokoban GUI supporting player interaction (Undo/Redo),

    real-time AI solving, playback controls, and search exploration heatmap.
    """

    ALGO_KEYS = [
        "bfs",
        "dfs",
        "gbfs",
        "astar",
        "astar-hungarian",
        "weighted-astar",
        "bidirectional",
        "deadlock-astar",
        "mcts",
    ]

    def __init__(self, level_path: str, icon_style: str = "images_v1"):
        pygame.init()
        pygame.display.set_caption("PySokoban: Chronicle of AI Search Algorithms")

        self.board = Board.from_file(level_path)
        self.current_state = self.board.initial_state
        self.icon_style = icon_style

        # Player history for Undo / Redo
        self.history: List[SokobanState] = [self.current_state]
        self.future: List[SokobanState] = []
        self.step_count = 0
        self.push_count = 0

        # AI Solver & Playback state
        self.selected_algo_idx = 3  # Default to A* (1968)
        self.playback_states: List[SokobanState] = []
        self.playback_idx = 0
        self.is_playing_solution = False
        self.is_paused = False
        self.playback_speed_fps = 6  # steps per second
        self.last_step_time = 0
        self.status_message = "Ready. Arrow keys to play, 'S' to solve, 1-9 to change AI."

        # Search exploration heatmap
        self.show_heatmap = True
        self.explored_tiles: Set[Coord] = set()
        self.last_search_metrics = None

        # Dimensions & Assets
        self.tile_size = 48
        self.header_height = 90
        self._setup_display()
        self._load_textures()

        self.clock = pygame.time.Clock()
        self.running = True

    def _setup_display(self) -> None:
        grid_w = max(self.board.width * self.tile_size, 640)
        grid_h = self.board.height * self.tile_size + self.header_height
        self.screen = pygame.display.set_mode((grid_w, grid_h))
        self.font = pygame.font.SysFont("Arial", 16)
        self.bold_font = pygame.font.SysFont("Arial", 18, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 13)

    def _load_textures(self) -> None:
        self.textures: Dict[str, pygame.Surface] = {}
        assets_dir = Path("assets") / self.icon_style
        tex_files = {
            "wall": "wall.png",
            "floor": "space.png" if (assets_dir / "space.png").exists() else "floor.png",
            "box": "box.png",
            "goal": "goal.png",
            "goalbox": "goalbox.png",
            "player": "player.png",
            "goalplayer": "goalplayer.png",
        }

        for key, fname in tex_files.items():
            fpath = assets_dir / fname
            if fpath.exists():
                img = pygame.image.load(str(fpath)).convert_alpha()
                self.textures[key] = pygame.transform.scale(img, (self.tile_size, self.tile_size))
            else:
                # Procedural fallback surfaces
                surf = pygame.Surface((self.tile_size, self.tile_size))
                if key == "wall":
                    surf.fill((100, 100, 100))
                elif key == "box":
                    surf.fill((180, 120, 50))
                elif key == "goal":
                    surf.fill((200, 200, 200))
                    pygame.draw.circle(
                        surf,
                        (200, 50, 50),
                        (self.tile_size // 2, self.tile_size // 2),
                        6,
                    )
                elif key == "player":
                    surf.fill((50, 100, 220))
                else:
                    surf.fill((220, 220, 220))
                self.textures[key] = surf

    def _execute_player_move(self, action: Action) -> None:
        if self.is_playing_solution:
            self.is_playing_solution = False
            self.playback_states.clear()

        valid_moves = self.board.get_valid_actions(self.current_state)
        for act, next_st, is_push in valid_moves:
            if act == action:
                self.history.append(self.current_state)
                self.future.clear()
                self.current_state = next_st
                self.step_count += 1
                if is_push:
                    self.push_count += 1
                if self.board.is_goal(self.current_state):
                    self.status_message = "🎉 Level Solved! Congratulations!"
                else:
                    self.status_message = (
                        f"Move: {action.name} (Steps: {self.step_count}, Pushes: {self.push_count})"
                    )
                break

    def _undo(self) -> None:
        if len(self.history) > 1:
            self.future.append(self.current_state)
            self.current_state = self.history.pop()
            self.step_count = max(0, self.step_count - 1)
            self.status_message = f"Undo (History: {len(self.history)})"

    def _redo(self) -> None:
        if self.future:
            self.history.append(self.current_state)
            self.current_state = self.future.pop()
            self.step_count += 1
            self.status_message = f"Redo (Future: {len(self.future)})"

    def _solve_with_selected_ai(self) -> None:
        algo_key = self.ALGO_KEYS[self.selected_algo_idx]
        algo = get_algorithm(algo_key)

        self.status_message = f"Searching with {algo.name}..."
        self._render_all()
        pygame.display.flip()

        res = algo.solve(self.board, initial_state=self.current_state, timeout_sec=20.0)
        self.last_search_metrics = res.metrics

        if res.solved:
            self.playback_states = res.states
            self.playback_idx = 0
            self.is_playing_solution = True
            self.is_paused = False

            # Set all tiles explored during the search algorithm execution
            self.explored_tiles = (
                set(res.explored_tiles)
                if res.explored_tiles
                else {b for st in res.states for b in st.boxes}
            )

            m = res.metrics
            self.status_message = (
                f"✓ Solved by {algo.name} ({algo.historical_year})! "
                f"Steps: {m.solution_steps}, Exp: {m.expanded_nodes:,}, Time: {m.duration_sec * 1000:.1f}ms. [Space]=Pause [F2]=Heatmap"
            )
        else:
            self.explored_tiles = set(res.explored_tiles)
            self.status_message = f"✗ {algo.name} failed (Expanded {res.metrics.expanded_nodes:,} nodes). Press [F2] to see explored area."

    def _render_hud(self) -> None:
        # Background bar
        hud_rect = pygame.Rect(0, 0, self.screen.get_width(), self.header_height)
        pygame.draw.rect(self.screen, (30, 34, 42), hud_rect)
        pygame.draw.line(
            self.screen,
            (60, 68, 84),
            (0, self.header_height),
            (self.screen.get_width(), self.header_height),
            2,
        )

        algo_key = self.ALGO_KEYS[self.selected_algo_idx]
        algo = get_algorithm(algo_key)

        # Line 1: Level Name & Active Algorithm
        lvl_text = self.bold_font.render(
            f"Level: {self.board.name} | Steps: {self.step_count} (Pushes: {self.push_count})",
            True,
            (240, 240, 240),
        )
        self.screen.blit(lvl_text, (15, 10))

        algo_label = f"AI [{self.selected_algo_idx + 1}]: {algo.name} ({algo.historical_year})"
        algo_text = self.bold_font.render(algo_label, True, (80, 200, 120))
        self.screen.blit(algo_text, (self.screen.get_width() - algo_text.get_width() - 15, 10))

        # Line 2: Status Message
        msg_text = self.font.render(self.status_message, True, (255, 215, 0))
        self.screen.blit(msg_text, (15, 38))

        # Line 3: Shortcuts guidance
        guide = "[Arrows] Move | [Z/U] Undo | [Y] Redo | [S] AI Solve | [1-9] Switch AI | [F2] Heatmap | [Space] Pause | [,] [.] Step"
        guide_text = self.small_font.render(guide, True, (160, 170, 185))
        self.screen.blit(guide_text, (15, 65))

    def _render_board(self) -> None:
        offset_y = self.header_height
        offset_x = max(0, (self.screen.get_width() - self.board.width * self.tile_size) // 2)

        # Draw grid tiles
        for r in range(self.board.height):
            for c in range(self.board.width):
                pos = (r, c)
                x = offset_x + c * self.tile_size
                y = offset_y + r * self.tile_size

                # Draw floor base
                if pos not in self.board.walls:
                    self.screen.blit(self.textures["floor"], (x, y))

                if pos in self.board.walls:
                    self.screen.blit(self.textures["wall"], (x, y))
                elif pos in self.board.goals:
                    if pos in self.current_state.boxes:
                        self.screen.blit(self.textures["goalbox"], (x, y))
                    elif pos == self.current_state.player:
                        self.screen.blit(self.textures["goalplayer"], (x, y))
                    else:
                        self.screen.blit(self.textures["goal"], (x, y))
                elif pos in self.current_state.boxes:
                    self.screen.blit(self.textures["box"], (x, y))
                elif pos == self.current_state.player:
                    self.screen.blit(self.textures["player"], (x, y))

                # Heatmap overlay: highlight tiles explored by AI
                if self.show_heatmap and pos in self.explored_tiles and pos not in self.board.walls:
                    overlay = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
                    overlay.fill((255, 60, 0, 80))  # Translucent orange/red
                    self.screen.blit(overlay, (x, y))

    def _render_all(self) -> None:
        self.screen.fill((20, 22, 28))
        self._render_hud()
        self._render_board()

    def run(self) -> None:
        while self.running:
            self.clock.tick(60)

            # Playback logic
            if self.is_playing_solution and not self.is_paused and self.playback_states:
                now = pygame.time.get_ticks()
                interval_ms = 1000 // self.playback_speed_fps
                if now - self.last_step_time >= interval_ms:
                    self.last_step_time = now
                    if self.playback_idx < len(self.playback_states):
                        self.current_state = self.playback_states[self.playback_idx]
                        self.playback_idx += 1
                    else:
                        self.is_playing_solution = False
                        self.status_message = "Solution playback completed."

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

                    # Movement
                    elif event.key == pygame.K_UP:
                        self._execute_player_move(Action.UP)
                    elif event.key == pygame.K_DOWN:
                        self._execute_player_move(Action.DOWN)
                    elif event.key == pygame.K_LEFT:
                        self._execute_player_move(Action.LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self._execute_player_move(Action.RIGHT)

                    # Undo / Redo / Reset
                    elif event.key in (pygame.K_u, pygame.K_z):
                        self._undo()
                    elif event.key == pygame.K_y:
                        self._redo()
                    elif event.key == pygame.K_r:
                        self.current_state = self.board.initial_state
                        self.history = [self.current_state]
                        self.future.clear()
                        self.step_count = 0
                        self.push_count = 0
                        self.playback_states.clear()
                        self.is_playing_solution = False
                        self.status_message = "Level reset."

                    # AI Solving
                    elif event.key == pygame.K_s:
                        self._solve_with_selected_ai()

                    # Number keys 1-9 to switch algorithm
                    elif pygame.K_1 <= event.key <= pygame.K_9:
                        idx = event.key - pygame.K_1
                        if idx < len(self.ALGO_KEYS):
                            self.selected_algo_idx = idx
                            algo_key = self.ALGO_KEYS[idx]
                            algo = get_algorithm(algo_key)
                            self.status_message = (
                                f"Selected AI: {algo.name} ({algo.historical_year})"
                            )

                    # Heatmap toggle
                    elif event.key == pygame.K_F2:
                        self.show_heatmap = not self.show_heatmap
                        self.status_message = (
                            f"Heatmap overlay: {'ON' if self.show_heatmap else 'OFF'}"
                        )

                    # Playback controls
                    elif event.key == pygame.K_SPACE:
                        if self.playback_states:
                            self.is_paused = not self.is_paused
                            self.status_message = (
                                "Playback paused" if self.is_paused else "Playback running"
                            )
                    elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                        self.playback_speed_fps = min(30, self.playback_speed_fps + 2)
                        self.status_message = f"Playback speed: {self.playback_speed_fps} fps"
                    elif event.key == pygame.K_MINUS:
                        self.playback_speed_fps = max(1, self.playback_speed_fps - 2)
                        self.status_message = f"Playback speed: {self.playback_speed_fps} fps"
                    # Single-frame step forward / backward
                    elif event.key in (pygame.K_PERIOD, pygame.K_GREATER):
                        if self.playback_states and self.playback_idx < len(self.playback_states):
                            self.is_paused = True
                            self.current_state = self.playback_states[self.playback_idx]
                            self.playback_idx += 1
                            self.status_message = f"Step {self.playback_idx}/{len(self.playback_states)} (Paused)"
                    elif event.key in (pygame.K_COMMA, pygame.K_LESS):
                        if self.playback_states and self.playback_idx > 1:
                            self.is_paused = True
                            self.playback_idx -= 1
                            self.current_state = self.playback_states[self.playback_idx - 1]
                            self.status_message = f"Step {self.playback_idx}/{len(self.playback_states)} (Paused)"

            self._render_all()
            pygame.display.flip()

        pygame.quit()


def run_gui(level_path: str, icon_style: str = "images_v1") -> None:
    gui = SokobanGUI(level_path=level_path, icon_style=icon_style)
    gui.run()
