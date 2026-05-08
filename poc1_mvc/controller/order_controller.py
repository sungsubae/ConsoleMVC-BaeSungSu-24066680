from datetime import datetime
from ..model.interfaces import IRepository
from ..model.entities import Customer, Sample, Order, Process, OrderStatus, ProcessStage
from ..view.interfaces import IView
from .interfaces import ISubController


class OrderController(ISubController):
    _MENU = ["1. 주문 목록", "2. 주문 등록", "3. 주문 상태 변경", "4. 주문 삭제"]
    _HEADERS = ["ID", "고객명", "시료명", "수량", "상태", "주문일시"]

    def __init__(
        self,
        order_repo: IRepository[Order],
        customer_repo: IRepository[Customer],
        sample_repo: IRepository[Sample],
        process_repo: IRepository[Process],
        view: IView,
    ) -> None:
        self._orders = order_repo
        self._customers = customer_repo
        self._samples = sample_repo
        self._processes = process_repo
        self._view = view

    def handle(self) -> None:
        while True:
            self._view.show_sub_menu("주문 관리", self._MENU)
            match self._view.get_choice():
                case "0":
                    break
                case "1":
                    self._list()
                case "2":
                    self._create()
                case "3":
                    self._update_status()
                case "4":
                    self._delete()
                case _:
                    self._view.show_error("잘못된 입력입니다.")

    # ── 내부 헬퍼 ──────────────────────────────────────────────────────────
    def _customer_name(self, id_: str) -> str:
        c = self._customers.find_by_id(id_)
        return c.name if c else id_

    def _sample_name(self, id_: str) -> str:
        s = self._samples.find_by_id(id_)
        return s.name if s else id_

    # ── CRUD ───────────────────────────────────────────────────────────────
    def _list(self) -> None:
        self._view.show_list(
            "주문 목록",
            self._orders.find_all(),
            self._HEADERS,
            lambda o: [
                o.id,
                self._customer_name(o.customer_id),
                self._sample_name(o.sample_id),
                o.quantity,
                o.status.value,
                o.created_at,
            ],
        )

    def _create(self) -> None:
        customers = self._customers.find_all()
        samples = self._samples.find_all()
        if not customers:
            self._view.show_error("등록된 고객이 없습니다. 먼저 고객을 등록해주세요.")
            return
        if not samples:
            self._view.show_error("등록된 시료가 없습니다. 먼저 시료를 등록해주세요.")
            return

        self._view.show_list("고객 목록", customers, ["ID", "이름", "회사명"],
                             lambda c: [c.id, c.name, c.company])
        customer_id = self._view.get_input("고객 ID")
        if not self._customers.find_by_id(customer_id):
            self._view.show_error("해당 고객을 찾을 수 없습니다.")
            return

        self._view.show_list("시료 목록", samples, ["ID", "시료명", "종류"],
                             lambda s: [s.id, s.name, s.type])
        sample_id = self._view.get_input("시료 ID")
        if not self._samples.find_by_id(sample_id):
            self._view.show_error("해당 시료를 찾을 수 없습니다.")
            return

        try:
            qty = int(self._view.get_input("수량"))
            if qty <= 0:
                raise ValueError
        except ValueError:
            self._view.show_error("수량은 양의 정수여야 합니다.")
            return

        order = self._orders.save(Order(customer_id=customer_id, sample_id=sample_id, quantity=qty))
        # 주문 생성 시 공정 레코드를 설계 단계로 자동 생성
        self._processes.save(Process(order_id=order.id, stage=ProcessStage.DESIGN))
        self._view.show_message(f"주문이 등록되었습니다. (ID: {order.id})")

    def _update_status(self) -> None:
        self._list()
        target = self._orders.find_by_id(self._view.get_input("상태를 변경할 주문 ID"))
        if not target:
            self._view.show_error("해당 주문을 찾을 수 없습니다.")
            return
        statuses = list(OrderStatus)
        self._view.show_options([f"{i}. {s.value}" for i, s in enumerate(statuses, 1)])
        try:
            target.status = statuses[int(self._view.get_input("상태 번호")) - 1]
        except (ValueError, IndexError):
            self._view.show_error("잘못된 선택입니다.")
            return
        self._orders.update(target)
        self._view.show_message(f"주문 상태가 '{target.status.value}'(으)로 변경되었습니다.")

    def _delete(self) -> None:
        self._list()
        if self._orders.delete(self._view.get_input("삭제할 주문 ID")):
            self._view.show_message("주문이 삭제되었습니다.")
        else:
            self._view.show_error("해당 주문을 찾을 수 없습니다.")
