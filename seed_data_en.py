"""Synthetic, hand-labeled English/transliterated menu-item dataset used to
seed the database's menu_items table (both the "training" and "test" data -
see the `split` column in db.py).

This mirrors seed_data.py but in English, so the rule engine and the ML
fallback model both work on English-language and transliterated-Persian menu
items (e.g. "Cheeseburger", "Chelo Kabab Koobideh") in addition to the
original Persian dataset. It is appended on top of the Persian data - see
`source="synthetic_en"` below - it never replaces it.

Users can add their own labeled data on top of this with import_dataset.py,
same as with the Persian dataset.
"""

import random

import taxonomy

# (item_name, sub_category) - main_category is derived from taxonomy.SUB_TO_MAIN
RAW_ITEMS = [
    # --- Fast Food ---------------------------------------------------------
    ("Margherita Pizza", "پیتزا"),
    ("Pepperoni Pizza", "پیتزا"),
    ("Vegetable Pizza", "پیتزا"),
    ("Mixed Pizza", "پیتزا"),
    ("Pizza Cheeseburger", "پیتزا"),          # exception case
    ("Pizza Hamburger", "پیتزا"),             # exception case
    ("Four Seasons Pizza", "پیتزا"),
    ("Family Special Pizza", "پیتزا"),

    ("Classic Hamburger", "برگر"),
    ("Cheeseburger", "برگر"),
    ("Double Cheeseburger", "برگر"),
    ("Chicken Burger", "برگر"),
    ("Royal Burger", "برگر"),
    ("Mushroom Cheese Burger", "برگر"),
    ("American Beef Burger", "برگر"),

    ("Chicken Sandwich", "ساندویچ"),
    ("Fillet Chicken Sandwich", "ساندویچ"),
    ("Cold Cuts Sandwich", "ساندویچ"),
    ("Ham Sandwich", "ساندویچ"),
    ("Club Sandwich", "ساندویچ"),

    ("Fried Chicken", "سوخاری"),
    ("Fried Chicken Wings", "سوخاری"),
    ("Fried Chicken Thigh", "سوخاری"),
    ("Chicken Nuggets", "سوخاری"),
    ("Crispy Chicken Strips", "سوخاری"),

    ("Classic Hot Dog", "هات‌داگ و سوسیس"),
    ("Double Hot Dog", "هات‌داگ و سوسیس"),
    ("Grilled Sausage", "هات‌داگ و سوسیس"),
    ("German Sausage", "هات‌داگ و سوسیس"),

    ("French Fries", "سیب‌زمینی و پیش‌غذای فست‌فودی"),
    ("Cheese Fries", "سیب‌زمینی و پیش‌غذای فست‌فودی"),
    ("Onion Rings", "سیب‌زمینی و پیش‌غذای فست‌فودی"),
    ("Garlic Bread", "سیب‌زمینی و پیش‌غذای فست‌فودی"),
    ("Cheese Sticks", "سیب‌زمینی و پیش‌غذای فست‌فودی"),

    # --- Iranian -------------------------------------------------------
    ("Kabab Koobideh", "کباب"),
    ("Saffron Chicken Kabab", "کباب"),
    ("Barg Kabab", "کباب"),
    ("Bakhtiari Kabab", "کباب"),
    ("Chenjeh Kabab", "کباب"),
    ("Joojeh Kabab With Bone", "کباب"),
    ("Lamb Shishlik", "کباب"),
    ("Chelo Kabab Koobideh", "کباب"),          # exception case
    ("Chelo Kabab Bakhtiari", "کباب"),         # exception case
    ("Chelo Joojeh Kabab", "کباب"),            # exception case

    ("Ghormeh Sabzi With Meat", "خورش"),
    ("Gheimeh Bademjan", "خورش"),
    ("Fesenjan With Chicken", "خورش"),
    ("Celery Khoresh", "خورش"),
    ("Chelo Khoresh Ghormeh Sabzi", "خورش"),   # exception case

    ("Zereshk Polo With Chicken", "پلو و چلو"),
    ("Baghali Polo With Lamb", "پلو و چلو"),
    ("Estanboli Polo", "پلو و چلو"),
    ("Lubia Polo", "پلو و چلو"),
    ("Adas Polo With Meat", "پلو و چلو"),
    ("Plain Chelo Rice", "پلو و چلو"),

    ("Ash Reshteh", "آش و سوپ ایرانی"),
    ("Ash Doogh", "آش و سوپ ایرانی"),
    ("Barley Soup", "آش و سوپ ایرانی"),

    ("Traditional Dizi", "دیزی و آبگوشت"),
    ("Lamb Abgoosht", "دیزی و آبگوشت"),

    ("Kashke Bademjan", "پیش‌غذای ایرانی"),
    ("Mirza Ghasemi", "پیش‌غذای ایرانی"),
    ("Yogurt With Cucumber", "پیش‌غذای ایرانی"),
    ("Grilled Chickpea Kabab", "پیش‌غذای ایرانی"),
    ("Zeytoon Parvardeh", "پیش‌غذای ایرانی"),
    ("Kuku Sabzi", "پیش‌غذای ایرانی"),

    # --- Chinese & Asian -------------------------------------------------
    ("Chicken And Vegetable Noodles", "نودل"),
    ("Thai Noodles", "نودل"),
    ("Shrimp Noodles", "نودل"),

    ("Chicken Fried Rice", "برنج و رایس چینی"),
    ("Shrimp Fried Rice", "برنج و رایس چینی"),
    ("Vegetable Chinese Rice", "برنج و رایس چینی"),

    ("Crispy Chinese Chicken", "سوخاری آسیایی"),
    ("Kung Pao Chicken", "سوخاری آسیایی"),
    ("Chili Chicken", "سوخاری آسیایی"),
    ("Sweet And Sour Chicken", "سوخاری آسیایی"),

    ("Tom Yum Shrimp Soup", "سوپ آسیایی"),
    ("Chicken Corn Soup", "سوپ آسیایی"),

    ("Salmon Roll", "سوشی"),
    ("Tuna Sashimi", "سوشی"),
    ("Shrimp Nigiri Sushi", "سوشی"),
    ("California Roll", "سوشی"),

    # --- Seafood -----------------------------------------------------------
    ("Grilled Trout", "ماهی"),
    ("Salmon Fillet", "ماهی"),
    ("Grilled White Fish", "ماهی"),

    ("Grilled Shrimp", "میگو"),
    ("Shrimp Polo", "میگو"),
    ("Shrimp Skewer", "میگو"),

    ("Grilled Shellfish", "صدف و اختاپوس"),
    ("Grilled Octopus", "صدف و اختاپوس"),

    ("Fried Fish", "غذای دریایی سرخ‌شده"),
    ("Fried Shrimp With Sauce", "غذای دریایی سرخ‌شده"),

    # --- Western & International ---------------------------------------
    ("Pasta Alfredo", "پاستا"),
    ("Spaghetti Bolognese", "پاستا"),
    ("Penne With Special Sauce", "پاستا"),
    ("Chicken Lasagna", "پاستا"),
    ("Macaroni With Ground Beef", "پاستا"),

    ("Beef Steak", "استیک و گریل"),
    ("Filet Mignon", "استیک و گریل"),
    ("T-Bone Steak", "استیک و گریل"),

    ("Mushroom Risotto", "ریزوتو"),
    ("Chicken Risotto", "ریزوتو"),

    ("Chicken Burrito", "غذای مکزیکی"),
    ("Beef Taco", "غذای مکزیکی"),
    ("Chicken Fajita", "غذای مکزیکی"),
    ("Cheese Quesadilla", "غذای مکزیکی"),

    # --- Dessert, Pastry & Ice Cream --------------------------------------
    ("Vanilla Ice Cream", "بستنی و فالوده"),
    ("Saffron Ice Cream", "بستنی و فالوده"),
    ("Shirazi Faloodeh", "بستنی و فالوده"),

    ("Chocolate Cake", "کیک و شیرینی"),
    ("New York Cheesecake", "کیک و شیرینی"),
    ("Brownie With Ice Cream", "کیک و شیرینی"),

    ("Chocolate Mousse", "موس و دسر سرد"),
    ("Tiramisu", "موس و دسر سرد"),
    ("Caramel Pudding", "موس و دسر سرد"),
    ("Strawberry Panna Cotta", "موس و دسر سرد"),

    ("Baklava", "شیرینی سنتی"),
    ("Zoolbia And Bamieh", "شیرینی سنتی"),
    ("Isfahan Gaz", "شیرینی سنتی"),

    # --- Breakfast -------------------------------------------------------
    ("Bread Cheese And Walnuts", "نان و پنیر و کره"),
    ("Butter And Jam", "نان و پنیر و کره"),
    ("Cheese And Walnuts", "نان و پنیر و کره"),

    ("Special Omelette", "تخم‌مرغ"),
    ("Sunny Side Up With Tomato", "تخم‌مرغ"),
    ("Boiled Egg", "تخم‌مرغ"),

    ("Wheat Halim", "حلیم"),
    ("Turkey Halim", "حلیم"),
    ("Beef Halim", "حلیم"),

    ("Traditional Lentil Soup", "عدسی و آش صبحانه"),
    ("Almond Harireh", "عدسی و آش صبحانه"),

    # --- Salad & Diet ---------------------------------------------------
    ("Fresh Green Salad", "سالاد سبز"),
    ("Lettuce And Cucumber Salad", "سالاد سبز"),
    ("Shirazi Salad", "سالاد سبز"),

    ("Chicken Caesar Salad", "سالاد سزار"),
    ("Shrimp Caesar Salad", "سالاد سزار"),

    ("Special Olivieh Salad", "سالاد الویه"),
    ("Olivieh Salad With Chicken", "سالاد الویه"),

    ("Chicken And Quinoa Bowl", "باول و غذای رژیمی"),
    ("Keto Diet Meal", "باول و غذای رژیمی"),
    ("Sugar Free Bowl", "باول و غذای رژیمی"),

    # --- Beverages -----------------------------------------------------
    ("Canned Soda", "نوشابه"),
    ("Coca Cola", "نوشابه"),
    ("Orange Fanta", "نوشابه"),

    ("Fresh Orange Juice", "آبمیوه طبیعی"),
    ("Fresh Carrot Juice", "آبمیوه طبیعی"),

    ("Sour Doogh", "دوغ"),
    ("Local Doogh", "دوغ"),

    ("Black Tea", "چای و قهوه"),
    ("Turkish Coffee", "چای و قهوه"),
    ("Espresso", "چای و قهوه"),
    ("Caramel Latte", "چای و قهوه"),

    ("Vanilla Milkshake", "شیک و اسموتی"),
    ("Banana Strawberry Smoothie", "شیک و اسموتی"),
]


