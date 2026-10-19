from copy import deepcopy
import curses
from curses import window, wrapper
from dataclasses import dataclass, field
from shutil import move
import time
from typing import override
@dataclass(frozen=True)
class CursesChar:
    char: str 
    attribute: int = field(default=curses.A_NORMAL)

class CursesFB:
    def __init__(self, y: int, x: int) -> None:
        self._y: int = y 
        self._x: int = x
        self._fb: list[list[CursesChar]] = [ 
        [CursesChar(" ") for _ in range(x)] for _ in range(y)
        ]
    @override
    def __repr__(self) -> str:
        return "\n".join(["".join([c.char for c in row]) for row in self._fb])
    def get_yx(self) -> tuple[int, int] :
        return (self._y, self._x)
    def get_at_yx(self, y: int, x: int) -> CursesChar:
        if y > self._y or x > self._x:
            raise ValueError("not inside the buffer")
        return self._fb[y][x]
    def set_at_yx(self, y: int, x: int, c: CursesChar) -> None:
        if y > self._y or x > self._x:
            raise ValueError("not inside the buffer")
        self._fb[y][x] = c
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
        self._cursoryx: tuple[int, int] = (0,0)
    def addstryx(self, string: str, y: int, x: int, attribute: int = curses.A_NORMAL):
        for x1 in range(len(string)):
            self._newfb.set_at_yx(y, x + x1, CursesChar(string[x1], attribute))
        self._cursoryx = (y,x)
    def addnstryx(self, string: str,n:int, y: int, x: int, attribute: int = curses.A_NORMAL):
        if n > len(string):
            self.addstryx(string,y,x, attribute)
        else:
            self.addstryx(string[:n],y,x, attribute)
 
    def move(self, y: int,x: int):
        self._cursoryx = (y,x)
    def addstr(self, string: str, attribute: int = curses.A_NORMAL):
        self.addstryx(string, *self._cursoryx, attribute)
    def addnstr(self, string: str,n: int, attribute: int = curses.A_NORMAL):
        if n > len(string):
            self.addstr(string, attribute)
        else:
            self.addstr(string[:n], attribute)
    def getch(self)-> int:
        return self._scr.getch()
        


    def clear(self):
        self._newfb: CursesFB = CursesFB(*self._scr.getmaxyx()) # changes are first made to this and then checked against the old one
    def draw(self, lazy: bool = True):
        """
            will only update what has actually changed
            tries to fix flickering
        """
        if not lazy:
            self._scr.clear()
            self._fb = CursesFB(*self._scr.getmaxyx())
        for y in range(self._fb.get_yx()[0]):
            for x in range(self._fb.get_yx()[1]):
                if (self._fb.get_at_yx(y,x) != self._newfb.get_at_yx(y,x)):
                    # not the same -> actual scr needs updating
                    self._scr.move(y,x)
                    self._scr.addch(self._newfb.get_at_yx(y,x).char, self._newfb.get_at_yx(y,x).attribute) # override old one 



        self._scr.move(*self._cursoryx)
        self._scr.refresh() # update screen 
        self._fb = self._newfb.copy() # we have drawn the new one so we need to to reflect that in the tracking

                



def main(stdscr: window):
    db = DrawBuffer(stdscr)
    db1 = DrawBuffer(curses.newwin(4, 4, 4, 4))
    i = 0
    while True: #stdscr.getkey() != curses.KEY_BACKSPACE:
        db1.clear()
        db1.addnstryx(str(i), 1, 0 , 3, attribute=curses.A_REVERSE)
        db1.draw()
        i+=1
        time.sleep(1/30)
    
if __name__ == "__main__":
    wrapper(main)

