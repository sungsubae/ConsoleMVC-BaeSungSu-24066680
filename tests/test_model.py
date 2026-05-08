import pytest
from poc1_mvc.model.entities import (
    Customer, Sample, Order, Inventory, Process,
    OrderStatus, ProcessStage, ProcessStatus,
)
from poc1_mvc.model.repository import InMemoryRepository


# ── Fixtures ───────────────────────────────────────────────────────────────
@pytest.fixture
def repo():
    return InMemoryRepository()


@pytest.fixture
def c1():
    return Customer(name="고객A", company="A사", contact="010-1111-1111")


@pytest.fixture
def c2():
    return Customer(name="고객B", company="B사", contact="010-2222-2222")


# ── 엔티티 기본값 ──────────────────────────────────────────────────────────
def test_customer_defaults():
    c = Customer(name="홍길동", company="S-Semi", contact="010-0000-0000")
    assert c.name == "홍길동"
    assert len(c.id) == 8


def test_sample_defaults():
    s = Sample(name="DRAM-A", type="DRAM", specification="16GB DDR5")
    assert s.specification == "16GB DDR5"
    assert s.id is not None


def test_order_defaults():
    o = Order(customer_id="CID", sample_id="SID", quantity=10)
    assert o.status == OrderStatus.PENDING
    assert o.created_at is not None


def test_inventory_defaults():
    inv = Inventory(sample_id="SID", quantity=100)
    assert inv.quantity == 100


def test_process_defaults():
    p = Process(order_id="OID", stage=ProcessStage.DESIGN)
    assert p.status == ProcessStatus.WAITING
    assert p.updated_at is not None


def test_unique_ids():
    c1 = Customer(name="A", company="B", contact="C")
    c2 = Customer(name="A", company="B", contact="C")
    assert c1.id != c2.id


# ── Enum 값 검증 ────────────────────────────────────────────────────────────
def test_order_status_enum():
    assert OrderStatus.PENDING.value == "대기"
    assert OrderStatus.IN_PROGRESS.value == "진행중"
    assert OrderStatus.COMPLETED.value == "완료"
    assert OrderStatus.CANCELLED.value == "취소"


def test_process_stage_enum():
    assert ProcessStage.DESIGN.value == "설계"
    assert ProcessStage.FABRICATION.value == "제조"
    assert ProcessStage.TESTING.value == "검사"
    assert ProcessStage.DELIVERY.value == "납품"


def test_process_status_enum():
    assert ProcessStatus.WAITING.value == "대기"
    assert ProcessStatus.IN_PROGRESS.value == "진행중"
    assert ProcessStatus.COMPLETED.value == "완료"


# ── InMemoryRepository ─────────────────────────────────────────────────────
def test_find_all_empty(repo):
    assert repo.find_all() == []


def test_save_and_find_all(repo, c1, c2):
    repo.save(c1)
    repo.save(c2)
    assert len(repo.find_all()) == 2


def test_find_by_id_found(repo, c1):
    repo.save(c1)
    assert repo.find_by_id(c1.id) == c1


def test_find_by_id_not_found(repo):
    assert repo.find_by_id("NOTEXIST") is None


def test_update_existing(repo, c1):
    repo.save(c1)
    c1.name = "수정된이름"
    assert repo.update(c1) is not None
    assert repo.find_by_id(c1.id).name == "수정된이름"


def test_update_not_existing(repo, c1):
    assert repo.update(c1) is None


def test_delete_existing(repo, c1):
    repo.save(c1)
    assert repo.delete(c1.id) is True
    assert repo.find_by_id(c1.id) is None


def test_delete_not_existing(repo):
    assert repo.delete("NOTEXIST") is False
