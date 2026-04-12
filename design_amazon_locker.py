# ═══════════════════════════════════════════════════════════════════════════
# REQUIREMENTS
#
# Example (Tic Tac Toe):
#   1. Two players alternate placing X and O on a 3x3 grid.
#   2. A player wins by completing a row, column, or diagonal.
#   Out of Scope: UI, AI opponent, networking
# ═══════════════════════════════════════════════════════════════════════════

#  - Fixed number of compartments in the locker.
#  - Three fixed sizes of compartment: small, medium, large.
#  - Package also has same size: small, medium, large.
#  - Delivery person can deposity the package and get the code.
#  - Users can use this code and take their package out.
#  - AccessCodes expire after 7 days.
#     - Once the code expires, it will be reject if customer tries to use it.
#     - But the package stays in the compartment untill staff manually removes the package.
#  - Staff can open expired compartments manually and empty the compartments.

# Error Handling
#  - System should validate access code (including rejecting expired codes).
#  - Enforce size matching b/w package and compartments at deposit time.
#  - If no compartments for the size are available reject with error.


# ═══════════════════════════════════════════════════════════════════════════
# ENTITIES & RELATIONSHIPS
#
# Example (Tic Tac Toe):
#   Game, Board, Player
# ═══════════════════════════════════════════════════════════════════════════

# - Locker (orchestrator)
# - Compartment
# - AccessCode
# - Size [SMALL, MEDIUM, LARGE]


# ═══════════════════════════════════════════════════════════════════════════
# CLASS DESIGN
#
# Example (Tic Tac Toe):
#   class Game:
#     - board: Board
#     - currentPlayer: Player
#     + makeMove(row, col) -> bool
# ═══════════════════════════════════════════════════════════════════════════


class Locker:
    compartments: list[Compartment]
    access_code_mapping: dict[str, AccessCode]

    def deposit_package(self, size: Size) -> str:
        pass

    def take_package(self, code: str):
        pass

    def _generate_access_code(self, compartment: Compartment) -> AccessCode:
        pass

    def open_expired_compartment(self) -> None:
        pass


class Compartment:
    size: Size
    occupied: bool

    @property
    def occupied(self) -> bool:
        pass

    def open_compartment(self) -> None:
        pass

    def mark_occupied(self) -> None:
        pass

    def mark_free(self) -> None:
        pass


class AccessCode:
    expires_at: int
    code: str
    compartment: Compartment

    def __init__(self, code: str, compartment: Compartment) -> None:
        self._code = code
        self._expires_at = time.now() + timedelta(days=7)
        self._compartment = compartment

    @property
    def code(self) -> str:
        pass

    @property
    def expired(self) -> bool:
        pass

    @property
    def compartment(self) -> Compartment:
        pass


