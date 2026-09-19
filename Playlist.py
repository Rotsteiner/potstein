from dataclasses import dataclass, field
from functools import cached_property
import os 
from typing import Any, List, Callable, Set
import random
from Song_Cache import Song_Cache
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
        


listdir_with_file_ending: Callable[[str, List[str]], List[str]] = \
        lambda path, allowed_endings: list(filter(
                lambda item: any([item.endswith(ending) for ending in allowed_endings]), 
                os.listdir(path)
                ))

def shuffle(sequence: list[Any]) :
    new_list= [i for i in range(len(sequence))]
    random.shuffle(new_list)
    for Index, item in enumerate(new_list):
        new_list[Index] = sequence[item]

    return new_list




@dataclass(frozen=True)
class Playlist_fetcher:
    songs_path: str
    music_extensions: list[str] = field(default_factory=lambda: [".ogg", ".mp3", ".mp4", ".opus"])

    def song_list(self):
        # get realpath, get .opus as songs, create songlist
        real_songs_path: str = os.path.realpath(self.songs_path)
        song_name_list = listdir_with_file_ending(real_songs_path,
                                                  self.music_extensions)
        song_path_list = map(lambda song_name: os.path.join(real_songs_path, song_name),
                             song_name_list)
        songs = [Song(Song_Cache().add_song_path(song_path),os.path.basename(song_path)) for song_path in song_path_list]
        return songs

    def song_list_sorted(self):
        sort_by = lambda song: song.name
        return sorted(self.song_list(), key=sort_by)

    def song_list_shuffled(self):
        return shuffle(self.song_list())

@dataclass(frozen=True)
class Playlist:
    index: int 
    songs: list[Song]
    @cached_property
    def next(self):
        return Playlist(self.index+1, self.songs)
    @cached_property
    def previous(self):
        return Playlist(self.index-1, self.songs)
    @cached_property
    def current(self):
        return self.songs[self.index%len(self.songs)]

@dataclass(frozen=True)
class Playlist_Factory: 
    @staticmethod
    def New(path: str):
        playlist_fetcher = Playlist_fetcher(path)
        playlist = Playlist(0,playlist_fetcher.song_list())
        return playlist
    @staticmethod
    def New_Shuffled(path: str):
        playlist_fetcher = Playlist_fetcher(path)
        playlist = Playlist(0,playlist_fetcher.song_list_shuffled())
        return playlist
    @staticmethod
    def New_Sorted(path: str):
        playlist_fetcher = Playlist_fetcher(path)
        playlist = Playlist(0,playlist_fetcher.song_list_sorted())
        return playlist



if __name__ == "__main__":
    playlist: Playlist = Playlist_Factory.New_Shuffled("/home/user/Musik/Linkin Park/meteora/")
    print(playlist)
    print(playlist.next)
    print(playlist.next.previous)
    print("\n".join(
        [str(s) for s in playlist.songs]))
