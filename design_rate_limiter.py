# ═══════════════════════════════════════════════════════════════════════════
# REQUIREMENTS
#
# Example (Tic Tac Toe):
#   1. Two players alternate placing X and O on a 3x3 grid.
#   2. A player wins by completing a row, column, or diagonal.
#   Out of Scope: UI, AI opponent, networking
# ═══════════════════════════════════════════════════════════════════════════

# REQUIREMENTS
# - In memory rate limiter for an endpoint and limiting configurations.
# - Each endpoint will have its own rate limiter, if an endpoint is missing the rate limiter, we will apply a default one.
# - The configuration parameters for each `algorithm` type will be different.
#     - for e.g
#     - {
#         "algorithm": "TokenBucket",
#         "config": {
#             "capacity": int,
#             "refill_rate": "float"
#         }
#     }
# - If no rate limiter is configured on an endpoint a default rate limiter should be applied.
# - given a client_id and endpoint rate limiter determines whether the request is allowed or denied and returns a structured result: { allowed: bool, remaining: float, retry_after: long }

# Out of Scope: UI, Concurrency, distributed rate limiter, dynamic configuration updates


# ═══════════════════════════════════════════════════════════════════════════
# ENTITIES & RELATIONSHIPS
#
# Example (Tic Tac Toe):
#   Game, Board, Player
# ═══════════════════════════════════════════════════════════════════════════

# ENTITIES
# RateLimiter, RateLimiterResult, RateLimiterStrategy


# ═══════════════════════════════════════════════════════════════════════════
# CLASS DESIGN
#
# Example (Tic Tac Toe):
#   class Game:
#     - board: Board
#     - currentPlayer: Player
#     + makeMove(row, col) -> bool
# ═══════════════════════════════════════════════════════════════════════════
from abc import ABC, abstractmethod


class RateLimiter:
    limiter_strategies: dict[str, IRateLimiterStrategy]
    default_limiter: IRateLimiterStrategy

    def __init__(self, configurations: list[dict], default_config: dict) -> None:
        pass

    def allowed(self, client_id: str, endpoint: str) -> RateLimiterResult:
        pass


class RateLimiterResult:
    allowed: bool
    remaining: float
    retry_after: int | None  # will be none when request is allowed.

    def __init__(self, allowed: bool, remaining: float, retry_after: int) -> None:
        pass


class IRateLimiterStrategy(ABC):
    @abstractmethod
    def allowed(self, client_id: str) -> RateLimiterResult:
        pass


class TokenBucketStrategy(IRateLimiterStrategy):
    def __init__(self, capacity: int, refill_rate_per_second: float) -> None:
        self._capacity = capacity
        self._refill_rate_per_second = refill_rate_per_second
        self._state: dict[
            str, dict
        ] = {}  # map client_id => { remaining: float, last_refill_at: int}

    def allowed(self, client_id: str) -> RateLimiterResult:
        # implementation
        pass


class RateLimiterFactory:
    @classmethod
    def create(cls, config: dict) -> IRateLimiterStrategy:
        algorithm = config.get("algorithm")
        match algorithm:
            case "TokenBucket":
                ...
            case "SlidingWindow":
                ...

            case _:
                pass
                # invalid algorithm error


# ═══════════════════════════════════════════════════════════════════════════
# IMPLEMENTATION
# ═══════════════════════════════════════════════════════════════════════════
import time
import math


class RateLimiterFactory:
    @classmethod
    def create(cls, config: dict) -> IRateLimiterStrategy:
        algorithm = config.get("algorithm")
        if not algorithm:
            raise ValueError("Algorithm param not provided")
        specific_config = config.get("config")
        if not specific_config or not isinstance(specific_config, dict):
            raise ValueError(f"Invalid `config` for algorithm: {algorithm}")
        match algorithm:
            case "TokenBucket":
                return TokenBucketStrategy(
                    capacity=specific_config["capacity"],
                    refill_rate_per_second=specific_config["refill_rate_per_second"],
                )
            case "SlidingWindow":
                return SlidingWindowStrategy(
                    capacity=specific_config["capacity"],
                    window_size=specific_config["window_size"],
                )
            case _:
                raise ValueError(f"Invalid algorithm: {algorithm}")


