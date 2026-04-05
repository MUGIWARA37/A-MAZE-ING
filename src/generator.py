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
        if self.seed:
            random.seed(str(self.seed))
        else:
            random.seed()
        self._place_42()        # place 42 FIRST
        self._carve_dfs()       # DFS avoids 42 cells
        if not self.perfect:
            self._make_imperfect()  # delete randome walls
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
        """Stamp the 42 pattern onto the maze before DFS carving.

        Shifts the pattern if it overlaps with entry or exit.
        """
        pattern_width = 9
        pattern_height = 5

        if self.width < pattern_width + 2 or self.height < pattern_height + 2:
            print("The maze dimention are too smalle to carve the 42 patern"
                  "The maze geneted without it !!")
            return

        PATTERN_42 = [
            "X  X XXXX",
            "X  X    X",
            "XXXX XXXX",
            "   X X   ",
            "   X XXXX",
        ]

        center_x = (self.width - pattern_width) // 2
        center_y = (self.height - pattern_height) // 2

        # generate all valid positions sorted by distance from center
        positions = []
        for sy in range(1, self.height - pattern_height):
            for sx in range(1, self.width - pattern_width):
                dist = abs(sx - center_x) + abs(sy - center_y)
                positions.append((dist, sx, sy))
        positions.sort()

        for _, start_x, start_y in positions:
            # build candidate pattern cells
            candidate_cells: set[tuple[int, int]] = set()
            for row_idx, row in enumerate(PATTERN_42):
                for col_idx, char in enumerate(row):
                    if char == "X":
                        candidate_cells.add(
                            (start_x + col_idx, start_y + row_idx)
                        )

            # skip if pattern overlaps entry or exit
            if self.entry in candidate_cells or self.exit in candidate_cells:
                continue

            # valid position found
            self._pattern_cells = candidate_cells
            for px, py in candidate_cells:
                self.grid[py][px] = 0xF
            return

        # no valid position found
        print("Warning: could not place '42' pattern without "
              "overlapping entry/exit")
        self._pattern_cells = set()

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

    def _make_imperfect(self) -> None:
        """Remove random walls to create loops in the maze.

        Only called when perfect=False. Creates multiple paths
        between cells by randomly opening walls.
        """
        import math
        # remove ~15% of walls randomly
        walls_to_remove = math.floor(self.width * self.height * 0.15)

        for _ in range(walls_to_remove):
            # pick a random cell
            x = random.randint(0, self.width - 2)
            y = random.randint(0, self.height - 2)

            # pick a random direction
            direction, vals = random.choice(list(DIRECTIONS.items()))
            dx, dy, current_wall, neighbour_wall = vals
            nx, ny = x + dx, y + dy

            # skip if neighbour is out of bounds or a pattern cell
            if not (0 <= nx < self.width and 0 <= ny < self.height):
                continue
            if (nx, ny) in self._pattern_cells:
                continue
            if (x, y) in self._pattern_cells:
                continue

            # remove the wall
            self.grid[y][x] &= ~current_wall
            self.grid[ny][nx] &= ~neighbour_wall
