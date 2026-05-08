import unittest
from poc1_mvc.model.entities import (
    Customer, Sample, Order, Inventory, Process,
    OrderStatus, ProcessStage, ProcessStatus,
)
from poc1_mvc.model.repository import InMemoryRepository


class TestEntities(unittest.TestCase):
    def test_customer_defaults(self):
        c = Customer(name="홍길동", company="S-Semi", contact="010-0000-0000")
        self.assertEqual(c.name, "홍길동")
        self.assertEqual(len(c.id), 8)

    def test_sample_defaults(self):
        s = Sample(name="DRAM-A", type="DRAM", specification="16GB DDR5")
        self.assertEqual(s.specification, "16GB DDR5")
        self.assertIsNotNone(s.id)

    def test_order_defaults(self):
        o = Order(customer_id="CID", sample_id="SID", quantity=10)
        self.assertEqual(o.status, OrderStatus.PENDING)
        self.assertIsNotNone(o.created_at)

    def test_inventory_defaults(self):
        inv = Inventory(sample_id="SID", quantity=100)
        self.assertEqual(inv.quantity, 100)

    def test_process_defaults(self):
        p = Process(order_id="OID", stage=ProcessStage.DESIGN)
        self.assertEqual(p.status, ProcessStatus.WAITING)
        self.assertIsNotNone(p.updated_at)

    def test_unique_ids(self):
        c1 = Customer(name="A", company="B", contact="C")
        c2 = Customer(name="A", company="B", contact="C")
        self.assertNotEqual(c1.id, c2.id)

    def test_order_status_enum(self):
        self.assertEqual(OrderStatus.PENDING.value, "대기")
        self.assertEqual(OrderStatus.IN_PROGRESS.value, "진행중")
        self.assertEqual(OrderStatus.COMPLETED.value, "완료")
        self.assertEqual(OrderStatus.CANCELLED.value, "취소")

    def test_process_stage_enum(self):
        self.assertEqual(ProcessStage.DESIGN.value, "설계")
        self.assertEqual(ProcessStage.FABRICATION.value, "제조")
        self.assertEqual(ProcessStage.TESTING.value, "검사")
        self.assertEqual(ProcessStage.DELIVERY.value, "납품")

    def test_process_status_enum(self):
        self.assertEqual(ProcessStatus.WAITING.value, "대기")
        self.assertEqual(ProcessStatus.IN_PROGRESS.value, "진행중")
        self.assertEqual(ProcessStatus.COMPLETED.value, "완료")


class TestInMemoryRepository(unittest.TestCase):
    def setUp(self):
        self.repo: InMemoryRepository[Customer] = InMemoryRepository()
        self.c1 = Customer(name="고객A", company="A사", contact="010-1111-1111")
        self.c2 = Customer(name="고객B", company="B사", contact="010-2222-2222")

    def test_find_all_empty(self):
        self.assertEqual(self.repo.find_all(), [])

    def test_save_and_find_all(self):
        self.repo.save(self.c1)
        self.repo.save(self.c2)
        result = self.repo.find_all()
        self.assertEqual(len(result), 2)

    def test_find_by_id_found(self):
        self.repo.save(self.c1)
        found = self.repo.find_by_id(self.c1.id)
        self.assertEqual(found, self.c1)

    def test_find_by_id_not_found(self):
        self.assertIsNone(self.repo.find_by_id("NOTEXIST"))

    def test_update_existing(self):
        self.repo.save(self.c1)
        self.c1.name = "수정된이름"
        result = self.repo.update(self.c1)
        self.assertIsNotNone(result)
        self.assertEqual(self.repo.find_by_id(self.c1.id).name, "수정된이름")

    def test_update_not_existing(self):
        result = self.repo.update(self.c1)
        self.assertIsNone(result)

    def test_delete_existing(self):
        self.repo.save(self.c1)
        self.assertTrue(self.repo.delete(self.c1.id))
        self.assertIsNone(self.repo.find_by_id(self.c1.id))

    def test_delete_not_existing(self):
        self.assertFalse(self.repo.delete("NOTEXIST"))


if __name__ == "__main__":
    unittest.main()
