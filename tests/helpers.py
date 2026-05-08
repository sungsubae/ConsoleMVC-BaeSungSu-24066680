from collections.abc import Callable
from poc1_mvc.view.interfaces import IView


class MockView(IView):
    """테스트용 View: 미리 등록된 입력을 순서대로 반환하고 출력을 기록한다."""

    def __init__(self) -> None:
        self._choices: list[str] = []
        self._inputs: list[str] = []
        self.messages: list[str] = []
        self.errors: list[str] = []
        self.shown_lists: list[tuple] = []
        self.shown_details: list[tuple] = []
        self.shown_options: list[list[str]] = []

    # ── 입력 준비 ───────────────────────────────────────────────────────────
    def push_choices(self, *choices: str) -> "MockView":
        self._choices.extend(choices)
        return self

    def push_inputs(self, *inputs: str) -> "MockView":
        self._inputs.extend(inputs)
        return self

    # ── IView 구현 ──────────────────────────────────────────────────────────
    def show_main_menu(self) -> None:
        pass

    def show_sub_menu(self, title: str, options: list[str]) -> None:
        pass

    def show_list(
        self,
        title: str,
        items: list,
        headers: list[str],
        row_fn: Callable[[object], list[str]],
    ) -> None:
        rows = [row_fn(item) for item in items]
        self.shown_lists.append((title, rows))

    def show_detail(self, title: str, fields: list[tuple[str, str]]) -> None:
        self.shown_details.append((title, fields))

    def show_options(self, options: list[str]) -> None:
        self.shown_options.append(options)

    def show_message(self, message: str) -> None:
        self.messages.append(message)

    def show_error(self, message: str) -> None:
        self.errors.append(message)

    def get_input(self, prompt: str) -> str:
        return self._inputs.pop(0) if self._inputs else ""

    def get_choice(self, prompt: str = "선택") -> str:
        return self._choices.pop(0) if self._choices else "0"
