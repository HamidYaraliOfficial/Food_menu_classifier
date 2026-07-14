"""
Category taxonomy for the Persian food/menu classifier.

This module is the single source of truth for:
 - the two-level category tree (cuisine -> food sub-category)
 - keyword phrases used by the rule engine (rule_classifier.py)
 - explicit exceptions for names that the generic "leftmost keyword" rule
   would otherwise get wrong (e.g. "چلو کباب" starts with a rice word but is
   a meat dish; "پیتزا چیزبرگر" contains a burger word but is a pizza).

db.py seeds the SQLite tables from these structures so everything can later
be extended/overridden at the database level (see import_dataset.py) without
touching this file.
"""

from normalize import normalize

# ---------------------------------------------------------------------------
# Level 1: main (cuisine / restaurant) categories
# ---------------------------------------------------------------------------

MAIN_CATEGORIES = [
    "فست‌فود",
    "ایرانی",
    "چینی و آسیایی",
    "دریایی",
    "فرنگی و بین‌الملل",
    "دسر، شیرینی و بستنی",
    "صبحانه",
    "سالاد و رژیمی",
    "نوشیدنی",
]

# Categories that show up on almost every restaurant's menu regardless of its
# cuisine (drinks, desserts). They are excluded when guessing a restaurant's
# overall cuisine from majority vote, since they are not distinguishing.
GENERIC_MAIN_CATEGORIES = {"نوشیدنی", "دسر، شیرینی و بستنی"}

# ---------------------------------------------------------------------------
# Level 2: sub-categories per main category
# ---------------------------------------------------------------------------

SUBCATEGORIES = {
    "فست‌فود": [
        "پیتزا",
        "برگر",
        "ساندویچ",
        "سوخاری",
        "هات‌داگ و سوسیس",
        "سیب‌زمینی و پیش‌غذای فست‌فودی",
    ],
    "ایرانی": [
        "کباب",
        "خورش",
        "پلو و چلو",
        "آش و سوپ ایرانی",
        "دیزی و آبگوشت",
        "پیش‌غذای ایرانی",
    ],
    "چینی و آسیایی": [
        "نودل",
        "برنج و رایس چینی",
        "سوخاری آسیایی",
        "سوپ آسیایی",
        "سوشی",
    ],
    "دریایی": [
        "ماهی",
        "میگو",
        "صدف و اختاپوس",
        "غذای دریایی سرخ‌شده",
    ],
    "فرنگی و بین‌الملل": [
        "پاستا",
        "استیک و گریل",
        "ریزوتو",
        "غذای مکزیکی",
    ],
    "دسر، شیرینی و بستنی": [
        "بستنی و فالوده",
        "کیک و شیرینی",
        "موس و دسر سرد",
        "شیرینی سنتی",
    ],
    "صبحانه": [
        "نان و پنیر و کره",
        "تخم‌مرغ",
        "حلیم",
        "عدسی و آش صبحانه",
    ],
    "سالاد و رژیمی": [
        "سالاد سبز",
        "سالاد سزار",
        "سالاد الویه",
        "باول و غذای رژیمی",
    ],
    "نوشیدنی": [
        "نوشابه",
        "آبمیوه طبیعی",
        "دوغ",
        "چای و قهوه",
        "شیک و اسموتی",
    ],
}

# Reverse lookup: sub_category -> main_category
SUB_TO_MAIN = {
    sub: main for main, subs in SUBCATEGORIES.items() for sub in subs
}

ALL_SUBCATEGORIES = list(SUB_TO_MAIN.keys())

# ---------------------------------------------------------------------------
# Keyword phrases per sub-category.
# Each entry is (phrase, weight). Phrases may be multi-word; they are matched
# token-by-token (see rule_classifier.py) so "برگ" never accidentally matches
# inside "همبرگر" (different tokens), and the same phrase list drives the
# "leftmost match wins" rule.
# ---------------------------------------------------------------------------

