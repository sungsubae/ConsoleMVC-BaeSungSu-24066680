import pytest
from poc1_mvc.model.entities import Sample
from poc1_mvc.model.repository import InMemoryRepository
from poc1_mvc.controller.sample_controller import SampleController
from tests.helpers import MockView


# ── Fixtures ───────────────────────────────────────────────────────────────
@pytest.fixture
def repo():
    return InMemoryRepository()


@pytest.fixture
def view():
    return MockView()


@pytest.fixture
def ctrl(repo, view):
    return SampleController(repo, view)


@pytest.fixture
def run(ctrl, view):
    def _inner(choices: list[str], inputs: list[str] | None = None):
        view.push_choices(*choices)
        if inputs:
            view.push_inputs(*inputs)
        ctrl.handle()
    return _inner


# ── 메뉴 라우팅 ────────────────────────────────────────────────────────────
def test_exit(run, view):
    run(["0"])
    assert len(view.errors) == 0


def test_invalid_choice(run, view):
    run(["7", "0"])
    assert len(view.errors) == 1


# ── 목록 ──────────────────────────────────────────────────────────────────
def test_list_empty(run, view):
    run(["1", "0"])
    assert len(view.shown_lists) == 1


def test_list_with_items(run, view, repo):
    repo.save(Sample(name="S1", type="DRAM", specification="16GB"))
    run(["1", "0"])
    assert len(view.shown_lists) == 1


# ── 등록 ──────────────────────────────────────────────────────────────────
def test_create_valid(run, view, repo):
    run(["2", "0"], ["NAND-X", "NAND", "256GB TLC"])
    assert len(repo.find_all()) == 1
    assert any("등록" in m for m in view.messages)


def test_create_missing_name(run, repo):
    run(["2", "0"], ["", "NAND", "256GB"])
    assert len(repo.find_all()) == 0


def test_create_missing_type(run, repo):
    run(["2", "0"], ["NAND-X", "", "256GB"])
    assert len(repo.find_all()) == 0


def test_create_missing_spec(run, repo):
    run(["2", "0"], ["NAND-X", "NAND", ""])
    assert len(repo.find_all()) == 0


# ── 수정 ──────────────────────────────────────────────────────────────────
def test_update_not_found(run, view):
    run(["3", "0"], ["INVALID"])
    assert any("찾을 수 없" in e for e in view.errors)


def test_update_all_fields(run, repo):
    s = repo.save(Sample(name="OLD", type="DRAM", specification="8GB"))
    run(["3", "0"], [s.id, "NEW", "NAND", "16GB"])
    updated = repo.find_by_id(s.id)
    assert updated.name == "NEW"
    assert updated.type == "NAND"
    assert updated.specification == "16GB"


def test_update_keep_empty_fields(run, repo):
    s = repo.save(Sample(name="OLD", type="DRAM", specification="8GB"))
    run(["3", "0"], [s.id, "", "", ""])
    updated = repo.find_by_id(s.id)
    assert updated.name == "OLD"
    assert updated.type == "DRAM"
    assert updated.specification == "8GB"


# ── 삭제 ──────────────────────────────────────────────────────────────────
def test_delete_valid(run, repo):
    s = repo.save(Sample(name="S1", type="DRAM", specification="8GB"))
    run(["4", "0"], [s.id])
    assert repo.find_by_id(s.id) is None


def test_delete_not_found(run, view):
    run(["4", "0"], ["INVALID"])
    assert any("찾을 수 없" in e for e in view.errors)
