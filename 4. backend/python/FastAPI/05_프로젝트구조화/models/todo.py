from datetime import datetime


class TodoDB:
    def __init__(self):
        self._data: dict[int, dict] = {}
        self._next_id = 1

    def create(self, title: str, description: str | None, priority: int) -> dict:
        todo = {
            "id": self._next_id,
            "title": title,
            "description": description,
            "priority": priority,
            "completed": False,
            "created_at": datetime.now(),
        }
        self._data[self._next_id] = todo
        self._next_id += 1
        return todo

    def get_all(self, skip: int = 0, limit: int = 10) -> list[dict]:
        items = list(self._data.values())
        return items[skip : skip + limit]

    def get_by_id(self, todo_id: int) -> dict | None:
        return self._data.get(todo_id)

    def count(self) -> int:
        return len(self._data)


# 애플리케이션 전체에서 공유하는 인스턴스
todo_db = TodoDB()
