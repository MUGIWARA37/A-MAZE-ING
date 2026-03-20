import random
from src.config_parser import MazeConfig
from src.pathfinder import DIRECTIONS


class MazeGenerator:
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