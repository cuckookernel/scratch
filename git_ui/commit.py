from textual.screen import Screen
from textual.app import ComposeResult

from git_runner import GitRunner


from textual import on, events
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Label, Input


class CommitScreen(Screen):
    """Screen for entering a commit message."""
    def __init__(self, app: App):
        super().__init__()
        self.app = app

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
