# طبقه‌بند دسته‌بندی غذا و منوی رستوران / Food & Menu Classifier

**زبان / Language / 语言 / Язык:**
[فارسی](#فارسی) · [English](#english) · [中文](#中文) · [Русский](#русский)

---

## فارسی

این ابزار با گرفتن نام یک غذا یا کل منوی یک رستوران، دو سطح دسته‌بندی انجام می‌دهد:

1. **دسته‌ی اصلی (کوزین/نوع رستوران)** — مثل «فست‌فود»، «ایرانی»، «چینی و آسیایی»، «دریایی»، «فرنگی و بین‌الملل»، «دسر، شیرینی و بستنی»، «صبحانه»، «سالاد و رژیمی»، «نوشیدنی».
2. **زیردسته‌ی غذا** — مثلاً داخل «فست‌فود»: پیتزا، برگر، ساندویچ، سوخاری، هات‌داگ و سوسیس، سیب‌زمینی و پیش‌غذا. لیست کامل در `taxonomy.py`.

سیستم **ترکیبی (Hybrid)** است:

- ابتدا یک **موتور قانون‌محور** با یک جدول **استثنا** (`EXCEPTIONS`) و قانون **«اولین کلمه‌ی کلیدی از چپ برنده است»** بررسی می‌شود. همین قانون است که مثلاً «پیتزا چیزبرگر» را — با اینکه کلمه‌ی «برگر» دارد — به‌درستی «پیتزا» تشخیص می‌دهد (چون «پیتزا» زودتر از «چیزبرگر» می‌آید)، و «چلو کباب کوبیده» را به‌جای «پلو» به‌عنوان «کباب» تشخیص می‌دهد (این یکی چون معمولاً استثناست، در جدول `EXCEPTIONS` صراحتاً ثبت شده).
- اگر هیچ قانونی مچ نشد (مثلاً یک غذای کاملاً جدید یا با املای متفاوت)، یک **مدل یادگیری ماشین** (TF-IDF کاراکتری + SVM خطی، از scikit-learn) که روی دیتاست آموزش دیده، حدس نهایی را می‌زند.
- اگر مدل هم مطمئن نبود، خروجی «نامشخص» به همراه نزدیک‌ترین حدس و درصد اطمینان برگردانده می‌شود — تا همیشه شفاف باشد که تشخیص از کجا آمده.

**دو زبانه:** موتور قانون‌محور و مدل یادگیری ماشین هر دو روی داده‌ی **فارسی و انگلیسی** کار می‌کنند (مثلاً هم «پیتزا چیز برگر» و هم «Pizza Cheeseburger» درست تشخیص داده می‌شوند). جزئیات در بخش «دیتاست انگلیسی» پایین‌تر.

### نصب

```bash
pip install -r requirements.txt
```

### شروع سریع

```bash
# ۱) ساخت دیتابیس + seed کردن taxonomy و دیتاست مصنوعی فارسی+انگلیسی (فقط یک‌بار لازم است)
python train.py --init

# ۲) آموزش مدل یادگیری ماشین روی داده‌های split=train
python train.py --train-model

# ۳) تست یک آیتم (فارسی یا انگلیسی)
python predict.py "پیتزا چیز برگر"
python predict.py "چلو کباب کوبیده"
python predict.py "Cheeseburger"
python predict.py "Chelo Kabab Koobideh"

# ۴) تست یک منوی کامل (فایل نمونه ضمیمه شده)
python predict.py --menu-file sample_menu.csv

# ۵) ارزیابی دقت روی داده‌ی تست
python evaluate.py
```

### رابط وب ساده

یک رابط وب مینیمال با Flask اضافه شده که می‌توانید نام غذا یا کل منو (هر خط یک آیتم) را در آن وارد کرده و نتیجه را ببینید:

```bash
python app.py
# سپس در مرورگر باز کنید: http://127.0.0.1:5000/
```

### افزودن دیتاست خودتان

هر وقت خواستید، می‌توانید دیتاست برچسب‌خورده‌ی خودتان (فارسی، انگلیسی یا هر دو) را روی دیتاست مصنوعی موجود اضافه کنید (این کار داده‌های فعلی را پاک نمی‌کند):

```bash
python import_dataset.py --list-categories        # دیدن اسم دقیق دسته‌ها/زیردسته‌های معتبر
python import_dataset.py --csv my_data.csv         # افزودن به split=train (پیش‌فرض)
python import_dataset.py --csv my_test.csv --split test
python train.py --train-model                      # آموزش مجدد مدل با داده‌ی جدید
```

فرمت CSV مورد نیاز (ستون‌های `main_category`, `restaurant_name`, `split` اختیاری‌اند):

```csv
item_name,sub_category
پیتزا سیر و پنیر,پیتزا
Cheeseburger,برگر
```

### دیتاست انگلیسی

علاوه بر دیتاست مصنوعی فارسی (`seed_data.py`)، یک دیتاست مصنوعی **انگلیسی** موازی (`seed_data_en.py`) هم وجود دارد که همان تاکسونومی را با نام‌های غذای انگلیسی/تلفظی (مثل `Cheeseburger`، `Chelo Kabab Koobideh`، `Caesar Salad`) پوشش می‌دهد. `taxonomy.py` هم برای هر زیردسته کلیدواژه‌های انگلیسی معادل دارد (مثلاً «برگر»: هم `برگر`/`همبرگر` و هم `burger`/`hamburger`/`cheeseburger`).

اجرای `python train.py --init` هر دو دیتاست را (اگر هنوز در دیتابیس نباشند) اضافه می‌کند — بدون پاک‌کردن داده‌ی فعلی. برای دیدن فقط تعداد ردیف‌های هرکدام:

```bash
python -c "import db,seed_data_en; print(len(seed_data_en.get_seed_rows()))"
```

### افزودن قانون/استثنای جدید

کلمات کلیدی و استثناها در `taxonomy.py` (متغیرهای `KEYWORDS` و `EXCEPTIONS`) قرار دارند — یک فایل پایتونی ساده و قابل ویرایش مستقیم؛ نیازی به دستکاری دیتابیس نیست. بعد از تغییر، دوباره `python train.py --init` را اجرا کنید تا نسخه‌ی داخل دیتابیس هم (که فقط برای مشاهده/گزارش نگه‌داری می‌شود) به‌روز شود.

### ساختار پروژه

| فایل | نقش |
|---|---|
| `taxonomy.py` | درخت دسته‌ها/زیردسته‌ها + کلمات کلیدی فارسی/انگلیسی + استثناها + برچسب‌های نمایشی انگلیسی |
| `normalize.py` | یکسان‌سازی متن فارسی (ی/ك عربی، نیم‌فاصله، علائم) و لاتین (lowercase) |
| `db.py` | اسکیمای SQLite (`food_data.db`) + توابع کمکی |
| `seed_data.py` | دیتاست مصنوعی فارسی برچسب‌خورده برای seed کردن دیتابیس |
| `seed_data_en.py` | دیتاست مصنوعی انگلیسی برچسب‌خورده، موازی با نسخه‌ی فارسی |
| `rule_classifier.py` | موتور قانون‌محور (استثنا + leftmost keyword match) |
| `ml_classifier.py` | مدل TF-IDF + SVM (fallback) |
| `hybrid_classifier.py` | ترکیب قانون + مدل، و تجمیع سطح-رستوران |
| `train.py` | CLI: ساخت/seed دیتابیس (فارسی+انگلیسی) + آموزش مدل |
| `import_dataset.py` | CLI: افزودن دیتاست دلخواه کاربر |
| `predict.py` | CLI: طبقه‌بندی آیتم/منو |
| `evaluate.py` | CLI: گزارش دقت روی داده‌ی تست |
| `app.py` + `templates/index.html` | رابط وب ساده با Flask |
| `sample_menu.csv` | یک نمونه منوی فست‌فودی برای تست دستی |

`food_data.db` هم دیتابیس آموزش و هم دیتابیس تست است؛ ستون `split` هر ردیف را train یا test مشخص می‌کند، پس یک فایل واحد کافی است. ستون `source` هم مشخص می‌کند هر ردیف از کجا آمده (`synthetic` فارسی، `synthetic_en` انگلیسی، یا `user_import`).

### محدودیت‌ها

دیتاست موجود **مصنوعی** و دستی است (به دیتای واقعی اسنپ‌فود دسترسی/مجوز اسکرپ نداریم)، اما با `import_dataset.py` می‌توانید هر دیتای واقعی/دلخواه خودتان را اضافه و مدل را دوباره آموزش دهید تا روی داده‌ی واقعی دقیق‌تر شود. نام دسته‌ها/زیردسته‌ها (`taxonomy.py`) همیشه فارسی می‌مانند — برچسب‌های انگلیسی (`CATEGORY_LABELS_EN`) فقط برای نمایش هستند، نه برای منطق طبقه‌بندی.

---

## English

Given the name of a single dish or a restaurant's entire menu, this tool performs two levels of classification:

1. **Main category (cuisine / restaurant type)** — e.g. "Fast Food", "Iranian", "Chinese & Asian", "Seafood", "Western & International", "Dessert, Pastry & Ice Cream", "Breakfast", "Salad & Diet", "Beverages".
2. **Food sub-category** — e.g. under "Fast Food": Pizza, Burger, Sandwich, Fried Chicken, Hot Dog & Sausage, Fries & Fast-Food Sides. The full list is in `taxonomy.py`.

The system is **hybrid**:

- First, a **rule-based engine** checks an **exceptions** table (`EXCEPTIONS`) and a **"leftmost keyword wins"** rule. This is what correctly classifies "Pizza Cheeseburger" as Pizza (even though it contains the word "burger") — because "pizza" comes before "cheeseburger" — and classifies "Chelo Kabab Koobideh" as Kabab rather than Rice (this one is explicitly listed in the `EXCEPTIONS` table since it's a common exception).
- If no rule matches (e.g. a brand-new dish name or a different spelling), a **machine learning model** (character-level TF-IDF + linear SVM, from scikit-learn) trained on the dataset makes the final guess.
- If the model isn't confident either, the output is "unknown" along with its closest guess and confidence percentage — so it's always transparent where a classification came from.

**Bilingual:** both the rule engine and the ML model work on **Persian and English** data (e.g. both "پیتزا چیز برگر" and "Pizza Cheeseburger" are classified correctly). See the "English Dataset" section below for details.

### Installation

```bash
pip install -r requirements.txt
```

### Quick Start

```bash
# 1) Create the database + seed the taxonomy and the Persian+English synthetic dataset (only needed once)
python train.py --init

# 2) Train the ML fallback model on split=train rows
python train.py --train-model

# 3) Classify a single item (Persian or English)
python predict.py "پیتزا چیز برگر"
python predict.py "چلو کباب کوبیده"
python predict.py "Cheeseburger"
python predict.py "Chelo Kabab Koobideh"

# 4) Classify a whole menu (a sample file is included)
python predict.py --menu-file sample_menu.csv

# 5) Evaluate accuracy on the test split
python evaluate.py
```

### Simple Web UI

A minimal Flask web UI is included, where you can type a dish name or a whole menu (one item per line) and see the result:

```bash
python app.py
# then open http://127.0.0.1:5000/ in your browser
```

### Adding Your Own Dataset

At any time you can add your own labeled dataset (Persian, English, or both) on top of the existing synthetic dataset (this never deletes existing data):

```bash
python import_dataset.py --list-categories        # see the exact valid category/sub-category names
python import_dataset.py --csv my_data.csv         # add to split=train (default)
python import_dataset.py --csv my_test.csv --split test
python train.py --train-model                      # retrain the model on the new data
```

Required CSV format (`main_category`, `restaurant_name`, `split` columns are optional):

```csv
item_name,sub_category
پیتزا سیر و پنیر,پیتزا
Cheeseburger,برگر
```

### English Dataset

Alongside the Persian synthetic dataset (`seed_data.py`), there is a parallel **English** synthetic dataset (`seed_data_en.py`) covering the same taxonomy with English/transliterated dish names (e.g. `Cheeseburger`, `Chelo Kabab Koobideh`, `Caesar Salad`). `taxonomy.py` also has English keyword equivalents for every sub-category (e.g. "Burger" matches both `برگر`/`همبرگر` and `burger`/`hamburger`/`cheeseburger`).

Running `python train.py --init` adds both datasets (whichever is still missing from the database) without deleting existing data. To just count the rows in each:

```bash
python -c "import db,seed_data_en; print(len(seed_data_en.get_seed_rows()))"
```

### Adding a New Rule/Exception

Keywords and exceptions live in `taxonomy.py` (the `KEYWORDS` and `EXCEPTIONS` variables) — a plain, directly editable Python file; there's no need to touch the database. After changing it, re-run `python train.py --init` to refresh the copy inside the database (which is kept purely for inspection/reporting).

### Project Structure

| File | Role |
|---|---|
| `taxonomy.py` | Category/sub-category tree + Persian/English keywords + exceptions + English display labels |
| `normalize.py` | Normalizes Persian text (Arabic ی/ك, half-spaces, punctuation) and Latin text (lowercasing) |
| `db.py` | SQLite schema (`food_data.db`) + helper functions |
| `seed_data.py` | Hand-labeled synthetic Persian dataset used to seed the database |
| `seed_data_en.py` | Hand-labeled synthetic English dataset, parallel to the Persian one |
| `rule_classifier.py` | Rule-based engine (exceptions + leftmost keyword match) |
| `ml_classifier.py` | TF-IDF + SVM model (fallback) |
| `hybrid_classifier.py` | Combines the rule engine + model, plus restaurant-level aggregation |
| `train.py` | CLI: build/seed the database (Persian + English) + train the model |
| `import_dataset.py` | CLI: import the user's own dataset |
| `predict.py` | CLI: classify an item/menu |
| `evaluate.py` | CLI: report accuracy on the test split |
| `app.py` + `templates/index.html` | Simple Flask web UI |
| `sample_menu.csv` | A sample fast-food menu for manual testing |

`food_data.db` serves as both the training and the test database; the `split` column on each row marks it as train or test, so a single file is enough. The `source` column marks where each row came from (`synthetic` = Persian, `synthetic_en` = English, or `user_import`).

### Limitations

The existing dataset is **synthetic** and hand-written (we don't have access to or permission to scrape real Snappfood data), but with `import_dataset.py` you can add any real/custom data of your own and retrain the model to become more accurate on real-world data. Category/sub-category names (`taxonomy.py`) always stay in Persian — the English labels (`CATEGORY_LABELS_EN`) are for display only, not for the classification logic.

---

## 中文

给定一道菜的名称或一家餐厅的完整菜单，本工具会进行两级分类：

1. **主分类（菜系/餐厅类型）** — 例如「快餐」「伊朗菜」「中式与亚洲菜」「海鲜」「西式与国际菜」「甜点、糕点与冰淇淋」「早餐」「沙拉与健康餐」「饮品」。
2. **食品子分类** — 例如「快餐」下包含：披萨、汉堡、三明治、炸鸡、热狗与香肠、薯条及快餐配菜。完整列表见 `taxonomy.py`。

系统采用**混合（Hybrid）架构**：

- 首先经过一个**基于规则的引擎**，它会查一个**例外表**（`EXCEPTIONS`）并应用**「从左到右第一个匹配的关键词获胜」**规则。正是这条规则让「Pizza Cheeseburger」（虽然含有「burger」一词）被正确识别为「披萨」——因为「pizza」出现在「cheeseburger」之前；也让「Chelo Kabab Koobideh」被识别为「烤肉（Kabab）」而不是「米饭」（这一条因为是常见例外，被显式写入了 `EXCEPTIONS` 表）。
- 如果没有规则匹配（例如全新的菜名或不同拼写），一个在数据集上训练好的**机器学习模型**（基于字符级 TF-IDF 特征 + 线性 SVM，使用 scikit-learn）会给出最终猜测。
- 如果模型也不够有把握，输出会标记为「未知（unknown）」，同时附上最接近的猜测和置信度百分比——确保分类来源始终透明。

**双语支持：** 规则引擎和机器学习模型都同时支持**波斯语和英语**数据（例如「پیتزا چیز برگر」和「Pizza Cheeseburger」都能被正确分类）。详见下方「英语数据集」部分。

### 安装

```bash
pip install -r requirements.txt
```

### 快速开始

```bash
# 1) 创建数据库并写入分类体系及波斯语+英语合成数据集（只需执行一次）
python train.py --init

# 2) 在 split=train 的数据上训练机器学习模型
python train.py --train-model

# 3) 测试单个菜品（波斯语或英语均可）
python predict.py "پیتزا چیز برگر"
python predict.py "چلو کباب کوبیده"
python predict.py "Cheeseburger"
python predict.py "Chelo Kabab Koobideh"

# 4) 测试完整菜单（附带一个示例文件）
python predict.py --menu-file sample_menu.csv

# 5) 在测试集上评估准确率
python evaluate.py
```

### 简易网页界面

项目内置一个基于 Flask 的极简网页界面，可以输入菜品名称或整份菜单（每行一个菜品）并查看结果：

```bash
python app.py
# 然后在浏览器中打开 http://127.0.0.1:5000/
```

### 添加自己的数据集

你可以随时在现有合成数据集之上追加自己的标注数据（波斯语、英语，或两者皆有），不会删除已有数据：

```bash
python import_dataset.py --list-categories        # 查看所有有效的分类/子分类名称
python import_dataset.py --csv my_data.csv         # 添加到 split=train（默认）
python import_dataset.py --csv my_test.csv --split test
python train.py --train-model                      # 用新数据重新训练模型
```

所需的 CSV 格式（`main_category`、`restaurant_name`、`split` 列为可选）：

```csv
item_name,sub_category
پیتزا سیر و پنیر,پیتزا
Cheeseburger,برگر
```

### 英语数据集

除了波斯语合成数据集（`seed_data.py`）之外，项目还包含一个并行的**英语**合成数据集（`seed_data_en.py`），覆盖相同的分类体系，使用英语/音译菜名（如 `Cheeseburger`、`Chelo Kabab Koobideh`、`Caesar Salad`）。`taxonomy.py` 也为每个子分类添加了对应的英语关键词（例如「汉堡」子分类同时匹配 `برگر`/`همبرگر` 和 `burger`/`hamburger`/`cheeseburger`）。

运行 `python train.py --init` 会把数据库中尚缺失的数据集（波斯语和/或英语）自动补齐，不会删除已有数据。若只想查看各数据集的行数：

```bash
python -c "import db,seed_data_en; print(len(seed_data_en.get_seed_rows()))"
```

### 添加新规则/例外

关键词和例外都定义在 `taxonomy.py` 中（`KEYWORDS` 和 `EXCEPTIONS` 变量）——一个可直接编辑的普通 Python 文件，无需操作数据库。修改后重新运行 `python train.py --init`，以更新数据库中的副本（该副本仅用于查看/报表用途）。

### 项目结构

| 文件 | 作用 |
|---|---|
| `taxonomy.py` | 分类/子分类树 + 波斯语/英语关键词 + 例外规则 + 英语展示标签 |
| `normalize.py` | 波斯语文本归一化（阿拉伯字母 ی/ك、半角空格、标点）以及拉丁字母小写化 |
| `db.py` | SQLite 数据库结构（`food_data.db`）+ 辅助函数 |
| `seed_data.py` | 用于初始化数据库的波斯语标注合成数据集 |
| `seed_data_en.py` | 与波斯语版本并行的英语标注合成数据集 |
| `rule_classifier.py` | 基于规则的分类引擎（例外 + 从左到右关键词匹配） |
| `ml_classifier.py` | TF-IDF + SVM 模型（后备方案） |
| `hybrid_classifier.py` | 组合规则引擎与模型，并进行餐厅整体维度的聚合 |
| `train.py` | 命令行工具：创建/初始化数据库（波斯语+英语）+ 训练模型 |
| `import_dataset.py` | 命令行工具：导入用户自定义数据集 |
| `predict.py` | 命令行工具：对菜品/菜单进行分类 |
| `evaluate.py` | 命令行工具：在测试集上输出准确率报告 |
| `app.py` + `templates/index.html` | 基于 Flask 的简易网页界面 |
| `sample_menu.csv` | 一份示例快餐菜单，用于手动测试 |

`food_data.db` 同时充当训练数据库和测试数据库；每一行的 `split` 列标明它属于 train 还是 test，因此单个文件就足够了。`source` 列标明每一行数据的来源（`synthetic` 为波斯语，`synthetic_en` 为英语，`user_import` 为用户导入）。

### 局限性

现有数据集是**人工编写的合成数据**（我们没有获取或抓取真实 Snappfood 数据的权限），但你可以通过 `import_dataset.py` 添加任何真实/自定义数据并重新训练模型，从而在真实数据上获得更高准确率。分类/子分类名称（`taxonomy.py`）始终以波斯语为准——英语标签（`CATEGORY_LABELS_EN`）仅用于展示，不参与分类逻辑。

---

## Русский

Получая название одного блюда или всё меню ресторана, этот инструмент выполняет классификацию на двух уровнях:

1. **Основная категория (кухня / тип ресторана)** — например, «Фастфуд», «Иранская кухня», «Китайская и азиатская кухня», «Морепродукты», «Западная и интернациональная кухня», «Десерты, выпечка и мороженое», «Завтрак», «Салаты и диетическое питание», «Напитки».
2. **Подкатегория блюда** — например, внутри «Фастфуда»: пицца, бургер, сэндвич, жареная курица, хот-дог и сосиски, картофель и фастфуд-закуски. Полный список — в `taxonomy.py`.

Система является **гибридной**:

- Сначала проверяется **движок на основе правил** с таблицей **исключений** (`EXCEPTIONS`) и правилом **«побеждает первое слева совпавшее ключевое слово»**. Именно это правило корректно относит «Pizza Cheeseburger» к категории «Пицца» (хотя в названии есть слово «burger») — потому что «pizza» стоит раньше, чем «cheeseburger», — а «Chelo Kabab Koobideh» относит к «Кабаб», а не к «Рис» (этот случай явно прописан в таблице `EXCEPTIONS`, так как встречается часто).
- Если ни одно правило не сработало (например, совершенно новое название блюда или другое написание), финальную догадку делает **модель машинного обучения** (символьный TF-IDF + линейный SVM из scikit-learn), обученная на датасете.
- Если модель тоже не уверена, возвращается результат «неизвестно» вместе с наиболее близкой догадкой и процентом уверенности — чтобы всегда было прозрачно, откуда взялась классификация.

**Двуязычность:** и движок на основе правил, и модель машинного обучения работают как с **персидскими, так и с английскими** данными (например, корректно классифицируются и «پیتزا چیز برگر», и «Pizza Cheeseburger»). Подробности — в разделе «Английский датасет» ниже.

### Установка

```bash
pip install -r requirements.txt
```

### Быстрый старт

```bash
# 1) Создать базу данных + заполнить таксономию и синтетический датасет (персидский+английский) (нужно один раз)
python train.py --init

# 2) Обучить модель машинного обучения на строках split=train
python train.py --train-model

# 3) Проверить одно блюдо (на персидском или английском)
python predict.py "پیتزا چیز برگر"
python predict.py "چلو کباب کوبیده"
python predict.py "Cheeseburger"
python predict.py "Chelo Kabab Koobideh"

# 4) Проверить целое меню (прилагается пример файла)
python predict.py --menu-file sample_menu.csv

# 5) Оценить точность на тестовых данных
python evaluate.py
```

### Простой веб-интерфейс

Добавлен минималистичный веб-интерфейс на Flask, где можно ввести название блюда или целое меню (по одному пункту на строку) и увидеть результат:

```bash
python app.py
# затем откройте в браузере http://127.0.0.1:5000/
```

### Добавление собственного датасета

В любой момент вы можете добавить свой размеченный датасет (персидский, английский или оба сразу) поверх существующего синтетического датасета (это не удаляет текущие данные):

```bash
python import_dataset.py --list-categories        # посмотреть точные названия категорий/подкатегорий
python import_dataset.py --csv my_data.csv         # добавить в split=train (по умолчанию)
python import_dataset.py --csv my_test.csv --split test
python train.py --train-model                      # переобучить модель на новых данных
```

Требуемый формат CSV (столбцы `main_category`, `restaurant_name`, `split` — необязательны):

```csv
item_name,sub_category
پیتزا سیر و پنیر,پیتزا
Cheeseburger,برگر
```

### Английский датасет

Помимо персидского синтетического датасета (`seed_data.py`), в проекте есть параллельный **английский** синтетический датасет (`seed_data_en.py`), покрывающий ту же таксономию английскими/транслитерированными названиями блюд (например, `Cheeseburger`, `Chelo Kabab Koobideh`, `Caesar Salad`). В `taxonomy.py` для каждой подкатегории также добавлены соответствующие английские ключевые слова (например, для подкатегории «Бургер» совпадают и `برگر`/`همبرگر`, и `burger`/`hamburger`/`cheeseburger`).

Выполнение `python train.py --init` добавит оба датасета (тот, которого ещё нет в базе), не удаляя существующие данные. Чтобы просто посчитать количество строк в каждом:

```bash
python -c "import db,seed_data_en; print(len(seed_data_en.get_seed_rows()))"
```

### Добавление нового правила/исключения

Ключевые слова и исключения находятся в `taxonomy.py` (переменные `KEYWORDS` и `EXCEPTIONS`) — обычный, напрямую редактируемый Python-файл; трогать базу данных не нужно. После изменения снова запустите `python train.py --init`, чтобы обновить копию в базе данных (она хранится только для просмотра/отчётности).

### Структура проекта

| Файл | Роль |
|---|---|
| `taxonomy.py` | Дерево категорий/подкатегорий + персидские/английские ключевые слова + исключения + английские метки для отображения |
| `normalize.py` | Нормализация персидского текста (арабские ی/ك, полупробелы, пунктуация) и латиницы (приведение к нижнему регистру) |
| `db.py` | Схема SQLite (`food_data.db`) + вспомогательные функции |
| `seed_data.py` | Размеченный синтетический персидский датасет для заполнения базы данных |
| `seed_data_en.py` | Размеченный синтетический английский датасет, параллельный персидскому |
| `rule_classifier.py` | Движок на основе правил (исключения + сопоставление по первому слева ключевому слову) |
| `ml_classifier.py` | Модель TF-IDF + SVM (запасной вариант) |
| `hybrid_classifier.py` | Объединяет движок правил и модель, а также агрегацию на уровне ресторана |
| `train.py` | CLI: создание/заполнение базы данных (персидский + английский) + обучение модели |
| `import_dataset.py` | CLI: импорт собственного датасета пользователя |
| `predict.py` | CLI: классификация блюда/меню |
| `evaluate.py` | CLI: отчёт о точности на тестовых данных |
| `app.py` + `templates/index.html` | Простой веб-интерфейс на Flask |
| `sample_menu.csv` | Пример меню фастфуда для ручного тестирования |

`food_data.db` служит одновременно и обучающей, и тестовой базой данных; столбец `split` каждой строки указывает train или test, поэтому достаточно одного файла. Столбец `source` указывает происхождение строки (`synthetic` — персидский, `synthetic_en` — английский, `user_import` — импортировано пользователем).

### Ограничения

Существующий датасет **синтетический** и составлен вручную (у нас нет доступа или разрешения на сбор реальных данных Snappfood), но с помощью `import_dataset.py` вы можете добавить любые реальные/собственные данные и переобучить модель, чтобы повысить точность на реальных данных. Названия категорий/подкатегорий (`taxonomy.py`) всегда остаются на персидском — английские метки (`CATEGORY_LABELS_EN`) используются только для отображения, а не в логике классификации.
