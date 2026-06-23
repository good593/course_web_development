from datetime import datetime


class UserDB:
    def __init__(self):
        self._data: dict[int, dict] = {
            1: {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com",
                "password_hash": "hashed_pw",
                "age": 30,
                "role": "admin",
                "active": True,
                "created_at": datetime(2024, 1, 1),
            }
        }
        self._next_id = 2

    def email_exists(self, email: str) -> bool:
        return any(user["email"] == email for user in self._data.values())

    def username_exists(self, username: str, exclude_user_id: int | None = None) -> bool:
        return any(
            user["username"] == username and user["id"] != exclude_user_id
            for user in self._data.values()
        )

    def create(self, user_data: dict) -> dict:
        user = {
            "id": self._next_id,
            "username": user_data["username"],
            "email": user_data["email"],
            "password_hash": f"hashed_{user_data['password']}",
            "age": user_data["age"],
            "role": user_data["role"],
            "active": True,
            "created_at": datetime.now(),
        }
        self._data[self._next_id] = user
        self._next_id += 1
        return user

    def get_all(self) -> list[dict]:
        return list(self._data.values())

    def get_by_id(self, user_id: int) -> dict | None:
        return self._data.get(user_id)

    def update(self, user_id: int, update_data: dict) -> dict | None:
        user = self.get_by_id(user_id)
        if not user:
            return None

        user.update(update_data)
        return user

    def delete(self, user_id: int) -> bool:
        if user_id not in self._data:
            return False

        del self._data[user_id]
        return True

    def deactivate(self, user_id: int) -> dict | None:
        user = self.get_by_id(user_id)
        if not user:
            return None

        user["active"] = False
        return user


# 애플리케이션 전체에서 공유하는 인스턴스
user_db = UserDB()