class Size(enum.Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


# ═══════════════════════════════════════════════════════════════════════════
# IMPLEMENTATION
# ═══════════════════════════════════════════════════════════════════════════


class CompartmentNotAvailableError(Exception):
    pass


class InvalidAccessCodeError(Exception):
    pass


class AccessCodeExpiredError(Exception):
    pass


class Locker:
    compartments: list[Compartment]
    access_code_mapping: dict[str, AccessCode]

    def __init__(self, compartments: list[Compartment]) -> None:
        self._compartments = compartments
        self._access_code_mapping = {}

    def deposit_package(self, size: Size) -> str:
        compartment = self._find_available_compartment(size)
        if compartment is None:
            raise CompartmentNotAvailableError("compartment not availabe at the moment")
        compartment.open_compartment()
        compartment.mark_occupied()
        access_code = self._generate_access_code(compartment)
        self._access_code_mapping[access_code.code] = access_code
        return access_code.code

    def _find_available_compartment(self, size: Size) -> Compartment | None:
        for compartment in self._compartments:
            if not compartment.occupied and compartment.size == size:
                return compartment
        return None

    def take_package(self, code: str):
        if len(code) != 6:
            raise InvalidAccessCodeError(f"Malformed code, invalid length: {len(code)}")
        if code not in self._access_code_mapping:
            raise InvalidAccessCodeError(f"Invalid code, not found")

        access_code = self._access_code_mapping[code]
        if access_code.expired:
            raise AccessCodeExpiredError(
                "Access Code expired, this package cannot be taken out"
            )

        compartment = access_code.compartment
        compartment.open_compartment()
        # customer takes out the package
        compartment.mark_free()
        del self._access_code_mapping[code]

    def _generate_access_code(self, compartment: Compartment) -> AccessCode:
        code = generateAlphNumericCode(size=6)
        access_code = AccessCode(code, compartment)
        return access_code

    def open_expired_compartment(self) -> None:
        pass


class Compartment:
    size: Size
    occupied: bool

    def __init__(self, size: Size) -> None:
        self._size = size
        self._occupied = False

    @property
    def occupied(self) -> bool:
        pass

    @property
    def size(self) -> Size:
        return self._size

    def open_compartment(self) -> None:
        pass

    def mark_occupied(self) -> None:
        pass

    def mark_free(self) -> None:
        pass


class AccessCode:
    expires_at: int
    code: str
    compartment: Compartment

    def __init__(self, code: str, compartment: Compartment) -> None:
        self._code = code
        self._expires_at = time.now() + timedelta(days=7)
        self._compartment = compartment

    @property
    def code(self) -> str:
        return self._code

    @property
    def expired(self) -> bool:
        return time.now() > self._expires_at

    @property
    def compartment(self) -> Compartment:
        return self._compartment


class Size(enum.Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


# ═══════════════════════════════════════════════════════════════════════════
# EXTENSIBILITY
# ═══════════════════════════════════════════════════════════════════════════

import threading
import enum


class LockerError(Exception):
    pass


class Locker:
    compartments: list[Compartment]
    access_code_mapping: dict[str, AccessCode]

    def __init__(self, compartments: list[Compartment]) -> None:
        self._compartments = compartments
        self._access_code_mapping = {}
        # Single lock covers both the scan and the reservation atomically,
        # preventing two threads from seeing the same AVAILABLE compartment
        # before either marks it RESERVED.
        self._lock = threading.Lock()

    def cleanup_reserved(self) -> None:
        """Periodic job to cleanup the reserved compartments"""
        pass

    def reserve_compartment(self, size: Size) -> Compartment:
        # The entire find-and-reserve sequence must be inside the critical
        # section. If only mark_reserved() were locked, two threads could
        # both complete _find_available_compartment() and return the same
        # compartment before either reserves it.
        with self._lock:
            compartment = self._find_available_compartment(size)
            if compartment is None:
                raise CompartmentNotAvailableError(
                    "compartment not available at the moment"
                )
            compartment.mark_reserved()
        compartment.open_compartment()
        return compartment

    def confirm_deposit(self, compartment: Compartment) -> str:
        if compartment.state != CompartmentState.RESERVED:
            raise LockerError("cannot confirm a compartment that is not reserved")
        compartment.mark_occupied()
        access_code = self._generate_access_code(compartment)
        with self._lock:
            self._access_code_mapping[access_code.code] = access_code
        return access_code.code

    def _find_available_compartment(self, size: Size) -> Compartment | None:
        # Called only while holding self._lock so the scan and subsequent
        # mark_reserved() are atomic together.
        for compartment in self._compartments:
            if not compartment.occupied and compartment.size == size:
                return compartment
        return None

    def take_package(self, code: str):
        if len(code) != 6:
            raise InvalidAccessCodeError(f"Malformed code, invalid length: {len(code)}")

        with self._lock:
            if code not in self._access_code_mapping:
                raise InvalidAccessCodeError(f"Invalid code, not found")
            access_code = self._access_code_mapping[code]
            if access_code.expired:
                raise AccessCodeExpiredError(
                    "Access Code expired, this package cannot be taken out"
                )
            del self._access_code_mapping[code]

        compartment = access_code.compartment
        compartment.open_compartment()
        # customer takes out the package
        compartment.mark_free()

    def _generate_access_code(self, compartment: Compartment) -> AccessCode:
        code = generateAlphaNumericCode(size=6)
        access_code = AccessCode(code, compartment)
        return access_code

    def open_expired_compartment(self) -> None:
        pass


class CompartmentState(enum.Enum):
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    AVAILABLE = "available"
    MAINTENANCE = "maintenance"


class Compartment:
    size: Size
    state: CompartmentState
    reserved_at: int

    def __init__(self, size: Size) -> None:
        self._size = size
        self._state = CompartmentState.AVAILABLE

    @property
    def occupied(self) -> bool:
        return self._state != CompartmentState.AVAILABLE

    @property
    def state(self) -> CompartmentState:
        return self._state

    @property
    def size(self) -> Size:
        return self._size

    def open_compartment(self) -> None:
        pass

    def mark_reserved(self) -> None:
        self._state = CompartmentState.RESERVED

    def mark_occupied(self) -> None:
        self._state = CompartmentState.OCCUPIED

    def mark_free(self) -> None:
        self._state = CompartmentState.AVAILABLE
