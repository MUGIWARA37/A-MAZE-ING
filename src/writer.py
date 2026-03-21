from __future__ import annotations


def write_maze(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit: tuple[int, int],
    path: list[str],
    output_file: str
) -> None:
    """Write the maze to the output file in the required format.

    Format:
        - One hex digit per cell, one row per line
        - Empty line
        - Entry coordinates as x,y
        - Exit coordinates as x,y
        - Shortest path as a string of N, E, S, W directions

    Args:
        grid: 2D list of wall bitmasks.
        entry: Entry coordinates (x, y).
        exit: Exit coordinates (x, y).
        path: List of directions from entry to exit.
        output_file: Path to the output file.

    Raises:
        IOError: If the file cannot be written.
    """
    try:
        with open(output_file, "w") as f:
            # write grid row by row
            for row in grid:
                f.write("".join(f"{cell:X}" for cell in row) + "\n")

            # empty line separating grid from metadata
            f.write("\n")

            # entry coordinates
            f.write(f"{entry[0]},{entry[1]}\n")

            # exit coordinates
            f.write(f"{exit[0]},{exit[1]}\n")

            # shortest path
            f.write("".join(path) + "\n")

    except IOError as e:
        raise IOError(f"Could not write to file '{output_file}': {e}")