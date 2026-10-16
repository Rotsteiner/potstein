import curses
import os
import sys
from typing import TypedDict
from cli import COMMAND_LINE_ARGS
class Keys(TypedDict):
    playpause_key: int
    exit_key: int 
    next_key: int
    previous_key: int
    jump_backward_key: int
    jump_forward_key: int
    volume_up_key: int
    volume_down_key: int
    shuffle_key: int 
    playlistmanageruiswitch_key: int
class Config(TypedDict):
    additional_file_extensions: list[str]
    keys: Keys
    jump_time_seconds: float
    dbus_integration: bool

default_config: Config = {
        "additional_file_extensions" : [".mp3", ".opus"],
        "keys": {
            "playpause_key" : ord(" "),
            "exit_key" : ord("q"),
            "next_key" : ord(">"),
            "previous_key" : ord("<"),
            "jump_backward_key" : curses.KEY_LEFT,
            "jump_forward_key" : curses.KEY_RIGHT,
            "volume_up_key" :  curses.KEY_UP,
            "volume_down_key":  curses.KEY_DOWN,
            "shuffle_key" : ord("s"),
            "playlistmanageruiswitch_key": ord("p")
            },
        "jump_time_seconds" : 10.0,
        "dbus_integration": True
    }

def apply_overrides(default, overrides):
    for key in overrides.keys():
        if key in default:
            if isinstance(default[key], dict):
                apply_overrides(default[key], overrides[key])
            else:
                default[key] = overrides[key]
def new_config(default: Config, overrides) -> Config:
    """
    Overrides to the orignal config, example:
    {
        "keys": {
            "exit_key" : ord("x"),
            },
    }
    this will change the exit key to x.
    You can directly override anything that is not a dictionary but 
    if you want to completly override a dictionary you will need to override 
    the value of each key.
    """
    old_config = default.copy()
    try:
        apply_overrides(old_config, overrides)
    except:
        print("Could not load user config, perhaps your dictionary is in the wrong or outdated format ?", file=sys.stderr)
        sys.exit(1)
    return old_config


if COMMAND_LINE_ARGS.config is None:
    # default config
    CONFIG: Config = default_config
else:
    with open(os.path.realpath(COMMAND_LINE_ARGS.config), "r") as config_file:
        user_config = eval(config_file.read())
        # just overrides to the original 
        CONFIG: Config = new_config(default_config, user_config)
