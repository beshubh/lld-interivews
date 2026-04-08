"""
Scarcity in concurrent systems
"""

import threading
from pathlib import Path
import queue

# Semaphores


# let's say some resource only accepts 5 concurrent requests at a time
class APIClient:
    def __init__(self) -> None:
        self._semaphore = threading.Semaphore(5)

    def make_request(self, endpoint: str):
        try:
            self._semaphore.acquire()
            self._http_client.get(endpoint)
        finally:
            self._semaphore.release()
        # or
        with self._semaphore:
            self._http_client.get(endpoint)


# resource pooling, for when you need to limit the usage but also need to hand out a actual object for usage


class ConnectionPool:
    def __init__(self, limit: int = 10) -> None:
        self._q = queue.Queue(limit)
        for _ in range(limit):
            self._q.put(self._create_connection())

    def _create_connection(self):
        pass

    def acquire(self):
        return self._q.get()  # waits if queue is empty

    def release(self, conn):
        self._q.put(conn)

    def execute_query(self, query: str):
        conn = self.acquire()
        try:
            res = conn.execute(query)
            return res
        finally:
            self.release(conn)


class ConnectionPoolWithTimeout:
    def __init__(self, limit: int = 10, timeout_s: float = 0.5) -> None:
        self._q = queue.Queue(limit)
        self._timeout_s = timeout_s
        for _ in range(limit):
            self._q.put(self._create_connection())

    def _create_connection(self):
        pass

    def acquire(self):
        try:
            self._q.get(timeout=self._timeout_s)  # waits if queue is empty
        except queue.Empty:
            raise RuntimeError(f"No connection available within {self._timeout_s}s")

    def release(self, conn):
        self._q.put(conn)

    def execute_query(self, query: str):
        conn = self.acquire()
        try:
            res = conn.execute(query)
            return res
        finally:
            self.release(conn)


class DownloadManager:
    def __init__(self) -> None:
        self._semaphore = threading.Semaphore(10)

    def download(self, url, destination):
        with self._semaphore:
            data = self._http_client.download(url)
            destination.write_bytes(data)


class DiskWriter:
    MB = 1024 * 1024

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
        self._available = 100

    def write_file(self, data: bytes, path: Path):
        permits = max(1, (len(data) + self.MB - 1) // self.MB)  # MBs
        with self._condition:
            while self._available < permits:
                self._condition.wait()
            self._available -= permits

        try:
            path.write_bytes(data)
        finally:
            with self._condition:
                self._available += permits
                self._condition.notify_all()
