from pydantic import BaseModel, Field, model_validator
from typing import Tuple, Any


class MazeConfig(BaseModel):
    """Validated configuration for maze generation.

        Attributes:
            width: Maze width in cells.
            height: Maze height in cells.
            entry: Entry coordinates (x, y).
            exit: Exit coordinates (x, y).
            output_file: Output filename for the maze.
            perfect: Whether to generate a perfect (loop-free) maze.
            seed: Random seed for reproducibility.
        """
    width: int = Field(..., gt=1, description="Maze width in cells")
    height: int = Field(..., gt=1, description="Maze height in cells")
    entry: Tuple[int, int] = Field(..., description="Entry coordinates (x, y)")
    exit: Tuple[int, int] = Field(..., description="Exit coordinates (x, y)")
    output_file: str = Field(..., min_length=1, description="Output filename")
    perfect: bool = Field(..., description="Generate a perfect maze")
    seed: int | None = Field(default=None, description="Random seed")

    @model_validator(mode="after")
    def validate_coordinates(self) -> "MazeConfig":
        """Validate entry/exit coordinates and output file constraints.

                Returns:
                    The validated MazeConfig instance.

                Raises:
                    ValueError: If coordinates are out of bounds, entry equals
                    exit,
                        output_file is not a .txt file, or output_file
                        conflicts with
                        reserved filenames.
                """
        for name, coord in [("entry", self.entry), ("exit", self.exit)]:
            x, y = coord
            if not (0 <= x < self.width):
                raise ValueError(
                    f"{name} x={x} out of bounds [0, {self.width - 1}]"
                )
            if not (0 <= y < self.height):
                raise ValueError(
                    f"{name} y={y} out of bounds [0, {self.height - 1}]"
                )
        if self.entry == self.exit:
            raise ValueError("entry and exit must be different cells")
        if not self.output_file.endswith(".txt"):
            raise ValueError("The out_put file must "
                             "be a txt file (example.txt) !")
        if (self.output_file == "config.txt"
           or self.output_file == "requirements.txt"):
            raise ValueError(f"{self.output_file} is a programme file please "
                             "change the output_file name")
        return self


def parse_config(filepath: str) -> MazeConfig:
    """Parse a key=value config file into a validated MazeConfig.

        Args:
            filepath: Path to the configuration file.

        Returns:
            A validated MazeConfig instance.

        Raises:
            FileNotFoundError: If the file does not exist.
            KeyError: If a required key is missing in the config.
            ValueError: If a line is malformed or a value cannot be parsed.
        """
    try:
        config_dict: dict[str, Any] = {}
        with open(filepath, "r") as config:
            for line in config:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ValueError(
                        f"Invalid line '{line}' — must "
                        "follow the format 'KEY=VALUE'"
                    )
                key, value = line.split("=", 1)
                config_dict[key.strip().lower()] = value.strip()

        config_dict["width"] = int(config_dict["width"])
        config_dict["height"] = int(config_dict["height"])

        entry_x, entry_y = config_dict["entry"].split(",")
        config_dict["entry"] = (int(entry_x.strip()), int(entry_y.strip()))

        exit_x, exit_y = config_dict["exit"].split(",")
        config_dict["exit"] = (int(exit_x.strip()), int(exit_y.strip()))

        config_dict["perfect"] = config_dict["perfect"].lower() == "true"

        if "seed" in config_dict:
            config_dict["seed"] = int(config_dict["seed"])
        else:
            config_dict["seed"] = None

        return MazeConfig(**config_dict)

    except FileNotFoundError:
        raise FileNotFoundError(f"Config file '{filepath}' not found")
    except KeyError as e:
        raise KeyError(f"Missing mandatory key in config: {e}")
    except ValueError as e:
        msg = e.errors()[0]["msg"]
        raise ValueError(f"{msg}")
    except ValueError as e:
        raise ValueError(f"Invalid config value: {e}")
