import pytest
from poc1_mvc.model.entities import Customer
from poc1_mvc.model.repository import InMemoryRepository
from poc1_mvc.controller.customer_controller import CustomerController
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
    return CustomerController(repo, view)


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
    run(["9", "0"])
    assert len(view.errors) == 1


# ── 목록 ──────────────────────────────────────────────────────────────────
def test_list_empty(run, view):
    run(["1", "0"])
    assert len(view.shown_lists) == 1


def test_list_with_items(run, view, repo):
    repo.save(Customer(name="A", company="B", contact="C"))
    run(["1", "0"])
    assert len(view.shown_lists) == 1


# ── 등록 ──────────────────────────────────────────────────────────────────
def test_create_valid(run, view, repo):
    run(["2", "0"], ["홍길동", "S-Semi", "010-1234-5678"])
    assert len(repo.find_all()) == 1
    assert any("등록" in m for m in view.messages)


def test_create_missing_name(run, view, repo):
    run(["2", "0"], ["", "S-Semi", "010"])
    assert len(repo.find_all()) == 0
    assert any("입력" in e for e in view.errors)


def test_create_missing_company(run, repo):
    run(["2", "0"], ["홍길동", "", "010"])
    assert len(repo.find_all()) == 0


def test_create_missing_contact(run, repo):
    run(["2", "0"], ["홍길동", "S-Semi", ""])
    assert len(repo.find_all()) == 0


# ── 수정 ──────────────────────────────────────────────────────────────────
def test_update_not_found(run, view):
    run(["3", "0"], ["INVALID"])
    assert any("찾을 수 없" in e for e in view.errors)


def test_update_all_fields(run, repo):
    c = repo.save(Customer(name="A", company="B", contact="C"))
    run(["3", "0"], [c.id, "새이름", "새회사", "새연락처"])
    updated = repo.find_by_id(c.id)
    assert updated.name == "새이름"
    assert updated.company == "새회사"
    assert updated.contact == "새연락처"


def test_update_keep_empty_fields(run, repo):
    c = repo.save(Customer(name="원본이름", company="원본회사", contact="원본연락처"))
    run(["3", "0"], [c.id, "새이름", "", ""])
    updated = repo.find_by_id(c.id)
    assert updated.name == "새이름"
    assert updated.company == "원본회사"
    assert updated.contact == "원본연락처"


# ── 삭제 ──────────────────────────────────────────────────────────────────
def test_delete_valid(run, view, repo):
    c = repo.save(Customer(name="A", company="B", contact="C"))
    run(["4", "0"], [c.id])
    assert repo.find_by_id(c.id) is None
    assert any("삭제" in m for m in view.messages)


def test_delete_not_found(run, view):
    run(["4", "0"], ["INVALID"])
    assert any("찾을 수 없" in e for e in view.errors)
