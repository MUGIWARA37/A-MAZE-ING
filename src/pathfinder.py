from collections import deque


DIRECTIONS: dict[str, tuple[int, int, int, int]] = {
    "N": (0, -1, 0x1, 0x4),
    "E": (1,  0, 0x2, 0x8),
    "S": (0,  1, 0x4, 0x1),
    "W": (-1, 0, 0x8, 0x2),
}


def find_shortest_path(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit: tuple[int, int]
) -> list[str]:
    """Find the shortest path from entry to exit using BFS.

    Args:
        grid: 2D list where grid[y][x] is the wall bitmask of that cell.
        entry: Starting coordinates (x, y).
        exit: Target coordinates (x, y).

    Returns:
        List of directions ['N', 'E', 'S', 'W'] from entry to exit.

    Raises:
        ValueError: If no path exists between entry and exit.
    """
    width = len(grid[0])
    height = len(grid)

    queue: deque[tuple[int, int]] = deque()
    queue.append(entry)

    visited: set[tuple[int, int]] = {entry}
    came_from: dict[
        tuple[int, int], tuple[tuple[int, int], str] | None
    ] = {entry: None}

    while queue:
        x, y = queue.popleft()

        if (x, y) == exit:
            return reconstruct_path(came_from, entry, exit)

        for direction, (dx, dy, current_wall, neighbour_wall) in DIRECTIONS.items():
            nx, ny = x + dx, y + dy

            if not (0 <= nx < width and 0 <= ny < height):
                continue

            if grid[y][x] & current_wall or grid[ny][nx] & neighbour_wall:
                continue

            if (nx, ny) in visited:
                continue

            visited.add((nx, ny))
            came_from[(nx, ny)] = ((x, y), direction)
            queue.append((nx, ny))

    raise ValueError(f"No path found between {entry} and {exit}")


def reconstruct_path(
    came_from: dict[tuple[int, int], tuple[tuple[int, int], str] | None],
    entry: tuple[int, int],
    exit: tuple[int, int]
) -> list[str]:
    """Walk came_from backwards from exit to entry and return directions.

    Args:
        came_from: Dict mapping each cell to its parent cell and direction.
        entry: Starting coordinates.
        exit: Target coordinates.

    Returns:
        List of directions from entry to exit.
    """
    path: list[str] = []
    current = exit

    while current != entry:
        parent = came_from[current]
        if parent is None:
            break
        cell, direction = parent
        path.append(direction)
        current = cell

    path.reverse()
    return path