KEYWORDS = {
    "پیتزا": [("پیتزا", 1.0), ("پیزا", 1.0), ("pizza", 1.0)],
    "برگر": [
        ("برگر", 1.0), ("همبرگر", 1.0), ("چیزبرگر", 1.0),
        ("دبل برگر", 1.1), ("بیف برگر", 1.1), ("مرغ برگر", 1.1),
        ("burger", 1.0), ("hamburger", 1.0), ("cheeseburger", 1.0),
        ("double burger", 1.1), ("beef burger", 1.1), ("chicken burger", 1.1),
    ],
    "ساندویچ": [
        ("ساندویچ", 1.0), ("ساندویج", 1.0), ("سندویچ", 1.0),
        ("sandwich", 1.0),
    ],
    "سوخاری": [
        ("سوخاری", 1.0), ("کریسپی", 1.0), ("ناگت", 1.0),
        ("مرغ سوخاری", 1.1), ("بال سوخاری", 1.1),
        ("fried chicken", 1.1), ("crispy chicken", 1.1), ("nugget", 1.0),
        ("nuggets", 1.0), ("fried wings", 1.1), ("chicken strips", 1.0),
    ],
    "هات‌داگ و سوسیس": [
        ("هات داگ", 1.0), ("هاتداگ", 1.0), ("سوسیس", 1.0),
        ("سوسیس بندری", 1.1), ("کوکتل", 0.9),
        ("hot dog", 1.0), ("hotdog", 1.0), ("sausage", 1.0),
    ],
    "سیب‌زمینی و پیش‌غذای فست‌فودی": [
        ("سیب زمینی", 1.0), ("چیپس", 1.0), ("نان سیر", 1.0),
        ("پیاز حلقه", 1.0), ("انگشتی", 0.9), ("پنیر سوخاری", 1.0),
        ("french fries", 1.1), ("fries", 1.0), ("onion rings", 1.1),
        ("garlic bread", 1.0), ("cheese sticks", 1.0),
    ],
    "کباب": [
        ("کباب", 1.0), ("جوجه کباب", 1.1), ("کوبیده", 1.0),
        ("برگ", 1.0), ("بختیاری", 1.0), ("چنجه", 1.0),
        ("شیشلیک", 1.0), ("جوجه", 0.8), ("سلطانی", 1.0),
        ("kabab", 1.0), ("kebab", 1.0), ("koobideh", 1.0), ("kubideh", 1.0),
        ("chicken kabab", 1.1), ("joojeh kabab", 1.1), ("bakhtiari", 1.0),
        ("shishlik", 1.0), ("soltani", 1.0),
    ],
    "خورش": [
        ("خورش", 1.0), ("خورشت", 1.0), ("قرمه سبزی", 1.1),
        ("قیمه", 1.0), ("فسنجان", 1.0), ("کرفس", 0.9), ("بامیه خورش", 1.0),
        ("khoresh", 1.0), ("ghormeh sabzi", 1.1), ("gheimeh", 1.0),
        ("fesenjan", 1.0),
    ],
    "پلو و چلو": [
        ("پلو", 1.0), ("چلو", 1.0), ("زرشک پلو", 1.1),
        ("باقالی پلو", 1.1), ("استانبولی پلو", 1.1), ("لوبیا پلو", 1.1),
        ("دمی", 0.9), ("عدس پلو", 1.1),
        ("polo", 1.0), ("chelo", 1.0), ("zereshk polo", 1.1),
        ("baghali polo", 1.1), ("lubia polo", 1.1), ("adas polo", 1.1),
    ],
    "آش و سوپ ایرانی": [
        ("آش", 1.0), ("آش رشته", 1.1), ("آش دوغ", 1.1), ("سوپ جو", 1.0),
        ("ash reshteh", 1.1), ("ash doogh", 1.1), ("barley soup", 1.0),
    ],
    "دیزی و آبگوشت": [
        ("دیزی", 1.0), ("آبگوشت", 1.0), ("dizi", 1.0), ("abgoosht", 1.0),
    ],
    "پیش‌غذای ایرانی": [
        ("کشک بادمجان", 1.2), ("میرزا قاسمی", 1.2), ("ماست و خیار", 1.1),
        ("نخود کباب", 1.1), ("زیتون پرورده", 1.2), ("بادمجان کبابی", 1.1),
        ("کوکو سبزی", 1.1), ("ماست موسیر", 1.1), ("کوکو", 1.0), ("دلمه", 1.0),
        ("kashke bademjan", 1.2), ("mirza ghasemi", 1.2), ("mast o khiar", 1.1),
        ("zeytoon parvardeh", 1.2), ("kuku", 1.0), ("kookoo", 1.0), ("dolma", 1.0),
    ],
    "نودل": [("نودل", 1.0), ("نودلز", 1.0), ("noodle", 1.0), ("noodles", 1.0)],
    "برنج و رایس چینی": [
        ("رایس", 1.0), ("برنج چینی", 1.1), ("فرايد رایس", 1.1), ("فرایدرایس", 1.1),
        ("fried rice", 1.1), ("chinese rice", 1.1),
    ],
    "سوخاری آسیایی": [
        ("کریسپی چینی", 1.2), ("کونگ پائو", 1.2), ("چیلی چیکن", 1.2),
        ("سویت اند ساور", 1.2),
        ("kung pao", 1.2), ("chili chicken", 1.2), ("sweet and sour", 1.2),
        ("crispy chicken chinese style", 1.2),
    ],
    "سوپ آسیایی": [
        ("تام یام", 1.1), ("سوپ تام یام", 1.2), ("سوپ مرغ و ذرت", 1.2),
        ("tom yum", 1.1), ("hot and sour soup", 1.2), ("corn soup", 1.0),
    ],
    "سوشی": [
        ("سوشی", 1.0), ("رول", 0.9), ("ساشیمی", 1.0), ("نیگیری", 1.0),
        ("sushi", 1.0), ("sashimi", 1.0), ("nigiri", 1.0), ("maki", 0.9),
    ],
    "ماهی": [
        ("ماهی", 1.0), ("قزل آلا", 1.1), ("سالمون", 1.0), ("فیله ماهی", 1.1),
        ("fish", 1.0), ("salmon", 1.0), ("trout", 1.0), ("grilled fish", 1.1),
    ],
    "میگو": [("میگو", 1.0), ("shrimp", 1.0), ("prawn", 1.0), ("prawns", 1.0)],
    "صدف و اختاپوس": [
        ("صدف", 1.0), ("اختاپوس", 1.0),
        ("shellfish", 1.0), ("octopus", 1.0), ("oyster", 1.0), ("oysters", 1.0),
    ],
    "غذای دریایی سرخ‌شده": [
        ("ماهی سرخ شده", 1.2), ("میگو سوخاری", 1.2),
        ("fried fish", 1.2), ("fried shrimp", 1.2), ("fish and chips", 1.2),
    ],
    "پاستا": [
        ("پاستا", 1.0), ("اسپاگتی", 1.0), ("پنه", 1.0),
        ("لازانیا", 1.0), ("فتوچینی", 1.0), ("ماکارونی", 1.0),
        ("pasta", 1.0), ("spaghetti", 1.0), ("penne", 1.0), ("lasagna", 1.0),
        ("fettuccine", 1.0), ("macaroni", 1.0),
    ],
    "استیک و گریل": [
        ("استیک", 1.0), ("گریل", 0.9), ("فیله مینیون", 1.1), ("تیبون", 1.1),
        ("steak", 1.0), ("filet mignon", 1.1), ("t-bone", 1.1), ("tbone", 1.1),
    ],
    "ریزوتو": [("ریزوتو", 1.0), ("risotto", 1.0)],
    "غذای مکزیکی": [
        ("بوریتو", 1.0), ("تاکو", 1.0), ("فاهیتا", 1.0),
        ("انچیلادا", 1.0), ("کسادیا", 1.0),
        ("burrito", 1.0), ("taco", 1.0), ("tacos", 1.0), ("fajita", 1.0),
        ("enchilada", 1.0), ("quesadilla", 1.0),
    ],
    "بستنی و فالوده": [
        ("بستنی", 1.0), ("فالوده", 1.0),
        ("ice cream", 1.0), ("faloodeh", 1.0), ("gelato", 1.0),
    ],
    "کیک و شیرینی": [
        ("کیک", 1.0), ("چیز کیک", 1.1), ("براونی", 1.0),
        ("cake", 1.0), ("cheesecake", 1.1), ("brownie", 1.0),
    ],
    "موس و دسر سرد": [
        ("موس", 1.0), ("تیرامیسو", 1.0), ("پودینگ", 1.0), ("پاناکوتا", 1.0),
        ("mousse", 1.0), ("tiramisu", 1.0), ("pudding", 1.0), ("panna cotta", 1.0),
    ],
    "شیرینی سنتی": [
        ("باقلوا", 1.0), ("زولبیا", 1.0), ("بامیه", 1.0), ("گز", 1.0),
        ("baklava", 1.0), ("zoolbia", 1.0), ("bamieh", 1.0), ("gaz", 1.0),
    ],
    "نان و پنیر و کره": [
        ("نان و پنیر", 1.1), ("کره و مربا", 1.1), ("پنیر و گردو", 1.1),
        ("نان بربری", 1.1), ("نان تافتون", 1.1), ("نان تست", 1.0), ("سنگک", 1.0),
        ("bread and cheese", 1.1), ("butter and jam", 1.1), ("cheese and walnut", 1.1),
        ("toast", 1.0), ("sangak", 1.0), ("barbari bread", 1.1),
    ],
    "تخم‌مرغ": [
        ("تخم مرغ", 1.0), ("املت", 1.0), ("نیمرو", 1.0),
        ("egg", 1.0), ("eggs", 1.0), ("omelette", 1.0), ("omelet", 1.0),
        ("sunny side up", 1.1),
    ],
    "حلیم": [("حلیم", 1.0), ("halim", 1.0), ("haleem", 1.0)],
    "عدسی و آش صبحانه": [
        ("عدسی", 1.0), ("حریره بادام", 1.1),
        ("lentil soup", 1.1), ("adasi", 1.0), ("harireh badam", 1.1),
    ],
    "سالاد سبز": [
        ("سالاد سبز", 1.1), ("سالاد کاهو", 1.1), ("سالاد فصل", 1.1), ("سالاد شیرازی", 1.1),
        ("green salad", 1.1), ("garden salad", 1.1), ("shirazi salad", 1.1),
    ],
    "سالاد سزار": [
        ("سزار", 1.0), ("سالاد سزار", 1.1),
        ("caesar", 1.0), ("caesar salad", 1.1),
    ],
    "سالاد الویه": [
        ("الویه", 1.0), ("سالاد الویه", 1.1),
        ("olivieh", 1.0), ("olivier salad", 1.1),
    ],
    "باول و غذای رژیمی": [
        ("باول", 1.0), ("رژیمی", 1.0), ("کتوژنیک", 1.0), ("بدون قند", 1.0),
        ("bowl", 1.0), ("diet food", 1.0), ("keto", 1.0), ("sugar free", 1.0),
    ],
    "نوشابه": [
        ("نوشابه", 1.0), ("کوکاکولا", 1.0), ("اسپرایت", 1.0), ("فانتا", 1.0),
        ("soda", 1.0), ("coca cola", 1.0), ("cola", 0.9), ("sprite", 1.0), ("fanta", 1.0),
    ],
    "آبمیوه طبیعی": [
        ("آبمیوه", 1.0), ("آب پرتقال", 1.1), ("آب هویج", 1.1),
        ("juice", 1.0), ("orange juice", 1.1), ("carrot juice", 1.1),
    ],
    "دوغ": [("دوغ", 1.0), ("doogh", 1.0), ("yogurt drink", 1.0)],
    "چای و قهوه": [
        ("چای", 1.0), ("قهوه", 1.0), ("اسپرسو", 1.0), ("لاته", 1.0), ("کاپوچینو", 1.0),
        ("tea", 1.0), ("coffee", 1.0), ("espresso", 1.0), ("latte", 1.0),
        ("cappuccino", 1.0), ("americano", 1.0),
    ],
    "شیک و اسموتی": [
        ("شیک", 1.0), ("میلک شیک", 1.1), ("اسموتی", 1.0),
        ("shake", 1.0), ("milkshake", 1.1), ("smoothie", 1.0),
    ],
}

