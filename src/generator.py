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
        self._pattern_cells: set[tuple[int, int]] = set()

    def generate(self) -> list[list[int]]:
        """Generate the maze and return the grid.

        Returns:
            2D list of ints representing the maze wall bitmasks.
        """
        random.seed(self.seed)
        self._place_42()        # place 42 FIRST
        self._carve_dfs()       # DFS avoids 42 cells
        self._enforce_borders()  # enforce borders last
        return self.grid

    def _carve_dfs(self) -> None:
        """Carve passages through the grid using iterative DFS.

        Pre-marks 42 pattern cells as visited so DFS routes around them.
        """
        stack: list[tuple[int, int]] = [self.entry]
        # pre-mark 42 cells as visited so DFS never carves through them
        visited: set[tuple[int, int]] = {self.entry} | self._pattern_cells

        while stack:
            x, y = stack[-1]

            neighbours: list[tuple[int, int, str, int, int]] = []
            for direction, value in DIRECTIONS.items():
                dx, dy, current_wall, neighbour_wall = value
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.width and
                        0 <= ny < self.height and
                        (nx, ny) not in visited):
                    neighbours.append(
                        (nx, ny, direction, current_wall, neighbour_wall))

            if neighbours:
                choice = random.choice(neighbours)
                nx, ny, direction, current_wall, neighbour_wall = choice
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
        """Stamp the '42' pattern onto the maze before DFS carving."""
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
                    px = start_x + col_idx
                    py = start_y + row_idx
                    pattern_cells.add((px, py))

        self._pattern_cells = pattern_cells

        # stamp 0xF on all pattern cells
        for px, py in pattern_cells:
            self.grid[py][px] = 0xF

    def _enforce_borders(self) -> None:
        """Ensure all border cells have their outer walls closed.
        Keeps entry and exit border walls open so the player
        can enter and exit the maze.
        """
        for x in range(self.width):
            # top row — close North wall
            self.grid[0][x] |= 0x1
            # bottom row — close South wall
            self.grid[self.height - 1][x] |= 0x4
        for y in range(self.height):
            # left column — close West wall
            self.grid[y][0] |= 0x8
            # right column — close East wall
            self.grid[y][self.width - 1] |= 0x2
        # reopen entry and exit border walls
        self._open_border_wall(self.entry)
        self._open_border_wall(self.exit)

    def _open_border_wall(self, cell: tuple[int, int]) -> None:
        """Open the outer wall of a border cell (entry or exit).

        Args:
            cell: The (x, y) coordinates of the border cell.
        """
        x, y = cell

        if y == 0:
            self.grid[y][x] &= ~0x1   # open North wall
        elif y == self.height - 1:
            self.grid[y][x] &= ~0x4   # open South wall
        elif x == 0:
            self.grid[y][x] &= ~0x8   # open West wall
        elif x == self.width - 1:
            self.grid[y][x] &= ~0x2   # open East wall

    def get_pattern_cells(self) -> set[tuple[int, int]]:
        """Return the set of cells used by the 42 pattern.

        Returns:
            Set of (x, y) coordinates of pattern cells.
        """
        return self._pattern_cells
