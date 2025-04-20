# pybinds
## Author: Frank William Hammond Espinosa
Assign nested keybinds to your scripts!

pybinds is a small program heavily inspired by my good friend Gerard's [flybinds](https://git.ricebes.cat/flybinds/file/README.md.html).

I created this after having used and loved flybinds for a long time, until I switched computers and started getting seemingly random segfaults which I really didn't want to debug. Python doesn't have those, so yeah.

### Dependencies
A Python interpreter with the following libraries installed:

- python-xlib
- pillow (for rendering the text)

### Configuration
There are two configuration files for this program, examples for which have been provided in `config_example`. The values there are also the defaults.

Specify your general configuration in `config.json`, including the path of your bindings file (either relative to `config.json` or absolute). The commands to be executed, and their associated keybinds and configurations are to be included in the bindings file, which by default is called `bindings.json`.

### Usage
Just call the script `main.py` with a Python interpreter. Optionally, pass it a `-c` flag containing the path for your `config.json`; the default is `$XDG_CONFIG_HOME/pybinds/config.json`.

I suggest you set up a key to call pybinds, maybe in your window manager or using something like [sxhkd](https://github.com/baskerville/sxhkd). I do the latter.

## License
This program is licensed under the GNU General Public License, version 3.
