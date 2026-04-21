# Настройка PostgreSQL

## Цель

Создать локальную базу данных для проекта, загрузить сгенерированные CSV-файлы и запустить первые аналитические запросы.

## Рекомендуемый порядок

1. Создать базу данных `product_analytics`.
2. Запустить скрипт создания схемы.
3. Загрузить CSV-данные.
4. Запустить проверочные запросы.
5. Запустить аналитические запросы.

## Пример команд

Использовать установленный клиент PostgreSQL:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d postgres
```

Внутри `psql` создать новую базу:

```sql
CREATE DATABASE product_analytics;
```

Подключиться к ней:

```sql
\c product_analytics
```

Запустить схему:

```sql
\i 'C:/Users/iliya/Desktop/product-analytics-pet-project/sql/01_create_schema.sql'
```

Загрузить данные:

```sql
\i 'C:/Users/iliya/Desktop/product-analytics-pet-project/sql/03_load_data.sql'
```

Проверить, что данные загрузились корректно:

```sql
\i 'C:/Users/iliya/Desktop/product-analytics-pet-project/sql/04_validation_queries.sql'
```

Запустить первый аналитический блок:

```sql
\i 'C:/Users/iliya/Desktop/product-analytics-pet-project/sql/02_analytics_queries.sql'
```
