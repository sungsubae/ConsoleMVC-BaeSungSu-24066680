from ..model.interfaces import IRepository
from ..model.entities import Customer
from ..view.interfaces import IView
from .interfaces import ISubController


class CustomerController(ISubController):
    _MENU = ["1. 고객 목록", "2. 고객 등록", "3. 고객 수정", "4. 고객 삭제"]
    _HEADERS = ["ID", "이름", "회사명", "연락처"]

    def __init__(self, repo: IRepository[Customer], view: IView) -> None:
        self._repo = repo
        self._view = view

    def handle(self) -> None:
        while True:
            self._view.show_sub_menu("고객 관리", self._MENU)
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
            "고객 목록",
            self._repo.find_all(),
            self._HEADERS,
            lambda c: [c.id, c.name, c.company, c.contact],
        )

    def _create(self) -> None:
        name = self._view.get_input("이름")
        company = self._view.get_input("회사명")
        contact = self._view.get_input("연락처")
        if not all([name, company, contact]):
            self._view.show_error("모든 항목을 입력해주세요.")
            return
        c = self._repo.save(Customer(name=name, company=company, contact=contact))
        self._view.show_message(f"고객이 등록되었습니다. (ID: {c.id})")

    def _update(self) -> None:
        self._list()
        target = self._repo.find_by_id(self._view.get_input("수정할 고객 ID"))
        if not target:
            self._view.show_error("해당 고객을 찾을 수 없습니다.")
            return
        self._view.show_detail(
            "현재 정보",
            [("이름", target.name), ("회사명", target.company), ("연락처", target.contact)],
        )
        name = self._view.get_input("이름 (변경 없으면 Enter)")
        company = self._view.get_input("회사명 (변경 없으면 Enter)")
        contact = self._view.get_input("연락처 (변경 없으면 Enter)")
        target.name = name or target.name
        target.company = company or target.company
        target.contact = contact or target.contact
        self._repo.update(target)
        self._view.show_message("고객 정보가 수정되었습니다.")

    def _delete(self) -> None:
        self._list()
        if self._repo.delete(self._view.get_input("삭제할 고객 ID")):
            self._view.show_message("고객이 삭제되었습니다.")
        else:
            self._view.show_error("해당 고객을 찾을 수 없습니다.")
