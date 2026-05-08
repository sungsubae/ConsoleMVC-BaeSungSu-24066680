from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


def _new_id() -> str:
    return str(uuid.uuid4())[:8].upper()


class OrderStatus(Enum):
    PENDING = "대기"
    IN_PROGRESS = "진행중"
    COMPLETED = "완료"
    CANCELLED = "취소"


class ProcessStage(Enum):
    DESIGN = "설계"
    FABRICATION = "제조"
    TESTING = "검사"
    DELIVERY = "납품"


class ProcessStatus(Enum):
    WAITING = "대기"
    IN_PROGRESS = "진행중"
    COMPLETED = "완료"


@dataclass
class Customer:
    name: str
    company: str
    contact: str
    id: str = field(default_factory=_new_id)


@dataclass
class Sample:
    name: str
    type: str
    specification: str
    id: str = field(default_factory=_new_id)


@dataclass
class Order:
    customer_id: str
    sample_id: str
    quantity: int
    id: str = field(default_factory=_new_id)
    status: OrderStatus = field(default=OrderStatus.PENDING)
    created_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


@dataclass
class Inventory:
    sample_id: str
    quantity: int
    id: str = field(default_factory=_new_id)


@dataclass
class Process:
    order_id: str
    stage: ProcessStage
    id: str = field(default_factory=_new_id)
    status: ProcessStatus = field(default=ProcessStatus.WAITING)
    updated_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
