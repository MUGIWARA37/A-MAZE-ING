*This project has been created as part of the 42 curriculum by  rhlou, yaqasbi.*

# A-Maze-ing

## Description

A-Maze-ing is a maze generator written in Python that creates perfect mazes
using the iterative DFS (Depth-First Search) algorithm. The program reads a
configuration file, generates a maze, finds the shortest path from entry to
exit, writes the result to an output file, and displays the maze visually
in the terminal using curses.

The maze always contains a visible "42" pattern made of fully closed cells,
and supports multiple wall colors including an RGB rainbow effect.

## Instructions

### Requirements

- Python 3.10 or later
- pip

### Installation
```bash
# clone the repository
git clone https://github.com/yourusername/a-maze-ing.git
cd a-maze-ing

# install dependencies
make install
```

### Running the program
```bash
make run
```

Or directly:
```bash
python3 a_maze_ing.py config.txt
```

### Makefile commands

| Command | Description |
|---|---|
| `make install` | Install dependencies |
| `make run` | Run the program |
| `make debug` | Run with pdb debugger |
| `make clean` | Remove caches and build files |
| `make lint` | Run flake8 and mypy |
| `make lint-strict` | Run flake8 and mypy --strict |
| `make build` | Build the mazegen pip package |

## Configuration file

The configuration file uses `KEY=VALUE` pairs, one per line.
Lines starting with `#` are comments and are ignored.

### Mandatory keys

| Key | Description | Example |
|---|---|---|
| `WIDTH` | Maze width in cells | `WIDTH=20` |
| `HEIGHT` | Maze height in cells | `HEIGHT=15` |
| `ENTRY` | Entry coordinates (x,y) | `ENTRY=0,0` |
| `EXIT` | Exit coordinates (x,y) | `EXIT=19,14` |
| `OUTPUT_FILE` | Output filename | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Generate a perfect maze | `PERFECT=True` |

### Optional keys

| Key | Description | Example |
|---|---|---|
| `SEED` | Random seed for reproducibility | `SEED=42` |

### Example config file
```
# A-Maze-ing default configuration
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

## Output file format

The output file contains:
- One hexadecimal digit per cell, one row per line
- Each hex digit encodes which walls are closed as bits:
  - bit 0 (0x1) = North wall
  - bit 1 (0x2) = East wall
  - bit 2 (0x4) = South wall
  - bit 3 (0x8) = West wall
- An empty line after the grid
- Entry coordinates as `x,y`
- Exit coordinates as `x,y`
- Shortest path as a string of `N`, `E`, `S`, `W` directions

## Visual display

The maze is displayed in the terminal using curses.

### Controls

| Key | Action |
|---|---|
| `r` | Regenerate a new maze |
| `p` | Show / hide shortest path |
| `c` | Cycle wall color |
| `q` | Quit |

### Available wall colors

- White
- Green
- Yellow
- Red
- Cyan
- RGB rainbow effect

## Maze generation algorithm

The program uses the **iterative DFS** algorithm (also known as recursive
backtracker).

### How it works

1. Start at the entry cell
2. Mark it as visited
3. Randomly pick an unvisited neighbour
4. Carve a passage between current cell and neighbour
5. Move to the neighbour and repeat
6. If no unvisited neighbours exist — backtrack to previous cell
7. Stop when all cells are visited

### Why DFS?

- Simple to implement and understand
- Generates long winding corridors — interesting mazes
- No recursion limit issues — uses an explicit stack
- Fast — O(n) where n is the number of cells
- Produces perfect mazes naturally — exactly one path between any two cells

## Reusable module

The maze generation logic is available as a standalone pip-installable
package called `mazegen`.

### Installation
```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Basic usage
```python
from mazegen import MazeGenerator

# create a generator
gen = MazeGenerator(width=20, height=15, seed=42)

# generate the maze
grid = gen.generate()

# get the solution
solution = gen.get_solution()
print("Solution:", "".join(solution))
```

### Custom parameters
```python
gen = MazeGenerator(
    width=30,
    height=20,
    entry=(0, 0),
    exit=(29, 19),
    seed=123,
    perfect=True,
)
```

### Accessing the grid
```python
# grid is a 2D list of ints
# grid[y][x] = wall bitmask for cell at (x, y)
# bit 0 = North, bit 1 = East, bit 2 = South, bit 3 = West
# 1 = wall closed, 0 = wall open

cell = grid[0][0]
has_north_wall = bool(cell & 0x1)
has_east_wall  = bool(cell & 0x2)
has_south_wall = bool(cell & 0x4)
has_west_wall  = bool(cell & 0x8)
```

### Accessing the solution
```python
# returns a list of directions from entry to exit
solution = gen.get_solution()
# example: ['S', 'S', 'E', 'E', 'N', 'E']
```

### Building the package
```bash
make build
```

## Team and project management

### Roles

- **<your_login>** — sole developer

### Planning

- Week 1 — config parser, pathfinder, maze generator
- Week 2 — writer, display, mazegen package
- Week 3 — debugging, testing, documentation

### What worked well

- Using iterative DFS instead of recursive — no recursion limit issues
- Pre-marking "42" cells as visited before DFS — guarantees solvability
- Separating concerns into small focused modules

### What could be improved

- Add support for multiple generation algorithms
- Add animation during maze generation
- Add a graphical display using pygame

### Tools used

- VS Code — code editor
- Git — version control
- Claude AI — used for guidance on algorithm design,
  debugging, and code structure.

## Resources

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Depth-first search — Wikipedia](https://en.wikipedia.org/wiki/Depth-first_search)
- [Breadth-first search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Python curses documentation](https://docs.python.org/3/library/curses.html)
- [Pydantic documentation](https://docs.pydantic.dev)
- [Jamis Buck's maze algorithms](https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap)
