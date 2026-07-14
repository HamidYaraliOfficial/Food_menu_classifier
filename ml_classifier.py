"""ML fallback classifier for food/menu items that the rule engine does not
confidently recognize (new dish names, spelling variants, typos, etc.).

Uses character n-gram TF-IDF (good for Persian without needing a
stemmer/tokenizer - it generalizes across prefixes/suffixes and small
spelling variations) + a linear SVM, wrapped so it outputs a probability-like
confidence via CalibratedClassifierCV.

Predicts the sub_category directly; the main_category is derived from
taxonomy.SUB_TO_MAIN.
"""

from pathlib import Path

import joblib
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer

import taxonomy
from normalize import normalize

DEFAULT_MODEL_PATH = Path(__file__).parent / "model.joblib"


def _build_pipeline(cv: int) -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(2, 4),
            min_df=1,
        )),
        ("clf", CalibratedClassifierCV(
            estimator=LinearSVC(class_weight="balanced"),
            cv=cv,
        )),
    ])


class MLClassifier:
    def __init__(self, pipeline: Pipeline = None):
        self.pipeline = pipeline

    @property
    def is_trained(self) -> bool:
        return self.pipeline is not None

    def train(self, item_names, sub_categories):
        """item_names: list[str] raw names. sub_categories: list[str] labels.
        Requires at least 2 examples per class for the internal cross
        validation used to calibrate confidences; classes with fewer
        examples are dropped with a warning."""
        from collections import Counter

        counts = Counter(sub_categories)
        usable = [i for i, sub in enumerate(sub_categories) if counts[sub] >= 2]
        dropped = len(sub_categories) - len(usable)
        if dropped:
            print(f"[ml_classifier] warning: dropped {dropped} example(s) "
                  f"from classes with fewer than 2 training rows")

        texts = [normalize(item_names[i]) for i in usable]
        labels = [sub_categories[i] for i in usable]

        min_class_count = min(Counter(labels).values())
        cv = max(2, min(3, min_class_count))

        pipeline = _build_pipeline(cv=cv)
        pipeline.fit(texts, labels)
        self.pipeline = pipeline
        return self

    def predict(self, name: str):
        """Return (sub_category, confidence) or (None, 0.0) if untrained."""
        if not self.is_trained:
            return None, 0.0
        text = normalize(name)
        proba = self.pipeline.predict_proba([text])[0]
        classes = self.pipeline.classes_
        best_idx = proba.argmax()
        return classes[best_idx], float(proba[best_idx])

    def save(self, path=DEFAULT_MODEL_PATH):
        joblib.dump(self.pipeline, path)

    @classmethod
    def load(cls, path=DEFAULT_MODEL_PATH):
        if not Path(path).exists():
            return cls(pipeline=None)
        pipeline = joblib.load(path)
        return cls(pipeline=pipeline)


def sub_to_main(sub_category: str) -> str:
    return taxonomy.SUB_TO_MAIN.get(sub_category, "نامشخص")
