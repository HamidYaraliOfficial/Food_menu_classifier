"""SQLite storage for the food/menu classifier.

One database file (default: food_data.db) holds:
 - categories: the level-1/level-2 taxonomy (mirrors taxonomy.py, for
   inspection/reporting)
 - keywords / exceptions: mirror of the rule tables in taxonomy.py, kept in
   the database purely for inspection/reporting - the rule engine itself
   reads taxonomy.py directly so editing rules stays a one-file, versionable
   change.
 - menu_items: the labeled dataset used for training/testing the ML
   fallback model. The same table serves as both the "training database"
   and the "test database" via the `split` column, so there is one place to
   look at the whole labeled dataset.
"""

import sqlite3
from pathlib import Path

import taxonomy

DEFAULT_DB_PATH = Path(__file__).parent / "food_data.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    level INTEGER NOT NULL CHECK (level IN (1, 2)),
    parent_id INTEGER REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phrase TEXT NOT NULL,
    subcategory_id INTEGER NOT NULL REFERENCES categories(id),
    weight REAL NOT NULL DEFAULT 1.0
);

CREATE TABLE IF NOT EXISTS exceptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phrase TEXT NOT NULL,
    subcategory_id INTEGER NOT NULL REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS menu_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    restaurant_name TEXT,
    main_category TEXT NOT NULL,
    sub_category TEXT NOT NULL,
    split TEXT NOT NULL CHECK (split IN ('train', 'test')),
    source TEXT NOT NULL DEFAULT 'synthetic'
);
"""


def get_connection(db_path=DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def reseed_taxonomy(conn: sqlite3.Connection) -> None:
    """(Re)seed categories/keywords/exceptions from taxonomy.py. Safe to
    call repeatedly - it clears and rewrites just those reference tables,
    never touching menu_items."""
    conn.execute("DELETE FROM keywords")
    conn.execute("DELETE FROM exceptions")
    conn.execute("DELETE FROM categories")

    main_ids = {}
    for main in taxonomy.MAIN_CATEGORIES:
        cur = conn.execute(
            "INSERT INTO categories (name, level, parent_id) VALUES (?, 1, NULL)",
            (main,),
        )
        main_ids[main] = cur.lastrowid

    sub_ids = {}
    for main, subs in taxonomy.SUBCATEGORIES.items():
        for sub in subs:
            cur = conn.execute(
                "INSERT INTO categories (name, level, parent_id) VALUES (?, 2, ?)",
                (sub, main_ids[main]),
            )
            sub_ids[sub] = cur.lastrowid

    for sub, phrases in taxonomy.KEYWORDS.items():
        for phrase, weight in phrases:
            conn.execute(
                "INSERT INTO keywords (phrase, subcategory_id, weight) VALUES (?, ?, ?)",
                (phrase, sub_ids[sub], weight),
            )

    for phrase, sub in taxonomy.EXCEPTIONS:
        conn.execute(
            "INSERT INTO exceptions (phrase, subcategory_id) VALUES (?, ?)",
            (phrase, sub_ids[sub]),
        )

    conn.commit()


def seed_menu_items(conn: sqlite3.Connection, rows, replace=False) -> int:
    """rows: iterable of (item_name, main_category, sub_category, split, source).
    If replace=True, wipes existing menu_items first (used for --reset)."""
    if replace:
        conn.execute("DELETE FROM menu_items")
    conn.executemany(
        "INSERT INTO menu_items (item_name, main_category, sub_category, split, source) "
        "VALUES (?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    return len(rows)


def add_menu_items(conn: sqlite3.Connection, rows) -> int:
    """Append user-provided rows (e.g. from import_dataset.py) without
    touching existing data. rows: iterable of
    (item_name, restaurant_name, main_category, sub_category, split, source)."""
    conn.executemany(
        "INSERT INTO menu_items "
        "(item_name, restaurant_name, main_category, sub_category, split, source) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    return len(rows)


def count_menu_items(conn: sqlite3.Connection, source: str = None) -> int:
    if source is None:
        return conn.execute("SELECT COUNT(*) FROM menu_items").fetchone()[0]
    return conn.execute(
        "SELECT COUNT(*) FROM menu_items WHERE source = ?", (source,)
    ).fetchone()[0]


def fetch_menu_items(conn: sqlite3.Connection, split=None):
    if split is None:
        cur = conn.execute(
            "SELECT item_name, restaurant_name, main_category, sub_category, split, source "
            "FROM menu_items"
        )
    else:
        cur = conn.execute(
            "SELECT item_name, restaurant_name, main_category, sub_category, split, source "
            "FROM menu_items WHERE split = ?",
            (split,),
        )
    return [dict(row) for row in cur.fetchall()]


def db_exists(db_path=DEFAULT_DB_PATH) -> bool:
    return Path(db_path).exists()
