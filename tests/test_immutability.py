from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path
from types import MappingProxyType
from typing import cast

import pytest

from app import load_players, pure_update_demo, run
from core import (
    add_match,
    add_role,
    apply_role_bonus,
    build_pipeline,
    cached_match_total,
    compose,
    freeze,
    match_total,
    mutable_add_role,
    only_active,
    reduce_stats,
    take,
    update_profile,
    update_rating,
)
from model import MatchStat, Player, make_player, make_profile


@pytest.fixture
def player() -> Player:
    return make_player(
        1, "Марко", (MatchStat("Команда А", 12, 3, 4),), frozenset({"forward"}), {"team": "ФЕКТ"}
    )


@pytest.fixture
def players() -> list[Player]:
    return load_players(Path(__file__).resolve().parents[1] / "data" / "sample_data.json")


def test_match_stat_is_frozen() -> None:
    match = MatchStat("A", 1, 2, 3)
    with pytest.raises(FrozenInstanceError):
        setattr(match, "points", 8)


def test_player_is_frozen(player: Player) -> None:
    with pytest.raises(FrozenInstanceError):
        setattr(player, "name", "Інше ім'я")


def test_tuple_and_frozenset(player: Player) -> None:
    assert isinstance(player.matches, tuple)
    assert isinstance(player.roles, frozenset)


def test_read_only_profile(player: Player) -> None:
    assert isinstance(player.profile, MappingProxyType)
    with pytest.raises(TypeError):
        cast(dict[str, str], player.profile)["team"] = "Інша"


def test_proxy_copies_input() -> None:
    original = {"city": "Львів"}
    proxy = make_profile(original)
    original["city"] = "Київ"
    assert proxy["city"] == "Львів"


def test_add_match_returns_new(player: Player) -> None:
    extra = MatchStat("B", 5, 1, 2)
    changed = add_match(player, extra)
    assert changed is not player
    assert len(changed.matches) == 2
    assert len(player.matches) == 1


def test_add_role_returns_new(player: Player) -> None:
    changed = add_role(player, "captain")
    assert "captain" in changed.roles
    assert "captain" not in player.roles


def test_update_rating_returns_new(player: Player) -> None:
    changed = update_rating(player, 12.345)
    assert changed.rating == 12.35
    assert player.rating == 0.0


def test_update_profile_returns_new(player: Player) -> None:
    changed = update_profile(player, "city", "Львів")
    assert changed.profile["city"] == "Львів"
    assert "city" not in player.profile
    with pytest.raises(TypeError):
        cast(dict[str, str], changed.profile)["city"] = "Київ"


def test_hashable_after_updates(player: Player) -> None:
    changed = add_role(player, "captain")
    assert len({player, changed}) == 2
    assert {player: "original", changed: "updated"}[changed] == "updated"


def test_equal_players_have_equal_hashes(player: Player) -> None:
    same = make_player(
        player.id, player.name, player.matches, player.roles, dict(player.profile), player.rating
    )
    assert same == player
    assert hash(same) == hash(player)


def test_match_score(player: Player) -> None:
    assert player.matches[0].score() == 22
    assert match_total(player) == 22


def test_role_bonus(player: Player) -> None:
    initial = update_rating(player, 50)
    assert apply_role_bonus(initial, "forward", 1.1).rating == 55.0
    assert apply_role_bonus(initial, "center", 1.1).rating == 50.0


def test_pipeline_top_and_sort(players: list[Player]) -> None:
    result = build_pipeline(top_n=3)(players)
    assert [p.id for p in result] == [101, 105, 102]
    assert [p.rating for p in result] == [40.7, 40.7, 35.0]


def test_pipeline_does_not_mutate(players: list[Player]) -> None:
    initial = tuple(players)
    result = build_pipeline()(players)
    assert players == list(initial)
    assert all(p.rating == 0.0 for p in players)
    assert all(all(output is not source for source in players) for output in result)


def test_pipeline_repeatable(players: list[Player]) -> None:
    pipeline = build_pipeline()
    assert pipeline(players) == pipeline(players)


def test_pipeline_filters_inactive(players: list[Player]) -> None:
    result = build_pipeline(top_n=10, min_matches=1)(players)
    assert 104 not in [p.id for p in result]


def test_pipeline_top_zero(players: list[Player]) -> None:
    assert build_pipeline(top_n=0)(players) == []


def test_pipeline_empty() -> None:
    assert build_pipeline()([]) == []
    assert reduce_stats([]) == {"count": 0, "total_rating": 0.0, "avg_rating": 0.0}


def test_pipeline_accepts_iterator(players: list[Player]) -> None:
    assert len(build_pipeline()(p for p in players)) == 3


def test_reduce_stats(players: list[Player]) -> None:
    result = build_pipeline(top_n=3)(players)
    assert reduce_stats(result) == {"count": 3, "total_rating": 116.4, "avg_rating": 38.8}


def test_composition_order(players: list[Player]) -> None:
    select = compose(take(1), only_active(2))
    assert [p.id for p in select(players)] == [101]


def test_freeze_nested() -> None:
    original: dict[str, object] = {
        "tags": ["a", "b"],
        "options": {"one", "two"},
        "meta": {"year": 2026},
    }
    frozen = cast(dict[str, object], freeze(original))
    assert isinstance(frozen, MappingProxyType)
    assert frozen["tags"] == ("a", "b")
    assert frozen["options"] == frozenset({"one", "two"})
    with pytest.raises(TypeError):
        cast(dict[str, int], frozen["meta"])["year"] = 2027
    cast(list[str], original["tags"]).append("c")
    assert frozen["tags"] == ("a", "b")


def test_cached_result(player: Player) -> None:
    cached_match_total.cache_clear()
    assert cached_match_total(player) == 22
    assert cached_match_total(player) == 22
    assert cached_match_total.cache_info().hits == 1


def test_negative_factor(player: Player) -> None:
    with pytest.raises(ValueError, match="Factor"):
        apply_role_bonus(player, "forward", -1)


def test_negative_top() -> None:
    with pytest.raises(ValueError, match="Top-N"):
        take(-1)


def test_negative_min_matches() -> None:
    with pytest.raises(ValueError, match="Minimum"):
        only_active(-1)


def test_demo_pure_updates(player: Player) -> None:
    updated = pure_update_demo(player)
    assert updated is not player
    assert len(updated.matches) == 2
    assert "leader" in updated.roles
    assert updated.profile["season"] == "2026"
    assert "leader" not in player.roles


def test_mutable_baseline_stays_separate() -> None:
    roles = {"player"}
    result = mutable_add_role(roles, "captain")
    assert roles == {"player"}
    assert result == {"player", "captain"}


def test_run_cli(capsys: pytest.CaptureFixture[str]) -> None:
    result, stats = run(["--top", "2"])
    assert len(result) == 2
    assert stats["count"] == 2
    assert "Рейтинг гравців" in capsys.readouterr().out
