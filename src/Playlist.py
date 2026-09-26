from dataclasses import dataclass, field
from functools import cached_property
import os 
import pprint
from typing import Callable
from Song_Cache import Song_Cache, STANDARD_FILE_EXTENSION
from config import CONFIG
from Common import shuffle, listdir_with_file_ending

@dataclass(frozen=True)
class Song:
    file_path: str
    custom_name: str | None = field(default=None)

    @cached_property
    def name(self):
        if self.custom_name:
            return self.custom_name
        else:
            return os.path.basename(self.file_path)

    @cached_property
    def realpath(self):
        return os.path.realpath(self.file_path)
        




@dataclass(frozen=True)
class Playlist_fetcher:
    songs_path: str
    music_extensions: list[str] = field(default_factory=lambda: CONFIG["additional_file_extensions"] + list(set([STANDARD_FILE_EXTENSION])))
    def song_list(self):
        # get realpath, get .opus as songs, create songlist
        real_songs_path: str = os.path.realpath(self.songs_path)
        song_name_list = listdir_with_file_ending(real_songs_path,
                                                  self.music_extensions)
        song_path_list = map(lambda song_name: os.path.join(real_songs_path, song_name),
                             song_name_list)

        get_song_from_song_path: Callable[[str], Song] = lambda song_path: \
            Song(Song_Cache().promise_to_add_song_path(song_path),os.path.basename(song_path))
            #Song(Song_Cache().add_song_path(song_path),os.path.basename(song_path))
        
        songs = list(map(get_song_from_song_path, song_path_list))


        Song_Cache().fulfill_promised_song_paths() # important because the files may not be converted already
        return songs

    def song_list_sorted(self):
        sort_by: Callable[[Song], str] = lambda song: song.name
        return sorted(self.song_list(), key=sort_by)

    def song_list_shuffled(self):
        return shuffle(self.song_list())

@dataclass(frozen=True)
class Playlist:
    songs: list[Song]
    _index: int = field(default=0)
    @cached_property
    def next(self) :
        return Playlist(self.songs, self._index + 1)
    @cached_property
    def previous(self):
        return Playlist(self.songs, self._index - 1)
    @cached_property
    def current(self):
        return self.songs[self._index%len(self.songs)]
    @property
    def index(self):
        return self._index%len(self.songs)

@dataclass(frozen=True)
class Playlist_Factory: 
    @staticmethod
    def New(path: str):
        playlist_fetcher = Playlist_fetcher(path)
        playlist = Playlist(playlist_fetcher.song_list())
        return playlist
    @staticmethod
    def New_Shuffled(path: str):
        playlist_fetcher = Playlist_fetcher(path)
        playlist = Playlist(playlist_fetcher.song_list_shuffled())
        return playlist
    @staticmethod
    def New_Sorted(path: str):
        playlist_fetcher = Playlist_fetcher(path)
        playlist = Playlist(playlist_fetcher.song_list_sorted())
        return playlist
    @staticmethod
    def New_Sorted_and_Custom_Reshuffled(path: str, swap_list: list[tuple[int, int]]):
        """
        lets say your path contains two songs at ".": 

        a.ogg 

        b.ogg 

        then
            Playlist_fetcher.New_Sorted_and_Custom_Reshuffled(".", [0,1]).songs 
        would have the songs in this order: [b.ogg, a.ogg]
        """
        playlist = Playlist_Factory.New_Sorted(path)
        songs = playlist.songs.copy()
        for swap in swap_list:
            i1, i2 = swap
            songs[i1], songs[i2] = songs[i2], songs[i1]

        return Playlist(songs)





if __name__ == "__main__":
    playlist1: Playlist = Playlist_Factory.New_Sorted("/home/user/Musik/Linkin Park/meteora/")
    playlist2: Playlist = Playlist_Factory.New_Sorted_and_Custom_Reshuffled("/home/user/Musik/Linkin Park/meteora/", [(0,1)])
    print(playlist1)
    print(playlist2)

