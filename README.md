# Product Analytics Pet Project

This repository contains a pet project for developing skills in:

- product analytics
- data analytics
- SQL and PostgreSQL
- Python and pandas
- Power BI

## Project idea

The project simulates analytics for an e-commerce product.
We will build a small analytical system from scratch:

- design a PostgreSQL database
- load sample product and user activity data
- calculate core business and product metrics with SQL
- analyze data in Python
- build dashboards in Power BI

## Main goals

- learn how to work with relational data in PostgreSQL
- practice SQL on realistic analytical tasks
- understand product metrics such as conversion, retention, revenue, and average order value
- create a portfolio-ready project for analyst roles

## Planned stack

- `PostgreSQL`
- `SQL`
- `Python`
- `pandas`
- `NumPy`
- `Jupyter Notebook`
- `Power BI`

## Repository structure

- `sql/` — schema, data loading scripts, and analytical queries
- `notebooks/` — Python notebooks for exploratory analysis
- `data/` — source and generated datasets
- `dashboards/` — dashboard files and screenshots
- `docs/` — project notes, metric definitions, and roadmap

## Project scenario

We assume that we work with an online store and want to answer questions such as:

- how many users visit the product
- how many of them add items to cart
- how many complete a purchase
- what the conversion rate is
- how revenue changes over time
- which categories sell the best
- how user retention changes by signup cohort

## First stage

At the first stage, this repository includes:

- database schema for PostgreSQL
- metric definitions
- starter SQL queries for business analysis
- sample data generator

## How to generate sample data

Run:

```bash
python scripts/generate_sample_data.py
```

The script will create CSV files in `data/sample/` for:

- `users`
- `products`
- `sessions`
- `orders`
- `order_items`
- `events`

## How to load data into PostgreSQL

Detailed steps are in:

- `docs/postgres_setup.md`

Main SQL scripts:

- `sql/01_create_schema.sql`
- `sql/03_load_data.sql`
- `sql/04_validation_queries.sql`
- `sql/02_analytics_queries.sql`
- `sql/05_product_analysis.sql`

Main analysis summary:

- `docs/analysis_summary.md`

## Python EDA

Install dependencies:

```bash
pip install -r requirements.txt
```

Run EDA:

```bash
python notebooks/eda_analysis.py
```

The script creates charts in `dashboards/figures/`.

Main notebook:

- `notebooks/01_eda_analysis.ipynb`

## Next steps

1. Create the database in PostgreSQL.
2. Generate or load sample data into the tables.
3. Run analytical SQL queries.
4. Build a Python notebook for exploratory analysis.
5. Create a Power BI dashboard.
