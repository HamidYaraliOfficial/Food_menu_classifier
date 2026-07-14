"""Combines the rule engine (taxonomy exceptions + leftmost keyword match)
with the ML fallback model into a single entry point, plus a restaurant/menu
-level aggregation that guesses the overall cuisine of a whole menu.
"""

from collections import Counter
from dataclasses import dataclass, field
from typing import List, Optional

import taxonomy
from rule_classifier import RuleClassifier
from ml_classifier import MLClassifier

# Below this ML confidence, we still report the model's best guess but flag
# it as not confident rather than presenting it as a firm answer.
UNKNOWN_CONFIDENCE_THRESHOLD = 0.25


@dataclass
class ClassificationResult:
    input: str
    main_category: Optional[str]
    sub_category: Optional[str]
    method: str  # "exception" | "rule" | "ml" | "unknown"
    confidence: float
    is_confident: bool
    matched_phrase: Optional[str] = None


class HybridClassifier:
    def __init__(self, model_path=None):
        self.rules = RuleClassifier()
        self.ml = MLClassifier.load(model_path) if model_path else MLClassifier.load()

    def classify_item(self, name: str) -> ClassificationResult:
        name = (name or "").strip()
        if not name:
            return ClassificationResult(
                input=name, main_category=None, sub_category=None,
                method="unknown", confidence=0.0, is_confident=False,
            )

        rule_result = self.rules.classify(name)
        if rule_result is not None:
            return ClassificationResult(
                input=name,
                main_category=rule_result.main_category,
                sub_category=rule_result.sub_category,
                method=rule_result.method,
                confidence=rule_result.confidence,
                is_confident=True,
                matched_phrase=rule_result.matched_phrase,
            )

        sub, confidence = self.ml.predict(name)
        if sub is None:
            return ClassificationResult(
                input=name, main_category=None, sub_category=None,
                method="unknown", confidence=0.0, is_confident=False,
            )

        main = taxonomy.SUB_TO_MAIN.get(sub, "نامشخص")
        is_confident = confidence >= UNKNOWN_CONFIDENCE_THRESHOLD
        return ClassificationResult(
            input=name,
            main_category=main if is_confident else None,
            sub_category=sub,  # always show the model's best guess
            method="ml" if is_confident else "unknown",
            confidence=confidence,
            is_confident=is_confident,
        )

    def classify_menu(self, item_names: List[str]):
        """Classify every item of a restaurant's menu, then guess the
        restaurant's overall cuisine(s) by majority vote over main_category,
        ignoring categories that show up on almost every menu (drinks,
        desserts) unless that is literally all the menu has."""
        results = [self.classify_item(name) for name in item_names]

        main_counts = Counter(
            r.main_category for r in results
            if r.main_category and r.is_confident
        )
        distinguishing = Counter({
            cat: n for cat, n in main_counts.items()
            if cat not in taxonomy.GENERIC_MAIN_CATEGORIES
        })

        vote_source = distinguishing if distinguishing else main_counts
        distribution = vote_source.most_common()
        predicted_cuisine = distribution[0][0] if distribution else "نامشخص"

        return {
            "items": results,
            "cuisine_distribution": distribution,
            "predicted_cuisine": predicted_cuisine,
        }
