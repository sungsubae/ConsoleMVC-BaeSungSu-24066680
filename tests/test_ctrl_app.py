from unittest.mock import patch, MagicMock
import pytest
from poc1_mvc.controller.app_controller import AppController
from poc1_mvc.main import main
from tests.helpers import MockView


# ── Fixtures ───────────────────────────────────────────────────────────────
@pytest.fixture
def view():
    return MockView()


@pytest.fixture
def ctrl(view):
    return AppController(view)


@pytest.fixture
def run(ctrl, view):
    def _inner(choices: list[str]):
        view.push_choices(*choices)
        ctrl.run()
    return _inner


# ── 메인 루프 ──────────────────────────────────────────────────────────────
def test_exit_on_zero(run, view):
    run(["0"])
    assert any("종료" in m for m in view.messages)


def test_invalid_route(run, view):
    run(["9", "0"])
    assert len(view.errors) == 1


# ── 서브 컨트롤러 라우팅 ───────────────────────────────────────────────────
def test_route_to_customer(run):
    run(["1", "0", "0"])


def test_route_to_sample(run):
    run(["2", "0", "0"])


def test_route_to_order(run):
    run(["3", "0", "0"])


def test_route_to_inventory(run):
    run(["4", "0", "0"])


def test_route_to_process(run):
    run(["5", "0", "0"])


def test_multiple_iterations(run):
    run(["1", "0", "2", "0", "0"])


# ── main() 진입점 ──────────────────────────────────────────────────────────
def test_main_entry_point():
    with patch("poc1_mvc.main.AppController") as mock_ctrl_cls, \
         patch("poc1_mvc.main.ConsoleView"):
        mock_ctrl = MagicMock()
        mock_ctrl_cls.return_value = mock_ctrl
        main()
        mock_ctrl.run.assert_called_once()
