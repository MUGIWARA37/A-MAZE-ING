import curses
import colorsys
import time
from src.config_parser import MazeConfig
from src.generator import MazeGenerator
from src.pathfinder import find_shortest_path

WALL_COLORS = ["white", "green", "yellow", "red", "cyan"]

COLOR_MAP = {
    "white":  1,
    "green":  2,
    "yellow": 3,
    "red":    4,
    "cyan":   5,
}

def setup_colors() -> None:
    """Initialize curses color pairs."""
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE,  -1)
    curses.init_pair(2, curses.COLOR_GREEN,  -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    curses.init_pair(4, curses.COLOR_RED,    -1)
    curses.init_pair(5, curses.COLOR_CYAN,   -1)
    curses.init_pair(6, curses.COLOR_MAGENTA,-1)


def render_maze(
    stdscr: curses.window,
    grid: list[list[int]],
    entry: tuple[int, int],
    exit: tuple[int, int],
    path: list[tuple[int, int]],
    show_path: bool,
    color_name: str,
    offset_y: int = 1,
    offset_x: int = 2,
) -> None:
    """Render the maze on the terminal screen.

    Args:
        stdscr: The curses window to draw on.
        grid: 2D list of wall bitmasks.
        entry: Entry coordinates (x, y).
        exit: Exit coordinates (x, y).
        path: List of (x, y) coordinates on the shortest path.
        show_path: Whether to display the path.
        color_name: Name of the wall color.
        offset_y: Vertical offset from top of screen.
        offset_x: Horizontal offset from left of screen.
    """
    height = len(grid)
    width = len(grid[0])
    path_set = set(path)
    is_rgb = color_name == "rgb"

    for row in range(2 * height + 1):
        for col in range(2 * width + 1):
            cy = row // 2
            cx = col // 2
            screen_y = offset_y + row
            screen_x = offset_x + (col * 2)

            try:
                if row % 2 == 0 and col % 2 == 0:
                    wall_attr = _get_wall_color(is_rgb, color_name)
                    stdscr.addstr(screen_y, screen_x, "+", wall_attr)

                elif row % 2 == 0 and col % 2 == 1:
                    has_wall = cy > 0 and (grid[cy - 1][cx] & 0x4)
                    if has_wall:
                        wall_attr = _get_wall_color(is_rgb, color_name)
                        stdscr.addstr(screen_y, screen_x, "──", wall_attr)
                    else:
                        stdscr.addstr(screen_y, screen_x, "  ")

                elif row % 2 == 1 and col % 2 == 0:
                    has_wall = cx > 0 and (grid[cy][cx - 1] & 0x2)
                    if has_wall:
                        wall_attr = _get_wall_color(is_rgb, color_name)
                        stdscr.addstr(screen_y, screen_x, "│", wall_attr)
                    else:
                        stdscr.addstr(screen_y, screen_x, " ")

                else:
                    _render_cell(
                        stdscr, screen_y, screen_x,
                        cx, cy, entry, exit,
                        path_set, show_path
                    )

            except curses.error:
                pass

    stdscr.refresh()


def _get_wall_color(is_rgb: bool, color_name: str) -> int:
    """Return the curses color attribute for walls.

    Args:
        is_rgb: Whether to use the RGB cycling effect.
        color_name: Name of the wall color.

    Returns:
        Curses color attribute integer.
    """
    if is_rgb:
        hue = (time.time() * 0.1) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        if curses.can_change_color():
            curses.init_color(
                10,
                int(r * 1000),
                int(g * 1000),
                int(b * 1000)
            )
            curses.init_pair(7, 10, -1)
            return curses.color_pair(7)
        return curses.color_pair(COLOR_MAP["cyan"])
    return curses.color_pair(COLOR_MAP[color_name])


def _render_cell(
    stdscr: curses.window,
    screen_y: int,
    screen_x: int,
    cx: int,
    cy: int,
    entry: tuple[int, int],
    exit: tuple[int, int],
    path_set: set[tuple[int, int]],
    show_path: bool,
) -> None:
    """Render the interior of a single maze cell.

    Args:
        stdscr: The curses window to draw on.
        screen_y: Screen row to draw at.
        screen_x: Screen column to draw at.
        cx: Cell x coordinate.
        cy: Cell y coordinate.
        entry: Entry coordinates (x, y).
        exit: Exit coordinates (x, y).
        path_set: Set of (x, y) path coordinates.
        show_path: Whether to display the path.
    """
    if (cx, cy) == entry:
        stdscr.addstr(
            screen_y, screen_x, "S",
            curses.color_pair(4) | curses.A_BOLD
        )
    elif (cx, cy) == exit:
        stdscr.addstr(
            screen_y, screen_x, "E",
            curses.color_pair(4) | curses.A_BOLD
        )
    elif show_path and (cx, cy) in path_set:
        stdscr.addstr(
            screen_y, screen_x, "·",
            curses.color_pair(5) | curses.A_BOLD
        )
    else:
        stdscr.addstr(screen_y, screen_x, " ")