from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence, cast

from core import add_match, add_role, build_pipeline, reduce_stats, update_profile
from model import MatchStat, Player, make_player


def load_players(path: Path) -> list[Player]:
    with path.open(encoding="utf-8") as file:
        records = json.load(file)
    if not isinstance(records, list):
        raise ValueError("JSON must contain a list of players")
    players: list[Player] = []
    for raw in records:
        record = cast(dict[str, object], raw)
        raw_matches = cast(list[dict[str, object]], record["matches"])
        matches = tuple(
            MatchStat(
                opponent=str(match["opponent"]),
                points=int(cast(int, match["points"])),
                assists=int(cast(int, match["assists"])),
                rebounds=int(cast(int, match["rebounds"])),
            )
            for match in raw_matches
        )
        raw_roles = cast(list[str], record["roles"])
        profile = cast(dict[str, str], record["profile"])
        players.append(
            make_player(
                id=int(cast(int, record["id"])),
                name=str(record["name"]),
                matches=matches,
                roles=frozenset(raw_roles),
                profile=profile,
            )
        )
    return players


def render_report(players: list[Player], stats: dict[str, float | int]) -> None:
    print("Лабораторна №3. Спортивна команда — варіант 10")
    print("Рейтинг гравців:")
    for index, player in enumerate(players, start=1):
        roles = ", ".join(sorted(player.roles))
        print(f"{index}. #{player.id} {player.name}: рейтинг {player.rating:.2f}; ролі: {roles}")
    print(f"Кількість гравців: {stats['count']}")
    print(f"Сумарний рейтинг: {stats['total_rating']:.2f}")
    print(f"Середній рейтинг: {stats['avg_rating']:.2f}")


def run(args: Sequence[str] | None = None) -> tuple[list[Player], dict[str, float | int]]:
    parser = argparse.ArgumentParser(description="Лабораторна №3, варіант 10")
    parser.add_argument(
        "--data",
        type=Path,
        default=Path(__file__).resolve().parent / "data" / "sample_data.json",
    )
    parser.add_argument("--top", type=int, default=3)
    parser.add_argument("--min-matches", type=int, default=1)
    parser.add_argument("--boost-role", default="captain")
    parser.add_argument("--factor", type=float, default=1.1)
    options = parser.parse_args(args)
    players = load_players(options.data)
    pipeline = build_pipeline(
        top_n=options.top,
        min_matches=options.min_matches,
        role=options.boost_role,
        factor=options.factor,
    )
    result = pipeline(players)
    stats = reduce_stats(result)
    render_report(result, stats)
    return result, stats


def pure_update_demo(player: Player) -> Player:
    changed = add_match(player, MatchStat("Демо", 10, 3, 2))
    changed = add_role(changed, "leader")
    return update_profile(changed, "season", "2026")
