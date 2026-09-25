import curses
from typing import TypedDict
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
class Config(TypedDict):
    additional_file_extensions: list[str]
    keys: Keys
    jump_time_seconds: float
    dbus_integration: bool

CONFIG: Config = {
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
        "shuffle_key" : ord("s")
        },
    "jump_time_seconds" : 10.0,
    "dbus_integration": True
}
