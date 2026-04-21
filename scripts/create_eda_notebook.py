from __future__ import annotations

import json
from textwrap import dedent
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = BASE_DIR / "notebooks" / "01_eda_analysis.ipynb"


def markdown_cell(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": dedent(source).strip().splitlines(keepends=True),
    }


def code_cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": dedent(source).strip().splitlines(keepends=True),
    }


def main() -> None:
    notebook = {
        "cells": [
            markdown_cell(
                """
                # E-commerce Product Analytics: EDA

                This notebook explores synthetic e-commerce data generated for a product analytics pet project.

                Main goals:

                - inspect the dataset structure
                - calculate core business metrics
                - analyze revenue dynamics
                - analyze the product funnel
                - compare product categories and device types
                """
            ),
            code_cell(
                """
                from pathlib import Path

                import matplotlib.pyplot as plt
                import pandas as pd
                import seaborn as sns

                sns.set_theme(style="whitegrid")

                BASE_DIR = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
                DATA_DIR = BASE_DIR / "data" / "sample"
                FIGURES_DIR = BASE_DIR / "dashboards" / "figures"
                FIGURES_DIR.mkdir(parents=True, exist_ok=True)
                """
            ),
            markdown_cell(
                """
                ## 1. Load Data

                The project uses six main tables:

                - users
                - products
                - sessions
                - orders
                - order_items
                - events
                """
            ),
            code_cell(
                """
                users = pd.read_csv(DATA_DIR / "users.csv", parse_dates=["signup_date", "first_session_at"])
                products = pd.read_csv(DATA_DIR / "products.csv", parse_dates=["created_at"])
                sessions = pd.read_csv(
                    DATA_DIR / "sessions.csv",
                    parse_dates=["session_started_at", "session_ended_at"],
                )
                orders = pd.read_csv(DATA_DIR / "orders.csv", parse_dates=["order_created_at"])
                order_items = pd.read_csv(DATA_DIR / "order_items.csv")
                events = pd.read_csv(DATA_DIR / "events.csv", parse_dates=["event_time"])

                tables = {
                    "users": users,
                    "products": products,
                    "sessions": sessions,
                    "orders": orders,
                    "order_items": order_items,
                    "events": events,
                }

                pd.DataFrame(
                    [{"table": name, "rows": len(df), "columns": df.shape[1]} for name, df in tables.items()]
                )
                """
            ),
            markdown_cell(
                """
                ## 2. Overall Metrics

                We calculate core project KPIs:

                - users
                - sessions
                - paid orders
                - revenue
                - average order value
                - session-to-order conversion
                """
            ),
            code_cell(
                """
                paid_orders = orders[orders["payment_status"] == "paid"].copy()

                overall_metrics = pd.DataFrame(
                    [
                        {
                            "users_count": users["user_id"].nunique(),
                            "sessions_count": sessions["session_id"].nunique(),
                            "paid_orders_count": paid_orders["order_id"].nunique(),
                            "revenue": paid_orders["total_amount"].sum(),
                            "average_order_value": paid_orders["total_amount"].mean(),
                            "session_to_order_conversion": (
                                paid_orders["order_id"].nunique() / sessions["session_id"].nunique()
                            ),
                        }
                    ]
                )

                overall_metrics
                """
            ),
            markdown_cell(
                """
                **Interpretation**

                This table gives a high-level view of the product.
                These KPIs are usually used as dashboard cards in BI tools.
                """
            ),
            markdown_cell(
                """
                ## 3. Monthly Revenue Dynamics
                """
            ),
            code_cell(
                """
                paid_orders["month"] = paid_orders["order_created_at"].dt.to_period("M").dt.to_timestamp()

                monthly_metrics = (
                    paid_orders.groupby("month", as_index=False)
                    .agg(
                        revenue=("total_amount", "sum"),
                        paid_orders_count=("order_id", "nunique"),
                        average_order_value=("total_amount", "mean"),
                    )
                    .sort_values("month")
                )

                monthly_metrics.tail()
                """
            ),
            code_cell(
                """
                plt.figure(figsize=(12, 6))
                sns.lineplot(data=monthly_metrics, x="month", y="revenue", marker="o", linewidth=2.5)
                plt.title("Monthly Revenue")
                plt.xlabel("Month")
                plt.ylabel("Revenue")
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig(FIGURES_DIR / "monthly_revenue.png", dpi=160)
                plt.show()
                """
            ),
            markdown_cell(
                """
                **Interpretation**

                Monthly revenue helps detect seasonality, growth periods, and possible drops.
                In the current generated dataset, December 2025 is the strongest month by revenue and order count.
                """
            ),
            markdown_cell(
                """
                ## 4. Funnel Analysis

                Funnel steps:

                1. `view_item`
                2. `add_to_cart`
                3. `purchase`
                """
            ),
            code_cell(
                """
                funnel_order = ["view_item", "add_to_cart", "purchase"]
                funnel = (
                    events.groupby("event_type", as_index=False)
                    .agg(users_count=("user_id", "nunique"))
                    .set_index("event_type")
                    .loc[funnel_order]
                    .reset_index()
                )

                funnel["conversion_from_previous_step"] = (
                    funnel["users_count"] / funnel["users_count"].shift(1)
                )
                funnel["conversion_from_first_step"] = funnel["users_count"] / funnel.loc[0, "users_count"]

                funnel
                """
            ),
            code_cell(
                """
                plt.figure(figsize=(9, 6))
                sns.barplot(data=funnel, x="event_type", y="users_count", hue="event_type", legend=False)
                plt.title("User Funnel")
                plt.xlabel("Event Type")
                plt.ylabel("Unique Users")
                plt.tight_layout()
                plt.savefig(FIGURES_DIR / "user_funnel.png", dpi=160)
                plt.show()
                """
            ),
            markdown_cell(
                """
                **Interpretation**

                The funnel shows where users drop off before purchase.
                This is one of the core tools in product analytics.
                """
            ),
            markdown_cell(
                """
                ## 5. Revenue by Product Category
                """
            ),
            code_cell(
                """
                category_revenue = (
                    order_items.merge(paid_orders[["order_id"]], on="order_id", how="inner")
                    .merge(products[["product_id", "category"]], on="product_id", how="left")
                    .groupby("category", as_index=False)
                    .agg(revenue=("item_amount", "sum"), items_sold=("quantity", "sum"))
                    .sort_values("revenue", ascending=False)
                )

                category_revenue
                """
            ),
            code_cell(
                """
                plt.figure(figsize=(10, 6))
                sns.barplot(data=category_revenue, x="category", y="revenue", hue="category", legend=False)
                plt.title("Revenue by Product Category")
                plt.xlabel("Category")
                plt.ylabel("Revenue")
                plt.tight_layout()
                plt.savefig(FIGURES_DIR / "category_revenue.png", dpi=160)
                plt.show()
                """
            ),
            markdown_cell(
                """
                **Interpretation**

                Category analysis helps identify the main revenue drivers.
                In the current dataset, Electronics and Home are the strongest categories by revenue.
                """
            ),
            markdown_cell(
                """
                ## 6. Device Conversion
                """
            ),
            code_cell(
                """
                paid_orders["order_date"] = paid_orders["order_created_at"].dt.date
                sessions["session_date"] = sessions["session_started_at"].dt.date

                device_metrics = (
                    sessions.merge(
                        paid_orders[["order_id", "user_id", "order_date", "total_amount"]],
                        left_on=["user_id", "session_date"],
                        right_on=["user_id", "order_date"],
                        how="left",
                    )
                    .groupby("device_type", as_index=False)
                    .agg(
                        sessions_count=("session_id", "nunique"),
                        paid_orders_count=("order_id", "nunique"),
                        revenue=("total_amount", "sum"),
                    )
                )

                device_metrics["session_to_order_conversion"] = (
                    device_metrics["paid_orders_count"] / device_metrics["sessions_count"]
                )

                device_metrics.sort_values("session_to_order_conversion", ascending=False)
                """
            ),
            code_cell(
                """
                plt.figure(figsize=(9, 6))
                sns.barplot(
                    data=device_metrics.sort_values("session_to_order_conversion", ascending=False),
                    x="device_type",
                    y="session_to_order_conversion",
                    hue="device_type",
                    legend=False,
                )
                plt.title("Session-to-Order Conversion by Device")
                plt.xlabel("Device Type")
                plt.ylabel("Conversion")
                plt.tight_layout()
                plt.savefig(FIGURES_DIR / "device_conversion.png", dpi=160)
                plt.show()
                """
            ),
            markdown_cell(
                """
                **Interpretation**

                Device analysis helps find UX or checkout problems.
                In this dataset, desktop users convert better than mobile users.
                """
            ),
            markdown_cell(
                """
                ## 7. Final Notes

                This notebook covers the first EDA stage.

                Next possible steps:

                - connect notebook directly to PostgreSQL
                - add acquisition cost data
                - calculate CAC, LTV, and payback
                - build Power BI dashboard
                - add a simple ML model for purchase probability
                """
            ),
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.12",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }

    NOTEBOOK_PATH.write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Notebook created: {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()
