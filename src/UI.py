from abc import abstractmethod


class UI:
    @abstractmethod
    def update_draw(self, song_played_back, total_song_length, force_redraw=False):
        raise NotImplemented

