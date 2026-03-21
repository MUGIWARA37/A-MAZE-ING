import random
from src.config_parser import MazeConfig
from src.pathfinder import DIRECTIONS


class MazeGenerator:
    """Maze generator using iterative DFS (recursive backtracker).

    Attributes:
        width: Maze width in cells.
        height: Maze height in cells.
        seed: Random seed for reproducibility.
        perfect: Whether to generate a perfect maze.
        entry: Entry coordinates (x, y).
        exit: Exit coordinates (x, y).
        grid: 2D list of wall bitmasks.
    """

    def __init__(self, config: MazeConfig) -> None:
        """Initialize the maze generator with a config.

        Args:
            config: A validated MazeConfig instance.
        """
        self.width: int = config.width
        self.height: int = config.height
        self.seed: int | None = config.seed
        self.perfect: bool = config.perfect
        self.entry: tuple[int, int] = config.entry
        self.exit: tuple[int, int] = config.exit
        self.grid: list[list[int]] = [
            [0xF for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def generate(self) -> list[list[int]]:
        """Generate the maze and return the grid.

        Returns:
            2D list of ints representing the maze wall bitmasks.
        """
        random.seed(self.seed)
        random.seed(self.seed)
        self._carve_dfs()
        self._enforce_borders()  # add this
        self._place_42()
        return self.grid

    def _carve_dfs(self) -> None:
        """Carve passages through the grid using iterative DFS.

        Visits every cell exactly once, opening walls between
        cells to create a perfect maze.
        """
        stack: list[tuple[int, int]] = [self.entry]
        visited: set[tuple[int, int]] = {self.entry}

        while stack:
            x, y = stack[-1]

            neighbours: list[tuple[int, int, str, int, int]] = []
            for direction, (dx, dy, current_wall, neighbour_wall) in DIRECTIONS.items():
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.width and
                        0 <= ny < self.height and
                        (nx, ny) not in visited):
                    neighbours.append((nx, ny, direction, current_wall, neighbour_wall))

            if neighbours:
                nx, ny, direction, current_wall, neighbour_wall = random.choice(neighbours)
                self._carve_passage(x, y, nx, ny, current_wall, neighbour_wall)
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()

    def _carve_passage(
        self,
        x: int,
        y: int,
        nx: int,
        ny: int,
        current_wall: int,
        neighbour_wall: int
    ) -> None:
        """Open the wall between two adjacent cells.

        Args:
            x: Current cell x coordinate.
            y: Current cell y coordinate.
            nx: Neighbour cell x coordinate.
            ny: Neighbour cell y coordinate.
            current_wall: Wall bit to clear on the current cell.
            neighbour_wall: Wall bit to clear on the neighbour cell.
        """
        self.grid[y][x] &= ~current_wall
        self.grid[ny][nx] &= ~neighbour_wall

    def _place_42(self) -> None:
        """Stamp the '42' pattern onto the maze using fully closed cells.

        Prints an error message if the maze is too small to fit the pattern.
        """
        pattern_width = 9
        pattern_height = 5

        if self.width < pattern_width + 2 or self.height < pattern_height + 2:
            print("Error: maze too small to display the '42' pattern")
            return

        start_x = (self.width - pattern_width) // 2
        start_y = (self.height - pattern_height) // 2

        PATTERN_42 = [
            "X  X XXXX",
            "X  X X   ",
            "XXXX XXX ",
            "   X X   ",
            "   X XXXX",
        ]

        # collect all "42" cells first
        pattern_cells: set[tuple[int, int]] = set()
        for row_idx, row in enumerate(PATTERN_42):
            for col_idx, char in enumerate(row):
                if char == "X":
                    px = start_x + col_idx
                    py = start_y + row_idx
                    pattern_cells.add((px, py))

        # stamp 0xF on all pattern cells
        for px, py in pattern_cells:
            self.grid[py][px] = 0xF

        # close walls of neighbours pointing into pattern cells
        for px, py in pattern_cells:
            for direction, (dx, dy, current_wall, neighbour_wall) in DIRECTIONS.items():
                nx, ny = px + dx, py + dy
                if (0 <= nx < self.width and
                        0 <= ny < self.height and
                        (nx, ny) not in pattern_cells):
                    self.grid[ny][nx] |= neighbour_wall