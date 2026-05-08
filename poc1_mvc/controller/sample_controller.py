from ..model.interfaces import IRepository
from ..model.entities import Sample
from ..view.interfaces import IView
from .interfaces import ISubController


class SampleController(ISubController):
    _MENU = ["1. 시료 목록", "2. 시료 등록", "3. 시료 수정", "4. 시료 삭제"]
    _HEADERS = ["ID", "시료명", "종류", "사양"]

    def __init__(self, repo: IRepository[Sample], view: IView) -> None:
        self._repo = repo
        self._view = view

    def handle(self) -> None:
        while True:
            self._view.show_sub_menu("시료 관리", self._MENU)
            match self._view.get_choice():
                case "0":
                    break
                case "1":
                    self._list()
                case "2":
                    self._create()
                case "3":
                    self._update()
                case "4":
                    self._delete()
                case _:
                    self._view.show_error("잘못된 입력입니다.")

    def _list(self) -> None:
        self._view.show_list(
            "시료 목록",
            self._repo.find_all(),
            self._HEADERS,
            lambda s: [s.id, s.name, s.type, s.specification],
        )

    def _create(self) -> None:
        name = self._view.get_input("시료명")
        type_ = self._view.get_input("종류 (예: DRAM, NAND, Logic)")
        spec = self._view.get_input("사양")
        if not all([name, type_, spec]):
            self._view.show_error("모든 항목을 입력해주세요.")
            return
        s = self._repo.save(Sample(name=name, type=type_, specification=spec))
        self._view.show_message(f"시료가 등록되었습니다. (ID: {s.id})")

    def _update(self) -> None:
        self._list()
        target = self._repo.find_by_id(self._view.get_input("수정할 시료 ID"))
        if not target:
            self._view.show_error("해당 시료를 찾을 수 없습니다.")
            return
        self._view.show_detail(
            "현재 정보",
            [("시료명", target.name), ("종류", target.type), ("사양", target.specification)],
        )
        name = self._view.get_input("시료명 (변경 없으면 Enter)")
        type_ = self._view.get_input("종류 (변경 없으면 Enter)")
        spec = self._view.get_input("사양 (변경 없으면 Enter)")
        target.name = name or target.name
        target.type = type_ or target.type
        target.specification = spec or target.specification
        self._repo.update(target)
        self._view.show_message("시료 정보가 수정되었습니다.")

    def _delete(self) -> None:
        self._list()
        if self._repo.delete(self._view.get_input("삭제할 시료 ID")):
            self._view.show_message("시료가 삭제되었습니다.")
        else:
            self._view.show_error("해당 시료를 찾을 수 없습니다.")
