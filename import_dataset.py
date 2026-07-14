"""CLI: import the user's own labeled menu-item dataset into the database,
on top of (not instead of) the synthetic seed data.

Expected CSV columns (header row required):
  item_name        (required) the raw food/dish name, e.g. "پیتزا مخصوص"
  sub_category      (required) must be one of the sub-categories in
                    taxonomy.SUBCATEGORIES (run --list-categories to see them)
  main_category     (optional) if given, must match the sub_category's real
                    main category - otherwise it is derived automatically
  restaurant_name    (optional)
  split             (optional) "train" or "test", default "train"

Usage:
  python import_dataset.py --csv mydata.csv
  python import_dataset.py --csv mydata.csv --split test
  python import_dataset.py --list-categories
"""

import argparse
import csv
import sys
from pathlib import Path

import db
import taxonomy

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def list_categories():
    for main, subs in taxonomy.SUBCATEGORIES.items():
        print(main)
        for sub in subs:
            print(f"  - {sub}")


def load_rows(csv_path, default_split):
    rows = []
    errors = []
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for line_no, record in enumerate(reader, start=2):
            item_name = (record.get("item_name") or "").strip()
            sub_category = (record.get("sub_category") or "").strip()
            restaurant_name = (record.get("restaurant_name") or "").strip() or None
            split = (record.get("split") or default_split).strip()
            main_category_given = (record.get("main_category") or "").strip()

            if not item_name or not sub_category:
                errors.append(f"line {line_no}: item_name/sub_category missing, skipped")
                continue
            if sub_category not in taxonomy.SUB_TO_MAIN:
                errors.append(
                    f"line {line_no}: unknown sub_category '{sub_category}' "
                    f"(see --list-categories), skipped"
                )
                continue
            if split not in ("train", "test"):
                errors.append(f"line {line_no}: split must be train/test, got '{split}', skipped")
                continue

            main_category = taxonomy.SUB_TO_MAIN[sub_category]
            if main_category_given and main_category_given != main_category:
                errors.append(
                    f"line {line_no}: main_category '{main_category_given}' does not match "
                    f"'{sub_category}' -> using '{main_category}' instead"
                )

            rows.append((item_name, restaurant_name, main_category, sub_category, split, "user_import"))

    return rows, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--csv", help="path to your labeled CSV file")
    parser.add_argument("--db", default=str(db.DEFAULT_DB_PATH), help="path to sqlite db file")
    parser.add_argument("--split", default="train", choices=["train", "test"],
                         help="default split for rows that don't specify one")
    parser.add_argument("--list-categories", action="store_true",
                         help="print all valid main/sub category names and exit")
    args = parser.parse_args()

    if args.list_categories:
        list_categories()
        return

    if not args.csv:
        parser.error("--csv is required (or use --list-categories)")

    rows, errors = load_rows(Path(args.csv), args.split)
    for err in errors:
        print(f"[import] {err}", file=sys.stderr)

    if not rows:
        print("[import] nothing valid to import", file=sys.stderr)
        sys.exit(1)

    conn = db.get_connection(Path(args.db))
    db.init_schema(conn)
    db.add_menu_items(conn, rows)
    conn.close()
    print(f"[import] added {len(rows)} row(s) to {args.db} "
          f"(run train.py --train-model to retrain on the updated data)")


if __name__ == "__main__":
    main()
