import curses
import time
from curses.textpad import rectangle
from SongOptions import *
import pygame
import sys
import os
from Song_Cache import Song_Cache
Song_Cache(".")
import Playlist
from config import CONFIG
not_bellow_zero = lambda x: x if x >= 0 else 0
class Player:
    def __init__(self) -> None:
        pygame.mixer.init()
        self.songoptions_width = 19
        self.songoptions_height = 10
        self.running = True
        self.song_is_paused = False
        self.playlist_path = sys.argv[1]
        self.playlist: Playlist.Playlist = \
            Playlist.Playlist_Factory.New_Sorted(self.playlist_path)
        self.volume = 1
        self.init_pygame_song()

        from dbus_mpris import mpris_dbus_start
        mpris_dbus_start(self)
    def set_volume(self, value):
        if value < 0:
            raise ValueError("Volume cannot be less than zero")
        if value > 1:
            raise ValueError("Volume cannot be more than one (100%)")
        self.volume = value
        pygame.mixer.music.set_volume(self.volume)

    def increment_volume(self, step):
        new_volume = not_bellow_zero(self.volume + step)
        if new_volume > 1:
            new_volume = 1 
        self.set_volume(new_volume)

    def decrement_volume(self, step):
        self.increment_volume(-step)
        
    def init_curses(self):
        curses.noecho()
        curses.curs_set(False)
    def init_pygame_song(self):
        pygame.mixer.music.load(self.playlist.current.file_path) 
        pygame.mixer.music.set_volume(self.volume)
        self.song_seconds = 0
        self.song_length  = pygame.mixer.Sound(self.playlist.current.file_path).get_length()
        pygame.mixer.music.play()
        if self.song_is_paused:
            pygame.mixer.music.pause()
    def init_songoptions(self,):
        self.songoptions = SongOptions(self.playlist.current.name
                                       ,self.song_is_paused, not self.song_is_paused,self.songoptions_width,self.songoptions_height,curses.LINES, curses.COLS)
    def init_scr_context(self, stdscr: curses.window):
        self.init_curses()
        stdscr.nodelay(True)
        stdscr.keypad(True)

        self.lines, self.cols = stdscr.getyx()
        self.init_songoptions()
        self.render(stdscr, )

    def load_playlist(self, playlist: Playlist.Playlist):
        self.playlist = playlist
        self.start_song()

    def shuffled_playlist(self):
        self.load_playlist(Playlist.Playlist_Factory.New_Shuffled(self.playlist_path))

    def render(self, stdscr:curses.window, ):
        self.update(stdscr)
        #stdscr.clear()
        while self.running:
            self.songoptions.calculate_dimensions(self.songoptions_width, self.songoptions_height, *(stdscr.getmaxyx()))
            self.songoptions.update_draw(self.song_seconds, self.song_length)
            self.update(stdscr)
    def play(self):
        self.songoptions.resume()
        self.song_is_paused = False 
        pygame.mixer.music.unpause()
    def stop(self):
        self.songoptions.pause()
        self.song_is_paused = True 
        pygame.mixer.music.pause()
    def playpause(self):
        if self.song_is_paused:
            self.play()
        else: 
            self.stop()


    def update(self, stdscr: curses.window):
        delta_time: float = 0
        start_time: float = time.time()

        self.lines, self.cols = stdscr.getyx()
        #stdscr.refresh()
        if not self.song_is_paused:
            if not (self.song_seconds >= self.song_length):
                self.song_seconds += not_bellow_zero(1/30 - delta_time)
            else:
                self.start_next_song()

        key = stdscr.getch()
        if key == CONFIG["playpause_key"]:
            self.playpause()
        if key == CONFIG["exit_key"]:
            sys.exit(0)
        if key == CONFIG["next_key"]:
            self.start_next_song()
        if key == CONFIG["previous_key"]:
            self.start_previous_song()

        jump_time_seconds = float(CONFIG["jump_time_seconds"])
        if key == CONFIG["jump_backward_key"]:
            pygame.mixer.music.set_pos(
                    not_bellow_zero(self.song_seconds-jump_time_seconds)
                    )
            self.song_seconds = not_bellow_zero(self.song_seconds-jump_time_seconds)
        if key == CONFIG["jump_forward_key"]:
            pygame.mixer.music.set_pos(
                    not_bellow_zero(self.song_seconds+jump_time_seconds)
                    )
            self.song_seconds += jump_time_seconds
        if key == CONFIG["volume_up_key"]:
            self.increment_volume(0.05)
        if key == CONFIG["volume_down_key"]:
            self.decrement_volume(0.05)

        if key == CONFIG["shuffle_key"]:
            self.shuffled_playlist()



        delta_time: float = time.time() - start_time

        time.sleep(not_bellow_zero(1/30 - delta_time))

    def start_song(self):
        self.init_songoptions()
        self.init_pygame_song()
        self.songoptions.update_draw(self.song_seconds,
                                     self.song_length,force_redraw=True)
        self.songoptions.forced_redraw()

    def start_next_song(self):
        self.playlist = self.playlist.next
        self.start_song()
    def start_previous_song(self):
        self.playlist = self.playlist.previous
        self.start_song()

    def run(self):
        render_func = self.init_scr_context
        curses.wrapper(render_func)
  
def main():
    p = Player()
    p.run()
if __name__ == "__main__":
    main()