def _combo(base, modifiers, base_first=True):
    """Generate '<base> <modifier>' (or '<modifier> <base>') dish names from
    a base word and a list of modifiers/flavors, mirroring seed_data.py's
    helper, to cover more realistic menu variants per sub-category."""
    if base_first:
        return [f"{base} {m}" for m in modifiers]
    return [f"{m} {base}" for m in modifiers]


GENERATED_ITEMS = []

GENERATED_ITEMS += [
    (name, "پیتزا") for name in _combo("Pizza", [
        "Hawaiian", "Chicken And Mushroom", "Garlic And Cheese", "House Special",
        "Chicken BBQ", "Chicken And Corn", "Double Cheese", "Triple Cheese",
        "Vegetarian", "Mediterranean", "Pineapple And Ham", "Pepperoni And Mushroom",
        "Steak", "Sausage", "Tuna", "Olive And Mushroom", "Meat Special", "Pesto",
    ])
]

GENERATED_ITEMS += [
    (name, "برگر") for name in _combo("Burger", [
        "Classic", "Double", "Double Cheese", "Mushroom And Cheese", "Bacon And Cheese",
        "Fish", "Veggie", "Spicy", "Royal", "Steak", "House Special", "Grilled Chicken",
    ])
]

GENERATED_ITEMS += [
    (name, "ساندویچ") for name in _combo("Sandwich", [
        "Club", "Fried Fillet", "German Sausage", "Cheese And Ham", "Chicken And Mushroom",
        "Grilled Chicken", "Ham", "Mixed", "Tuna", "Saffron Chicken",
    ])
]

