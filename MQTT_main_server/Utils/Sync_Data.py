import threading


class Sync_Data:
    def __init__(self):
            self.value = None
            self.lock = threading.Lock()
            self.updated = threading.Event()

    def read_value(self):
        self.updated.wait()
        with self.lock:
            value = self.value
        self.updated.clear()
        return value

    def write_value(self, new_value):
        with self.lock:
            self.value = new_value
        self.updated.set()
