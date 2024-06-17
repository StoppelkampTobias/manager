import curses
from source.ui import UI

def main(stdscr):
    ui = UI(stdscr)
    ui.start()

if __name__ == "__main__":
    curses.wrapper(main)
