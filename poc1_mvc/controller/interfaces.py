from abc import ABC, abstractmethod


class IController(ABC):
    """최상위 앱 컨트롤러 — 메인 루프를 소유한다."""

    @abstractmethod
    def run(self) -> None: ...


class ISubController(ABC):
    """단일 도메인(고객/시료/주문 등)의 CRUD 흐름을 담당하는 서브 컨트롤러."""

    @abstractmethod
    def handle(self) -> None: ...
