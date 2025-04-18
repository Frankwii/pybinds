import json
import argparse
import os

from bind_node import BindNode
from parse_config import BindNodeData

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    xdg_config_home = str(os.getenv("XDG_CONFIG_HOME"))
    command_config_dir = "pybinds/commands.json"
    parser.add_argument(
            "-c",
            "--config",
            help=f"Path to configuration file. Default: $XDG_CONFIG_HOME/{command_config_dir}",
            default=f"{xdg_config_home}/{command_config_dir}"
        )

    return parser.parse_args()

def load_config_dict(args: argparse.Namespace) -> dict[str, str]:
    args = parse_args()

    with open(args.config, 'r') as f:
        config_dict = json.load(f)

    return config_dict

def build_tree(config_dict: dict[str, str]) -> BindNode:
    data = BindNodeData.from_config_dict(config_dict)
    root_node = BindNode(data)

    return root_node

if __name__ == "__main__":

    args = parse_args()
    config_dict = load_config_dict(args)

    root_node = build_tree(config_dict)

    print(root_node)

    # TODO: Speak to dmenu!
