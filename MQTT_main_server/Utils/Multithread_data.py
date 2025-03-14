from typing import Generic, TypeVar
import threading

T = TypeVar("T")  # Обобщённый тип

class Shared_data(Generic[T]):
    def __init__(self, value: T):
        self.value = value
        self.lock = threading.Lock()
        self.updated = threading.Event()

    def read_value(self) -> T:
        print("Try to read")
        self.updated.wait()  # Ждём изменения
        with self.lock:
            value = self.value
        self.updated.clear()  # Сбрасываем флаг
        return value

    def write_value(self, new_value : T):
        print("Try to write")
        with self.lock:
            self.value = new_value
        self.updated.set()  # Сообщаем, что данные обновились
