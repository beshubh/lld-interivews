# ═══════════════════════════════════════════════════════════════════════════
# REQUIREMENTS
#
# Example (Tic Tac Toe):
#   1. Two players alternate placing X and O on a 3x3 grid.
#   2. A player wins by completing a row, column, or diagonal.
#   Out of Scope: UI, AI opponent, networking
# ═══════════════════════════════════════════════════════════════════════════
# - we have 3 elevators, in a single building and 10 floors (0-9)
# - Movement is a simulation controlled by step function instead of relying on a physical sensor.
# - Users call the elevators using hall call (UP/DOWN).
# - Once inside the elevators users can select the destination floor directly via panel inside the car.
# - On hall call system is responsible to send one of the three elevators. Algorithm for dispatching the elevator will depend on the implementation later.

# Error Handling:
#  - Any request for a floor outside the valid range of 0-9 should be rejected.
#  - Both for hall calls and inside the car requests.
# Out of Scope: 
#  - UI rendering
#  - physical sensors.
#  - No need for configurable elevators or floors.


# ═══════════════════════════════════════════════════════════════════════════
# ENTITIES & RELATIONSHIPS
#
# Example (Tic Tac Toe):
#   Game, Board, Player
# ═══════════════════════════════════════════════════════════════════════════
# Class
#     - Elevator
#     - ElevatorController
#     - Request
# Enums
#     - RequestType[PICKUP_UP, PICKUP_DOWN, DESITNATION]
#     - Direction[UP, DOWN, IDLE]

import enum


class ElevatorController:
    elevators: list[Elevator]


class Elevator:
    requests: set<Request>


class Request:
    floor: int
    type: RequestType


class RequestType(enum.Enum):
    PICKUP_UP = 'pickup_up'
    PICKUP_DOWN = 'pickup_down'
    DESITNATION = 'destination'


# ═══════════════════════════════════════════════════════════════════════════
# CLASS DESIGN
#
# Example (Tic Tac Toe):
#   class Game:
#     - board: Board
#     - currentPlayer: Player
#     + makeMove(row, col) -> bool
# ═══════════════════════════════════════════════════════════════════════════
import enum


class ElevatorController:
    elevators: list[Elevator]
    
    def requestElevator(self, floor: int, type: RequestType) -> bool

    def step(self) -> None

    def _select_best_elevator(self, floor: int, direction: Direction) -> Elevator


class Elevator:
    current_floor: int
    direction: Direction
    requests: set<Request>

    def __init__(self):
        self._current_floor = 0
        self._direction = Direction.IDLE
        self._requests = set()
    
    def add_request(self, floor, type: RequestType) -> bool

    def step(self) -> None


class Request:
    floor: int
    type: RequestType

    @property
    def floor(self)

    @property
    def type(self)

    def __eq__(self, other):
        return self.floor == other.floor and self.type == other.type
    
    def __hash__(self, other):
        # hash the floor and type


class RequestType(enum.Enum):
    PICKUP_UP = 'pickup_up'
    PICKUP_DOWN = 'pickup_down'
    DESITNATION = 'destination'

class Direction(enum.Enum):
    UP = 'up'
    DOWN = 'down'
    IDLE = 'idle'


# ═══════════════════════════════════════════════════════════════════════════
# IMPLEMENTATION
# ═══════════════════════════════════════════════════════════════════════════

import enum


