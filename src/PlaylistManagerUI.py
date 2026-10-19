from typing import override
from AppState import *
from DrawBuffer import DrawBuffer
from UI import UI
import curses
from Playlist import Playlist
class PlaylistManagerUI(UI):
    def __init__(self, parrent_rows: int, parrent_cols: int, playlist: Playlist) -> None:
        super().__init__()
        self.window: curses.window = curses.newwin(parrent_rows, parrent_cols, 0,0) 
        self.fb = DrawBuffer(self.window)
        self.playlist = playlist
        self.parrent_cols = parrent_cols
        self.parrent_rows = parrent_rows

    def calculate_dimensions(self, parrent_rows: int, parrent_cols: int):
        self.parrent_cols = parrent_cols
        self.parrent_rows = parrent_rows
        self.window: curses.window = curses.newwin(parrent_rows, parrent_cols, 0,0) 
        self.fb = DrawBuffer(self.window)

    def update_draw(self, playlist: Playlist, parrent_cols:int,parrent_rows: int, force_redraw: bool=False):
        if force_redraw and AppState().state.value == AppStates.playlistmanagerui.value:
            ...
            #self.window.clear()
        self.draw(playlist, parrent_cols, parrent_rows)
    def draw( self, playlist: Playlist, parrent_cols: int, parrent_rows: int, lazy: bool = True):
        if AppState().state.value != AppStates.playlistmanagerui.value:
            return
        self.fb.clear()
        self.parrent_rows = parrent_rows
        self.parrent_cols = parrent_cols
        self.playlist = playlist
        page: int = playlist.index // parrent_rows
        for i in range(len(playlist.songs)):
            if i < parrent_rows:
                playlist_index = page*parrent_rows + i
                if playlist_index < len(playlist.songs):
                    self.fb.addnstryx( playlist.songs[playlist_index].name[0:parrent_cols], parrent_cols, i, 0,curses.A_REVERSE if i == (playlist.index%parrent_rows) else curses.A_NORMAL)
        self.fb.draw(lazy)
    def clear(self):
        self.fb.clear()
        self.fb.draw()

