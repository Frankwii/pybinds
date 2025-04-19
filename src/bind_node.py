import shlex
import subprocess

from dataclasses import dataclass
from typing import Optional

from Xlib.XK import keysym_to_string, string_to_keysym

@dataclass()
class Command:
    def __init__(self, cmd: str, keep_running: bool = False):
        self.__command = self.__create_command(cmd)
        self.__keep_running = keep_running

    def __create_command(self, cmd: str) -> list[str]:
        return shlex.split(shlex.quote(cmd))

    def execute(self, shell: str):
        subprocess.Popen([shell, "-c"] + self.__command)
        
    def keep_running(self):
        return self.__keep_running

    def __repr__(self):
        return f"Command({self.__command})"


class Keybind:
    def __init__(self, key: str | int):
        """Key should be either a string or an XK_* keysym"""
        if isinstance(key, str):
            self.__string = key
            self.__keysym = string_to_keysym(key)
        elif isinstance(key, int):
            self.__string = str(keysym_to_string(key))
            self.__keysym = key
        else:
            raise TypeError(f"Unexpected type for `{key}` when instantiating a Keybind. Expected str or string, got {type(key)}.")

    def __hash__(self) -> int:
        return self.__keysym

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Keybind) and hash(self) == hash(other)

    def __str__(self) -> str:
        return self.__string

@dataclass()
class BindNodeData:
    name: str
    key: Keybind
    termination: Command | list ["BindNodeData"]

class BindNode:
    def __init__(self, data: BindNodeData):
        self.__name: str = data.name
        self._key: Keybind = data.key

        self._parent: Optional[BindNode] = None

        self.__children_index: dict[Keybind, BindNode] = {}
        self.__command: Optional[Command] = None

        if isinstance(data.termination, Command):
            self.__command = data.termination

        else:
            children = list(
                map(
                    lambda child_data: BindNode(child_data),
                    data.termination
                )
            )

            for child in children:
                child._parent = self

            self.__children_index = {
                child._key: child for child in children
            }

    def get_child(self, key: Keybind) -> Optional["BindNode"]:
        return self.__children_index.get(key)

    def get_parent(self) -> Optional["BindNode"]:
        return self._parent

    def __repr__(self):
        return f"BindNode(name={self.__name}, key={self._key}, children={repr(list(self.__children_index.values()))})"

    def __getitem__(self, char: str) -> "BindNode":
        key = Keybind(char)
        res = self.get_child(key)
        if res is None:
            expected_key_string = ", ".join(
                    map(
                        lambda k: str(k),
                        self.__children_index.keys()
                        )
                    )
            errstring = f"Invalid key!\nGot: {key}\nValid keys in this context: {expected_key_string}"

            raise KeyError(errstring)

        return res

    def get_all_children(self) -> list["BindNode"]:
        return list(self.__children_index.values())

    def get_key(self) -> Keybind:
        return self._key

    def get_name(self) -> str:
        return self.__name

    def get_command(self) -> Optional[Command]:
        return self.__command
