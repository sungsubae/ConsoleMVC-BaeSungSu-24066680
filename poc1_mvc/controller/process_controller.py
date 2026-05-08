from datetime import datetime
from ..model.interfaces import IRepository
from ..model.entities import Order, Process, ProcessStage, ProcessStatus
from ..view.interfaces import IView
from .interfaces import ISubController


class ProcessController(ISubController):
    _MENU = ["1. 공정 현황 조회", "2. 공정 단계 변경", "3. 공정 상태 변경"]
    _HEADERS = ["ID", "주문ID", "단계", "상태", "갱신일시"]

    def __init__(
        self,
        process_repo: IRepository[Process],
        order_repo: IRepository[Order],
        view: IView,
    ) -> None:
        self._processes = process_repo
        self._orders = order_repo
        self._view = view

    def handle(self) -> None:
        while True:
            self._view.show_sub_menu("공정 현황", self._MENU)
            match self._view.get_choice():
                case "0":
                    break
                case "1":
                    self._list()
                case "2":
                    self._update_stage()
                case "3":
                    self._update_status()
                case _:
                    self._view.show_error("잘못된 입력입니다.")

    def _list(self) -> None:
        self._view.show_list(
            "공정 현황",
            self._processes.find_all(),
            self._HEADERS,
            lambda p: [p.id, p.order_id, p.stage.value, p.status.value, p.updated_at],
        )

    def _update_stage(self) -> None:
        self._list()
        target = self._processes.find_by_id(self._view.get_input("변경할 공정 ID"))
        if not target:
            self._view.show_error("해당 공정을 찾을 수 없습니다.")
            return
        stages = list(ProcessStage)
        self._view.show_options([f"{i}. {s.value}" for i, s in enumerate(stages, 1)])
        try:
            target.stage = stages[int(self._view.get_input("단계 번호")) - 1]
            target.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, IndexError):
            self._view.show_error("잘못된 선택입니다.")
            return
        self._processes.update(target)
        self._view.show_message(f"공정 단계가 '{target.stage.value}'(으)로 변경되었습니다.")

    def _update_status(self) -> None:
        self._list()
        target = self._processes.find_by_id(self._view.get_input("변경할 공정 ID"))
        if not target:
            self._view.show_error("해당 공정을 찾을 수 없습니다.")
            return
        statuses = list(ProcessStatus)
        self._view.show_options([f"{i}. {s.value}" for i, s in enumerate(statuses, 1)])
        try:
            target.status = statuses[int(self._view.get_input("상태 번호")) - 1]
            target.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, IndexError):
            self._view.show_error("잘못된 선택입니다.")
            return
        self._processes.update(target)
        self._view.show_message(f"공정 상태가 '{target.status.value}'(으)로 변경되었습니다.")
