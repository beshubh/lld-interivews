"""
Concurrency and locks
"""

import threading


class TicketBookingCoarseGrainedLocks:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._seat_locks = {}
        self._seat_owners = {}

    def book(self, seat_id: str, visitor_id: str) -> bool:
        with self._lock:
            if seat_id not in self._seat_owners:
                # here some other thread can book the same seat
                self._seat_owners[seat_id] = visitor_id
                return True
        return False


class TicketBookingFineGrainedLocks:
    def __init__(self) -> None:
        self._locks_lock = threading.Lock()
        self._seat_locks = {}
        self._seat_owners = {}

    def _get_lock(self, seat_id: str) -> threading.Lock:
        with self._locks_lock:
            if seat_id not in self._seat_locks:
                self._seat_locks[seat_id] = threading.Lock()
            return self._seat_locks[seat_id]

    def book(self, seat_id: str, visitor_id: str) -> bool:
        with self._get_lock(seat_id):
            if seat_id in self._seat_owners:
                return False
            self._seat_owners[seat_id] = visitor_id
            return True
        return False

    # swap seats (prevent deadlocks)

    def swap_seats(self, seat1: str, visitor1: str, seat2: str, visitor2: str):

        if seat1 > seat2:
            seat1, seat2 = seat2, seat1

        with self._get_lock(seat1):
            with self._get_lock(seat2):
                # perform swap
                pass
