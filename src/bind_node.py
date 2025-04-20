# This file is part of pybinds.
# 
# pybinds is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# 
# pybinds is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with pybinds. If not, see <https://www.gnu.org/licenses/>. 

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
    command: Optional[Command]
    children: list ["BindNodeData"]

class BindNode:
    def __init__(self, data: BindNodeData):
        self.__name: str = data.name
        self._key: Keybind = data.key

        self._parent: Optional[BindNode] = None

        self.__command: Optional[Command] = data.command

        children = list(
            map(
                lambda child_data: BindNode(child_data),
                data.children
            )
        )

        for child in children:
            child._parent = self

        self.__children_index: dict[Keybind, BindNode] = {
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
