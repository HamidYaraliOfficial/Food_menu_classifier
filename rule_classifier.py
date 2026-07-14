"""Rule-based classifier: explicit exceptions + "leftmost keyword wins".

Matching is token-based (never raw substring), so a keyword like "برگ"
(brisk grilled skewer) never accidentally fires inside "همبرگر" (hamburger) -
they are different tokens even though "برگ" is a character-substring of
"برگر".

Order of checks for a given item name:
  1. Explicit exceptions (taxonomy.EXCEPTIONS) - longest phrase first.
     These exist for names where the first significant word is misleading,
     e.g. "چلو کباب کوبیده" starts with the rice word "چلو" but the dish is
     a kabab plate, not a rice dish.
  2. Leftmost keyword match: scan the name's tokens left to right; at each
     position, try the longest keyword phrase (up to 3 tokens) first. The
     first position that matches anything wins. This is what makes
     "پیتزا چیزبرگر" resolve to پیتزا: the "پیتزا" token at position 0
     matches immediately, before "چیزبرگر" (a burger keyword) is ever
     reached at position 1.
  3. If nothing matched at all, return None so the caller can fall back to
     the ML model.
"""

from dataclasses import dataclass
from typing import Optional

import taxonomy
from normalize import tokenize


@dataclass
class RuleResult:
    main_category: str
    sub_category: str
    method: str  # "exception" | "rule"
    confidence: float
    matched_phrase: str


class RuleClassifier:
    def __init__(self):
        self._keyword_index = taxonomy.normalized_keyword_index()
        self._exceptions = taxonomy.normalized_exceptions()
        self._max_phrase_tokens = max(
            (len(phrase.split()) for phrase in self._keyword_index),
            default=1,
        )

    def _match_exception(self, tokens):
        n = len(tokens)
        for ex_tokens, sub in self._exceptions:
            k = len(ex_tokens)
            if k == 0 or k > n:
                continue
            for start in range(0, n - k + 1):
                if tuple(tokens[start:start + k]) == ex_tokens:
                    return sub, " ".join(ex_tokens)
        return None

    def _match_leftmost_keyword(self, tokens):
        n = len(tokens)
        for start in range(n):
            max_len = min(self._max_phrase_tokens, n - start)
            for length in range(max_len, 0, -1):
                phrase = " ".join(tokens[start:start + length])
                candidates = self._keyword_index.get(phrase)
                if candidates:
                    sub, weight = max(candidates, key=lambda c: c[1])
                    return sub, weight, phrase
        return None

    def classify(self, name: str) -> Optional[RuleResult]:
        tokens = tokenize(name)
        if not tokens:
            return None

        exception_hit = self._match_exception(tokens)
        if exception_hit:
            sub, phrase = exception_hit
            return RuleResult(
                main_category=taxonomy.SUB_TO_MAIN[sub],
                sub_category=sub,
                method="exception",
                confidence=0.99,
                matched_phrase=phrase,
            )

        keyword_hit = self._match_leftmost_keyword(tokens)
        if keyword_hit:
            sub, weight, phrase = keyword_hit
            confidence = min(0.97, 0.75 + 0.1 * weight)
            return RuleResult(
                main_category=taxonomy.SUB_TO_MAIN[sub],
                sub_category=sub,
                method="rule",
                confidence=confidence,
                matched_phrase=phrase,
            )

        return None
