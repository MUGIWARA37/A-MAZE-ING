import curses
import colorsys
import time
from src.config_parser import MazeConfig
from src.generator import MazeGenerator
from src.pathfinder import find_shortest_path, DIRECTIONS


WALL_COLORS = ["white", "green", "yellow", "red", "cyan", "HLWASA"]

COLOR_MAP = {
    "white": 1,
    "green": 2,
    "yellow": 3,
    "red": 4,
    "cyan": 5,
}


def setup_colors() -> None:
    """Initialize curses color pairs."""
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    curses.init_pair(4, curses.COLOR_RED, -1)
    curses.init_pair(5, curses.COLOR_CYAN, -1)
    curses.init_pair(6, curses.COLOR_MAGENTA, -1)


def _get_wall_color(is_rgb: bool, color_name: str) -> int:
    """Return the curses color attribute for walls.

    Args:
        is_rgb: Whether to use the RGB cycling effect.
        color_name: Name of the wall color.

    Returns:
        Curses color attribute integer.
    """
    if is_rgb:
        if curses.can_change_color():
            hue = (time.time() * 0.05) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
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


def _get_pattern_bg_attr() -> int:
    """Return curses attr for the 42 pattern with RGB background."""
    if curses.can_change_color():
        hue = (time.time() * 0.1) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)

        curses.init_color(
            11,
            int(r * 1000),
            int(g * 1000),
            int(b * 1000)
        )
        curses.init_pair(8, curses.COLOR_BLACK, 11)
        return curses.color_pair(8) | curses.A_BOLD

    return curses.color_pair(6) | curses.A_BOLD


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
    pattern_cells: set[tuple[int, int]],
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
        pattern_cells: Set of (x, y) coordinates of the 42 pattern.
    """
    try:
        if (cx, cy) == entry:
            stdscr.addstr(
                screen_y, screen_x, "🎮",
            )
        elif (cx, cy) == exit:
            stdscr.addstr(
                screen_y, screen_x, "👾",
            )
        elif (cx, cy) in pattern_cells:
            stdscr.addstr(
                screen_y, screen_x, " ",
                _get_pattern_bg_attr()
            )
        elif show_path and (cx, cy) in path_set:
            stdscr.addstr(
                screen_y, screen_x, "◽",

            )
        else:
            stdscr.addstr(screen_y, screen_x, " ")
    except curses.error:
        pass


def render_maze(
    stdscr: curses.window,
    grid: list[list[int]],
    entry: tuple[int, int],
    exit: tuple[int, int],
    path: list[tuple[int, int]],
    show_path: bool,
    color_name: str,
    pattern_cells: set[tuple[int, int]],
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
        pattern_cells: Set of (x, y) coordinates of the 42 pattern.
        offset_y: Vertical offset from top of screen.
        offset_x: Horizontal offset from left of screen.
    """
    height = len(grid)
    width = len(grid[0])
    path_set = set(path)
    is_rgb = color_name == "HLWASA"

    max_y, max_x = stdscr.getmaxyx()

    if 2 * height + 10 > max_y or 4 * width + 10 > max_x:
        try:
            stdscr.clear()
            stdscr.addstr(
                0, 0,
                "Terminal too small! Resize to continue.",
                curses.color_pair(4) | curses.A_BOLD
            )
            stdscr.refresh()
        except curses.error:
            pass
        return

    for row in range(2 * height + 1):
        for col in range(2 * width + 1):
            cy = row // 2
            cx = col // 2
            screen_y = offset_y + row
            screen_x = offset_x + (col * 2)

            if screen_y >= max_y - 1 or screen_x >= max_x - 2:
                continue

            try:
                if row % 2 == 0 and col % 2 == 0:
                    wall_attr = _get_wall_color(is_rgb, color_name)
                    stdscr.addstr(screen_y, screen_x, "✢", wall_attr)

                elif row % 2 == 0 and col % 2 == 1:
                    if row == 0 or row == 2 * height:
                        has_wall = True
                    else:
                        has_wall = bool(grid[cy - 1][cx] & 0x4)
                    if has_wall:
                        wall_attr = _get_wall_color(is_rgb, color_name)
                        stdscr.addstr(screen_y, screen_x, "— ", wall_attr)
                    else:
                        stdscr.addstr(screen_y, screen_x, "  ")

                elif row % 2 == 1 and col % 2 == 0:
                    if col == 0 or col == 2 * width:
                        has_wall = True
                    else:
                        has_wall = bool(grid[cy][cx - 1] & 0x2)
                    if has_wall:
                        wall_attr = _get_wall_color(is_rgb, color_name)
                        stdscr.addstr(screen_y, screen_x, "|", wall_attr)
                    else:
                        stdscr.addstr(screen_y, screen_x, " ")

                else:
                    _render_cell(
                        stdscr,
                        screen_y,
                        screen_x,
                        cx,
                        cy,
                        entry,
                        exit,
                        path_set,
                        show_path,
                        pattern_cells,
                    )

            except curses.error:
                pass

    stdscr.refresh()


