from __future__ import annotations

from time import perf_counter

from core import add_role
from model import MatchStat, make_player


def test_pure_updates_are_correct_after_repetition() -> None:
    original = make_player(1, "Гравець", (MatchStat("A", 1, 1, 1),), frozenset(), {"team": "ФЕКТ"})
    current = original
    for index in range(1000):
        current = add_role(current, f"role_{index}")
    assert len(current.roles) == 1000
    assert not original.roles


def test_performance_comparison() -> None:
    original = make_player(1, "Гравець", (), frozenset({"player"}), {"team": "ФЕКТ"})
    repeat = 5000
    start = perf_counter()
    for index in range(repeat):
        mutable_roles = set(original.roles)
        mutable_roles.add(str(index))
    mutable_seconds = perf_counter() - start

    start = perf_counter()
    for index in range(repeat):
        updated = add_role(original, str(index))
    immutable_seconds = perf_counter() - start

    assert "player" in mutable_roles
    assert "player" in updated.roles
    assert original.roles == frozenset({"player"})
    assert mutable_seconds >= 0
    assert immutable_seconds >= 0
