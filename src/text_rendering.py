# This file is part of pybinds.
# 
# pybinds is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# 
# pybinds is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with pybinds. If not, see <https://www.gnu.org/licenses/>. 

from dataclasses import dataclass
from pathlib import Path

from PIL import ImageFont, Image, ImageDraw

Font = ImageFont.ImageFont | ImageFont.FreeTypeFont

@dataclass
class TextRendererConfig:
    font_path: Path
    font_size: int
    background_color: str
    foreground_color: str

class TextRenderer:
    def __init__(self, config: TextRendererConfig):
        self.__background_color = config.background_color
        self.__foreground_color = config.foreground_color
        self.__font = self.__get_font(config.font_path, config.font_size)
        self.__height_in_pixels = config.font_size

    def __get_font(self, font_path: Path, font_size: int) -> Font:
        match font_path.suffix:
            case ".ttf" | ".otf":
                return ImageFont.truetype(font_path, font_size)
            case _:
                return ImageFont.load(font_path.name)

    def render(self, text: str) -> Image.Image:
        width_in_pixels = round(self.__font.getlength(text))

        # Heuristic for aligning the text vertically
        dy = - self.__height_in_pixels // 8 

        canvas = Image.new(
                    mode="RGB",
                    size = (width_in_pixels, self.__height_in_pixels),
                    color = self.__background_color
                )

        draw = ImageDraw.Draw(canvas)


        draw.text((0, dy), text, font = self.__font, fill = self.__foreground_color)

        return canvas

if __name__ == "__main__":
    path = "/usr/share/fonts/TTF/UbuntuNerdFont-Regular.ttf"
    size = 18

    config = TextRendererConfig(Path(path), size, "#00ff00", "#ff0000")

    renderer = TextRenderer(config)

    hello = renderer.render("Hello")
    world = renderer.render("world")

    hello.save("/tmp/hello.png", "PNG")
    world.save("/tmp/world.png", "PNG")


