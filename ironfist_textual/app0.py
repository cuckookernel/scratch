from textual.app import App
from textual.widgets import OptionList


class CommandsApp(App):
    BINDING = [
        ("q", "quit", "Quit"),
    ]

    def compose(self):
        yield OptionList("git add", "git commit", "git push")


