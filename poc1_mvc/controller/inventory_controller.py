from ..model.interfaces import IRepository
from ..model.entities import Sample, Inventory
from ..view.interfaces import IView
from .interfaces import ISubController


class InventoryController(ISubController):
    _MENU = ["1. 재고 조회", "2. 재고 등록", "3. 재고 수량 수정"]
    _HEADERS = ["ID", "시료명", "재고량"]

    def __init__(
        self,
        inv_repo: IRepository[Inventory],
        sample_repo: IRepository[Sample],
        view: IView,
    ) -> None:
        self._inv = inv_repo
        self._samples = sample_repo
        self._view = view

    def handle(self) -> None:
        while True:
            self._view.show_sub_menu("재고 관리", self._MENU)
            match self._view.get_choice():
                case "0":
                    break
                case "1":
                    self._list()
                case "2":
                    self._create()
                case "3":
                    self._update_quantity()
                case _:
                    self._view.show_error("잘못된 입력입니다.")

    def _sample_name(self, id_: str) -> str:
        s = self._samples.find_by_id(id_)
        return s.name if s else id_

    def _list(self) -> None:
        self._view.show_list(
            "재고 현황",
            self._inv.find_all(),
            self._HEADERS,
            lambda i: [i.id, self._sample_name(i.sample_id), i.quantity],
        )

    def _create(self) -> None:
        samples = self._samples.find_all()
        if not samples:
            self._view.show_error("등록된 시료가 없습니다.")
            return
        self._view.show_list("시료 목록", samples, ["ID", "시료명", "종류"],
                             lambda s: [s.id, s.name, s.type])
        sample_id = self._view.get_input("시료 ID")
        if not self._samples.find_by_id(sample_id):
            self._view.show_error("해당 시료를 찾을 수 없습니다.")
            return
        try:
            qty = int(self._view.get_input("초기 재고량"))
            if qty < 0:
                raise ValueError
        except ValueError:
            self._view.show_error("재고량은 0 이상의 정수여야 합니다.")
            return
        inv = self._inv.save(Inventory(sample_id=sample_id, quantity=qty))
        self._view.show_message(f"재고가 등록되었습니다. (ID: {inv.id})")

    def _update_quantity(self) -> None:
        self._list()
        target = self._inv.find_by_id(self._view.get_input("수정할 재고 ID"))
        if not target:
            self._view.show_error("해당 재고를 찾을 수 없습니다.")
            return
        try:
            target.quantity = int(self._view.get_input(f"새 재고량 (현재: {target.quantity})"))
            if target.quantity < 0:
                raise ValueError
        except ValueError:
            self._view.show_error("재고량은 0 이상의 정수여야 합니다.")
            return
        self._inv.update(target)
        self._view.show_message("재고 수량이 수정되었습니다.")
