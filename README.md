# Пет-проект по продуктовой аналитике

Портфолио-проект для практики data analytics и product analytics на синтетических данных интернет-магазина.

Проект охватывает полный аналитический цикл:

- генерация данных
- проектирование базы данных в PostgreSQL
- SQL-анализ
- EDA в Python
- подготовка визуализаций для дашборда
- формулирование бизнес-выводов

## Сценарий проекта

Мы анализируем условный интернет-магазин и отвечаем на продуктовые и бизнес-вопросы:

- сколько пользователей приходит в продукт
- сколько пользователей добавляет товары в корзину
- сколько пользователей завершает покупку
- какая конверсия из сессии в заказ
- какие каналы дают больше выручки
- какие источники трафика лучше конвертируют
- какие категории товаров приносят больше денег
- как меняется retention по когортам регистрации

## Стек

- PostgreSQL
- SQL
- Python
- pandas
- NumPy
- matplotlib
- seaborn
- Jupyter Notebook
- Power BI, запланировано

## Модель данных

В базе используется шесть основных таблиц:

- `users` - пользователи и данные о привлечении
- `products` - каталог товаров
- `sessions` - пользовательские сессии
- `events` - события пользователей: `view_item`, `add_to_cart`, `purchase`
- `orders` - заказы
- `order_items` - товары внутри заказов

## Структура репозитория

- `data/sample/` - сгенерированные CSV-данные
- `sql/` - схема БД, загрузка данных и аналитические запросы
- `notebooks/` - EDA в Python и Jupyter Notebook
- `dashboards/figures/` - сгенерированные графики
- `dashboards/powerbi_data/` - подготовленные CSV-файлы для Power BI
- `docs/` - описание проекта, roadmap, настройка PostgreSQL и выводы
- `scripts/` - скрипты генерации данных и notebook

## Ключевые метрики

Текущий сгенерированный датасет:

- Пользователи: 500
- Сессии: 2 225
- Оплаченные заказы: 425
- События: 6 752
- Выручка: 221 082.40
- Средний чек: 520.19
- Конверсия из сессии в заказ: 19.10%

## Основные выводы

### Динамика по месяцам

Самый сильный месяц в данных - декабрь 2025:

- Выручка: 23 873.00
- Оплаченные заказы: 48
- Конверсия из сессии в заказ: 24.49%

### Воронка

Продуктовая воронка:

`view_item -> add_to_cart -> purchase`

Результаты:

- Пользователи, просмотревшие товар: 500
- Пользователи, добавившие товар в корзину: 385
- Пользователи, совершившие покупку: 290
- Конверсия из просмотра в корзину: 77.00%
- Конверсия из корзины в покупку: 75.32%
- Конверсия из просмотра в покупку: 58.00%

### Источники трафика

Лучший источник по конверсии из просмотра в покупку:

- `telegram`: 32.16%

Самый слабый источник:

- `google`: 23.36%

### Каналы привлечения

Лучшие каналы по выручке:

- `referral`: 51 970.96
- `social`: 51 335.17
- `email`: 45 207.53

Лучший канал по конверсии пользователя в покупателя:

- `email`: 62.37%

### Категории товаров

Лучшие категории по выручке:

- Electronics: 80 141.63
- Home: 67 450.40
- Sports: 48 133.28
- Beauty: 32 551.16

## Визуализации

Сгенерированные графики EDA:

- [Выручка по месяцам](dashboards/figures/monthly_revenue.png)
- [Пользовательская воронка](dashboards/figures/user_funnel.png)
- [Выручка по категориям](dashboards/figures/category_revenue.png)
- [Конверсия по устройствам](dashboards/figures/device_conversion.png)

## Основные файлы

SQL:

- [Схема базы данных](sql/01_create_schema.sql)
- [Загрузка данных](sql/03_load_data.sql)
- [Проверочные запросы](sql/04_validation_queries.sql)
- [Продуктовый анализ](sql/05_product_analysis.sql)
- [Views для Power BI](sql/06_powerbi_views.sql)

Python:

- [EDA notebook](notebooks/01_eda_analysis.ipynb)
- [EDA script](notebooks/eda_analysis.py)
- [Генератор данных](scripts/generate_sample_data.py)

Документация:

- [Итоги анализа](docs/analysis_summary.md)
- [Инструкция по Power BI](docs/powerbi_dashboard_guide.md)
- [Настройка PostgreSQL](docs/postgres_setup.md)
- [Описание проекта](docs/project_scope.md)
- [Roadmap](docs/roadmap.md)

## Как воспроизвести проект

Установить зависимости:

```bash
pip install -r requirements.txt
```

Сгенерировать тестовые данные:

```bash
python scripts/generate_sample_data.py
```

Создать схему PostgreSQL:

```sql
\i 'C:/Users/iliya/Desktop/product-analytics-pet-project/sql/01_create_schema.sql'
```

Загрузить данные:

```sql
\i 'C:/Users/iliya/Desktop/product-analytics-pet-project/sql/03_load_data.sql'
```

Проверить загрузку:

```sql
\i 'C:/Users/iliya/Desktop/product-analytics-pet-project/sql/04_validation_queries.sql'
```

Запустить продуктовый анализ:

```sql
\i 'C:/Users/iliya/Desktop/product-analytics-pet-project/sql/05_product_analysis.sql'
```

Запустить Python EDA:

```bash
python notebooks/eda_analysis.py
```

Подготовить CSV-файлы для Power BI:

```bash
python scripts/export_powerbi_data.py
```

## Следующие шаги

- собрать дашборд в Power BI по инструкции `docs/powerbi_dashboard_guide.md`
- добавить скриншоты дашборда
- добавить данные о стоимости привлечения
- рассчитать CAC, LTV и payback period
- добавить анализ повторных покупок
- добавить простую ML-модель для оценки вероятности покупки
