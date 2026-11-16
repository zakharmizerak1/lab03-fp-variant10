from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True, slots=True)
class MatchStat:
    opponent: str
    points: int
    assists: int
    rebounds: int

    def score(self) -> int:
        return self.points + self.assists * 2 + self.rebounds


@dataclass(frozen=True, slots=True)
class Player:
    id: int
    name: str
    matches: tuple[MatchStat, ...]
    roles: frozenset[str]
    profile: Mapping[str, str]
    rating: float = 0.0

    def __hash__(self) -> int:
        return hash(
            (
                self.id,
                self.name,
                self.matches,
                self.roles,
                tuple(sorted(self.profile.items())),
                self.rating,
            )
        )


def make_profile(source: Mapping[str, str]) -> Mapping[str, str]:
    return MappingProxyType(dict(source))


def make_player(
    id: int,
    name: str,
    matches: tuple[MatchStat, ...],
    roles: frozenset[str],
    profile: Mapping[str, str],
    rating: float = 0.0,
) -> Player:
    return Player(id, name, matches, roles, make_profile(profile), rating)
