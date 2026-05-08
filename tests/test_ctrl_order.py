import pytest
from poc1_mvc.model.entities import Customer, Sample, Order, Process, OrderStatus
from poc1_mvc.model.repository import InMemoryRepository
from poc1_mvc.controller.order_controller import OrderController
from tests.helpers import MockView


# ── Fixtures ───────────────────────────────────────────────────────────────
@pytest.fixture
def orders():
    return InMemoryRepository()


@pytest.fixture
def customers():
    return InMemoryRepository()


@pytest.fixture
def samples():
    return InMemoryRepository()


@pytest.fixture
def processes():
    return InMemoryRepository()


@pytest.fixture
def view():
    return MockView()


@pytest.fixture
def ctrl(orders, customers, samples, processes, view):
    return OrderController(orders, customers, samples, processes, view)


@pytest.fixture
def run(ctrl, view):
    def _inner(choices: list[str], inputs: list[str] | None = None):
        view.push_choices(*choices)
        if inputs:
            view.push_inputs(*inputs)
        ctrl.handle()
    return _inner


@pytest.fixture
def seeded(customers, samples):
    """고객 1명 + 시료 1개를 미리 저장한다."""
    c = customers.save(Customer(name="고객A", company="A사", contact="010"))
    s = samples.save(Sample(name="DRAM-A", type="DRAM", specification="16GB"))
    return c, s


# ── 메뉴 라우팅 ────────────────────────────────────────────────────────────
def test_exit(run):
    run(["0"])


def test_invalid_choice(run, view):
    run(["9", "0"])
    assert len(view.errors) == 1


# ── 목록 ──────────────────────────────────────────────────────────────────
def test_list_empty(run):
    run(["1", "0"])


def test_list_with_items_shows_names(run, view, seeded, orders):
    c, s = seeded
    orders.save(Order(customer_id=c.id, sample_id=s.id, quantity=5))
    run(["1", "0"])
    assert len(view.shown_lists) == 1


def test_list_unknown_ids_fallback_to_id(run, orders):
    orders.save(Order(customer_id="GHOST_C", sample_id="GHOST_S", quantity=1))
    run(["1", "0"])


# ── 등록 — 사전 조건 실패 ─────────────────────────────────────────────────
def test_create_no_customers(run, view):
    run(["2", "0"])
    assert any("고객" in e for e in view.errors)


def test_create_no_samples(run, view, customers):
    customers.save(Customer(name="A", company="B", contact="C"))
    run(["2", "0"])
    assert any("시료" in e for e in view.errors)


# ── 등록 — 유효성 실패 ───────────────────────────────────────────────────
def test_create_invalid_customer_id(run, view, seeded):
    run(["2", "0"], ["INVALID_CID"])
    assert any("고객" in e for e in view.errors)


def test_create_invalid_sample_id(run, view, seeded):
    c, _ = seeded
    run(["2", "0"], [c.id, "INVALID_SID"])
    assert any("시료" in e for e in view.errors)


def test_create_quantity_not_integer(run, orders, seeded):
    c, s = seeded
    run(["2", "0"], [c.id, s.id, "abc"])
    assert len(orders.find_all()) == 0


def test_create_quantity_zero(run, orders, seeded):
    c, s = seeded
    run(["2", "0"], [c.id, s.id, "0"])
    assert len(orders.find_all()) == 0


def test_create_quantity_negative(run, orders, seeded):
    c, s = seeded
    run(["2", "0"], [c.id, s.id, "-5"])
    assert len(orders.find_all()) == 0


# ── 등록 — 정상 ──────────────────────────────────────────────────────────
def test_create_valid(run, view, seeded, orders, processes):
    c, s = seeded
    run(["2", "0"], [c.id, s.id, "10"])
    assert len(orders.find_all()) == 1
    assert len(processes.find_all()) == 1  # 공정 레코드 자동 생성
    assert any("등록" in m for m in view.messages)


# ── 상태 변경 ──────────────────────────────────────────────────────────────
def test_update_status_not_found(run, view):
    run(["3", "0"], ["INVALID"])
    assert any("찾을 수 없" in e for e in view.errors)


def test_update_status_valid(run, seeded, orders):
    c, s = seeded
    o = orders.save(Order(customer_id=c.id, sample_id=s.id, quantity=5))
    run(["3", "0"], [o.id, "2"])  # "2" → IN_PROGRESS
    assert orders.find_by_id(o.id).status == OrderStatus.IN_PROGRESS


def test_update_status_invalid_choice_text(run, view, seeded, orders):
    c, s = seeded
    o = orders.save(Order(customer_id=c.id, sample_id=s.id, quantity=5))
    run(["3", "0"], [o.id, "abc"])
    assert any("잘못" in e for e in view.errors)


def test_update_status_out_of_range(run, view, seeded, orders):
    c, s = seeded
    o = orders.save(Order(customer_id=c.id, sample_id=s.id, quantity=5))
    run(["3", "0"], [o.id, "99"])
    assert any("잘못" in e for e in view.errors)


# ── 삭제 ──────────────────────────────────────────────────────────────────
def test_delete_valid(run, seeded, orders):
    c, s = seeded
    o = orders.save(Order(customer_id=c.id, sample_id=s.id, quantity=5))
    run(["4", "0"], [o.id])
    assert orders.find_by_id(o.id) is None


def test_delete_not_found(run, view):
    run(["4", "0"], ["INVALID"])
    assert any("찾을 수 없" in e for e in view.errors)