GENERATED_ITEMS += [
    (name, "سوخاری") for name in [
        "Crispy Chicken Breast", "Crispy Chicken Fillet", "Fried Mushrooms",
        "Fried Onions", "Mixed Crispy Chicken",
    ]
]

GENERATED_ITEMS += [
    (name, "هات‌داگ و سوسیس") for name in _combo("Hot Dog", [
        "Double", "German", "Mexican", "Cheesy", "Mushroom And Cheese", "House Special",
    ])
] + [
    (name, "هات‌داگ و سوسیس") for name in _combo("Sausage", [
        "Cocktail With Bread", "Grilled", "With Cheese",
    ])
]

GENERATED_ITEMS += [
    (name, "سیب‌زمینی و پیش‌غذای فست‌فودی") for name in _combo("Potato", [
        "With Cheese And Mushroom", "With Chili Sauce", "With Mushroom", "Spicy", "Special",
    ])
]

GENERATED_ITEMS += [
    (name, "کباب") for name in [
        "Kabab Loghme", "Liver And Heart Kabab", "Grilled Wings", "Sirloin Kabab",
        "Turkish Kabab", "Kabab Hosseini", "Kabab Vaziri", "Mixed Grill Kabab",
        "Boneless Joojeh Kabab", "Sultani Kabab", "Chenjeh Chicken",
    ]
]