class ElevatorController:
    elevators: list[Elevator]
    
    def requestElevator(self, floor: int, type: RequestType) -> bool:
        if floor < 0 or floor > 9:
            return False
        # TODO: destination request
        direction = Direction.UP if type.PICKUP_UP else Direction.DOWN
        elevator = self._select_best_elevator(floor, direction)
        return elevator.add_request(floor, type)

    def step(self) -> None:
        for e in self._elevators:
            e.step()

    def _select_best_elevator(self, floor: int, direction: Direction) -> Elevator:
        best = self._find_moving_towards(floor, direction)
        if best:
            return best
        best = self._find_idle()
        if best:
            return best
        return self._find_nearest(floor)
 
    def self._find_moving_towards(self, floor: int, direction: Direction) -> Elevator | None:
        best = None
        min_distance = float('inf')
        for e in self._elevators:
            if e.direction != direction:
                continue
            if direction == Direction.UP and e.current_floor < floor:
                distance = abs(floor - e.current_floor)
                if distance < min_distance:
                    min_distance = distance
                    best = e
            if direction == Direction.DOWN and e.current_floor > floor:
                distance = abs(floor - e.current_floor)
                if distance < min_distance:
                    min_distance = distance
                    best = e
        return best
    
    def _find_idle(self) -> Elevator | None:
        for e in self._elevators:
            if e.direction == Direction.IDLE:
                return e
        return None
    
    def _find_nearest(self, floor: int) -> Elevator:
        best = self._elevators[0]
        min_distance = abs(floor - best.current_floor)
        for e in self._elevators:
            distance = abs(e.current_floor - floor)
            if distance < min_distance:
                min_distance = distance
                best = e
        return best


class Elevator:
    current_floor: int
    direction: Direction
    requests: set[Request]

    def __init__(self):
        self._current_floor = 0
        self._direction = Direction.IDLE
        self._requests = set()
    
    @property
    def current_floor(self):
        return self._current_floor
    
    @property
    def direction(self):
        return self._direction
    
    def add_request(self, floor, type: RequestType) -> bool:
        if floor < 0 or floor > 9:
            return False
        request = Request(floor, type)
        self._requests.add(request)
        if self.direction == Direction.IDLE:
            if request.floor == self.current_floor:
                continue
            if request.floor > self.current_floor:
                self._direction = Direction.UP
            else:
                self._direction = Direction.DOWN
        return True

    def step(self) -> None:
        if not self._requests:
            self._direction = Direction.IDLE
            return
        
        if self._direction == Direction.IDLE:
            # choose the nearest request to me
            min_distance = float('inf')
            nearest = None
            for req in self._requests:
                distance = abs(self._current_floor - req.floor)
                if distance < min_distance:
                    min_distance = distance
                    nearest = req
                # if there's tie, prefer going down
                elif distance == min_distance and req.floor < nearest.floor:
                    min_distance = distance
                    nearest = req

            if nearest.floor == self._current_floor:
                # Request is right here — set direction to match the request type
                # so we service it immediately without an unnecessary reversal cycle
                if nearest.type == RequestType.PICKUP_UP:
                    self._direction = Direction.UP
                elif nearest.type == RequestType.PICKUP_DOWN:
                    self._direction = Direction.DOWN
                else:
                    # DESTINATION at current floor: pick any direction, we'll service it below
                    self._direction = Direction.UP
            else:
                self._direction = Direction.UP if nearest.floor > self._current_floor else Direction.DOWN

        pickup_type = RequestType.PICKUP_UP if self._direction == Direction.UP else RequestType.PICKUP_DOWN
        request_pickup = Request(self._current_floor, pickup_type)
        request_destination = Request(self._current_floor, RequestType.DESTINATION)

        if request_pickup in self._requests or request_destination in self._requests:
            self._requests.discard(request_pickup)
            self._requests.discard(request_destination)
            return
            
        if not self._requests:
            self._direction = Direction.IDLE
            return
        
        if not self._has_request_ahead():
            # reverse the direction
            if self._direction == Direction.UP:
                self._direction = Direction.DOWN
            else:
                self._direction = Direction.UP
            return

        # tick
        if self._direction == Direction.UP:
            self._current_floor += 1
        else:
            self._current_floor -= 1
    
    def _has_request_ahead(self):
        for req in self._requests:
            if self._direction == Direction.UP and req.floor > self._current_floor:
                return True
            if self._direction == Direction.DOWN and req.floor < self._current_floor:
                return True
        return False


class Request:
    floor: int
    type: RequestType

    @property
    def floor(self):
        pass

    @property
    def type(self):
        pass

    def __eq__(self, other):
        return self.floor == other.floor and self.type == other.type
    
    def __hash__(self):
        # hash the floor and type
        pass


