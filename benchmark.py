from __future__ import annotations

from timeit import repeat

from core import add_role
from model import Player, make_player


def main() -> None:
    player = make_player(1, "Гравець", (), frozenset({"player"}), {"team": "ФЕКТ"})

    def baseline() -> set[str]:
        return set(player.roles) | {"captain"}

    def immutable() -> Player:
        return add_role(player, "captain")

    runs = 10000
    before = min(repeat(baseline, number=runs, repeat=5))
    after = min(repeat(immutable, number=runs, repeat=5))
    print(f"Мутабельний підхід (копія set + оновлення): {before:.6f} с")
    print(f"Незмінна модель (pure update Player): {after:.6f} с")
    print(f"Операцій у кожному вимірюванні: {runs}")
    print(f"Співвідношення часу: {after / before:.2f}x")


if __name__ == "__main__":
    main()
