from __future__ import annotations

import subprocess
import os
import sys
from typing import List, Dict, Optional, Tuple

from textual import on, events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Label, Input
from rich.text import Text

# Selection mapping: 1-9, then a-z
SELECTION_CHARS = "123456789abcdefghijklmnopqrstuvwxyz"

def find_git_root() -> Optional[str]:
    """Traverse upwards to find the .git directory."""
    curr = os.getcwd()
    while True:
        if os.path.isdir(os.path.join(curr, ".git")):
            return curr
        parent = os.path.dirname(curr)
        if parent == curr:  # Reached root
            return None
        curr = parent

class GitRunner:
    @staticmethod
    def run(args: List[str]) -> Tuple[int, str, str]:
        process = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr

    @staticmethod
    def get_status_groups() -> Dict[str, List[str]]:
        # Using core.quotepath=false to get clean paths (no quotes for spaces)
        _, stdout, _ = GitRunner.run(["git", "-c", "core.quotepath=false", "status", "--porcelain"])

        groups = {"untracked": [], "modified": [], "added": []}
        for line in stdout.splitlines():
            if not line:
                continue
            status = line[:2]
            path = line[3:].strip()

            if status == "??":
                groups["untracked"].append(path)
            elif status[0] in "MADR" and status[1] == " ":
                groups["added"].append(path)
            elif status[1] in "MA" or status[0] == " ":
                groups["modified"].append(path)

        return groups

    @staticmethod
    def get_branch_name() -> str:
        _, stdout, _ = GitRunner.run(["git", "branch", "--show-current"])
        return stdout.strip() or "Detached HEAD"

    @staticmethod
    def get_diff(path: Optional[str] = None, cached: bool = False) -> str:
        cmd = ["git", "diff", "--color=always"]
        if cached:
            cmd.append("--cached")
        if path:
            cmd.append(path)
        _, stdout, _ = GitRunner.run(cmd)
        return stdout

    @staticmethod
    def get_blame(path: str) -> str:
        _, stdout, _ = GitRunner.run(["git", "blame", "--color=always", path])
        return stdout

class CommitScreen(Screen):
    """Screen for entering a commit message."""
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Enter commit message:"),
            Input(placeholder="Type message and press Enter...", id="commit-msg"),
            Label("Press Esc to cancel"),
            id="commit-container"
        )

    @on(Input.Submitted, "#commit-msg")
    def on_submit(self, event: Input.Submitted) -> None:
        msg = event.value.strip()
        if msg:
            ret, _, stderr = GitRunner.run(["git", "commit", "-m", msg])
            if ret == 0:
                self.app.notify(f"Committed: {msg}")
                self.dismiss(True)
            else:
                self.app.notify(f"Git Error: {stderr}", severity="error", timeout=5)
        else:
            self.app.notify("Commit message cannot be empty", severity="error")

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.dismiss(False)

class FileActionScreen(Screen):
    """Screen for acting on a specific file."""

    def __init__(self, file_path: str, status_type: str):
        super().__init__()
        self.file_path = file_path
        self.status_type = status_type

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Static(f"File: [bold yellow]{self.file_path}[/]", id="file-header")
            yield Static("", id="diff-view", expand=True)
            yield Label(self.get_options_text(), id="options-footer")
        yield Footer()

    def on_mount(self) -> None:
        self.update_diff()

    def update_diff(self) -> None:
        if self.status_type == "untracked":
            try:
                # Try to read local file content
                if os.path.isfile(self.file_path):
                    with open(self.file_path, "r", errors="replace") as f:
                        content = f.read(5000)
                        if len(content) == 5000:
                            content += "\n... (truncated)"
                else:
                    content = f"Error: {self.file_path} is not a file or does not exist."
            except Exception as e:
                content = f"Error reading file {self.file_path}: {e}"
        else:
            cached = (self.status_type == "added")
            content = GitRunner.get_diff(self.file_path, cached=cached)

        self.query_one("#diff-view", Static).update(Text.from_ansi(content))

    def get_options_text(self) -> str:
        if self.status_type == "untracked":
            return "[a] add  [l] list  [m] back to main"
        elif self.status_type == "modified":
            return "[a] add  [d] diff  [b] blame  [r] restore  [m] back to main"
        elif self.status_type == "added":
            return "[r] restore staged  [m] back to main"
        return "[m] back to main"

    def _process_key(self, key: str) -> None:
        if key == "m" or key == "escape":
            self.dismiss(False)
        elif key == "a" and self.status_type in ("untracked", "modified"):
            ret, _, stderr = GitRunner.run(["git", "add", self.file_path])
            if ret == 0:
                self.app.notify(f"Added [bold]{self.file_path}[/]")
                self.dismiss(True)
            else:
                self.app.notify(f"Git Error: {stderr}", severity="error", timeout=5)
        elif key == "b" and self.status_type == "modified":
            content = GitRunner.get_blame(self.file_path)
            self.query_one("#diff-view", Static).update(Text.from_ansi(content))
            self.query_one("#file-header", Static).update(f"Blame: [bold yellow]{self.file_path}[/]")
        elif key == "r":
            if self.status_type == "modified":
                ret, _, stderr = GitRunner.run(["git", "checkout", "--", self.file_path])
                op = "Restored"
            elif self.status_type == "added":
                ret, _, stderr = GitRunner.run(["git", "restore", "--staged", self.file_path])
                op = "Unstaged"
            else:
                return

            if ret == 0:
                self.app.notify(f"{op} [bold]{self.file_path}[/]")
                self.dismiss(True)
            else:
                self.app.notify(f"Git Error: {stderr}", severity="error", timeout=5)
        elif key == "d" and self.status_type == "modified":
            self.update_diff()
        elif key == "l" and self.status_type == "untracked":
            self.update_diff()

    def on_key(self, event: events.Key) -> None:
        # Use event.character for single-key strokes, event.key for non-printables
        key = event.character or event.key
        self._process_key(key)

    def action_back(self) -> None:
        self.dismiss(False)

class MainScreen(Screen):
    """Main activity showing git status."""

    BINDINGS = [
        Binding("C", "commit", "Commit"),
        Binding("S", "switch", "Switch Branch"),
        Binding("B", "branch", "Create Branch"),
        Binding("D", "delete", "Delete Branch"),
        Binding("T", "stash", "Stash"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.files_map: Dict[str, Tuple[str, str]] = {} # char -> (path, type)

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

        def add_group(name: str, files: List[str], color: str):
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
        self.app.push_screen(CommitScreen(), callback=lambda _: self.refresh_status())

    def action_switch(self):
        self.app.notify("Switch branch feature coming soon!")

    def action_branch(self):
        self.app.notify("Create branch feature coming soon!")

    def action_delete(self):
        self.app.notify("Delete branch feature coming soon!")

    def action_stash(self):
        self.app.notify("Stash feature coming soon!")

    def on_key(self, event: events.Key) -> None:
        key = event.character or event.key
        if key in self.files_map:
            path, status_type = self.files_map[key]
            self.app.push_screen(FileActionScreen(path, status_type), callback=lambda _: self.refresh_status())

class QitApp(App):
    """A simple Git TUI."""

    CSS = """
    Screen {
        layout: vertical;
    }

    #upper-view {
        height: 25%;
        border-bottom: solid $accent;
        overflow-y: scroll;
        background: $boost;
        padding: 1;
    }

    #status-list {
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

    #diff-view {
        height: 70%;
        border: tall $accent;
        overflow-y: scroll;
        padding: 1;
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

    def on_mount(self) -> None:
        self.push_screen(MainScreen())

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
