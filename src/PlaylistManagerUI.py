from typing import override
from AppState import *
from UI import UI
import curses
from Playlist import Playlist
class PlaylistManagerUI(UI):
    def __init__(self, parrent_rows: int, parrent_cols: int, playlist: Playlist) -> None:
        super().__init__()
        self.window: curses.window = curses.newwin(parrent_rows, parrent_cols, 0,0) 
    def update_draw(self, playlist: Playlist, parrent_cols:int,parrent_rows: int, force_redraw: bool=False):
        if force_redraw and AppState().state.value == AppStates.playlistmanagerui.value:
            self.window.clear()
        self.draw(playlist, parrent_cols, parrent_rows)
    def draw( self, playlist: Playlist, parrent_cols: int, parrent_rows: int):
        if AppState().state.value != AppStates.playlistmanagerui.value:
            return

        self.window: curses.window = curses.newwin(parrent_rows, parrent_cols, 0,0) 
        page: int = playlist.index // parrent_rows
        for i in range(len(playlist.songs)):
            if i < parrent_rows:
                playlist_index = page*parrent_rows + i
                if playlist_index < len(playlist.songs):
                    self.window.addnstr(i, 0, playlist.songs[playlist_index].name, parrent_cols, curses.A_REVERSE if i == (playlist.index%parrent_rows) else curses.A_NORMAL)
        self.window.refresh()
    def clear(self):
        self.window.clear()
        self.window.refresh()