GENERATED_ITEMS += [
    (name, "خورش") for name in [
        "Zucchini Khoresh", "Okra Khoresh", "Plum And Spinach Khoresh", "Carrot Khoresh",
        "Green Bean Khoresh", "Quince Khoresh", "Fesenjan With Meatballs",
        "Ghormeh Sabzi With Chicken",
    ]
]

GENERATED_ITEMS += [
    (name, "پلو و چلو") for name in [
        "Carrot Polo", "Reshteh Polo", "Herb Polo With Fish", "Sour Cherry Polo",
        "Sweet Polo", "Adas Polo With Dates", "Zereshk Polo With Joojeh",
        "Baghali Polo With Lamb Shank",
    ]
]

GENERATED_ITEMS += [
    (name, "آش و سوپ ایرانی") for name in ["Pomegranate Ash", "Herb Ash", "Sagh Ash", "Chicken Barley Soup"]
]

GENERATED_ITEMS += [
    (name, "دیزی و آبگوشت") for name in ["Sangi Dizi", "Bozbash Abgoosht"]
]

GENERATED_ITEMS += [
    (name, "پیش‌غذای ایرانی") for name in [
        "Grilled Eggplant With Walnuts", "Haji Baba", "Grape Leaf Dolma", "Potato Kuku",
        "Mirza Ghasemi With Egg", "Special Zeytoon Parvardeh",
    ]
]

GENERATED_ITEMS += [
    (name, "نودل") for name in [
        "Chicken Noodles", "Shrimp Noodles Special", "Vegetable Noodles", "Spicy Korean Noodles",
    ]
]

GENERATED_ITEMS += [
    (name, "برنج و رایس چینی") for name in [
        "Shrimp Rice", "Vegetable Rice", "Special Fried Rice", "Chicken And Vegetable Rice",
    ]
]

GENERATED_ITEMS += [
    (name, "سوخاری آسیایی") for name in ["Thai Crispy Chicken", "Crispy Chinese Wings"]
]

GENERATED_ITEMS += [
    (name, "سوپ آسیایی") for name in ["Chinese Vegetable Soup", "Chicken And Mushroom Chinese Soup"]
]

GENERATED_ITEMS += [
    (name, "سوشی") for name in [
        "Tempura Roll", "Spicy Roll", "Veggie Roll", "Salmon Nigiri", "Salmon Sashimi",
        "Dragon Roll",
    ]
]

GENERATED_ITEMS += [
    (name, "ماهی") for name in [
        "Grilled Trout Fillet", "Grilled Salmon", "Grouper Fish", "Grilled Kingfish",
    ]
]

GENERATED_ITEMS += [
    (name, "میگو") for name in ["Shrimp With Garlic Sauce", "Korean Style Shrimp", "Special Shrimp Skewer"]
]

GENERATED_ITEMS += [
    (name, "صدف و اختاپوس") for name in ["Special Grilled Shellfish", "Char-Grilled Octopus"]
]

GENERATED_ITEMS += [
    (name, "غذای دریایی سرخ‌شده") for name in ["Battered Fried Fish", "Breaded Shrimp"]
]

GENERATED_ITEMS += [
    (name, "پاستا") for name in [
        "Pasta Pesto", "House Special Pasta", "Pasta With Special Sauce", "Penne Alfredo",
        "Spaghetti Carbonara", "Beef Lasagna", "Penne With Chicken Alfredo",
    ]
]

GENERATED_ITEMS += [
    (name, "استیک و گریل") for name in ["Chicken Steak", "Fish Steak", "Steak With Pepper Sauce"]
]

GENERATED_ITEMS += [
    (name, "ریزوتو") for name in ["Shrimp Risotto", "Vegetable Risotto"]
]

GENERATED_ITEMS += [
    (name, "غذای مکزیکی") for name in ["Chicken Taco", "Beef Burrito", "Chicken Enchilada", "Chicken Quesadilla"]
]

GENERATED_ITEMS += [
    (name, "بستنی و فالوده") for name in [
        "Chocolate Ice Cream", "Nutella Ice Cream", "Pistachio Ice Cream",
        "Strawberry Ice Cream", "Faloodeh With Ice Cream",
    ]
]

GENERATED_ITEMS += [
    (name, "کیک و شیرینی") for name in [
        "Vanilla Cake", "Red Velvet Cake", "Carrot Cake", "Lemon Cake", "Banana Cake",
    ]
]

GENERATED_ITEMS += [
    (name, "موس و دسر سرد") for name in ["Nutella Mousse", "Strawberry Mousse", "Chocolate Pudding"]
]

