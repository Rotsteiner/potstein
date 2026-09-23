from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
from os import makedirs
from os.path import realpath
import hashlib
import os
import shutil
import ffmpeg
from typing import Callable, Self
import multiprocessing 
from config import CONFIG

STANDARD_FILE_EXTENSION: str = ".ogg"
is_standard_filetype: Callable[[str],bool] = lambda file_path: \
    realpath(file_path).endswith(STANDARD_FILE_EXTENSION)

def compute_file_hash(file_path, algorithm='sha256'):
    """Compute the hash of a file using the specified algorithm."""
    hash_func = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as file:
        # Read the file in chunks of 8192 bytes
        while chunk := file.read(8192):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()

class Song_Cache:
    instance: Self | None = None 
    def init(self, cache_directory_path: str = ".") -> None:
        self.cache_directory_path: str = realpath(cache_directory_path)
        self.songs: dict[str, str] = {}
        self.song_cache_sub_directory_name = "song_cache"
        self.promised_song_paths: list[tuple[str, str]] = []
    def __new__(cls, *args,**kwargs)-> Self:
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.init(*args,**kwargs)
        return cls.instance
    
    @staticmethod
    def convert(original_file_path: str, final_file_path: str):
        f = ffmpeg.input(realpath(original_file_path)).\
               output(realpath(final_file_path))
        print(f.compile())
        f.run()


    def promise_to_add_song_path(self, file_path: str) -> str:
        """
        promises to add a file to the song_cache and returns the location 
        of a different file which will have
        with the same audio data but with the standard codec 

        to fulfill the promise, self.fulfill_promised_song_paths() must be called
        """
        if self.songs.get(realpath(file_path)):
            return self.songs[realpath(file_path)]

        if is_standard_filetype(file_path):
            self.songs[realpath(file_path)] = realpath(file_path)
        else:
            cache_dir = os.path.join(self.cache_directory_path,
                                  self.song_cache_sub_directory_name)
            if not os.path.isdir(cache_dir): makedirs(cache_dir)
            file_hash = \
                compute_file_hash(realpath(file_path))
            cached_file_filename = file_hash +  STANDARD_FILE_EXTENSION

            cache_file_path: str = os.path.join(cache_dir, cached_file_filename)
            if os.path.isfile(cache_file_path):
                ...
            else:
                self.promised_song_paths.append((realpath(file_path), cache_file_path))
            self.songs[realpath(file_path)] =  cache_file_path
        return self.songs[realpath(file_path)]

    def fulfill_promised_song_paths(self)-> None:
        with ThreadPool(multiprocessing.cpu_count()) as p:
            list(p.imap_unordered(
                lambda x: self.convert(x[0],x[1])
                , self.promised_song_paths)
                 ) # list() forces it to not be lazy
            self.promised_song_paths = [] # nothing is promised anymore 

            
    def add_song_path(self, file_path: str) -> str:
        """
        adds a file to the song_cache and returns the location of a different file 
        with the same audio data but with the standard codec 
        """
        if self.songs.get(realpath(file_path)):
            return self.songs[realpath(file_path)]

        if is_standard_filetype(file_path):
            self.songs[realpath(file_path)] = realpath(file_path)
        else:
            cache_dir = os.path.join(self.cache_directory_path,
                                  self.song_cache_sub_directory_name)
            if not os.path.isdir(cache_dir): makedirs(cache_dir)
            file_hash = \
                compute_file_hash(realpath(file_path))
            cached_file_filename = file_hash +  STANDARD_FILE_EXTENSION

            cache_file_path: str = os.path.join(cache_dir, cached_file_filename)
            if os.path.isfile(cache_file_path):
                ...
            else:
                Song_Cache.convert(realpath(file_path), cache_file_path)
                
            self.songs[realpath(file_path)] =  cache_file_path
            
        return self.songs[realpath(file_path)]
