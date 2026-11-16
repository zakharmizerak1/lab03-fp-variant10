from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import replace
from functools import lru_cache, reduce
from types import MappingProxyType
from typing import TypeAlias

from model import MatchStat, Player, make_profile

PlayerTransform: TypeAlias = Callable[[Iterable[Player]], list[Player]]


def add_match(player: Player, match: MatchStat) -> Player:
    return replace(player, matches=player.matches + (match,))


def add_role(player: Player, role: str) -> Player:
    return replace(player, roles=player.roles | frozenset({role}))


def update_rating(player: Player, rating: float) -> Player:
    return replace(player, rating=round(rating, 2))


def update_profile(player: Player, key: str, value: str) -> Player:
    return replace(player, profile=make_profile({**player.profile, key: value}))


def match_total(player: Player) -> int:
    return sum(match.score() for match in player.matches)


def average_score(player: Player) -> float:
    return round(match_total(player) / len(player.matches), 2) if player.matches else 0.0


def apply_role_bonus(player: Player, role: str, factor: float) -> Player:
    if factor < 0:
        raise ValueError("Factor must not be negative")
    return update_rating(player, player.rating * (factor if role in player.roles else 1.0))


def compose(*functions: PlayerTransform) -> PlayerTransform:
    def process(players: Iterable[Player]) -> list[Player]:
        result: Iterable[Player] = players
        for function in reversed(functions):
            result = function(result)
        return list(result)

    return process


def with_ratings() -> PlayerTransform:
    return lambda players: [update_rating(player, average_score(player)) for player in players]


def only_active(min_matches: int) -> PlayerTransform:
    if min_matches < 0:
        raise ValueError("Minimum matches must not be negative")
    return lambda players: list(filter(lambda player: len(player.matches) >= min_matches, players))


def boost_role(role: str, factor: float) -> PlayerTransform:
    if factor < 0:
        raise ValueError("Factor must not be negative")
    return lambda players: [apply_role_bonus(player, role, factor) for player in players]


def sort_by_rating() -> PlayerTransform:
    return lambda players: sorted(players, key=lambda player: (-player.rating, player.id))


def take(top_n: int) -> PlayerTransform:
    if top_n < 0:
        raise ValueError("Top-N must not be negative")
    return lambda players: list(players)[:top_n]


def build_pipeline(
    *, top_n: int = 3, min_matches: int = 1, role: str = "captain", factor: float = 1.1
) -> PlayerTransform:
    return compose(
        take(top_n),
        sort_by_rating(),
        boost_role(role, factor),
        with_ratings(),
        only_active(min_matches),
    )


def reduce_stats(players: Iterable[Player]) -> dict[str, float | int]:
    count, total = reduce(
        lambda acc, player: (acc[0] + 1, acc[1] + player.rating), players, (0, 0.0)
    )
    return {
        "count": count,
        "total_rating": round(total, 2),
        "avg_rating": round(total / count, 2) if count else 0.0,
    }


def freeze(value: object) -> object:
    if isinstance(value, Mapping):
        return MappingProxyType({key: freeze(item) for key, item in value.items()})
    if isinstance(value, (set, frozenset)):
        return frozenset(freeze(item) for item in value)
    if isinstance(value, (list, tuple)):
        return tuple(freeze(item) for item in value)
    return value


@lru_cache(maxsize=256)
def cached_match_total(player: Player) -> int:
    return match_total(player)


def mutable_add_role(roles: set[str], role: str) -> set[str]:
    copy = set(roles)
    copy.add(role)
    return copy
