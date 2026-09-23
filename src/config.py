import curses
CONFIG = {
    "additional_file_extensions" : [".mp3", ".mp4", ".opus", ".mkv", ".mkv"],
    "playpause_key" : ord(" "),
    "exit_key" : ord("q"),
    "next_key" : ord(">"),
    "previous_key" : ord("<"),
    "jump_backward_key" : curses.KEY_LEFT,
    "jump_forward_key" : curses.KEY_RIGHT,
    "volume_up_key" :  curses.KEY_UP,
    "volume_down_key":  curses.KEY_DOWN,
    "shuffle_key" : ord("s"),
    "jump_time_seconds" : 10.0
}
