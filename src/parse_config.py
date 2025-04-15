import shlex
import subprocess

from dataclasses import dataclass

@dataclass()
class Command:
    def __init__(self, cmd: str):
        self.__commands = self.create_commands(cmd)

    def create_commands(self, cmd: str) -> list[list[str]]:
        return list(
            map(
                lambda subcommand: shlex.split(subcommand.strip()),
                cmd.split(";")
            )
        )

    def execute(self):
        for command in self.__commands:
            subprocess.Popen(command)

    def __repr__(self):
        return f"Command({self.__commands})"

@dataclass()
class Keybind:
    key: str

    def __hash__(self) -> int:
        return hash(self.key)

@dataclass()
class BindNodeData:
    name: str
    key: Keybind
    termination: Command | list ["BindNodeData"]

    @staticmethod
    def from_config_dict(config_dict: dict[str, str]) -> "BindNodeData":
        if isinstance(config_dict["termination"], str):
            return BindNodeData(
                    name=config_dict["name"],
                    key=Keybind(config_dict["key"]),
                    termination=Command(config_dict["termination"])
                    )
        else:
            return BindNodeData(
                    name=config_dict["name"],
                    key=Keybind(config_dict["key"]),
                    termination=list(
                            map(
                                lambda d: BindNodeData.from_config_dict(d),
                                config_dict["termination"]
                            )
                        )
                    )
