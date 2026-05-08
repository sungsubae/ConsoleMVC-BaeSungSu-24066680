import unittest
from poc1_mvc.model.entities import Customer
from poc1_mvc.model.repository import InMemoryRepository
from poc1_mvc.controller.customer_controller import CustomerController
from tests.helpers import MockView


class TestCustomerController(unittest.TestCase):
    def setUp(self):
        self.repo: InMemoryRepository[Customer] = InMemoryRepository()
        self.view = MockView()
        self.ctrl = CustomerController(self.repo, self.view)

    def _run(self, choices: list[str], inputs: list[str] | None = None):
        self.view.push_choices(*choices)
        if inputs:
            self.view.push_inputs(*inputs)
        self.ctrl.handle()

    # ── 메뉴 라우팅 ───────────────────────────────────────────────────────
    def test_exit(self):
        self._run(["0"])
        self.assertEqual(len(self.view.errors), 0)

    def test_invalid_choice(self):
        self._run(["9", "0"])
        self.assertEqual(len(self.view.errors), 1)

    # ── 목록 ─────────────────────────────────────────────────────────────
    def test_list_empty(self):
        self._run(["1", "0"])
        self.assertEqual(len(self.view.shown_lists), 1)

    def test_list_with_items(self):
        self.repo.save(Customer(name="A", company="B", contact="C"))
        self._run(["1", "0"])
        self.assertEqual(len(self.view.shown_lists), 1)

    # ── 등록 ─────────────────────────────────────────────────────────────
    def test_create_valid(self):
        self._run(["2", "0"], ["홍길동", "S-Semi", "010-1234-5678"])
        self.assertEqual(len(self.repo.find_all()), 1)
        self.assertTrue(any("등록" in m for m in self.view.messages))

    def test_create_missing_name(self):
        self._run(["2", "0"], ["", "S-Semi", "010"])
        self.assertEqual(len(self.repo.find_all()), 0)
        self.assertTrue(any("입력" in e for e in self.view.errors))

    def test_create_missing_company(self):
        self._run(["2", "0"], ["홍길동", "", "010"])
        self.assertEqual(len(self.repo.find_all()), 0)

    def test_create_missing_contact(self):
        self._run(["2", "0"], ["홍길동", "S-Semi", ""])
        self.assertEqual(len(self.repo.find_all()), 0)

    # ── 수정 ─────────────────────────────────────────────────────────────
    def test_update_not_found(self):
        self._run(["3", "0"], ["INVALID"])
        self.assertTrue(any("찾을 수 없" in e for e in self.view.errors))

    def test_update_all_fields(self):
        c = self.repo.save(Customer(name="A", company="B", contact="C"))
        # 목록 → ID 입력 → 이름/회사/연락처 변경
        self._run(["3", "0"], [c.id, "새이름", "새회사", "새연락처"])
        updated = self.repo.find_by_id(c.id)
        self.assertEqual(updated.name, "새이름")
        self.assertEqual(updated.company, "새회사")
        self.assertEqual(updated.contact, "새연락처")

    def test_update_keep_empty_fields(self):
        c = self.repo.save(Customer(name="원본이름", company="원본회사", contact="원본연락처"))
        # 이름만 변경, 나머지 빈 값(Enter) → 기존 값 유지
        self._run(["3", "0"], [c.id, "새이름", "", ""])
        updated = self.repo.find_by_id(c.id)
        self.assertEqual(updated.name, "새이름")
        self.assertEqual(updated.company, "원본회사")
        self.assertEqual(updated.contact, "원본연락처")

    # ── 삭제 ─────────────────────────────────────────────────────────────
    def test_delete_valid(self):
        c = self.repo.save(Customer(name="A", company="B", contact="C"))
        self._run(["4", "0"], [c.id])
        self.assertIsNone(self.repo.find_by_id(c.id))
        self.assertTrue(any("삭제" in m for m in self.view.messages))

    def test_delete_not_found(self):
        self._run(["4", "0"], ["INVALID"])
        self.assertTrue(any("찾을 수 없" in e for e in self.view.errors))


if __name__ == "__main__":
    unittest.main()