class RequestType(enum.Enum):
    PICKUP_UP = 'pickup_up'
    PICKUP_DOWN = 'pickup_down'
    DESTINATION = 'destination'

class Direction(enum.Enum):
    UP = 'up'
    DOWN = 'down'
    IDLE = 'idle'


# ═══════════════════════════════════════════════════════════════════════════
# EXTENSIBILITY
# ═══════════════════════════════════════════════════════════════════════════

from abc import ABC, abstractmethod


class ISchedulingStrategy(ABC):

    @abstractmethod
    def schedule_elevator(self, floor: int, direction: Direction) -> Elevator | None:
        raise NotImplementedError("method not implemented")


class ElevatorController:
    elevators: list[Elevator]
    schedule_strategy: ISchedulingStrategy

# or we could go ahead with list of strategies as well, starting from preferring the first, second and so on till last

class ElevatorController:
    elevators: list[Elevator]
    schedule_strategy: list[ISchedulingStrategy]


    def _select_best_elevator(self, floor: int, direction):
        for strategy in self._schedule_strategy:
            e = strategy.schedule_elevator(floor, direction)
            if e:
                return e
        # maybe fallback to find the nearest agnostic of the direction


# Express Elevators

import enum


class ElevatorController:
    elevators: list[Elevator]
    
    def requestElevator(self, floor: int, type: RequestType) -> bool:
        if floor < 0 or floor > 9:
            return False
        # TODO: destination request
        direction = Direction.UP if type.PICKUP_UP else Direction.DOWN
        elevator = self._select_best_elevator(floor, direction)
        return elevator.add_request(floor, type)

    def step(self) -> None:
        for e in self._elevators:
            e.step()

    def _select_best_elevator(self, floor: int, direction: Direction) -> Elevator:
        best = self._find_moving_towards(floor, direction)
        if best:
            return best
        best = self._find_idle(floor)
        if best:
            return best
        return self._find_nearest(floor)
 
    def _find_moving_towards(self, floor: int, direction: Direction) -> Elevator | None:
        best = None
        min_distance = float('inf')
        for e in self._elevators:
            if e.direction != direction:
                continue
            # Use handles_floor() to centralize eligibility check
            if not e.handles_floor(floor):
                continue
            if direction == Direction.UP and e.current_floor < floor:
                distance = abs(floor - e.current_floor)
                if distance < min_distance:
                    min_distance = distance
                    best = e
            if direction == Direction.DOWN and e.current_floor > floor:
                distance = abs(floor - e.current_floor)
                if distance < min_distance:
                    min_distance = distance
                    best = e
        return best
    
    def _find_idle(self, floor: int) -> Elevator | None:
        for e in self._elevators:
            if e.direction == Direction.IDLE and e.handles_floor(floor):
                return e
        return None
    
    def _find_nearest(self, floor: int) -> Elevator:
        eligible = [e for e in self._elevators if e.handles_floor(floor)]
        if not eligible:
            # should be impossible
            raise RuntimeError('no elevator handles this floor request')
        best = eligible[0]
        min_distance = abs(floor - best.current_floor)
        for e in eligible[1:]:
            distance = abs(e.current_floor - floor)
            if distance < min_distance:
                min_distance = distance
                best = e
        return best


class Elevator:
    current_floor: int
    direction: Direction
    requests: set[Request]
    floors: set[int]

    def __init__(self, floors: list[int]):
        self._current_floor = 0
        self._direction = Direction.IDLE
        self._requests = set()
        self._floors = set(floors)
    
    @property
    def current_floor(self):
        return self._current_floor
    
    @property
    def direction(self):
        return self._direction

    def handles_floor(self, floor: int) -> bool:
        """Centralizes floor eligibility — express elevators only serve their designated floors."""
        return floor in self._floors
    
    def add_request(self, floor: int, type: RequestType) -> bool:
        if not self.handles_floor(floor):
            return False
        request = Request(floor, type)
        self._requests.add(request)
        if self._direction == Direction.IDLE:
            if request.floor == self._current_floor:
                pass
            elif request.floor > self._current_floor:
                self._direction = Direction.UP
            else:
                self._direction = Direction.DOWN
        return True
