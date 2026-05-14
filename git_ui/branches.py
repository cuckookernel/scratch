from textual import events
from textual.app import App
from textual.screen import Screen
from textual.app import ComposeResult
from textual.binding import Binding
from .git_runner import GitRunner
from .common import SELECTION_CHARS
from textual.widgets import Header, Footer, Static
from rich.text import Text
from textual.containers import Vertical


class BranchScreen(Screen):
    """Screen for branch management."""
    BINDINGS = [
        Binding("H", "status", "Home/Status Screen"),
        Binding("escape", "back", "Back"),
        Binding("C", "switch", "Switch to branch"),
        Binding("B", "create", "Create branch"),
        Binding("D", "delete", "Delete branch"),
        Binding("R", "refresh", "Refresh"),
    ]

    def __init__(self, app: App):
        super().__init__()
        self.app = app
        self.branches_map: dict[str, str] = {} # char -> branch_name

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Static("", id="branch-info")
            yield Static("", id="branch-list")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_branches()

    def refresh_branches(self) -> None:
        current_branch = GitRunner.get_branch_name()
        branches = GitRunner.get_all_branches()
        self.branches_map = {}
        char_idx = 0

        info_text = Text()
        info_text.append("Current Branch: ", style="bold cyan")
        info_text.append(f"{current_branch}\n", style="bold yellow")
        self.query_one("#branch-info", Static).update(info_text)

        list_text = Text()
        list_text.append("LOCAL BRANCHES:\n", style="bold underline")
        for b in branches:
            if char_idx < len(SELECTION_CHARS):
                char = SELECTION_CHARS[char_idx]
                self.branches_map[char] = b
                list_text.append(f" {char} ", style="bold cyan")
                style = "bold yellow" if b == current_branch else "white"
                indicator = "*" if b == current_branch else " "
                list_text.append(f"{indicator} {b}\n", style=style)
                char_idx += 1

        self.query_one("#branch-list", Static).update(list_text)

    def action_back(self) -> None:
        self.dismiss()

    def action_refresh(self) -> None:
        self.refresh_branches()

    def action_switch(self) -> None:
        self.app.notify("Select a branch with its shortcut key (e.g., 1, 2, a) to switch.")

    def action_create(self) -> None:
        self.app.notify("Create branch logic coming soon!")

    def action_delete(self) -> None:
        self.app.notify("Select a branch then press D to delete (coming soon).")

    def on_key(self, event: events.Key) -> None:
        key = event.character or event.key
        if key in self.branches_map:
            branch_name = self.branches_map[key]
            # Handle switch to this branch
            ret, _, stderr = GitRunner.run(["git", "checkout", branch_name])
            if ret == 0:
                self.app.notify(f"Switched to [bold yellow]{branch_name}[/]")
                self.refresh_branches()
            else:
                self.app.notify(f"Git Error: {stderr}", severity="error", timeout=5)
