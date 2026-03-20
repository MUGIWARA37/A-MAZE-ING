from pydantic import BaseModel, Field, model_validator
from typing import Tuple


class MazeConfig(BaseModel):
    width: int = Field(..., gt=0, description="Maze width in cells")
    height: int = Field(..., gt=0, description="Maze height in cells")
    entry: Tuple[int, int] = Field(..., description="Entry coordinates (x, y)")
    exit: Tuple[int, int] = Field(..., description="Exit coordinates (x, y)")
    output_file: str = Field(..., min_length=1, description="Output filename")
    perfect: bool = Field(..., description="Generate a perfect maze")
    seed: int | None = Field(default=None, description="Random seed")

    @model_validator(mode="after")
    def validate_coordinates(self) -> "MazeConfig":
        for name, coord in [("entry", self.entry), ("exit", self.exit)]:
            x, y = coord
            if not (0 <= x < self.width):
                raise ValueError(f"{name} x={x} out of bounds [0, {self.width - 1}]")
            if not (0 <= y < self.height):
                raise ValueError(f"{name} y={y} out of bounds [0, {self.height - 1}]")
        if self.entry == self.exit:
            raise ValueError("entry and exit must be different cells")
        return self


def parse_config(filepath: str) -> MazeConfig:
    try:
        config_dict: dict[str, any] = {}
        with open(filepath, "r") as config:
            for line in config:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ValueError(
                        f"Invalid line '{line}' — must follow the format 'KEY=VALUE'"
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

        return MazeConfig(**config_dict)

    except FileNotFoundError:
        raise FileNotFoundError(f"Config file '{filepath}' not found")
    except KeyError as e:
        raise KeyError(f"Missing mandatory key in config: {e}")
    except ValueError as e:
        raise ValueError(f"Invalid config value: {e}")