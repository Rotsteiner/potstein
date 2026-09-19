import curses
def format_seconds(seconds):
    minutes,seconds = divmod(seconds, 60)
    return f"{minutes}:{seconds:02}"

def mk_playback_string(song_played_back, total_song_length, playback_length):
    return f"{format_seconds(int(song_played_back))}/{format_seconds(int(total_song_length))}"[0:playback_length]

class SongOptions:
    def __init__(self, currently_playing:str, is_paused:bool, is_namescrolling:bool,
                 width: int, height: int, parrent_rows: int, parrent_cols: int) -> None:
        self.window = curses.newwin(height, width, int(parrent_rows / 2 - (height / 2)),int(parrent_cols / 2 - (width /  2))) 
        self.playback_y = height // 2
        self.playback_string = ""
        self.playback_length = width
        self.song_name_y = self.playback_y - 1
        self.song_name_length = width
        self.song_name_x = width // 2 - self.song_name_length // 2

        self.control_field_y = height - self.playback_y + 1
        self.control_field_x = self.song_name_x 
        self.control_field_length = width
        self.stop_button_x = self.control_field_length / 2

        self.current_song_name_index = self.song_name_length
        self.is_namescrolling = is_namescrolling

        self.currently_playing = " "*self.song_name_length+ currently_playing 

        self.current_song_slice = self.currently_playing[0+self.current_song_name_index:self.song_name_length+self.current_song_name_index]
        self.is_paused = is_paused
        self.draw()
    def update_draw(self, song_played_back, total_song_length, force_redraw=False):
        self.playback_string = f"{format_seconds(int(song_played_back))}/{format_seconds(int(total_song_length))}"[0:self.playback_length]
        self.current_song_slice = self.currently_playing[0+int(self.current_song_name_index):self.song_name_length+int(self.current_song_name_index)]
        if self.is_namescrolling or force_redraw:
            self.window.clear()
            self.draw()
            self.window.refresh()
            self.current_song_name_index += 0.05 * int(self.is_namescrolling)
            if self.current_song_name_index > len(self.currently_playing):
                self.current_song_name_index = 0

    def draw(self):
        self.window.addnstr(self.song_name_y, self.song_name_x, self.current_song_slice,self.song_name_length)
        # currently playing

        self.window.addstr(self.playback_y, self.playback_length // 2 - len(self.playback_string) // 2,
                            self.playback_string,)

        self.window.addstr(self.control_field_y, 0, "<")
        self.window.addstr(self.control_field_y,
                           self.control_field_length-1, ">")
        pause_icon =  ""
        resume_icon = "󰐊"
        self.window.addstr(self.control_field_y, int(self.stop_button_x), resume_icon if self.is_paused else pause_icon if not self.is_paused else "--")
        # centered
    def forced_redraw(self):
        self.window.clear()
        self.draw()
        self.window.refresh()
    def pause(self):
        self.is_paused = True 
        self.is_namescrolling = False 
        self.forced_redraw()


    def resume(self):
        self.is_paused = False 
        self.is_namescrolling = True 
        self.forced_redraw()



