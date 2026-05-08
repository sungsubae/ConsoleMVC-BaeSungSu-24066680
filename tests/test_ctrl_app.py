import unittest
from unittest.mock import patch, MagicMock
from poc1_mvc.controller.app_controller import AppController
from poc1_mvc.main import main
from tests.helpers import MockView


class TestAppController(unittest.TestCase):
    def setUp(self):
        self.view = MockView()
        self.ctrl = AppController(self.view)

    def _run(self, choices: list[str]):
        self.view.push_choices(*choices)
        self.ctrl.run()

    def test_exit_on_zero(self):
        self._run(["0"])
        self.assertTrue(any("종료" in m for m in self.view.messages))

    def test_invalid_route(self):
        self._run(["9", "0"])
        self.assertEqual(len(self.view.errors), 1)

    def test_route_to_customer(self):
        # "1" → CustomerController.handle() → "0" exits sub, "0" exits app
        self._run(["1", "0", "0"])

    def test_route_to_sample(self):
        self._run(["2", "0", "0"])

    def test_route_to_order(self):
        self._run(["3", "0", "0"])

    def test_route_to_inventory(self):
        self._run(["4", "0", "0"])

    def test_route_to_process(self):
        self._run(["5", "0", "0"])

    def test_multiple_iterations(self):
        # 여러 서브메뉴를 순서대로 방문 후 종료
        self._run(["1", "0", "2", "0", "0"])

    def test_main_entry_point(self):
        with patch("poc1_mvc.main.AppController") as mock_ctrl_cls, \
             patch("poc1_mvc.main.ConsoleView"):
            mock_ctrl = MagicMock()
            mock_ctrl_cls.return_value = mock_ctrl
            main()
            mock_ctrl.run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
