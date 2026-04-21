# PostgreSQL Setup

## Goal

Create a local database for the project, load generated CSV files, and run the first analytical queries.

## Recommended flow

1. Create a database named `product_analytics`.
2. Run the schema script.
3. Load sample CSV data.
4. Run validation queries.
5. Run analytical queries.

## Example commands

Use the installed PostgreSQL client:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d postgres
```

Inside `psql`, create a new database:

```sql
CREATE DATABASE product_analytics;
```

Then connect to it:

```sql
\c product_analytics
```

Run the schema:

```sql
\i 'C:/Users/iliya/Desktop/product-analytics-pet-project/sql/01_create_schema.sql'
```

Load the data:

```sql
\i 'C:/Users/iliya/Desktop/product-analytics-pet-project/sql/03_load_data.sql'
```

Check that everything loaded correctly:

```sql
\i 'C:/Users/iliya/Desktop/product-analytics-pet-project/sql/04_validation_queries.sql'
```

Run the first analytics:

```sql
\i 'C:/Users/iliya/Desktop/product-analytics-pet-project/sql/02_analytics_queries.sql'
```
