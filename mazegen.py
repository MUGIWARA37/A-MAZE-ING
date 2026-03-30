"""Mazegen — a standalone maze generator using iterative DFS.

Example usage:
    from mazegen import MazeGenerator

    gen = MazeGenerator(width=20, height=15, seed=42)
    grid = gen.generate()
    solution = gen.get_solution()
    print("Solution:", "".join(solution))
"""

from __future__ import annotations
import random
from collections import deque
from typing import Optional


DIRECTIONS: dict[str, tuple[int, int, int, int]] = {
    "N": (0, -1, 0x1, 0x4),
    "E": (1,  0, 0x2, 0x8),
    "S": (0,  1, 0x4, 0x1),
    "W": (-1, 0, 0x8, 0x2),
}


class MazeGenerator:
    """Maze generator using iterative DFS (recursive backtracker).

    The maze is represented as a 2D list of integers where each integer
    encodes the walls of a cell as bits:
        bit 0 (0x1) = North wall
        bit 1 (0x2) = East wall
        bit 2 (0x4) = South wall
        bit 3 (0x8) = West wall
    1 = wall closed, 0 = wall open.

    Attributes:
        width: Maze width in cells.
        height: Maze height in cells.
        seed: Random seed for reproducibility.
        perfect: Whether to generate a perfect maze.
        entry: Entry coordinates (x, y).
        exit: Exit coordinates (x, y).
        grid: 2D list of wall bitmasks.

    Example:
        >>> gen = MazeGenerator(width=20, height=15, seed=42)
        >>> grid = gen.generate()
        >>> solution = gen.get_solution()
        >>> print("Solution:", "".join(solution))
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int] = (0, 0),
        exit: Optional[tuple[int, int]] = None,
        seed: Optional[int] = None,
        perfect: bool = True,
    ) -> None:
        """Initialize the maze generator.

        Args:
            width: Maze width in cells. Must be > 0.
            height: Maze height in cells. Must be > 0.
            entry: Entry coordinates (x, y). Defaults to (0, 0).
            exit: Exit coordinates (x, y). Defaults to (width-1, height-1).
            seed: Random seed for reproducibility. None for random.
            perfect: Whether to generate a perfect maze.

        Raises:
            ValueError: If width or height are <= 0.
            ValueError: If entry or exit are out of bounds.
            ValueError: If entry and exit are the same cell.
        """
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be greater than 0")

        self.width: int = width
        self.height: int = height
        self.seed: Optional[int] = seed
        self.perfect: bool = perfect
        self.entry: tuple[int, int] = entry
        self.exit: tuple[int, int] = (
            exit if exit is not None else (width - 1, height - 1)
        )

        if not (0 <= self.entry[0] < width and 0 <= self.entry[1] < height):
            raise ValueError(f"entry {self.entry} is out of bounds")
        if not (0 <= self.exit[0] < width and 0 <= self.exit[1] < height):
            raise ValueError(f"exit {self.exit} is out of bounds")
        if self.entry == self.exit:
            raise ValueError("entry and exit must be different cells")

        self.grid: list[list[int]] = [
            [0xF for _ in range(width)]
            for _ in range(height)
        ]
        self._pattern_cells: set[tuple[int, int]] = set()
        self._solution: list[str] = []

    def generate(self) -> list[list[int]]:
        """Generate the maze and return the grid.

        Returns:
            2D list of ints where each int encodes walls as bits.
            Access as grid[y][x].
        """
        random.seed(self.seed)
        self._place_42()
        self._carve_dfs()
        self._enforce_borders()
        self._solution = self._find_path()
        return self.grid

    def get_solution(self) -> list[str]:
        """Return the shortest path from entry to exit.

        Must be called after generate().

        Returns:
            List of directions ['N', 'E', 'S', 'W'] from entry to exit.
            Empty list if no path exists.
        """
        return self._solution

    def get_pattern_cells(self) -> set[tuple[int, int]]:
        """Return the set of cells used by the 42 pattern.

        Must be called after generate().

        Returns:
            Set of (x, y) coordinates of pattern cells.
        """
        return self._pattern_cells

    def _place_42(self) -> None:
        """Stamp the 42 pattern onto the maze before DFS carving."""
        pattern_width = 9
        pattern_height = 5

        if self.width < pattern_width + 2 or self.height < pattern_height + 2:
            print("Error: maze too small to display the '42' pattern")
            return

        start_x = (self.width - pattern_width) // 2
        start_y = (self.height - pattern_height) // 2

        PATTERN_42 = [
            "X  X XXXX",
            "X  X    X",
            "XXXX XXXX",
            "   X X   ",
            "   X XXXX",
        ]

        pattern_cells: set[tuple[int, int]] = set()
        for row_idx, row in enumerate(PATTERN_42):
            for col_idx, char in enumerate(row):
                if char == "X":
                    pattern_cells.add(
                        (start_x + col_idx, start_y + row_idx)
                    )

        self._pattern_cells = pattern_cells
        for px, py in pattern_cells:
            self.grid[py][px] = 0xF

    def _carve_dfs(self) -> None:
        """Carve passages using iterative DFS.

        Pre-marks 42 pattern cells as visited so DFS routes around them.
        """
        stack: list[tuple[int, int]] = [self.entry]
        visited: set[tuple[int, int]] = {self.entry} | self._pattern_cells

        while stack:
            x, y = stack[-1]
            neighbours: list[tuple[int, int, str, int, int]] = []

            for direction, (dx, dy, cw, nw) in DIRECTIONS.items():
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.width and
                        0 <= ny < self.height and
                        (nx, ny) not in visited):
                    neighbours.append((nx, ny, direction, cw, nw))

            if neighbours:
                nx, ny, direction, cw, nw = random.choice(neighbours)
                self._carve_passage(x, y, nx, ny, cw, nw)
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()

    def _carve_passage(
        self,
        x: int, y: int,
        nx: int, ny: int,
        current_wall: int,
        neighbour_wall: int,
    ) -> None:
        """Open the wall between two adjacent cells.

        Args:
            x: Current cell x coordinate.
            y: Current cell y coordinate.
            nx: Neighbour cell x coordinate.
            ny: Neighbour cell y coordinate.
            current_wall: Wall bit to clear on current cell.
            neighbour_wall: Wall bit to clear on neighbour cell.
        """
        self.grid[y][x] &= ~current_wall
        self.grid[ny][nx] &= ~neighbour_wall

    def _enforce_borders(self) -> None:
        """Ensure all border cells have their outer walls closed."""
        for x in range(self.width):
            self.grid[0][x] |= 0x1
            self.grid[self.height - 1][x] |= 0x4

        for y in range(self.height):
            self.grid[y][0] |= 0x8
            self.grid[y][self.width - 1] |= 0x2

        self._open_border_wall(self.entry)
        self._open_border_wall(self.exit)

    def _open_border_wall(self, cell: tuple[int, int]) -> None:
        """Open the outer wall of a border cell.

        Args:
            cell: The (x, y) coordinates of the border cell.
        """
        x, y = cell
        if y == 0:
            self.grid[y][x] &= ~0x1
        elif y == self.height - 1:
            self.grid[y][x] &= ~0x4
        elif x == 0:
            self.grid[y][x] &= ~0x8
        elif x == self.width - 1:
            self.grid[y][x] &= ~0x2

    def _find_path(self) -> list[str]:
        """Find shortest path from entry to exit using BFS.

        Returns:
            List of directions from entry to exit.
            Empty list if no path exists.
        """
        queue: deque[tuple[int, int]] = deque([self.entry])
        came_from: dict[
            tuple[int, int],
            tuple[tuple[int, int], str] | None
        ] = {self.entry: None}

        while queue:
            x, y = queue.popleft()
            if (x, y) == self.exit:
                path: list[str] = []
                current = self.exit
                while current != self.entry:
                    parent = came_from[current]
                    if parent is None:
                        break
                    cell, direction = parent
                    path.append(direction)
                    current = cell
                path.reverse()
                return path

            for direction, (dx, dy, cw, nw) in DIRECTIONS.items():
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.width and
                        0 <= ny < self.height and
                        (nx, ny) not in came_from and
                        not (self.grid[y][x] & cw) and
                        not (self.grid[ny][nx] & nw)):
                    came_from[(nx, ny)] = ((x, y), direction)
                    queue.append((nx, ny))

        return []
