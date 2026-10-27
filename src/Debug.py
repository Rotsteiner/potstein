import functools
from sys import stdout
from typing import Self, TextIO
from config import CONFIG
class Debug():
    instance: Self | None = None 
    def init(self, file: TextIO = stdout, enabled: bool = False) -> None:
        self.file = file
        self.enabled = enabled
    def __new__(cls, *args,**kwargs)-> Self:
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.init(*args,**kwargs)
        return cls.instance
    def set_file(self, file: TextIO):
        self.file = file
    def log(self, *args, **kwargs):
        if self.enabled:
            log_func = functools.partial(print, file=self.file)
            log_func(*args,**kwargs)

