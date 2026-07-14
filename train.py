"""CLI: build/seed the database and train the ML fallback model.

Usage:
  python train.py --init                 # create db + seed taxonomy + synthetic data (once)
  python train.py --init --reset         # also wipe any previously imported menu_items
  python train.py --train-model          # (re)train the ML model from split='train' rows
  python train.py --init --train-model   # do both in one go
"""

import argparse
import sys
from pathlib import Path

import db
import seed_data
import seed_data_en
from ml_classifier import MLClassifier, DEFAULT_MODEL_PATH

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def run_init(db_path, reset: bool):
    conn = db.get_connection(db_path)
    db.init_schema(conn)
    db.reseed_taxonomy(conn)

    if reset:
        fa_rows = seed_data.get_seed_rows()
        en_rows = seed_data_en.get_seed_rows()
        db.seed_menu_items(conn, fa_rows, replace=True)
        db.add_menu_items(conn, en_rows)
        print(f"[train] reset menu_items and inserted {len(fa_rows)} Persian + "
              f"{len(en_rows)} English synthetic rows")
    else:
        # Persian (fa) and English (en) synthetic sets are seeded
        # independently and additively, so re-running --init on an existing
        # database only fills in whichever language is still missing,
        # without touching Persian data, English data, or user imports.
        fa_count = db.count_menu_items(conn, source="synthetic")
        if fa_count == 0:
            fa_rows = seed_data.get_seed_rows()
            db.seed_menu_items(conn, fa_rows, replace=False)
            print(f"[train] seeded menu_items with {len(fa_rows)} Persian synthetic rows")
        else:
            print(f"[train] Persian synthetic data already present ({fa_count} rows), leaving as-is")

        en_count = db.count_menu_items(conn, source="synthetic_en")
        if en_count == 0:
            en_rows = seed_data_en.get_seed_rows()
            db.add_menu_items(conn, en_rows)
            print(f"[train] seeded menu_items with {len(en_rows)} English synthetic rows")
        else:
            print(f"[train] English synthetic data already present ({en_count} rows), leaving as-is")

    conn.close()


def run_train_model(db_path, model_path):
    conn = db.get_connection(db_path)
    train_rows = db.fetch_menu_items(conn, split="train")
    conn.close()

    if not train_rows:
        print("[train] no split='train' rows found - run --init first", file=sys.stderr)
        sys.exit(1)

    names = [r["item_name"] for r in train_rows]
    subs = [r["sub_category"] for r in train_rows]

    model = MLClassifier()
    model.train(names, subs)
    model.save(model_path)
    print(f"[train] trained ML model on {len(names)} rows -> {model_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default=str(db.DEFAULT_DB_PATH), help="path to sqlite db file")
    parser.add_argument("--model", default=str(DEFAULT_MODEL_PATH), help="path to save model.joblib")
    parser.add_argument("--init", action="store_true", help="create/seed the database")
    parser.add_argument("--reset", action="store_true", help="wipe menu_items before reseeding (with --init)")
    parser.add_argument("--train-model", action="store_true", help="train the ML fallback model")
    args = parser.parse_args()

    if not args.init and not args.train_model:
        parser.print_help()
        return

    if args.init:
        run_init(Path(args.db), reset=args.reset)
    if args.train_model:
        run_train_model(Path(args.db), Path(args.model))


if __name__ == "__main__":
    main()
