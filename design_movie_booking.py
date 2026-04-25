# ═══════════════════════════════════════════════════════════════════════════
# REQUIREMENTS
#
# Example (Tic Tac Toe):
#   1. Two players alternate placing X and O on a 3x3 grid.
#   2. A player wins by completing a row, column, or diagonal.
#   Out of Scope: UI, AI opponent, networking
# ═══════════════════════════════════════════════════════════════════════════
# REQUIREMENTS
# - System supports multiple theaters
# - Browse movies across theaters.
# - User can search movies using title.
# - Select theaters and showtimes.
# - Book tickets for a specific showtime in a theater.
# - Cancel the booked tickets using confirmation ID.
# - System should be correct under concurrent load.
#     - no double booking of the same seat in concurrent environment.
# - Each theater have static seats, rows A - Z, with seat numbers 0 - 20.
# - A user can book multiple seats in a single booking.
# - Error handling:
#     - no double booking is allowed.
#     - already booked seats should be rejected.
#     - bookings with invalid confirmation id should be rejected.

# Out of scope: Variable seat configuration, UI, networking, payment processing, persistence layers


# ═══════════════════════════════════════════════════════════════════════════
# ENTITIES & RELATIONSHIPS
#
# Example (Tic Tac Toe):
#   Game, Board, Player
# ═══════════════════════════════════════════════════════════════════════════
- Theater, Reservation, Movie, ShowTime, BookingSystem


# ═══════════════════════════════════════════════════════════════════════════
# CLASS DESIGN
#
# Example (Tic Tac Toe):
#   class Game:
#     - board: Board
#     - currentPlayer: Player
#     + makeMove(row, col) -> bool
# ═══════════════════════════════════════════════════════════════════════════



class BookingSystem:
    theaters: dict[str, Theater]
    reservations_idx: dict[str, Reservation]

    def search_movies(self, name: str) -> list[Movies]:
        pass
    
    def book(self, theater_id: str, movie_id: str, showtime_id: str, seats: list[str]) -> str:
        theater = self._theaters.get(theater_id)
        if not theater:
            raise ValueError(f'No such theater:{theater_id}')
        reservation = theater.book(movie_id, seats, showtime_id)
        self._reservations_idx[reservation.id] = reservation
        return reservation.id
    
    def cancel(self, reservation_id: str) -> None:
        reservation = self._reservations_idx.get(reservation_id)
        if not reservation:
            raise ValueError(f'No such reservation: {reservation_id}')
        reservation.cancel()
        del self._reservations_idx[reservation_id]


class Theater:
    _id: str
    name: str
    movies: dict[str, Movie]
    showtimes: dict[str, ShowTime]

    @property
    def id(self):
        self._id
    
    def search_movies(self, name: str) -> list[Movie]:
        pass

    def book(self, movie_id: str, seats: list[str], showtime_id: str) -> Reservation:
        movie = self._movies.get(movie_id)
        if not movie:
            raise ValueError(f'No such movie: {movie_id}')
        showtime = self._showtimes.get(showtime_id)

    
        if not showtime:
            raise ValueError(f'No such showtime: {showtime_id}')
        assert showtime.movie == movie
        return showtime.book(seats)
    
    def cancel(self, reservation_id: str) -> None:
        # raises on error
        pass
    


class Movie:
    _id: str
    name: str
    theater: Theater

    def __init__(self, theater: Theater, name: str) -> None:
        self._name = name
        self._theater = theater
    
    @property
    def id(self):
        return self._id


class ShowTime:
    _id:
    movie: Movie
    theater: Theater
    reservations: dict[str, Reservation]
    lock: threading.Lock()


    @property
    def id(self):
        return self._id

    def book(self, seats: list[str]) -> Reservation:
        with self._lock:
            if not self._is_available(seats):
                raise ValueError(f'Some seats are not available for booking')
            reservation = Reservation(
                id=generate_reservation_id(),
                theater=self._theater,
                movie=self._movie,
                showtime=showtime,
                seats=seats
            )
            self._reservation[reservation.id] = reservation
            return reservation


    
    def cancel(self, reservation_id: str) -> None:
        # we could validate here but in favor of time am skipping
        with self._lock:
            del self._reservations[reservation_id]

    def _is_available(self, seats: list[str]) -> bool:
        available_seats = self.get_available_seats()
        for seat in seats:
            if seat not in available_seats:
                return False
        return True

    def get_available_seats(self) -> list[str] | None:
        if not self._seats:
            seats = []
            for r in ['A...', 'Z']:
                for c in range(1, 21):
                    seats.append(f'{r}{c}')
            self._seats = seats
        available_seats = []
        for seat in self._seats:
            if seat not in [*r.seats for r in self.reservations.values()]:
                available_seats.append(seat)
        return available_seats 


class Reservation:
    _id: str
    theater: Theater
    movie: Movie 
    showtime: ShowTime
    seats: list[str]

    @property
    def id(self):
        return self._id

    def cancel(self) -> None:
        self._showtimes.cancel(self.id)

# ═══════════════════════════════════════════════════════════════════════════
# IMPLEMENTATION
# ═══════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════
# EXTENSIBILITY
# ═══════════════════════════════════════════════════════════════════════════


class ShowTime:
    _id:
    movie: Movie
    theater: Theater
    reservations: dict[str, Reservation]
    lock: threading.Lock()


    @property
    def id(self):
        return self._id

    def book(self, seats: list[str]) -> Reservation:
        seats = sorted(seats)
        seat_locks = [self._locks[s] for s in seats]
        try:
            for lock in seat_locks:
                lock.acquire()
            if not self._is_available(seats):
                raise ValueError(f'Some seats are not available for booking')
            reservation = Reservation(
                id=generate_reservation_id(),
                theater=self._theater,
                movie=self._movie,
                showtime=showtime,
                seats=seats
            )
            self._reservation[reservation.id] = reservation
            return reservation
        finally:
            for lock in seat_locks:
                lock.release()

