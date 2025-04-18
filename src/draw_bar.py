from dataclasses import dataclass
from pathlib import Path

from PIL.Image import Image
from Xlib import display
from Xlib.X import Expose, ExposureMask, KeyPressMask

from itertools import accumulate, chain, cycle, repeat

from Xlib.protocol.rq import Event

from text_rendering import TextRendererConfig, TextRenderer

@dataclass
class XOrgConfig:
    bar_height: int
    border_size: int

class XOrgHandler():
    def __init__(self, config: XOrgConfig):
        self.__display = display.Display()
        self.__screen = self.__display.screen()
        self.__root_window = self.__screen.root

        self.__width_in_pixels = self.__screen.width_in_pixels
        self.__height_in_pixels = config.bar_height
        self.__border_size = config.border_size

        self.bar = self.__root_window.create_window(
                    x = 0,
                    y = 0,
                    width = self.__width_in_pixels,
                    height = self.__height_in_pixels,
                    depth = self.__screen.root_depth,
                    border_width = self.__border_size,
                    background_pixel = self.__screen.black_pixel, # TODO: Investigate how to pass this through config.
                    border_pixel = self.__screen.white_pixel, # TODO: Investigate how to pass this through config.
                    event_mask = (ExposureMask | KeyPressMask), # TODO: Investigate 
                    override_redirect = 1 # dgaf about the window manager
                )

        # Really don't care about this. It's necessary for the graphics context
        font = self.__display.open_font("fixed") 
        self.gc = self.bar.create_gc(font = font, foreground = self.__screen.white_pixel)

        self.bar.map()
    
    def get_dimensions_in_pixels(self) -> tuple[int, int]:
        """Returns (width, height)"""
        return self.__width_in_pixels, self.__height_in_pixels

    def next_event(self) -> Event:
        return self.__display.next_event()

    def flush(self):
        self.__display.flush()

@dataclass
class DrawingConfig:
    initial_padding_in_pixels: int
    padding_in_pixels: int
    skip_in_pixels: int

class DrawManager():
    def __init__(
            self,
            graphics_handler: XOrgHandler,
            separator_image: Image,
            key_images: list[Image],
            text_images: list[Image],
            config: DrawingConfig
            ):
        self.__bar = graphics_handler.bar
        self.__gc = graphics_handler.gc
        self.__max_width, self.__bar_height = graphics_handler.get_dimensions_in_pixels()
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
        self.__y_position = (self.__bar_height - self.__text_height) // 2

        if self.__y_position < 0:
            print("WARNING: Bar height is smaller than text height. Decrease font size or increase bar size.")

        if self.__max_width < self.__x_positions[-1] + self.__images[-1].size[0]:
            print("WARNING: Keybinds too long to fit on screen. Decrease font size or paddings. Or get a bigger screen, lol.")

    def draw(self):
        # TODO: Handle case where total len is more than screen width.
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
    xconfig = XOrgConfig(
            bar_height=20,
            border_size=0
            )


    drawconfig = DrawingConfig(
            initial_padding_in_pixels=10,
            padding_in_pixels=5,
            skip_in_pixels=10
            )

    font = "JetBrainsMonoNLNerdFont-Bold.ttf"
    # font = "UbuntuNerdFont-Regular.ttf"

    textconfig = TextRendererConfig(Path(f"/usr/share/fonts/TTF/{font}"), 14, "#000000", "#ffffff")
    renderer = TextRenderer(textconfig)

    keys=["w", "l", "s"]
    texts=["Write", "Launch", "System"]
    sep=":"

    key_images = [renderer.render(k) for k in keys]
    text_images = [renderer.render(f" {t}") for t in texts]
    separator = renderer.render(sep)

    graphics_handler = XOrgHandler(xconfig)
    draw_manager = DrawManager(
            graphics_handler,
            separator_image=separator,
            key_images=key_images,
            text_images=text_images,
            config=drawconfig
            )

    print(draw_manager.get_positions())

    while True:
        event = graphics_handler.next_event()

        if event.type == Expose:
            draw_manager.draw()

        graphics_handler.flush()
