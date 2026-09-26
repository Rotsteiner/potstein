from typing import override

from UI import UI
import curses
from Playlist import Playlist
class PlaylistManagerUI(UI):
    def __init__(self, parrent_rows: int, parrent_cols: int, playlist: Playlist) -> None:
        super().__init__()
        self.window: curses.window = curses.newwin(parrent_rows, parrent_cols, 0,0) 
        self.playlist: Playlist = playlist
        if len(playlist.songs) > parrent_rows:
            raise ValueError
        self.parrent_cols: int = parrent_cols
    @override
    def update_draw(self, song_played_back, total_song_length, force_redraw=False):
        if force_redraw:
            self.window.clear()
        for i in range(len(self.playlist.songs)):
            self.window.addnstr(i, 0, self.playlist.songs[i].name, self.parrent_cols)
        self.window.refresh()
