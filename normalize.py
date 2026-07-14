"""Persian text normalization shared by the rule engine, the ML model and the
database seeding code, so keywords, training data and user input all line up
on the same representation.

All special characters are referenced via explicit \\uXXXX escapes rather
than pasted literally, since zero-width/directional marks are invisible and
easy to corrupt in a source file.
"""

import re

# Arabic-style letters that commonly appear in typed Persian text but should
# be unified to their standard Persian form.
_CHAR_MAP = {
    "ي": "ی",  # ي -> ی
    "ك": "ک",  # ك -> ک
    "ة": "ه",  # ة -> ه
    "ۀ": "ه",  # ۀ -> ه
    "ء": "",        # standalone hamza ء, drop
}

# Arabic diacritics (harakat/tashkeel) - not meaningful for matching.
_DIACRITICS_RE = re.compile("[ً-ْٰ]")

# Any kind of whitespace-like character (regular space, ZWNJ/half-space,
# no-break space, various unicode spaces) collapses to a single space.
_SPACE_CHARS = (
    "​‌‍‎‏"  # zero-width / directional marks
    "  　"              # no-break / narrow / ideographic space
    + "".join(chr(c) for c in range(0x2000, 0x200B))  # general punctuation spaces
)
_SPACE_RE = re.compile("[" + _SPACE_CHARS + "]+")

# Punctuation that never carries category meaning.
_PUNCT_RE = re.compile(r"[.,!?؟،؛:\"'`\(\)\[\]{}\-_/\\|+*%]+")

_MULTI_SPACE_RE = re.compile(r"\s+")


def normalize(text: str) -> str:
    """Normalize a Persian food/menu string for keyword and ML matching.

    - Unifies Arabic look-alike letters to Persian.
    - Strips diacritics.
    - Turns ZWNJ/half-spaces and other unicode spaces into plain spaces
      (so compound words like "سیب‌زمینی" tokenize the same as "سیب زمینی").
    - Removes punctuation and collapses whitespace.
    - Lowercases any Latin characters that might be mixed in.
    """
    if text is None:
        return ""
    result = text.strip()
    for src, dst in _CHAR_MAP.items():
        result = result.replace(src, dst)
    result = _DIACRITICS_RE.sub("", result)
    result = _SPACE_RE.sub(" ", result)
    result = _PUNCT_RE.sub(" ", result)
    result = result.lower()
    result = _MULTI_SPACE_RE.sub(" ", result).strip()
    return result


def tokenize(text: str) -> list:
    normalized = normalize(text)
    return normalized.split() if normalized else []
