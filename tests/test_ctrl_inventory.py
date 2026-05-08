import pytest
from poc1_mvc.model.entities import Sample, Inventory
from poc1_mvc.model.repository import InMemoryRepository
from poc1_mvc.controller.inventory_controller import InventoryController
from tests.helpers import MockView


# ── Fixtures ───────────────────────────────────────────────────────────────
@pytest.fixture
def inv_repo():
    return InMemoryRepository()


@pytest.fixture
def sample_repo():
    return InMemoryRepository()


@pytest.fixture
def view():
    return MockView()


@pytest.fixture
def ctrl(inv_repo, sample_repo, view):
    return InventoryController(inv_repo, sample_repo, view)


@pytest.fixture
def run(ctrl, view):
    def _inner(choices: list[str], inputs: list[str] | None = None):
        view.push_choices(*choices)
        if inputs:
            view.push_inputs(*inputs)
        ctrl.handle()
    return _inner


@pytest.fixture
def sample(sample_repo):
    return sample_repo.save(Sample(name="DRAM-A", type="DRAM", specification="16GB"))


# ── 메뉴 라우팅 ────────────────────────────────────────────────────────────
def test_exit(run):
    run(["0"])


def test_invalid_choice(run, view):
    run(["9", "0"])
    assert len(view.errors) == 1


# ── 조회 ──────────────────────────────────────────────────────────────────
def test_list_empty(run):
    run(["1", "0"])


def test_list_with_items(run, view, sample, inv_repo):
    inv_repo.save(Inventory(sample_id=sample.id, quantity=50))
    run(["1", "0"])
    assert len(view.shown_lists) == 1


def test_list_unknown_sample_fallback(run, inv_repo):
    inv_repo.save(Inventory(sample_id="GHOST", quantity=10))
    run(["1", "0"])


# ── 등록 ──────────────────────────────────────────────────────────────────
def test_create_no_samples(run, view):
    run(["2", "0"])
    assert any("시료" in e for e in view.errors)


def test_create_invalid_sample_id(run, inv_repo, sample):
    run(["2", "0"], ["INVALID"])
    assert len(inv_repo.find_all()) == 0


def test_create_negative_quantity(run, inv_repo, sample):
    run(["2", "0"], [sample.id, "-1"])
    assert len(inv_repo.find_all()) == 0


def test_create_non_integer_quantity(run, inv_repo, sample):
    run(["2", "0"], [sample.id, "abc"])
    assert len(inv_repo.find_all()) == 0


def test_create_valid(run, view, inv_repo, sample):
    run(["2", "0"], [sample.id, "100"])
    assert len(inv_repo.find_all()) == 1
    assert any("등록" in m for m in view.messages)


def test_create_zero_quantity(run, inv_repo, sample):
    run(["2", "0"], [sample.id, "0"])
    assert inv_repo.find_all()[0].quantity == 0


# ── 수량 수정 ──────────────────────────────────────────────────────────────
def test_update_quantity_not_found(run, view):
    run(["3", "0"], ["INVALID"])
    assert any("찾을 수 없" in e for e in view.errors)


def test_update_quantity_valid(run, inv_repo, sample):
    inv = inv_repo.save(Inventory(sample_id=sample.id, quantity=50))
    run(["3", "0"], [inv.id, "200"])
    assert inv_repo.find_by_id(inv.id).quantity == 200


def test_update_quantity_negative(run, view, inv_repo, sample):
    inv = inv_repo.save(Inventory(sample_id=sample.id, quantity=50))
    run(["3", "0"], [inv.id, "-10"])
    assert any("0 이상" in e for e in view.errors)


def test_update_quantity_non_integer(run, view, inv_repo, sample):
    inv = inv_repo.save(Inventory(sample_id=sample.id, quantity=50))
    run(["3", "0"], [inv.id, "abc"])
    assert len(view.errors) > 0
