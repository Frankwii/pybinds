# This file is part of pybinds.
# 
# pybinds is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# 
# pybinds is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with pybinds. If not, see <https://www.gnu.org/licenses/>. 

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

    action_handler.grab_keyboard()

    action_handler.loop()