# ---------------------------------------------------------------------------
# Explicit exceptions: contiguous token sequences that must win over whatever
# the generic leftmost-keyword rule would otherwise pick. Checked first and
# in order (longest phrase first), before any keyword scan.
# ---------------------------------------------------------------------------

EXCEPTIONS = [
    # Pizza named after a burger flavor -> still pizza, not burger.
    ("پیتزا چیزبرگر", "پیتزا"),
    ("پیتزا همبرگر", "پیتزا"),
    ("پیتزا مخصوص همبرگر", "پیتزا"),
    # "چلو" + meat word -> a kabab/khoresh combo plate, not a rice dish.
    ("چلو کباب", "کباب"),
    ("چلو خورش", "خورش"),
    ("چلو جوجه", "کباب"),
    ("چلوکباب", "کباب"),
    # Well-known Iranian dish names, kept explicit for clarity/safety net.
    ("کشک بادمجان", "پیش‌غذای ایرانی"),
    ("سالاد شیرازی", "سالاد سبز"),
    ("زیتون پرورده", "پیش‌غذای ایرانی"),
    # English/transliterated equivalents of the exceptions above.
    ("pizza cheeseburger", "پیتزا"),
    ("pizza hamburger", "پیتزا"),
    ("chelo kabab", "کباب"),
    ("chelo koobideh", "کباب"),
    ("chelo khoresh", "خورش"),
    ("chelo joojeh", "کباب"),
    ("polo kabab", "کباب"),
    ("kashke bademjan", "پیش‌غذای ایرانی"),
    ("shirazi salad", "سالاد سبز"),
    ("zeytoon parvardeh", "پیش‌غذای ایرانی"),
]

