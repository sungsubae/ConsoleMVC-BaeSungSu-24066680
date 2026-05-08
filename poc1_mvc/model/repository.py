from typing import TypeVar, Generic
from .interfaces import IRepository

T = TypeVar("T")


class InMemoryRepository(IRepository[T], Generic[T]):
    def __init__(self) -> None:
        self._store: dict[str, T] = {}

    def find_all(self) -> list[T]:
        return list(self._store.values())

    def find_by_id(self, id: str) -> T | None:
        return self._store.get(id)

    def save(self, entity: T) -> T:
        self._store[entity.id] = entity  # type: ignore[attr-defined]
        return entity

    def update(self, entity: T) -> T | None:
        if entity.id not in self._store:  # type: ignore[attr-defined]
            return None
        self._store[entity.id] = entity  # type: ignore[attr-defined]
        return entity

    def delete(self, id: str) -> bool:
        if id in self._store:
            del self._store[id]
            return True
        return False
