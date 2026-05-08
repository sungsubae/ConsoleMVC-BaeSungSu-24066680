from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    @abstractmethod
    def find_all(self) -> list[T]: ...

    @abstractmethod
    def find_by_id(self, id: str) -> T | None: ...

    @abstractmethod
    def save(self, entity: T) -> T: ...

    @abstractmethod
    def update(self, entity: T) -> T | None: ...

    @abstractmethod
    def delete(self, id: str) -> bool: ...
