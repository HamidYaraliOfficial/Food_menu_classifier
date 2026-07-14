"""CLI: classify one or more food/menu item names, or a whole menu file.

Usage:
  python predict.py "پیتزا چیز برگر"
  python predict.py "پیتزا چیز برگر" "چلو کباب کوبیده" "دوغ"
  python predict.py --menu-file sample_menu.csv
  python predict.py --menu-file my_items.txt
"""

import argparse
import csv
import sys
from pathlib import Path

from hybrid_classifier import HybridClassifier, ClassificationResult

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def read_menu_file(path: Path):
    if path.suffix.lower() == ".csv":
        with open(path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames and "item_name" in reader.fieldnames:
                return [row["item_name"].strip() for row in reader if row.get("item_name", "").strip()]
            f.seek(0)
            plain_reader = csv.reader(f)
            return [row[0].strip() for row in plain_reader if row and row[0].strip()]
    with open(path, encoding="utf-8-sig") as f:
        return [line.strip() for line in f if line.strip()]


def format_result(r: ClassificationResult) -> str:
    if r.method == "unknown":
        guess = f" (نزدیک‌ترین حدس: {r.sub_category})" if r.sub_category else ""
        return f"{r.input:<30} -> نامشخص{guess}"
    conf_pct = f"{r.confidence * 100:.0f}%"
    extra = f"  [{r.matched_phrase}]" if r.matched_phrase else ""
    return (f"{r.input:<30} -> {r.main_category} / {r.sub_category} "
            f"  (روش: {r.method}, اطمینان: {conf_pct}){extra}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("items", nargs="*", help="one or more food/dish names")
    parser.add_argument("--menu-file", help="path to a .csv (item_name column) or .txt (one item per line) menu file")
    parser.add_argument("--model", default=None, help="path to a trained model.joblib (default: ./model.joblib)")
    args = parser.parse_args()

    if not args.items and not args.menu_file:
        parser.print_help()
        return

    classifier = HybridClassifier(model_path=Path(args.model) if args.model else None)

    if args.menu_file:
        item_names = read_menu_file(Path(args.menu_file))
        outcome = classifier.classify_menu(item_names)
        for r in outcome["items"]:
            print(format_result(r))
        print()
        print("توزیع دسته‌های اصلی (بدون احتساب موارد عمومی مثل نوشیدنی/دسر مگر اینکه کل منو همان باشد):")
        for cat, count in outcome["cuisine_distribution"]:
            print(f"  {cat}: {count}")
        print(f"\nحدس دسته‌ی اصلی/کوزین رستوران: {outcome['predicted_cuisine']}")
    else:
        for name in args.items:
            print(format_result(classifier.classify_item(name)))


if __name__ == "__main__":
    main()