GENERATED_ITEMS += [
    (name, "شیرینی سنتی") for name in ["Zaban Pastry", "Cream Filled Pastry", "Qom Sohan"]
]

GENERATED_ITEMS += [
    (name, "نان و پنیر و کره") for name in ["Barbari Bread With Cheese", "Butter And Honey", "Cheese Walnut And Tomato"]
]

GENERATED_ITEMS += [
    (name, "تخم‌مرغ") for name in ["Special Omelette With Mushroom", "Sunny Side Up With Sausage", "Honey Glazed Egg"]
]

GENERATED_ITEMS += [
    (name, "حلیم") for name in ["Special Halim", "Saffron Halim"]
]

GENERATED_ITEMS += [
    (name, "عدسی و آش صبحانه") for name in ["Special Lentil Soup", "Traditional Almond Harireh"]
]

GENERATED_ITEMS += [
    (name, "سالاد سبز") for name in ["Greek Salad", "Cucumber And Tomato Salad", "Special Garden Salad"]
]

GENERATED_ITEMS += [
    (name, "سالاد سزار") for name in ["Special Caesar Salad", "Deluxe Shrimp Caesar Salad"]
]

GENERATED_ITEMS += [
    (name, "سالاد الویه") for name in ["Olivieh Salad With Mushroom", "Classic Olivieh Salad"]
]

GENERATED_ITEMS += [
    (name, "باول و غذای رژیمی") for name in [
        "Chicken And Vegetable Bowl", "Quinoa Bowl", "Diet Chicken Plate", "Salmon Bowl",
    ]
]

GENERATED_ITEMS += [
    (name, "نوشابه") for name in ["Diet Soda", "Bottled Soda", "Mirinda"]
]

GENERATED_ITEMS += [
    (name, "آبمیوه طبیعی") for name in ["Pineapple Juice", "Pomegranate Juice", "Mango Juice", "Mixed Fruit Juice"]
]

GENERATED_ITEMS += [
    (name, "دوغ") for name in ["Sparkling Doogh", "Homemade Doogh"]
]

GENERATED_ITEMS += [
    (name, "چای و قهوه") for name in ["Green Tea", "Masala Tea", "Americano", "Mocha", "Caramel Cappuccino"]
]

GENERATED_ITEMS += [
    (name, "شیک و اسموتی") for name in ["Chocolate Shake", "Banana Shake", "Nutella Shake", "Mango Smoothie"]
]

ALL_ITEMS = RAW_ITEMS + GENERATED_ITEMS

# De-duplicate by name (case-insensitive), keeping the first occurrence
# (RAW_ITEMS wins on conflicts since it comes first, e.g. hand-picked
# exceptions).
_seen_names = set()
_DEDUPED_ITEMS = []
for _name, _sub in ALL_ITEMS:
    _key = _name.lower()
    if _key not in _seen_names:
        _seen_names.add(_key)
        _DEDUPED_ITEMS.append((_name, _sub))
ALL_ITEMS = _DEDUPED_ITEMS


def stratified_split(items, test_ratio=0.2, seed=42):
    """Split (name, sub) pairs into train/test, stratified per sub_category
    so every sub-category has at least one test example when possible."""
    rng = random.Random(seed)
    by_sub = {}
    for name, sub in items:
        by_sub.setdefault(sub, []).append(name)

    train_rows = []
    test_rows = []
    for sub, names in by_sub.items():
        names = names[:]
        rng.shuffle(names)
        n_test = max(1, round(len(names) * test_ratio)) if len(names) > 1 else 0
        test_names = set(names[:n_test])
        main = taxonomy.SUB_TO_MAIN[sub]
        for name in names:
            split = "test" if name in test_names else "train"
            # (item_name, restaurant_name, main_category, sub_category, split,
            # source) - matches db.add_menu_items, since this dataset is
            # always appended on top of the Persian one, never used to
            # replace the whole table.
            row = (name, None, main, sub, split, "synthetic_en")
            (test_rows if split == "test" else train_rows).append(row)
    return train_rows + test_rows


def get_seed_rows():
    """Return all synthetic English rows as
    (item_name, restaurant_name, main_category, sub_category, split, source)
    tuples, ready to insert into menu_items via db.add_menu_items."""
    return stratified_split(ALL_ITEMS)


if __name__ == "__main__":
    rows = get_seed_rows()
    train_n = sum(1 for r in rows if r[3] == "train")
    test_n = sum(1 for r in rows if r[3] == "test")
    print(f"total={len(rows)} train={train_n} test={test_n}")
