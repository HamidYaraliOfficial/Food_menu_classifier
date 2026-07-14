"""Simple Flask web UI for the hybrid food/menu classifier.

Lets a user paste one item or a whole menu (one item per line) into a
textarea and see the classification result for each line, plus the guessed
overall cuisine when more than one item is given.

Usage:
  python app.py
  (then open http://127.0.0.1:5000/)
"""

from flask import Flask, render_template, request

import taxonomy
from hybrid_classifier import HybridClassifier

app = Flask(__name__)
classifier = HybridClassifier()

EXAMPLE_TEXT = "پیتزا چیز برگر\nChelo Kabab Koobideh\nCaesar Salad\nدوغ محلی"


def _row_for_template(result):
    return {
        "input": result.input,
        "main_fa": result.main_category,
        "main_en": taxonomy.label_en(result.main_category) if result.main_category else None,
        "sub_fa": result.sub_category,
        "sub_en": taxonomy.label_en(result.sub_category) if result.sub_category else None,
        "method": result.method,
        "confidence_pct": round(result.confidence * 100),
        "is_confident": result.is_confident,
        "matched_phrase": result.matched_phrase,
    }


@app.route("/", methods=["GET", "POST"])
def index():
    items_text = EXAMPLE_TEXT
    rows = None
    cuisine = None
    cuisine_en = None
    distribution = None

    if request.method == "POST":
        items_text = request.form.get("items_text", "")
        item_names = [line.strip() for line in items_text.splitlines() if line.strip()]

        if item_names:
            outcome = classifier.classify_menu(item_names)
            rows = [_row_for_template(r) for r in outcome["items"]]
            if len(item_names) > 1:
                cuisine = outcome["predicted_cuisine"]
                cuisine_en = taxonomy.label_en(cuisine) if cuisine else None
                distribution = [
                    (cat, taxonomy.label_en(cat), count)
                    for cat, count in outcome["cuisine_distribution"]
                ]

    return render_template(
        "index.html",
        items_text=items_text,
        rows=rows,
        cuisine=cuisine,
        cuisine_en=cuisine_en,
        distribution=distribution,
    )


if __name__ == "__main__":
    app.run(debug=True)
