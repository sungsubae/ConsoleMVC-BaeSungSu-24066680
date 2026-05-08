from .view.console_view import ConsoleView
from .controller.app_controller import AppController


def main() -> None:
    view = ConsoleView()
    controller = AppController(view)
    controller.run()
