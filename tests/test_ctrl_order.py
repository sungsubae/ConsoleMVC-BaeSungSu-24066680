import unittest
from poc1_mvc.model.entities import Customer, Sample, Order, Process
from poc1_mvc.model.repository import InMemoryRepository
from poc1_mvc.controller.order_controller import OrderController
from tests.helpers import MockView


def _make_ctrl(order_repo, customer_repo, sample_repo, process_repo, view):
    return OrderController(order_repo, customer_repo, sample_repo, process_repo, view)


class TestOrderController(unittest.TestCase):
    def setUp(self):
        self.orders: InMemoryRepository[Order] = InMemoryRepository()
        self.customers: InMemoryRepository[Customer] = InMemoryRepository()
        self.samples: InMemoryRepository[Sample] = InMemoryRepository()
        self.processes: InMemoryRepository[Process] = InMemoryRepository()
        self.view = MockView()
        self.ctrl = _make_ctrl(
            self.orders, self.customers, self.samples, self.processes, self.view
        )

    def _run(self, choices: list[str], inputs: list[str] | None = None):
        self.view.push_choices(*choices)
        if inputs:
            self.view.push_inputs(*inputs)
        self.ctrl.handle()

    def _seed(self):
        c = self.customers.save(Customer(name="고객A", company="A사", contact="010"))
        s = self.samples.save(Sample(name="DRAM-A", type="DRAM", specification="16GB"))
        return c, s

    # ── 메뉴 ──────────────────────────────────────────────────────────────
    def test_exit(self):
        self._run(["0"])

    def test_invalid_choice(self):
        self._run(["9", "0"])
        self.assertEqual(len(self.view.errors), 1)

    # ── 목록 ──────────────────────────────────────────────────────────────
    def test_list_empty(self):
        self._run(["1", "0"])

    def test_list_with_items_shows_names(self):
        c, s = self._seed()
        self.orders.save(Order(customer_id=c.id, sample_id=s.id, quantity=5))
        self._run(["1", "0"])
        self.assertEqual(len(self.view.shown_lists), 1)

    def test_list_unknown_ids_fallback_to_id(self):
        # 고객/시료 레코드 없이 주문만 있는 경우 → ID 그대로 표시
        self.orders.save(Order(customer_id="GHOST_C", sample_id="GHOST_S", quantity=1))
        self._run(["1", "0"])

    # ── 등록 — 사전 조건 실패 ─────────────────────────────────────────────
    def test_create_no_customers(self):
        self._run(["2", "0"])
        self.assertTrue(any("고객" in e for e in self.view.errors))

    def test_create_no_samples(self):
        self.customers.save(Customer(name="A", company="B", contact="C"))
        self._run(["2", "0"])
        self.assertTrue(any("시료" in e for e in self.view.errors))

    # ── 등록 — 유효성 실패 ────────────────────────────────────────────────
    def test_create_invalid_customer_id(self):
        self._seed()
        self._run(["2", "0"], ["INVALID_CID"])
        self.assertTrue(any("고객" in e for e in self.view.errors))

    def test_create_invalid_sample_id(self):
        c, _ = self._seed()
        self._run(["2", "0"], [c.id, "INVALID_SID"])
        self.assertTrue(any("시료" in e for e in self.view.errors))

    def test_create_quantity_not_integer(self):
        c, s = self._seed()
        self._run(["2", "0"], [c.id, s.id, "abc"])
        self.assertEqual(len(self.orders.find_all()), 0)

    def test_create_quantity_zero(self):
        c, s = self._seed()
        self._run(["2", "0"], [c.id, s.id, "0"])
        self.assertEqual(len(self.orders.find_all()), 0)

    def test_create_quantity_negative(self):
        c, s = self._seed()
        self._run(["2", "0"], [c.id, s.id, "-5"])
        self.assertEqual(len(self.orders.find_all()), 0)

    # ── 등록 — 정상 ───────────────────────────────────────────────────────
    def test_create_valid(self):
        c, s = self._seed()
        self._run(["2", "0"], [c.id, s.id, "10"])
        self.assertEqual(len(self.orders.find_all()), 1)
        # 공정 레코드 자동 생성 확인
        self.assertEqual(len(self.processes.find_all()), 1)
        self.assertTrue(any("등록" in m for m in self.view.messages))

    # ── 상태 변경 ─────────────────────────────────────────────────────────
    def test_update_status_not_found(self):
        self._run(["3", "0"], ["INVALID"])
        self.assertTrue(any("찾을 수 없" in e for e in self.view.errors))

    def test_update_status_valid(self):
        c, s = self._seed()
        o = self.orders.save(Order(customer_id=c.id, sample_id=s.id, quantity=5))
        self._run(["3", "0"], [o.id, "2"])  # "2" → IN_PROGRESS
        updated = self.orders.find_by_id(o.id)
        from poc1_mvc.model.entities import OrderStatus
        self.assertEqual(updated.status, OrderStatus.IN_PROGRESS)

    def test_update_status_invalid_choice_text(self):
        c, s = self._seed()
        o = self.orders.save(Order(customer_id=c.id, sample_id=s.id, quantity=5))
        self._run(["3", "0"], [o.id, "abc"])
        self.assertTrue(any("잘못" in e for e in self.view.errors))

    def test_update_status_out_of_range(self):
        c, s = self._seed()
        o = self.orders.save(Order(customer_id=c.id, sample_id=s.id, quantity=5))
        self._run(["3", "0"], [o.id, "99"])
        self.assertTrue(any("잘못" in e for e in self.view.errors))

    # ── 삭제 ─────────────────────────────────────────────────────────────
    def test_delete_valid(self):
        c, s = self._seed()
        o = self.orders.save(Order(customer_id=c.id, sample_id=s.id, quantity=5))
        self._run(["4", "0"], [o.id])
        self.assertIsNone(self.orders.find_by_id(o.id))

    def test_delete_not_found(self):
        self._run(["4", "0"], ["INVALID"])
        self.assertTrue(any("찾을 수 없" in e for e in self.view.errors))


if __name__ == "__main__":
    unittest.main()
