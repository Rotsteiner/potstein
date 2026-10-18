from copy import deepcopy
import curses
from curses import window, wrapper
import time
from typing import override
class CursesFB:
    def __init__(self, y: int, x: int) -> None:
        self._y: int = y 
        self._x: int = x
        self._fb: list[list[str]] = [ 
        [" " for _ in range(x)] for _ in range(y)
        ]
    @override
    def __repr__(self) -> str:
        return "\n".join(["".join(row) for row in self._fb])
    def get_yx(self) -> tuple[int, int] :
        return (self._y, self._x)
    def get_at_yx(self, y: int, x: int) -> str:
        if y > self._y or x > self._x:
            raise ValueError("not inside the buffer")
        return self._fb[y][x]
    def set_at_yx(self, y: int, x: int, c: str | int) -> None:
        if y > self._y or x > self._x:
            raise ValueError("not inside the buffer")
        if type(c) == str:
            self._fb[y][x] = c 
        if type(c) == int:
            self._fb[y][x] = chr(c)
    def copy(self):
        new_fb = CursesFB(self._y, self._x)
        new__fb = deepcopy(self._fb)
        new_fb._fb = new__fb 
        return new_fb

class DrawBuffer:
    def __init__(self, scr: window) -> None:
        self._scr: window = scr
        self._fb: CursesFB = CursesFB(*scr.getmaxyx())
        self._newfb: CursesFB = CursesFB(*scr.getmaxyx()) # changes are first made to this and then checked against the old one
    def addstryx(self, string: str, y: int, x: int):
        for x1 in range(len(string)):
            self._newfb.set_at_yx(y, x + x1, string[x1])
    def clear(self):
        self._newfb: CursesFB = CursesFB(*self._scr.getmaxyx()) # changes are first made to this and then checked against the old one
    def draw(self):
        """
            will only update what has actually changed
            tries to fix flickering
        """
        for y in range(self._fb.get_yx()[0]):
            for x in range(self._fb.get_yx()[1]):
                if self._fb.get_at_yx(y,x) != self._newfb.get_at_yx(y,x):
                    # not the same -> actual scr needs updating
                    self._scr.move(y,x)
                    self._scr.addch(self._newfb.get_at_yx(y,x)) # override old one 
        self._scr.refresh() # update screen 
        self._fb = self._newfb.copy() # we have drawn the new one so we need to to reflect that in the tracking

                



def main(stdscr: window):
    db = DrawBuffer(stdscr)
    i = 0
    while True: #stdscr.getkey() != curses.KEY_BACKSPACE:
        db.clear()
        db.addstryx(str(i), i % 10 , 0 + i % 50)
        db.draw()
        i+=1
        time.sleep(1/30)
    
if __name__ == "__main__":
    wrapper(main)

