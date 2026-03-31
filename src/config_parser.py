class MazeConfig:
    """
    Configuration class for the Maze game.
    """

    def __init__(self, width, height, num_mazes):
        self.width = width
        self.height = height
        self.num_mazes = num_mazes

    def validate_coordinates(self, x, y):
        """
        Validates if the given (x, y) coordinates are within the maze bounds.

        :param x: X-coordinate
        :param y: Y-coordinate
        :return: True if coordinates are valid, otherwise False
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def parse_config(self, config_data):
        """
        Parses the configuration data for the Maze game.

        :param config_data: Configuration data
        :return: None
        """
        # Implementation of the parsing logic
        pass
        