from __future__ import annotations

import os
import sys
from typing import Self, Callable
from textual.app import App

from .status import StatusScreen
from .commit import CommitScreen
from .branches import BranchScreen
from .common import find_git_root
from .file_action import FileActionScreen


class QitApp(App):
    """A simple Git TUI."""

    CSS = """
    Screen {
        layout: vertical;
    }

    #upper-view, #branch-info {
        height: 25%;
        border-bottom: solid $accent;
        overflow-y: scroll;
        background: $boost;
        padding: 1;
    }

    #status-list, #branch-list {
        height: 75%;
        overflow-y: scroll;
        padding: 1;
    }

    #file-header {
        height: 3;
        padding: 1;
        background: $primary;
        color: $text;
    }

    #diff-scroll {
        height: 70%;
        border: tall $accent;
        padding: 1;
        background: $boost;
    }

    #diff-view {
        height: auto;
    }

    #options-footer {
        height: 3;
        padding: 1;
        content-align: center middle;
        background: $surface;
    }

    #commit-container {
        padding: 2;
        border: thick $accent;
        width: 60%;
        height: auto;
        align: center middle;
        background: $surface;
    }
    """

    def __init__(self):
        super().__init__()
        self.status_screen_mkr: Callable[[Self], StatusScreen] = StatusScreen
        self.branch_screen_mkr: Callable[[Self], BranchScreen] = BranchScreen
        self.commit_screen_mkr: Callable[[Self], CommitScreen] = CommitScreen
        self.file_action_screen_mkr: Callable[[Self, str, str], FileActionScreen] = FileActionScreen

    def on_mount(self) -> None:
        self.push_screen(self.status_screen_mkr(self))

if __name__ == "__main__":
    git_root = find_git_root()
    if not git_root:
        print("\nERROR: Not a git repository (or any of the parent directories): .git not found")
        sys.exit(1)

    os.chdir(git_root)

    try:
        app = QitApp()
        app.run()
    except Exception as e:
        print(f"\nAPPLICATION CRASHED: {e}")
        print(f"Current Working Directory: {os.getcwd()}")
        sys.exit(1)
