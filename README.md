# Product Analytics Pet Project

Portfolio project for practicing data analytics and product analytics on synthetic e-commerce data.

The project covers the full analytical workflow:

- data generation
- PostgreSQL database design
- SQL analysis
- Python EDA
- dashboard-ready visualizations
- business insights

## Project Scenario

We analyze a simulated online store and answer product and business questions:

- How many users visit the product?
- How many users add items to cart?
- How many users complete purchases?
- What is the session-to-order conversion?
- Which channels generate the most revenue?
- Which traffic sources convert best?
- Which product categories drive revenue?
- How does retention change by signup cohort?

## Stack

- PostgreSQL
- SQL
- Python
- pandas
- NumPy
- matplotlib
- seaborn
- Jupyter Notebook
- Power BI, planned

## Data Model

The database contains six main tables:

- `users` - user profile and acquisition data
- `products` - product catalog
- `sessions` - user visits
- `events` - product events such as `view_item`, `add_to_cart`, `purchase`
- `orders` - order-level data
- `order_items` - product-level order data

## Repository Structure

- `data/sample/` - generated CSV data
- `sql/` - database schema, data loading scripts, and analytical queries
- `notebooks/` - Python EDA notebook and script
- `dashboards/figures/` - generated charts
- `docs/` - project scope, roadmap, setup guide, and analysis summary
- `scripts/` - data and notebook generation scripts

## Key Metrics

Current generated dataset:

- Users: 500
- Sessions: 2,225
- Paid orders: 425
- Events: 6,752
- Revenue: 221,082.40
- Average order value: 520.19
- Session-to-order conversion: 19.10%

## Key Findings

### Monthly Dynamics

December 2025 is the strongest month:

- Revenue: 23,873.00
- Paid orders: 48
- Session-to-order conversion: 24.49%

### Funnel

Product funnel:

`view_item -> add_to_cart -> purchase`

Results:

- Viewed users: 500
- Cart users: 385
- Purchase users: 290
- View-to-cart conversion: 77.00%
- Cart-to-purchase conversion: 75.32%
- View-to-purchase conversion: 58.00%

### Traffic Sources

Best source by view-to-purchase conversion:

- `telegram`: 32.16%

Lowest source:

- `google`: 23.36%

### Acquisition Channels

Top channels by revenue:

- `referral`: 51,970.96
- `social`: 51,335.17
- `email`: 45,207.53

Best channel by user-to-buyer conversion:

- `email`: 62.37%

### Categories

Top categories by revenue:

- Electronics: 80,141.63
- Home: 67,450.40
- Sports: 48,133.28
- Beauty: 32,551.16

## Visualizations

Generated EDA charts:

- [Monthly revenue](dashboards/figures/monthly_revenue.png)
- [User funnel](dashboards/figures/user_funnel.png)
- [Revenue by category](dashboards/figures/category_revenue.png)
- [Device conversion](dashboards/figures/device_conversion.png)

## Main Files

SQL:

- [Database schema](sql/01_create_schema.sql)
- [Data loading script](sql/03_load_data.sql)
- [Validation queries](sql/04_validation_queries.sql)
- [Product analysis queries](sql/05_product_analysis.sql)

Python:

- [EDA notebook](notebooks/01_eda_analysis.ipynb)
- [EDA script](notebooks/eda_analysis.py)
- [Sample data generator](scripts/generate_sample_data.py)

Documentation:

- [Analysis summary](docs/analysis_summary.md)
- [PostgreSQL setup](docs/postgres_setup.md)
- [Project scope](docs/project_scope.md)
- [Roadmap](docs/roadmap.md)

## How to Reproduce

Install dependencies:

```bash
pip install -r requirements.txt
```

Generate sample data:

```bash
python scripts/generate_sample_data.py
```

Create PostgreSQL schema:

```sql
\i 'C:/Users/iliya/Desktop/product-analytics-pet-project/sql/01_create_schema.sql'
```

Load sample data:

```sql
\i 'C:/Users/iliya/Desktop/product-analytics-pet-project/sql/03_load_data.sql'
```

Run validation:

```sql
\i 'C:/Users/iliya/Desktop/product-analytics-pet-project/sql/04_validation_queries.sql'
```

Run product analysis:

```sql
\i 'C:/Users/iliya/Desktop/product-analytics-pet-project/sql/05_product_analysis.sql'
```

Run Python EDA:

```bash
python notebooks/eda_analysis.py
```

## Next Steps

- Build Power BI dashboard
- Add dashboard screenshots
- Add acquisition cost data
- Calculate CAC, LTV, and payback period
- Add repeat purchase analysis
- Add a simple ML model for purchase probability
