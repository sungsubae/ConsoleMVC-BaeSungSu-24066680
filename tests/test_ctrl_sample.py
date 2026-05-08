import unittest
from poc1_mvc.model.entities import Sample
from poc1_mvc.model.repository import InMemoryRepository
from poc1_mvc.controller.sample_controller import SampleController
from tests.helpers import MockView


class TestSampleController(unittest.TestCase):
    def setUp(self):
        self.repo: InMemoryRepository[Sample] = InMemoryRepository()
        self.view = MockView()
        self.ctrl = SampleController(self.repo, self.view)

    def _run(self, choices: list[str], inputs: list[str] | None = None):
        self.view.push_choices(*choices)
        if inputs:
            self.view.push_inputs(*inputs)
        self.ctrl.handle()

    def test_exit(self):
        self._run(["0"])
        self.assertEqual(len(self.view.errors), 0)

    def test_invalid_choice(self):
        self._run(["7", "0"])
        self.assertEqual(len(self.view.errors), 1)

    def test_list_empty(self):
        self._run(["1", "0"])
        self.assertEqual(len(self.view.shown_lists), 1)

    def test_list_with_items(self):
        self.repo.save(Sample(name="S1", type="DRAM", specification="16GB"))
        self._run(["1", "0"])
        self.assertEqual(len(self.view.shown_lists), 1)

    def test_create_valid(self):
        self._run(["2", "0"], ["NAND-X", "NAND", "256GB TLC"])
        self.assertEqual(len(self.repo.find_all()), 1)
        self.assertTrue(any("등록" in m for m in self.view.messages))

    def test_create_missing_name(self):
        self._run(["2", "0"], ["", "NAND", "256GB"])
        self.assertEqual(len(self.repo.find_all()), 0)

    def test_create_missing_type(self):
        self._run(["2", "0"], ["NAND-X", "", "256GB"])
        self.assertEqual(len(self.repo.find_all()), 0)

    def test_create_missing_spec(self):
        self._run(["2", "0"], ["NAND-X", "NAND", ""])
        self.assertEqual(len(self.repo.find_all()), 0)

    def test_update_not_found(self):
        self._run(["3", "0"], ["INVALID"])
        self.assertTrue(any("찾을 수 없" in e for e in self.view.errors))

    def test_update_all_fields(self):
        s = self.repo.save(Sample(name="OLD", type="DRAM", specification="8GB"))
        self._run(["3", "0"], [s.id, "NEW", "NAND", "16GB"])
        updated = self.repo.find_by_id(s.id)
        self.assertEqual(updated.name, "NEW")
        self.assertEqual(updated.type, "NAND")
        self.assertEqual(updated.specification, "16GB")

    def test_update_keep_empty_fields(self):
        s = self.repo.save(Sample(name="OLD", type="DRAM", specification="8GB"))
        self._run(["3", "0"], [s.id, "", "", ""])
        updated = self.repo.find_by_id(s.id)
        self.assertEqual(updated.name, "OLD")
        self.assertEqual(updated.type, "DRAM")
        self.assertEqual(updated.specification, "8GB")

    def test_delete_valid(self):
        s = self.repo.save(Sample(name="S1", type="DRAM", specification="8GB"))
        self._run(["4", "0"], [s.id])
        self.assertIsNone(self.repo.find_by_id(s.id))

    def test_delete_not_found(self):
        self._run(["4", "0"], ["INVALID"])
        self.assertTrue(any("찾을 수 없" in e for e in self.view.errors))


if __name__ == "__main__":
    unittest.main()
