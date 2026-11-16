# Лабораторна робота №3 — варіант 10

**Тема:** Нездатні до змін структури даних (immutability) у Python.

**Предметна область:** Спортивна команда.

Розроблено незмінні моделі `Player` та `MatchStat` із `@dataclass(frozen=True, slots=True)`. Статистика матчів зберігається у `tuple`, ролі — у `frozenset`, профіль — через `MappingProxyType` на копії словника. Зміни реалізовано чистими функціями `add_match`, `add_role`, `update_rating`, `update_profile` з поверненням нового об’єкта. Є функціональний рейтинг з композицією, `reduce`-статистикою, рекурсивне `freeze`, кешування через `lru_cache`, тести на хешованість, read-only та відсутність мутацій.

## Структура

```text
lab03_variant10/
├── main.py
├── benchmark.py
├── app.py
├── model.py
├── core.py
├── data/sample_data.json
├── tests/test_immutability.py
├── tests/test_performance.py
├── requirements.txt
├── pyproject.toml
├── mypy.ini
└── README.md
```

## Запуск у Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m pytest -q --durations=5
.\.venv\Scripts\python.exe -m mypy .
.\.venv\Scripts\python.exe -m black --check .
.\.venv\Scripts\python.exe -m ruff check .
```

Можна запускати через уже встановлений системний Python, замінивши `\.venv\Scripts\python.exe` на `python`.

## Приклад CLI

```powershell
python main.py --top 2 --min-matches 1 --boost-role captain --factor 1.1
python benchmark.py
```

## Вимірювання продуктивності

`benchmark.py` виводить виміряний час повторного створення змінених наборів ролей для мутабельного підходу та незмінної моделі. `tests/test_performance.py` перевіряє правильність операцій і вимірює їхній час. Щоб побачити тривалість тестів, запустіть `python -m pytest -q --durations=5`. Час залежить від комп’ютера й навантаження; тест не робить необґрунтованого висновку, що незмінні структури завжди швидші.

## Висновок

Незмінні моделі запобігають випадковим змінам даних і полегшують тестування та повторне використання об’єктів. `tuple` і `frozenset` дають змогу безпечно зберігати вкладені колекції, а `MappingProxyType` захищає метадані від запису. Накладні витрати — створення нових об’єктів під час оновлень і копіювання даних; їх доцільно вимірювати, а не вважати нульовими.
