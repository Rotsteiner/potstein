from enum import Enum
from typing import Self
class AppStates(Enum):
    SongOptions = 1
class AppState:
    instance: None | Self = None 
    def init(self, default_state: AppStates = AppStates.SongOptions) -> None:
        self.state = default_state
    def __new__(cls, *args,**kwargs)-> Self:
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.init()
        return cls.instance
