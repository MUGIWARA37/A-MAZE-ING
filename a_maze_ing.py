import sys
from src.config_parser import parse_config
from src.generator import MazeGenerator
from src.pathfinder import find_shortest_path
from src.writer import write_maze
from src.display import run_display


def main() -> None:
    """Main entry point for the maze generator.

    Reads config file, generates maze, writes output,
    and launches the visual display.
    """
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        sys.exit(1)

    filepath = sys.argv[1]

    try:
        config = parse_config(filepath)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except (KeyError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    try:
        generator = MazeGenerator(config)
        grid = generator.generate()
    except Exception as e:
        print(f"Error generating maze: {e}")
        sys.exit(1)

    try:
        directions = find_shortest_path(grid, config.entry, config.exit)
    except ValueError as e:
        print(f"Error finding path: {e}")
        sys.exit(1)

    try:
        write_maze(
            grid,
            config.entry,
            config.exit,
            directions,
            config.output_file
        )
    except IOError as e:
        print(f"Error writing output: {e}")
        sys.exit(1)

    try:
        run_display(config)
    except KeyboardInterrupt:
        print("\nBye!")
        sys.exit(0)
    except Exception as e:
        print(f"Display error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
