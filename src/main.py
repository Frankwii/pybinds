import argparse
import os

from pathlib import Path

from action_handler import ActionHandler
from bind_node import BindNode
from config_handler import ConfigManager
from draw_bar import XOrgHandler
from text_rendering import TextRenderer

def parse_cli_args() -> Path:
    parser = argparse.ArgumentParser()

    xdg_config_home = str(os.getenv("XDG_CONFIG_HOME"))
    config_path = "pybinds/config.json"
    parser.add_argument(
            "-c",
            "--config",
            help=f"Path to configuration file. Default: $XDG_CONFIG_HOME/{config_path}",
            default=f"{xdg_config_home}/{config_path}"
        )

    args = parser.parse_args()

    return Path(args.config)

def initialize_renderers(config_handler: ConfigManager):
    seprend = TextRenderer(config_handler.separator_renderer())
    keyrend = TextRenderer(config_handler.key_renderer())
    texrend = TextRenderer(config_handler.text_renderer())

    return {
        "separator": seprend,
        "keys": keyrend,
        "texts": texrend
    }

if __name__ == "__main__":

    config_path = parse_cli_args()

    ch = ConfigManager(config_path)

    renderers = initialize_renderers(ch)

    xorg_handler = XOrgHandler(ch.xorg())

    root = BindNode(ch.bindnode())

    action_handler = ActionHandler(
        root = root,
        renderers = renderers,
        xorg_handler = xorg_handler,
        config = ch.action_handler()
    )

    action_handler.loop()
