import unittest
from poc1_mvc.model.entities import Sample, Inventory
from poc1_mvc.model.repository import InMemoryRepository
from poc1_mvc.controller.inventory_controller import InventoryController
from tests.helpers import MockView


class TestInventoryController(unittest.TestCase):
    def setUp(self):
        self.inv_repo: InMemoryRepository[Inventory] = InMemoryRepository()
        self.sample_repo: InMemoryRepository[Sample] = InMemoryRepository()
        self.view = MockView()
        self.ctrl = InventoryController(self.inv_repo, self.sample_repo, self.view)

    def _run(self, choices: list[str], inputs: list[str] | None = None):
        self.view.push_choices(*choices)
        if inputs:
            self.view.push_inputs(*inputs)
        self.ctrl.handle()

    def _seed_sample(self) -> Sample:
        return self.sample_repo.save(Sample(name="DRAM-A", type="DRAM", specification="16GB"))

    def test_exit(self):
        self._run(["0"])

    def test_invalid_choice(self):
        self._run(["9", "0"])
        self.assertEqual(len(self.view.errors), 1)

    # ── 조회 ─────────────────────────────────────────────────────────────
    def test_list_empty(self):
        self._run(["1", "0"])

    def test_list_with_items(self):
        s = self._seed_sample()
        self.inv_repo.save(Inventory(sample_id=s.id, quantity=50))
        self._run(["1", "0"])
        self.assertEqual(len(self.view.shown_lists), 1)

    def test_list_unknown_sample_fallback(self):
        self.inv_repo.save(Inventory(sample_id="GHOST", quantity=10))
        self._run(["1", "0"])

    # ── 등록 ─────────────────────────────────────────────────────────────
    def test_create_no_samples(self):
        self._run(["2", "0"])
        self.assertTrue(any("시료" in e for e in self.view.errors))

    def test_create_invalid_sample_id(self):
        self._seed_sample()
        self._run(["2", "0"], ["INVALID"])
        self.assertEqual(len(self.inv_repo.find_all()), 0)

    def test_create_negative_quantity(self):
        s = self._seed_sample()
        self._run(["2", "0"], [s.id, "-1"])
        self.assertEqual(len(self.inv_repo.find_all()), 0)

    def test_create_non_integer_quantity(self):
        s = self._seed_sample()
        self._run(["2", "0"], [s.id, "abc"])
        self.assertEqual(len(self.inv_repo.find_all()), 0)

    def test_create_valid(self):
        s = self._seed_sample()
        self._run(["2", "0"], [s.id, "100"])
        self.assertEqual(len(self.inv_repo.find_all()), 1)
        self.assertTrue(any("등록" in m for m in self.view.messages))

    def test_create_zero_quantity(self):
        s = self._seed_sample()
        self._run(["2", "0"], [s.id, "0"])
        self.assertEqual(self.inv_repo.find_all()[0].quantity, 0)

    # ── 수량 수정 ─────────────────────────────────────────────────────────
    def test_update_quantity_not_found(self):
        self._run(["3", "0"], ["INVALID"])
        self.assertTrue(any("찾을 수 없" in e for e in self.view.errors))

    def test_update_quantity_valid(self):
        s = self._seed_sample()
        inv = self.inv_repo.save(Inventory(sample_id=s.id, quantity=50))
        self._run(["3", "0"], [inv.id, "200"])
        self.assertEqual(self.inv_repo.find_by_id(inv.id).quantity, 200)

    def test_update_quantity_negative(self):
        s = self._seed_sample()
        inv = self.inv_repo.save(Inventory(sample_id=s.id, quantity=50))
        self._run(["3", "0"], [inv.id, "-10"])
        self.assertTrue(any("0 이상" in e for e in self.view.errors))

    def test_update_quantity_non_integer(self):
        s = self._seed_sample()
        inv = self.inv_repo.save(Inventory(sample_id=s.id, quantity=50))
        self._run(["3", "0"], [inv.id, "abc"])
        self.assertTrue(len(self.view.errors) > 0)


if __name__ == "__main__":
    unittest.main()
