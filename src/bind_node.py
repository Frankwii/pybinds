from typing import Optional
from parse_config import BindNodeData, Command, Keybind

class BindNode:
    def __init__(self, data: BindNodeData):
        self.__name: str = data.name
        self._key: Keybind = data.key

        self._parent: Optional[BindNode]

        self.__children_index: dict[Keybind, BindNode] = {}
        self.__command: Optional[Command]

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


    def execute(self):
        if self.__command:
            self.__command.execute()

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
                        lambda k: k.key,
                        self.__children_index.keys()
                        )
                    )
            errstring = f"Invalid key!\nGot: {key.key}\nValid keys in this context: {expected_key_string}"

            raise KeyError(errstring)

        return res
