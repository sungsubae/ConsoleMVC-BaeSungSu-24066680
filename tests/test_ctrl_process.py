import pytest
from poc1_mvc.model.entities import Order, Process, ProcessStage, ProcessStatus
from poc1_mvc.model.repository import InMemoryRepository
from poc1_mvc.controller.process_controller import ProcessController
from tests.helpers import MockView


# ── Fixtures ───────────────────────────────────────────────────────────────
@pytest.fixture
def process_repo():
    return InMemoryRepository()


@pytest.fixture
def order_repo():
    return InMemoryRepository()


@pytest.fixture
def view():
    return MockView()


@pytest.fixture
def ctrl(process_repo, order_repo, view):
    return ProcessController(process_repo, order_repo, view)


@pytest.fixture
def run(ctrl, view):
    def _inner(choices: list[str], inputs: list[str] | None = None):
        view.push_choices(*choices)
        if inputs:
            view.push_inputs(*inputs)
        ctrl.handle()
    return _inner


@pytest.fixture
def process(process_repo):
    return process_repo.save(Process(order_id="ORDER-01", stage=ProcessStage.DESIGN))


# ── 메뉴 라우팅 ────────────────────────────────────────────────────────────
def test_exit(run):
    run(["0"])


def test_invalid_choice(run, view):
    run(["9", "0"])
    assert len(view.errors) == 1


# ── 조회 ──────────────────────────────────────────────────────────────────
def test_list_empty(run):
    run(["1", "0"])


def test_list_with_items(run, view, process):
    run(["1", "0"])
    assert len(view.shown_lists) == 1


# ── 단계 변경 ──────────────────────────────────────────────────────────────
def test_update_stage_not_found(run, view):
    run(["2", "0"], ["INVALID"])
    assert any("찾을 수 없" in e for e in view.errors)


def test_update_stage_valid(run, process_repo, process):
    run(["2", "0"], [process.id, "2"])  # "2" → FABRICATION
    assert process_repo.find_by_id(process.id).stage == ProcessStage.FABRICATION


def test_update_stage_invalid_text(run, view, process):
    run(["2", "0"], [process.id, "xyz"])
    assert any("잘못" in e for e in view.errors)


def test_update_stage_out_of_range(run, view, process):
    run(["2", "0"], [process.id, "99"])
    assert any("잘못" in e for e in view.errors)


# ── 상태 변경 ──────────────────────────────────────────────────────────────
def test_update_status_not_found(run, view):
    run(["3", "0"], ["INVALID"])
    assert any("찾을 수 없" in e for e in view.errors)


def test_update_status_valid(run, process_repo, process):
    run(["3", "0"], [process.id, "2"])  # "2" → IN_PROGRESS
    assert process_repo.find_by_id(process.id).status == ProcessStatus.IN_PROGRESS


def test_update_status_invalid_text(run, view, process):
    run(["3", "0"], [process.id, "abc"])
    assert any("잘못" in e for e in view.errors)


def test_update_status_out_of_range(run, view, process):
    run(["3", "0"], [process.id, "99"])
    assert any("잘못" in e for e in view.errors)
