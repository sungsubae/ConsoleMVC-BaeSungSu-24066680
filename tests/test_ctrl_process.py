import unittest
from poc1_mvc.model.entities import Order, Process, ProcessStage, ProcessStatus
from poc1_mvc.model.repository import InMemoryRepository
from poc1_mvc.controller.process_controller import ProcessController
from tests.helpers import MockView


class TestProcessController(unittest.TestCase):
    def setUp(self):
        self.process_repo: InMemoryRepository[Process] = InMemoryRepository()
        self.order_repo: InMemoryRepository[Order] = InMemoryRepository()
        self.view = MockView()
        self.ctrl = ProcessController(self.process_repo, self.order_repo, self.view)

    def _run(self, choices: list[str], inputs: list[str] | None = None):
        self.view.push_choices(*choices)
        if inputs:
            self.view.push_inputs(*inputs)
        self.ctrl.handle()

    def _seed(self) -> Process:
        return self.process_repo.save(
            Process(order_id="ORDER-01", stage=ProcessStage.DESIGN)
        )

    def test_exit(self):
        self._run(["0"])

    def test_invalid_choice(self):
        self._run(["9", "0"])
        self.assertEqual(len(self.view.errors), 1)

    # ── 조회 ─────────────────────────────────────────────────────────────
    def test_list_empty(self):
        self._run(["1", "0"])

    def test_list_with_items(self):
        self._seed()
        self._run(["1", "0"])
        self.assertEqual(len(self.view.shown_lists), 1)

    # ── 단계 변경 ─────────────────────────────────────────────────────────
    def test_update_stage_not_found(self):
        self._run(["2", "0"], ["INVALID"])
        self.assertTrue(any("찾을 수 없" in e for e in self.view.errors))

    def test_update_stage_valid(self):
        p = self._seed()
        self._run(["2", "0"], [p.id, "2"])  # "2" → FABRICATION
        updated = self.process_repo.find_by_id(p.id)
        self.assertEqual(updated.stage, ProcessStage.FABRICATION)

    def test_update_stage_invalid_text(self):
        p = self._seed()
        self._run(["2", "0"], [p.id, "xyz"])
        self.assertTrue(any("잘못" in e for e in self.view.errors))

    def test_update_stage_out_of_range(self):
        p = self._seed()
        self._run(["2", "0"], [p.id, "99"])
        self.assertTrue(any("잘못" in e for e in self.view.errors))

    # ── 상태 변경 ─────────────────────────────────────────────────────────
    def test_update_status_not_found(self):
        self._run(["3", "0"], ["INVALID"])
        self.assertTrue(any("찾을 수 없" in e for e in self.view.errors))

    def test_update_status_valid(self):
        p = self._seed()
        self._run(["3", "0"], [p.id, "2"])  # "2" → IN_PROGRESS
        updated = self.process_repo.find_by_id(p.id)
        self.assertEqual(updated.status, ProcessStatus.IN_PROGRESS)

    def test_update_status_invalid_text(self):
        p = self._seed()
        self._run(["3", "0"], [p.id, "abc"])
        self.assertTrue(any("잘못" in e for e in self.view.errors))

    def test_update_status_out_of_range(self):
        p = self._seed()
        self._run(["3", "0"], [p.id, "99"])
        self.assertTrue(any("잘못" in e for e in self.view.errors))


if __name__ == "__main__":
    unittest.main()
