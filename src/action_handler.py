from dataclasses import dataclass
import subprocess

from Xlib.X import Expose, KeyPress, KeyRelease

from Xlib.XK import XK_Shift_L, XK_Shift_R

from bind_node import BindNode, Command, Keybind
from text_rendering import TextRenderer
from draw_bar import DrawManager, DrawingConfig, XOrgHandler

@dataclass
class VisualsHandlerConfig:
    separator: str
    drawing_config: DrawingConfig

class VisualsHandler:
    def __init__(
            self,
            root: BindNode,
            config: VisualsHandlerConfig,
            renderers: dict[str, TextRenderer],
            xorg_handler: XOrgHandler
        ):
        self.__xorg_handler = xorg_handler
        self.__separator = config.separator
        self.__renderers = renderers
        self.__drawing_config = config.drawing_config

        self.__drawer: DrawManager

        self.update_node(root)

    def update_node(self, node: BindNode) -> None:
        """
        Render texts and update drawer.
        """
        separator_image = self.__renderers["separator"].render(self.__separator)

        children = node.get_all_children()

        key_images = [self.__renderers["keys"].render(str(child.get_key())) for child in children]
        text_images = [self.__renderers["texts"].render(str(child.get_name())) for child in children]

        self.__drawer = DrawManager(
            xorg_handler=self.__xorg_handler,
            separator_image = separator_image,
            key_images = key_images,
            text_images = text_images,
            config = self.__drawing_config
        )

    def draw(self):
        self.__drawer.draw()

@dataclass
class KeyHandlerConfig:
    back_keys: list[Keybind]
    exit_keys: list[Keybind]


class ExitProgram:
    pass

Action = BindNode | Command | ExitProgram

class KeyHandler:
    def __init__(self, root: BindNode, xorg_handler: XOrgHandler, config: KeyHandlerConfig) -> None:
        self.__current_node : BindNode
        self.__children_hashmap: dict[int, BindNode]

        self.__is_shifted = False

        self.__xorg_handler = xorg_handler

        self.__shift_keycodes = {
            self.__keysym_to_keycode(XK_Shift_L), self.__keysym_to_keycode(XK_Shift_R)
        }

        # Sets for faster lookup
        self.__back_keys = set(map(hash, config.back_keys))
        self.__exit_keys = set(map(hash, config.exit_keys))
        self.update_node(root)

    def __keycode_to_keysym(self, keycode: int) -> int:
        return self.__xorg_handler.keycode_to_keysym(keycode, is_shifted=self.__is_shifted)

    def __keysym_to_keycode(self, keysym: int) -> int:
        return self.__xorg_handler.keysym_to_keycode(keysym)

    def resolve_keypress(self, keycode: int) -> Action:
        keysym = self.__keycode_to_keysym(keycode)

        if keysym in self.__back_keys:
            parent = self.__current_node.get_parent()
            return self.__current_node if parent is None else parent

        elif keysym in self.__exit_keys:
            return ExitProgram()

        elif (child := self.__children_hashmap.get(keysym)) is not None:
            command = child.get_command()
            return command if command is not None else child

        else:
            if keycode in self.__shift_keycodes:
                self.__is_shifted = True

            return self.__current_node

    def resolve_keyrelease(self, keycode: int):
        if keycode in self.__shift_keycodes:
            self.__is_shifted = False

    def update_node(self, node: BindNode) -> None:
        self.__current_node = node
        self.__children_hashmap = {hash(child.get_key()):child for child in node.get_all_children()}

@dataclass
class ActionHandlerConfig:
    visuals_config: VisualsHandlerConfig
    key_config: KeyHandlerConfig
    shell: str

class ActionHandler:
    def __init__(
            self,
            root: BindNode,
            renderers: dict[str, TextRenderer],
            xorg_handler: XOrgHandler,
            config: ActionHandlerConfig,
        ) -> None:

        self.__current_node = root
        self.__xorg_handler = xorg_handler

        self.__visuals_handler = VisualsHandler(
            root = self.__current_node,
            renderers = renderers,
            xorg_handler = xorg_handler,
            config = config.visuals_config
        )

        self.__key_handler = KeyHandler(root=root, xorg_handler=xorg_handler, config=config.key_config)

        self.__shell = config.shell

    def __execute(self, cmd: Command):
        cmd.execute(shell = self.__shell)

    def __navigate(self, node: BindNode):
        if node is not self.__current_node:
            self.__visuals_handler.update_node(node)
            self.__key_handler.update_node(node)

            self.__xorg_handler.request_redraw()

            self.__visuals_handler.draw()
            
            self.__current_node = node

    def __handle_expose_event(self):
        self.__visuals_handler.draw()

    def __handle_keypress_event(self, keycode: int):
        """Returns whether to exit the program"""
        action = self.__key_handler.resolve_keypress(keycode)

        if isinstance(action, BindNode):
            self.__navigate(action)
            return False
        elif isinstance(action, Command):
            self.__execute(action)
            return not action.keep_running()
        elif isinstance(action, ExitProgram):
            return True
        else:
            return False

    def __handle_keyrelease_event(self, keycode: int):
        self.__key_handler.resolve_keyrelease(keycode)


    def loop(self):
        while True:
            event = self.__xorg_handler.next_event()

            event_type = event.type
            if event_type == Expose:
                self.__handle_expose_event()

            elif event_type == KeyPress:
                self.__notify(str(event.detail))
                exit_program = self.__handle_keypress_event(event.detail)
                if exit_program:
                    break
            elif event_type == KeyRelease:
                self.__handle_keyrelease_event(event.detail)

    def __notify(self, message: str):
        # Just for debugging
        subprocess.run(["notify-send", message])

