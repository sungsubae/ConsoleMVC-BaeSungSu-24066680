from abc import ABC, abstractmethod
from collections.abc import Callable


class IView(ABC):
    @abstractmethod
    def show_main_menu(self) -> None: ...

    @abstractmethod
    def show_sub_menu(self, title: str, options: list[str]) -> None: ...

    @abstractmethod
    def show_list(
        self,
        title: str,
        items: list,
        headers: list[str],
        row_fn: Callable[[object], list[str]],
    ) -> None: ...

    @abstractmethod
    def show_detail(self, title: str, fields: list[tuple[str, str]]) -> None: ...

    @abstractmethod
    def show_message(self, message: str) -> None: ...

    @abstractmethod
    def show_error(self, message: str) -> None: ...

    @abstractmethod
    def get_input(self, prompt: str) -> str: ...

    @abstractmethod
    def show_options(self, options: list[str]) -> None: ...

    @abstractmethod
    def get_choice(self, prompt: str = "선택") -> str: ...
