import os
from textual import events
from textual.binding import Binding
from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Header, Footer, Static
from rich.text import Text
from .git_runner import GitRunner
from .common import SELECTION_CHARS


class FileActionScreen(Screen):
    """Screen for acting on a specific file."""

    BINDINGS = [
        Binding("m", "back", "Main Menu"),
        Binding("escape", "back", "Back"),
        Binding("a", "add", "Add"),
        Binding("d", "diff", "Diff"),
        Binding("b", "blame", "Blame"),
        Binding("r", "restore", "Restore"),
        Binding("l", "list", "List"),
    ]

    def __init__(self, app: App, file_path: str, status_type: str):
        super().__init__()
        self.file_path = file_path
        self.status_type = status_type

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Static(f"File Diff: [bold yellow]{self.file_path}[/]", id="file-header")
            yield Static("", id="diff-view", expand=True)
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

    def action_back(self) -> None:
        self.dismiss(False)

    def action_add(self) -> None:
        if self.status_type in ("untracked", "modified"):
            ret, _, stderr = GitRunner.run(["git", "add", self.file_path])
            if ret == 0:
                self.app.notify(f"Added [bold]{self.file_path}[/]")
                self.dismiss(True)
            else:
                self.app.notify(f"Git Error: {stderr}", severity="error", timeout=5)

    def action_blame(self) -> None:
        if self.status_type == "modified":
            content = GitRunner.get_blame(self.file_path)
            self.query_one("#diff-view", Static).update(Text.from_ansi(content))
            self.query_one("#file-header", Static).update(f"Blame: [bold yellow]{self.file_path}[/]")

    def action_restore(self) -> None:
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

    def action_diff(self) -> None:
        if self.status_type == "modified":
            self.update_diff()

    def action_list(self) -> None:
        if self.status_type == "untracked":
            self.update_diff()

class StatusScreen(Screen):
    """Main activity showing git status."""

    BINDINGS = [
        Binding("C", "commit", "Commit"),
        Binding("B", "branches", "Branches"),
        Binding("T", "stash", "Stash"),
        Binding("P", "stash_pop", "Stash Pop"),
        Binding("R", "refresh", "Refresh"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self, home_screen_cls: type[Screen], branch_screen_cls: type[Screen]):
        super().__init__()
        self.files_map: dict[str, tuple[str, str]] = {} # char -> (path, type)
        self.home_screen_cls = home_screen_cls
        self.branch_screen_cls = branch_screen_cls

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
        self.app.push_screen(self.app.commit_screen_mkr(), callback=lambda _: self.refresh_status())

    def action_branches(self):
        self.app.push_screen(self.app.branch_screen_cls(), callback=lambda _: self.refresh_status())

    def action_stash(self):
        self.app.notify("Stash feature coming soon!")

    def action_stash_pop(self):
        self.app.notify("Stash pop feature coming soon!")

    def action_refresh(self):
        self.refresh_status()

    def on_key(self, event: events.Key) -> None:
        key = event.character or event.key
        if key in self.files_map:
            path, status_type = self.files_map[key]
            self.app.push_screen(FileActionScreen(path, status_type), callback=lambda result: self.refresh_status() if result else None)
