import shlex
import subprocess

from dataclasses import dataclass

@dataclass()
class Command:
    def __init__(self, cmd: str):
        self.__command = self.create_command(cmd)

    def create_command(self, cmd: str) -> list[str]:
        return shlex.split(shlex.quote(cmd))

    def execute(self):
        # TODO: Let user choose shell in config file
        subprocess.Popen(["/bin/sh", "-c"] + self.__command)

    def __repr__(self):
        return f"Command({self.__command})"

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

if __name__ == "__main__":
    cmd="sleep 3; notify-send \"hi\""

    comm = Command(cmd)
    comm.execute()
