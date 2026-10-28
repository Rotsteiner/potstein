from copy import deepcopy
import curses
from curses import window, wrapper
from dataclasses import dataclass, field
from shutil import move
import sys
import time
import traceback
from typing import override
import numba
import numpy as np

from Debug import Debug

CursesCharType = np.dtype([("char", np.uint32), ("attribute", np.uint32)]) # 8 bytes 
@dataclass(frozen=True)
class CursesChar:
    char: str 
    attribute: int = field(default=curses.A_NORMAL)

def new_fb_matrix(y: int,x: int):
    _fb = np.full((y,x), ord(" "), dtype=CursesCharType)
    _fb["attribute"] = curses.A_NORMAL
    return _fb


class CursesFB:
    def __init__(self, y: int, x: int) -> None:
        self._y: int = y 
        self._x: int = x
        self._fb = new_fb_matrix(y,x)
    def get_yx(self) -> tuple[int, int] :
        return (self._y, self._x)
    def get_at_yx(self, y: int, x: int) -> CursesChar:
        _fb = self.get_at_yx_CursesCharType(y,x)
        return CursesChar(chr(_fb[y,x]["char"].item()),_fb[y,x]["attribute"].item())

    def get_at_yx_CursesCharType(self, y: int, x: int) :
        if y >= self._y or x >= self._x:
            raise ValueError("not inside the buffer")
        return self._fb[y,x]

    def set_at_yx(self, y: int, x: int, c: CursesChar) -> None:
        if y >= self._y or x >= self._x:
            raise ValueError("not inside the buffer")
        self._fb[y, x]["char"] = ord(c.char)
        self._fb[y, x]["attribute"] = c.attribute
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
        try:
            for x1 in range(len(string)):
                self._newfb.set_at_yx(y, x + x1, CursesChar(string[x1], attribute))
            self._cursoryx = (y,x)
        except Exception as e:
            Debug().log(e)
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
        something_changed = False
        if not lazy:
            self._scr.clear()
            self._fb = CursesFB(*self._scr.getmaxyx())
        for y in range(self._fb.get_yx()[0]):
            for x in range(self._fb.get_yx()[1]):
                try:
                    new_char = self._newfb.get_at_yx_CursesCharType(y,x)
                    old_char = self._fb.get_at_yx_CursesCharType(y,x)
                except Exception as e:
                    Debug().log(e)
                    return
                if (old_char["char"] != new_char["char"] or old_char["attribute"] != new_char["attribute"]):
                    something_changed = True
                    # not the same -> actual scr needs updating
                    self._scr.move(y,x)
                    try:
                        self._scr.addch(chr(new_char["char"].item()), new_char["attribute"].item()) # override old one 
                    except curses.error as ce:
                        print(ce, file=sys.stderr)
                        Debug().log(ce)


        self._scr.move(*self._cursoryx)
        self._scr.refresh() # update screen 
        if something_changed or not lazy:
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

