"""CLI: evaluate the hybrid classifier's accuracy on the split='test' rows
of the database (never seen during ML training).

Usage:
  python evaluate.py
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

import db
from hybrid_classifier import HybridClassifier

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default=str(db.DEFAULT_DB_PATH))
    parser.add_argument("--model", default=None)
    args = parser.parse_args()

    conn = db.get_connection(Path(args.db))
    test_rows = db.fetch_menu_items(conn, split="test")
    conn.close()

    if not test_rows:
        print("[evaluate] no split='test' rows found - run train.py --init first", file=sys.stderr)
        sys.exit(1)

    classifier = HybridClassifier(model_path=Path(args.model) if args.model else None)

    total = len(test_rows)
    main_correct = 0
    sub_correct = 0
    method_counts = Counter()
    mistakes = []

    for row in test_rows:
        result = classifier.classify_item(row["item_name"])
        method_counts[result.method] += 1
        if result.main_category == row["main_category"]:
            main_correct += 1
        if result.sub_category == row["sub_category"]:
            sub_correct += 1
        else:
            mistakes.append((row["item_name"], row["sub_category"], result.sub_category, result.method))

    print(f"تعداد نمونه‌های تست: {total}")
    print(f"دقت دسته‌ی اصلی (main_category): {main_correct}/{total} = {main_correct / total * 100:.1f}%")
    print(f"دقت زیردسته (sub_category):      {sub_correct}/{total} = {sub_correct / total * 100:.1f}%")
    print()
    print("روش استفاده‌شده برای پیش‌بینی:")
    for method, count in method_counts.most_common():
        print(f"  {method}: {count}")

    if mistakes:
        print(f"\nموارد اشتباه در زیردسته ({len(mistakes)}):")
        for name, expected, predicted, method in mistakes:
            print(f"  {name!r}: انتظار={expected!r} پیش‌بینی={predicted!r} (روش={method})")


if __name__ == "__main__":
    main()
