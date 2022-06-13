
import edifice as ed
from edifice import View, Label, ScrollView, Button, Table


APP_STATE = ed.StateManager(
    {"text": "this\nis a\ntest"}
)


class App(ed.Component):
    """The commander app"""
    window_style = {"margin": 20, "width": 400, "height": 800,
                    "subcontrol-position": "top"}

    def render( self ):
        """produce the main window"""
        text_lines = APP_STATE.subscribe(self, "text").value.split('\n')

        # line_labels = [Label(line, selectable=True, on_click=self._set_selected,
        #                     style={"height": 15, "subcontrol-position": "top"})
        #               for line in text_lines]

        lines = Table(rows=30, columns=1)

        return ed.Window(title="Commander")(
            View(layout="column",
                 style=App.window_style)(
                lines,
                Button( title='Ok', on_click=self._on_ok )
            ),
        )

    def _on_ok( self, x ):
        print(f'ok pressed: {x}')

    def _set_selected( self, x ):
        print( f'set_selected: {x}' )


def _interactive_testing(app):
    # %%
    runfile("commander_gui/gui.py")
    # del app
    # %%
    app = App()
    ed.App( app ).start()
    # %%


if __name__ == "__main__":
    ed.App(App()).start()
# %%
