# This file is part of pybinds.
# 
# pybinds is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# 
# pybinds is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with pybinds. If not, see <https://www.gnu.org/licenses/>. 

from dataclasses import dataclass

from PIL.Image import Image
from Xlib import display
from Xlib.X import CurrentTime, ExposureMask, KeyPressMask, KeyReleaseMask, RevertToParent

from itertools import accumulate, chain, cycle, repeat

from Xlib.protocol.rq import Event

from bind_node import Keybind

@dataclass
class XOrgConfig:
    bar_height: int
    border_size: int
    background_color: tuple[int, int, int]
    border_color: tuple[int, int, int]


class XOrgHandler():
    def __init__(self, config: XOrgConfig):
        self.__display = display.Display()
        self.__screen = self.__display.screen()
        self.__root_window = self.__screen.root
        self.__width_in_pixels = self.__screen.width_in_pixels
        self.__height_in_pixels = config.bar_height
        self.__border_size = config.border_size

        self.__colormap = self.__screen.default_colormap
        
        background_color = self.__colormap.alloc_color(*config.background_color)
        border_color = self.__colormap.alloc_color(*config.border_color)

        self.bar = self.__root_window.create_window(
                    x = 0,
                    y = 0,
                    width = self.__width_in_pixels,
                    height = self.__height_in_pixels,
                    depth = self.__screen.root_depth,
                    border_width = 0,
                    background_pixel = background_color.pixel,
                    border_pixel = self.__screen.white_pixel,
                    event_mask = (ExposureMask | KeyPressMask | KeyReleaseMask),
                    override_redirect = 1 # dgaf about the window manager
                )

        if self.__border_size > 0:
            self.border = self.__root_window.create_window(
                    x = 0,
                    y = self.__height_in_pixels,
                    width = self.__width_in_pixels,
                    height = self.__border_size,
                    depth = self.__screen.root_depth,
                    border_width = 0,
                    background_pixel = border_color.pixel,
                    border_pixel = self.__screen.white_pixel,
                    event_mask = (ExposureMask),
                    override_redirect = 1 # dgaf about the window manager
            )

            self.border.map()

        # Really don't care about this. It's just necessary for the graphics context
        font = self.__display.open_font("fixed") 
        self.gc = self.bar.create_gc(font = font, foreground = self.__screen.white_pixel)

        self.bar.map()
        self.bar.set_input_focus(RevertToParent, CurrentTime)
    
    def get_dimensions_in_pixels(self) -> tuple[int, int]:
        """Returns (width, height)"""
        return self.__width_in_pixels, self.__height_in_pixels

    def next_event(self) -> Event:
        return self.__display.next_event()

    def flush(self):
        self.__display.flush()

    def keycode_to_keysym(self, keycode: int, is_shifted: bool) -> int:
        return self.__display.keycode_to_keysym(keycode, is_shifted)

    def keysym_to_keycode(self, keysym: int) -> int:
        return self.__display.keysym_to_keycode(keysym)

    def keysym_to_keybind(self, keysym: int) -> Keybind:
        return Keybind(self.__display.keysym_translations[keysym])

    def request_redraw(self):
        self.bar.clear_area(
            x = 0,
            y = 0,
            width = self.__width_in_pixels,
            height = self.__height_in_pixels
        )

@dataclass
class DrawingConfig:
    initial_padding_in_pixels: int
    padding_in_pixels: int
    skip_in_pixels: int

class DrawManager():
    def __init__(
            self,
            xorg_handler: XOrgHandler,
            separator_image: Image,
            key_images: list[Image],
            text_images: list[Image],
            config: DrawingConfig
            ):
        self.__bar = xorg_handler.bar
        self.__gc = xorg_handler.gc
        self.__max_width, self.__bar_height = xorg_handler.get_dimensions_in_pixels()
        self.__text_height = separator_image.size[1]

        seps = repeat(separator_image)

        images_tup = zip(key_images, seps, text_images)

        self.__images = list(chain.from_iterable(images_tup))
        widths = chain((0,), map(lambda img: img.size[0], self.__images[:-1]))
        extras = chain(
                (config.initial_padding_in_pixels,),
                cycle((config.padding_in_pixels, config.padding_in_pixels, config.skip_in_pixels))
                )

        total_widths = map(sum, zip(widths, extras))
        
        self.__x_positions = list(accumulate(total_widths))
        self.__y_position = (self.__bar_height - self.__text_height)

        if self.__y_position < 0:
            print("WARNING: Bar height is smaller than text height. Decrease font size or increase bar size.")

        if self.__max_width < self.__x_positions[-1] + self.__images[-1].size[0]:
            print("WARNING: Keybinds too long to fit on screen. Decrease font size or paddings. Or get a bigger screen, lol.")

    def draw(self):
        for i in range(len(self.__images)):
            self.__bar.put_pil_image(
                gc = self.__gc,
                x = self.__x_positions[i],
                y = self.__y_position,
                image = self.__images[i]
            )

    def get_positions(self):
        return list(zip(self.__x_positions, repeat(self.__y_position)))

if __name__ == "__main__":
    config = XOrgConfig(20, 1, (255*256, 0, 16*256), (0, 255*256, 0))


    handler = XOrgHandler(config)
