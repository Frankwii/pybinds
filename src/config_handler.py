import subprocess
import json

from pathlib import Path
from typing import Any

from action_handler import ActionHandlerConfig, KeyHandlerConfig, VisualsHandlerConfig
from draw_bar import DrawingConfig, XOrgConfig
from bind_node import BindNodeData, Keybind, Command
from text_rendering import TextRendererConfig

class ConfigManager:
    def __init__(self, config_file_path: Path):
        self.__config_path = config_file_path

        self.__pybinds_config = self.__parse_json(config_file_path)
        bindings_file = self.__find_bindings_file()
        self.__bindings_dict = self.__parse_json(bindings_file)
        self.__font_path, self.__font_size = self.__get_font_info()

        self.__background_color = self.__pybinds_config.get("color", {}).get("background", "#5533ff")

    @staticmethod
    def __parse_json(path: Path) -> dict[str, Any]:
        with open(path, 'r') as f:
            d = json.load(f)

        return d

    def __find_bindings_file(self) -> Path:
        bindings = self.__pybinds_config.get("bindings_file", "bindings.json")
        path = Path(bindings)

        if not path.is_absolute():
            path = self.__config_path.parent.joinpath(path)

        if not path.exists():
            raise ValueError(f"Unable to find bindings file at {path}")

        return path

    def __get_bindnode_data_internal(self, bindings_dict) -> BindNodeData:
        if isinstance(bindings_dict["termination"], str):
            return BindNodeData(
                    name=bindings_dict["name"],
                    key=Keybind(bindings_dict["key"]),
                    termination=Command(bindings_dict["termination"])
                    )
        else:
            return BindNodeData(
                    name=bindings_dict["name"],
                    key=Keybind(bindings_dict["key"]),
                    termination=list(
                        map(
                            lambda d: self.__get_bindnode_data_internal(d),
                            bindings_dict["termination"]
                            )
                        )
                    )
    def bindnode(self) -> BindNodeData:
        return self.__get_bindnode_data_internal(self.__bindings_dict)

    @staticmethod
    def __str_to_rgb(color: str) -> tuple[int, int, int]:
        stripped = color.lstrip("#")

        r, g, b = [256 * int(stripped[i:i+2], 16) for i in range(0, 6, 2)]

        return r, g, b
        
    def xorg(self) -> XOrgConfig:
        display = self.__pybinds_config.get("display", {})
        color = self.__pybinds_config.get("color", {})

        bar_height = display.get("bar_height_in_pixels", 20)
        border_size = display.get("border_size_in_pixels", 1)

        background_color = color.get("background", "#55bbff")
        border_color = color.get("border", "#ffffff")

        return XOrgConfig(
            bar_height=bar_height,
            border_size=border_size,
            background_color=self.__str_to_rgb(background_color),
            border_color=self.__str_to_rgb(border_color)
        )

    def __drawing(self) -> DrawingConfig:
        display = self.__pybinds_config.get("display", {})

        leftmost_padding = display.get("initial_padding_in_pixels", 50)
        padding = display.get("padding_in_pixels", 5)
        skip = display.get("skip_in_pixels", 10)

        return DrawingConfig(
            initial_padding_in_pixels=leftmost_padding,
            padding_in_pixels=padding,
            skip_in_pixels=skip
        )

    def __get_font_info(self):
        font = self.__pybinds_config.get("font", {})
        name: str = font.get("name", "UbuntuMono")
        style: str = font.get("style", "Bold")
        font_size: int = font.get("size", 12)

        name_pattern = "".join(
            filter(
                lambda s: len(s)>0,
                map(
                    lambda p: p.strip().capitalize(),
                    name.strip().split(" ")
                )
            )
        )
        pattern = f"{name_pattern}.*-{style.capitalize()}"

        p1 = subprocess.run(["fc-list"], capture_output=True, text=True, check=True)
        output = str(subprocess.run(["grep", pattern], input=p1.stdout, capture_output=True, text=True).stdout)
        first = output.split(":", 1)

        if len(first)==1:
            raise ValueError(f"Unable to find font with fc-list and pattern {pattern}")

        font_path = Path(first[0])

        return font_path, font_size

    def __text_renderer(self, name: str, default: str) -> TextRendererConfig:
        color = self.__pybinds_config.get("color", {}).get(name, default)
        return TextRendererConfig(
            font_path=self.__font_path,
            font_size=self.__font_size,
            background_color=self.__background_color,
            foreground_color=color
        )

    def separator_renderer(self) -> TextRendererConfig:
        return self.__text_renderer("separator", "#ffff00")

    def key_renderer(self) -> TextRendererConfig:
        return self.__text_renderer("key", "#ff0000")

    def text_renderer(self) -> TextRendererConfig:
        return self.__text_renderer("text", "#00ff00")

    def __visuals_handler(self) -> VisualsHandlerConfig:
        drawing_config = self.__drawing()
        separator = self.__pybinds_config.get("separator", ":")

        return VisualsHandlerConfig(
            separator = separator,
            drawing_config = drawing_config
        )

    @staticmethod
    def __process_key(k: str) -> Keybind:
        if len(k) != 1:
            raise ValueError(f"Invalid key specified: {k} should have length 1. It has length {len(k)}")

        return Keybind(k)

    def __key_handler(self) -> KeyHandlerConfig:
        back_keys_input = self.__pybinds_config.get("back_keys", ["h"])
        exit_keys_input = self.__pybinds_config.get("exit_keys", ["q"])

        back_keys = list(map(ConfigManager.__process_key, back_keys_input))
        exit_keys = list(map(ConfigManager.__process_key, exit_keys_input))

        return KeyHandlerConfig(back_keys = back_keys, exit_keys=exit_keys)

    def action_handler(self) -> ActionHandlerConfig:
        shell = self.__pybinds_config.get("shell", "/bin/sh")

        return ActionHandlerConfig(
            visuals_config = self.__visuals_handler(),
            key_config = self.__key_handler(),
            shell = shell
        )

if __name__ == "__main__":
    path = Path("/home/frank/.config/pybinds/config.json")

    config_handler = ConfigManager(path)

    # print(config_handler.drawing())
    # print(config_handler.xorg())
    print(config_handler.action_handler())





