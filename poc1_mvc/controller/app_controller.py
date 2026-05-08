from ..model.entities import Customer, Sample, Order, Inventory, Process
from ..model.repository import InMemoryRepository
from ..view.interfaces import IView
from .interfaces import IController, ISubController
from .customer_controller import CustomerController
from .sample_controller import SampleController
from .order_controller import OrderController
from .inventory_controller import InventoryController
from .process_controller import ProcessController


class AppController(IController):
    def __init__(self, view: IView) -> None:
        self._view = view

        # 모든 Repository를 여기서 생성 — PoC 2에서 JSON 구현체로 교체 가능
        customer_repo: InMemoryRepository[Customer] = InMemoryRepository()
        sample_repo: InMemoryRepository[Sample] = InMemoryRepository()
        order_repo: InMemoryRepository[Order] = InMemoryRepository()
        inv_repo: InMemoryRepository[Inventory] = InMemoryRepository()
        process_repo: InMemoryRepository[Process] = InMemoryRepository()

        self._routes: dict[str, ISubController] = {
            "1": CustomerController(customer_repo, view),
            "2": SampleController(sample_repo, view),
            "3": OrderController(order_repo, customer_repo, sample_repo, process_repo, view),
            "4": InventoryController(inv_repo, sample_repo, view),
            "5": ProcessController(process_repo, order_repo, view),
        }

    def run(self) -> None:
        self._view.show_message("S-Semi 시스템을 시작합니다.")
        while True:
            self._view.show_main_menu()
            choice = self._view.get_choice()
            if choice == "0":
                self._view.show_message("시스템을 종료합니다.")
                break
            elif choice in self._routes:
                self._routes[choice].handle()
            else:
                self._view.show_error("잘못된 입력입니다.")
