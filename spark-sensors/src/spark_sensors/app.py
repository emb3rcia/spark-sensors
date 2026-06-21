from textual.app import App, ComposeResult
from textual.binding import BindingType, Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header

class SensorsApp(App):

    TITLE = "spark-sensors"

    BINDINGS: list[BindingType] = [
        Binding("d", "toggle_dark", "Toggle dark mode"),
    ]

    CSS_PATH = "spark_sensors.tcss"

    def compose(self) -> ComposeResult:
        yield Header()

        yield Footer()

    def action_toggle_dark(self):
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


def main() -> None:
    app = SensorsApp()
    app.run()

if __name__ == "__main__":
    main()
    