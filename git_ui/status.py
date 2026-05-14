
import os
from textual import events
from textual.screen import Screen
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import Header, Footer, Static
from rich.text import Text
from .git_runner import GitRunner
from .common import SELECTION_CHARS

class StatusScreen(Screen):
    """Main activity showing git status."""

    BINDINGS = [
        Binding("C", "commit", "Commit"),
        Binding("B", "branches", "Branches"),
        Binding("T", "stash", "Stash"),
        Binding("R", "refresh", "Refresh"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self, app):
        super().__init__()
        self.files_map: dict[str, tuple[str, str]] = {} # char -> (path, type)
        self.app = app

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Static("", id="upper-view", expand=True)
            yield Static("", id="status-list")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_status()

    def refresh_status(self) -> None:
        groups = GitRunner.get_status_groups()
        self.files_map = {}
        char_idx = 0

        # Upper view: Minimal info (Branch and CWD)
        branch = GitRunner.get_branch_name()
        cwd = os.getcwd()
        header_text = Text()
        header_text.append(f"Branch: ", style="bold cyan")
        header_text.append(f"{branch}\n")
        header_text.append(f"CWD:    ", style="bold cyan")
        header_text.append(f"{cwd}\n")

        self.query_one("#upper-view", Static).update(header_text)

        # Bottom view: Custom file listing for selection
        display_text = Text()

        def add_group(name: str, files: list[str], color: str):
            nonlocal char_idx
            if not files:
                return
            display_text.append(f"{name.upper()}:\n", style="bold underline")
            for f in files:
                if char_idx < len(SELECTION_CHARS):
                    char = SELECTION_CHARS[char_idx]
                    self.files_map[char] = (f, name)
                    display_text.append(f" {char} ", style="bold cyan")
                    display_text.append(f"{f}\n", style=color)
                    char_idx += 1

        add_group("untracked", groups["untracked"], "red")
        add_group("modified", groups["modified"], "red")
        add_group("added", groups["added"], "green")

        if not self.files_map:
            display_text = Text("Nothing to commit, working tree clean", style="italic")
        self.query_one("#status-list", Static).update(display_text)

    def action_commit(self):
        self.app.push_screen(
            self.app.commit_screen_mkr(self.app),
            callback=lambda _: self.refresh_status()
    )

    def action_switch(self):
        self.app.notify("Switch branch feature coming soon!")

    def action_branch(self):
        self.app.notify("Create branch feature coming soon!")

    def action_delete(self):
        self.app.notify("Delete branch feature coming soon!")

    def action_stash(self):
        self.app.notify("Stash feature coming soon!")

    def action_refresh(self):
        self.refresh_status()

    def on_key(self, event: events.Key) -> None:
        key = event.character or event.key
        if key in self.files_map:
            path, status_type = self.files_map[key]
            self.app.push_screen(
                self.app.file_action_screen_mkr(self.app, path, status_type),
                callback=lambda _: self.refresh_status()
            )