class RateLimiter:
    limiter_strategies: dict[str, IRateLimiterStrategy]
    default_limiter: IRateLimiterStrategy

    def __init__(self, configurations: list[dict], default_config: dict) -> None:
        self._limiter_strategies = {}
        for config in configurations:
            if "endpoint" not in config:
                raise ValueError(f"No endpoint found in the {config}")
            endpoint = config["endpoint"]
            self._limiter_strategies[endpoint] = RateLimiterFactory.create(config)

        self._default_limiter = RateLimiterFactory.create(default_config)

    def allowed(self, client_id: str, endpoint: str) -> RateLimiterResult:
        limiter = self._limiter_strategies.get(endpoint)
        if not limiter:
            limiter = self._default_limiter
        return limiter.allowed(client_id)


class TokenBucketStrategy(IRateLimiterStrategy):
    def __init__(self, capacity: int, refill_rate_per_second: float) -> None:
        self._capacity = capacity
        self._refill_rate_per_second = refill_rate_per_second
        self._state: dict[
            str, dict
        ] = {}  # map client_id => { remaining: float, last_refill_at: int}

    def allowed(self, client_id: str) -> RateLimiterResult:
        client_state = self._get_or_create_client_state(client_id)
        epoch_now = time.time()
        refill_tokens = (
            epoch_now - client_state["last_refill_at"]
        ) * self._refill_rate_per_second
        client_state["remaining"] += refill_tokens
        client_state["remaining"] = min(client_state["remaining"], self._capacity)
        client_state["last_refill_at"] = epoch_now
        if client_state["remaining"] > 0:
            client_state["remaining"] -= 1
            return RateLimiterResult(
                allowed=True, remaining=client_state["remaining"], retry_after=None
            )
        else:
            retry_after = math.ceil(
                ((1 - client_state["remaining"]) / self._refill_rate_per_second)
            )
            return RateLimiterResult(
                allowed=False,
                remaining=client_state["remaining"],
                retry_after=retry_after,
            )

    def _get_or_create_client_state(self, client_id: str) -> dict:
        client_state = self._state.get(client_id)
        if not client_state:
            self._state[client_id] = {
                "remaining": self._capacity,
                "last_refill_at": time.time(),
            }
        return self._state[client_id]


# ═══════════════════════════════════════════════════════════════════════════
# EXTENSIBILITY
# ═══════════════════════════════════════════════════════════════════════════
class RateLimiterFactory:
    @classmethod
    def create(cls, config: dict) -> IRateLimiterStrategy:
        algorithm = config.get("algorithm")
        if not algorithm:
            raise ValueError("Algorithm param not provided")
        specific_config = config.get("config")
        if not specific_config or not isinstance(specific_config, dict):
            raise ValueError(f"Invalid `config` for algorithm: {algorithm}")
        match algorithm:
            case "TokenBucket":
                return TokenBucketStrategy(
                    capacity=specific_config["capacity"],
                    refill_rate_per_second=specific_config["refill_rate_per_second"],
                )
            case "SlidingWindow":
                return SlidingWindowStrategy(
                    capacity=specific_config["capacity"],
                    window_size=specific_config["window_size"],
                )
            case "LeakyBucket":
                ...
            case _:
                raise ValueError(f"Invalid algorithm: {algorithm}")


# factory with strategy pattern


class RateLimiterFactory:
    @classmethod
    def register(cls, strategy_type: str, strategy_cls: IRateLimiterStrategy) -> None:
        cls._registry[strategy_type] = strategy_cls

    @classmethod
    def create(cls, config: dict) -> IRateLimiterStrategy:
        algorithm = config.get("algorithm")
        if not algorithm:
            raise ValueError("Algorithm param not provided")
        specific_config = config.get("config")
        if not specific_config or not isinstance(specific_config, dict):
            raise ValueError(f"Invalid `config` for algorithm: {algorithm}")
        strategy_cls = cls._registry.get(algorithm)
        if not strategy_cls:
            raise ValueError("invalid algorithm")
        return strategy_cls(...)


RateLimiterFactory.register("TokenBucket", TokenBucketStrategy)


class IRateLimiterStrategy(ABC):
    def __init__(self, eviction_policy: IEvictionPolicy, *args, **kwargs) -> None: ...