# ---------------------------------------------------------------------------
# English display labels for main/sub categories - used only by the web UI
# and documentation, never by the classifier itself (which always keys on
# the canonical Persian names above).
# ---------------------------------------------------------------------------

CATEGORY_LABELS_EN = {
    "فست‌فود": "Fast Food",
    "ایرانی": "Iranian",
    "چینی و آسیایی": "Chinese & Asian",
    "دریایی": "Seafood",
    "فرنگی و بین‌الملل": "Western & International",
    "دسر، شیرینی و بستنی": "Dessert, Pastry & Ice Cream",
    "صبحانه": "Breakfast",
    "سالاد و رژیمی": "Salad & Diet",
    "نوشیدنی": "Beverages",
    "پیتزا": "Pizza",
    "برگر": "Burger",
    "ساندویچ": "Sandwich",
    "سوخاری": "Fried Chicken",
    "هات‌داگ و سوسیس": "Hot Dog & Sausage",
    "سیب‌زمینی و پیش‌غذای فست‌فودی": "Fries & Fast-Food Sides",
    "کباب": "Kabab",
    "خورش": "Khoresh (Persian Stew)",
    "پلو و چلو": "Rice (Polo/Chelo)",
    "آش و سوپ ایرانی": "Persian Ash & Soup",
    "دیزی و آبگوشت": "Dizi & Abgoosht",
    "پیش‌غذای ایرانی": "Persian Appetizers",
    "نودل": "Noodles",
    "برنج و رایس چینی": "Chinese Rice",
    "سوخاری آسیایی": "Asian Fried Chicken",
    "سوپ آسیایی": "Asian Soup",
    "سوشی": "Sushi",
    "ماهی": "Fish",
    "میگو": "Shrimp",
    "صدف و اختاپوس": "Shellfish & Octopus",
    "غذای دریایی سرخ‌شده": "Fried Seafood",
    "پاستا": "Pasta",
    "استیک و گریل": "Steak & Grill",
    "ریزوتو": "Risotto",
    "غذای مکزیکی": "Mexican Food",
    "بستنی و فالوده": "Ice Cream & Faloodeh",
    "کیک و شیرینی": "Cake & Pastry",
    "موس و دسر سرد": "Mousse & Cold Dessert",
    "شیرینی سنتی": "Traditional Sweets",
    "نان و پنیر و کره": "Bread, Cheese & Butter",
    "تخم‌مرغ": "Eggs",
    "حلیم": "Halim",
    "عدسی و آش صبحانه": "Lentil Soup & Breakfast Ash",
    "سالاد سبز": "Green Salad",
    "سالاد سزار": "Caesar Salad",
    "سالاد الویه": "Olivieh Salad",
    "باول و غذای رژیمی": "Bowl & Diet Food",
    "نوشابه": "Soda",
    "آبمیوه طبیعی": "Fresh Juice",
    "دوغ": "Doogh (Yogurt Drink)",
    "چای و قهوه": "Tea & Coffee",
    "شیک و اسموتی": "Shake & Smoothie",
}


def label_en(category_name):
    """English display label for a Persian main/sub category name, falling
    back to the Persian name itself if no translation is registered."""
    return CATEGORY_LABELS_EN.get(category_name, category_name)


def normalized_keyword_index():
    """Build {normalized phrase: [(sub_category, weight), ...]} for lookup."""
    index = {}
    for sub, phrases in KEYWORDS.items():
        for phrase, weight in phrases:
            norm = normalize(phrase)
            index.setdefault(norm, []).append((sub, weight))
    return index


def normalized_exceptions():
    """Return exceptions as (tuple_of_tokens, sub_category), longest first."""
    result = []
    for phrase, sub in EXCEPTIONS:
        tokens = tuple(normalize(phrase).split())
        result.append((tokens, sub))
    result.sort(key=lambda item: len(item[0]), reverse=True)
    return result