def show_menu(
    stdscr: curses.window,
    height: int,
    color_name: str,
    show_path: bool,
) -> None:
    """Render the interaction menu below the maze.

    Args:
        stdscr: The curses window to draw on.
        height: Maze height in cells.
        color_name: Current wall color name.
        show_path: Whether the path is currently shown.
    """
    menu_y = (2 * height + 1) + 3

    try:
        stdscr.addstr(
            menu_y, 2,
            "=== A-Maze-ing ===",
            curses.color_pair(5) | curses.A_BOLD,
        )
        stdscr.addstr(
            menu_y + 1, 2, "[r]",
            curses.color_pair(3) | curses.A_BOLD
        )
        stdscr.addstr(menu_y + 1, 6, " regenerate maze")

        stdscr.addstr(
            menu_y + 2, 2, "[p]",
            curses.color_pair(3) | curses.A_BOLD
        )
        stdscr.addstr(
            menu_y + 2, 6,
            " show/hide path  (currently: "
            f"{'shown' if show_path else 'hidden'})",
        )

        stdscr.addstr(
            menu_y + 3, 2, "[c]",
            curses.color_pair(3) | curses.A_BOLD
        )
        stdscr.addstr(
            menu_y + 3, 6,
            f" cycle wall color (currently: {color_name})"
        )

        stdscr.addstr(
            menu_y + 4, 2, "[q]",
            curses.color_pair(4) | curses.A_BOLD
        )
        stdscr.addstr(menu_y + 4, 6, " quit")

    except curses.error:
        pass


def _build_path_coords(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit: tuple[int, int],
) -> list[tuple[int, int]]:
    """Convert path directions to a list of (x, y) coordinates.

    Args:
        grid: 2D list of wall bitmasks.
        entry: Entry coordinates (x, y).
        exit: Exit coordinates (x, y).

    Returns:
        List of (x, y) coordinates along the shortest path.
    """
    try:
        directions = find_shortest_path(grid, entry, exit)
    except ValueError:
        return []

    coords: list[tuple[int, int]] = [entry]
    x, y = entry

    for direction in directions:
        dx, dy, _, _ = DIRECTIONS[direction]
        x, y = x + dx, y + dy
        coords.append((x, y))

    return coords


def run_display(config: MazeConfig) -> None:
    """Main display loop — renders maze and handles user input.

    Args:
        config: A validated MazeConfig instance.
    """
    def _main(stdscr: curses.window) -> None:
        setup_colors()
        curses.curs_set(0)
        stdscr.nodelay(True)

        color_index: int = 0
        show_path: bool = False

        generator = MazeGenerator(config)
        grid = generator.generate()
        pattern_cells = generator.get_pattern_cells()
        path_coords = _build_path_coords(
            grid, config.entry, config.exit
        )

        while True:
            color_name = WALL_COLORS[color_index]

            stdscr.erase()

            render_maze(
                stdscr,
                grid,
                config.entry,
                config.exit,
                path_coords,
                show_path,
                color_name,
                pattern_cells,
            )
            show_menu(stdscr, config.height, color_name, show_path)
            stdscr.refresh()

            key = stdscr.getch()

            if key == -1:
                if color_name == "rgb":
                    time.sleep(0.00000001)
                else:
                    time.sleep(0.1)
                continue
            elif key == ord("q"):
                break
            elif key == ord("r"):
                generator = MazeGenerator(config)
                grid = generator.generate()
                pattern_cells = generator.get_pattern_cells()
                path_coords = _build_path_coords(
                    grid, config.entry, config.exit
                )
            elif key == ord("p"):
                show_path = not show_path
            elif key == ord("c"):
                color_index = (color_index + 1) % len(WALL_COLORS)

    curses.wrapper(_main)
