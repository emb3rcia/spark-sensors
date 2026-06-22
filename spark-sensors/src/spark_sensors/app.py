from textual.app import App, ComposeResult
from textual.binding import BindingType, Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, ListView, Label, ListItem

from rich.text import Text

from spark_sensors.collectors.collector_manager import CollectorManager

class SensorsApp(App):

    TITLE = "spark-sensors"

    BINDINGS: list[BindingType] = [
        Binding("d", "toggle_dark", "Toggle dark mode"),
    ]

    CSS_PATH = "spark_sensors.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(classes="height-one border-gray"):
            yield ListView(classes="width-one height-one", id="selector")
            yield ListView(classes="width-two height-one", id="details")
        yield Footer()

    def action_toggle_dark(self):
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def on_mount(self) -> None:
        self.categories = []
        self.manager = CollectorManager()
        self.dynamic_details = self.manager.dynamic_collect()
        self.static_details = self.manager.static_collect()
        list_view = self.query_one("#selector")
        list_items = []
        for result in self.dynamic_details:
            if result.category not in self.categories:
                self.categories.append(result.category)
        for result in self.static_details:
            if result.category not in self.categories:
                self.categories.append(result.category)
        for category_found in self.categories:
            list_items.append(
                ListItem(
                    Label(category_found)
                )
            )
        for list_item in list_items:
            list_view.append(list_item)

        details = self.query_one("#details")

        if not self.static_details and not self.dynamic_details:
            details.update("No data found")
            return

        self.index_selected = 0
        
        self.set_interval(1, self.refresh_data)

        self.data_update()
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:

        details = self.query_one("#details")

        if not self.static_details and not self.dynamic_details:
            details.update("No data found")
            return

        list_view = event.list_view
        index_list = list_view.index

        if index_list is None:
            index_list = 0

        self.index_selected = index_list

        self.data_update()

    def data_update(self) -> None:
        details = self.query_one("#details")
        self.dynamic_details = self.manager.dynamic_collect()
        list_items_data = []
        
        for static_detail in self.static_details:
            if static_detail.category == self.categories[self.index_selected]: 
                detail_string = Text()
                detail_string.append(f"ID: {static_detail.id}\n")
                detail_string.append(f"Name: {static_detail.name}\n")
                detail_string.append(f"Value: {static_detail.value} {static_detail.unit}\n")
                list_items_data.append(
                    ListItem(
                        Label(detail_string)
                    )
                )
        for dynamic_detail in self.dynamic_details:
            if dynamic_detail.category == self.categories[self.index_selected]:
                detail_string = Text()
                detail_string.append(f"ID: {dynamic_detail.id}\n")
                detail_string.append(f"Name: {dynamic_detail.name}\n")
                detail_string.append(f"Value: {dynamic_detail.value} {dynamic_detail.unit}\n")
                list_items_data.append(
                    ListItem(
                        Label(detail_string)
                    )
                )
        details.clear()
        for list_item in list_items_data:
            details.append(list_item)
    
    def refresh_data(self):
        self.dynamic_details = self.manager.dynamic_collect()
        self.data_update()
            

def main() -> None:
    app = SensorsApp()
    app.run()

if __name__ == "__main__":
    main()
    