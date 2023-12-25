"""A terminal ui for git"""

import curses
import subprocess
from collections import defaultdict
from curses import wrapper
from subprocess import Popen
from typing import Dict, List, Tuple

BOTTOM_OPTS_Y = 40


class WindowPrinter:
    """Print succesively to window"""

    def __init__( self, win, start_y: int, x: int ):
        self.win = win
        self.y = start_y  # line offset
        self.x = x  # column offset

    def print(self, a_str: str, x_offset: int = 0, endl=True):
        """Print to the current position and advance the line offset"""
        lines = a_str.split("\n")

        for i, line in enumerate(lines):
            self.win.addstr( self.y, self.x + x_offset, line )
            newline = i < len(lines) - 1 or endl
            self.y += 1 if newline else 0


def ui(stdscr):

    # for i in range(11):
    #    stdscr.addstr(i, 0, f"{i}")
    # branches_win = curses.newwin( 10, 25, 0, 50 )

    app = App( stdscr )
    app.main_loop()



class App:
    """A terminal app"""

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.status_dict = {}

    def main_loop(self):
        activity = 'main_menu'

        while True:
            self.stdscr.clear()
            if activity == 'main_menu':
                activity = self.main_menu_activity( )
            elif activity == 'add':
                activity = self.add_activity()
            elif activity == 'commit':
                activity = self.commit_activity()
            elif activity == 'exit':
                break
            else:
                raise ValueError(f"activity='{activity}' not recognized")

    def main_menu_activity(self) -> str:
        """Show main menu"""
        self.refresh_branches_win()

        self.refresh_status_win()
        self.stdscr.addstr(BOTTOM_OPTS_Y, 0, '[a] add   [c] commit   [r] revert')

        c = self.stdscr.getch()
        if c == ord('q'):
            return "exit"
        elif c == ord('a'):
            return "add"
        elif c == ord('c'):
            return "commit"

    def refresh_branches_win( self ):
        """Refresh branches"""
        branches_printer = WindowPrinter(self.stdscr, start_y=0, x=50)

        out_lines, _ = run_command_get_output( 'git branch'.split() )

        for out_line in out_lines:
            branches_printer.print( out_line )

    def refresh_status_win( self ):
        """Issue git status command, parse output, print to view"""
        printer = WindowPrinter(self.stdscr, start_y=0, x=0)

        status_lines, _ = run_command_get_output( 'git status'.split() )

        self.status_dict = parse_status_output( status_lines )

        for key, vals in self.status_dict.items():
            printer.print( key  )
            for val in vals:
                printer.print( val, x_offset=4 )

            printer.print('')

    def add_activity(self):
        """Add a file to commit queue"""
        self.stdscr.clear()
        printer = WindowPrinter(self.stdscr, start_y=0, x=0)

        printer.print("To be added:\n")

        to_be_added = self.status_dict.get('to_be_added', [])

        for i, val in enumerate(to_be_added):
            printer.print(f"{i:3d} : {val}")

        printer.print("\nPress number to add file, [backspace] to go back")

        while True:
            c = self.stdscr.getch()
            if c == 127:
                return "main_menu"

            elif ord('0') <= c <= ord('9'):
                idx = c - ord('0')
                if idx < len(to_be_added):
                    outlines, _ = run_command_get_output( ['git', 'add', to_be_added[idx]] )

                    if len(outlines) == 0:
                        printer.print(f"added: {to_be_added[idx]}")
                    else:
                        printer.print(f"outlines has: {len(outlines)}")
            else:
                printer.print(str(c))

    def commit_activity(self) -> str:
        """Ask for a commit message and commit files in commit queue"""
        self.stdscr.clear()
        printer = WindowPrinter(self.stdscr, start_y=0, x=0)

        printer.print("To be committed:\n")

        to_be_committed = self.status_dict.get('to_be_committed', [])

        for val in to_be_committed:
            printer.print(val)

        printer.print("\nCommit message:", endl=False )

        curses.echo()
        # msg = input()
        msg = self.stdscr.getstr( printer.y + 1, printer.x, 20).decode('utf-8')
        self.stdscr.refresh()
        curses.noecho()
        printer.print(f"\nmsg: {msg}")
        out_lines, err_lines = run_command_get_output( ['git', 'commit', '-m', msg ])
        # outlines, err_lines = [], []

        printer.print('commit out:')
        for line in out_lines:
            printer.print( line, x_offset=4 )

        printer.print('\ncommit err:')
        for line in err_lines:
            printer.print(line, x_offset=4)

        printer.print("\nPress any key to continue")

        c = self.stdscr.getch()
        return 'main_menu'


def parse_status_output( status_lines: List[str]) -> Dict[str, List[str]]:
    """Parse output from git status"""
    ret = defaultdict( list)
    state = None
    for line in status_lines:
        line = line.strip()
        if line.startswith('Changes to be committed:'):
            state = 'to_be_committed'
        elif line.startswith('Changes not staged for commit:'):
            state = 'to_be_added'
        elif line.startswith('Untracked files'):
            state = 'untracked'
        elif line.startswith('new file:'):
            ret[state].append(line[len('New file:'):].strip())
        elif line.startswith('modified:'):
            ret[state].append(line[len('modified:'):].strip())
        elif line.startswith('On branch'):
            ret['branch'].append(line[len('On branch '):])
        elif line.startswith('Your branch is'):
            ret['branch_status'].append(line[len('Your branch is '):])
        elif line == '' or line.startswith('(use "git'):
            continue
        elif state == 'untracked':
            ret[state].append(line)
        else:
            raise ValueError(f"Unrecognized git status line: '{line}'")

    return ret


def run_command_get_output( cmd:  List[str] ) -> Tuple[List[str], List[str]]:
    """Run command in shell and get list of line from stdout and stderr"""
    popen = Popen( cmd, stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE, env={'LANG': 'en'})

    stdout, stderr = popen.communicate()

    return ( stdout.decode('utf-8').split('\n'),
             stderr.decode('utf-8').split('\n') )

try:
    wrapper(ui)
except Exception as exc:
    print( exc )
# %%
