from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "sample"
OUTPUT_DIR = BASE_DIR / "dashboards" / "powerbi_data"


def load_data() -> dict[str, pd.DataFrame]:
    return {
        "users": pd.read_csv(DATA_DIR / "users.csv", parse_dates=["signup_date", "first_session_at"]),
        "products": pd.read_csv(DATA_DIR / "products.csv", parse_dates=["created_at"]),
        "sessions": pd.read_csv(
            DATA_DIR / "sessions.csv",
            parse_dates=["session_started_at", "session_ended_at"],
        ),
        "orders": pd.read_csv(DATA_DIR / "orders.csv", parse_dates=["order_created_at"]),
        "order_items": pd.read_csv(DATA_DIR / "order_items.csv"),
        "events": pd.read_csv(DATA_DIR / "events.csv", parse_dates=["event_time"]),
    }


def export_csv(df: pd.DataFrame, filename: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_DIR / filename, index=False, encoding="utf-8-sig")


def build_kpi_overview(users: pd.DataFrame, sessions: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
    paid_orders = orders[orders["payment_status"] == "paid"]
    sessions_count = sessions["session_id"].nunique()
    paid_orders_count = paid_orders["order_id"].nunique()

    rows = [
        {"metric": "Пользователи", "value": users["user_id"].nunique()},
        {"metric": "Сессии", "value": sessions_count},
        {"metric": "Оплаченные заказы", "value": paid_orders_count},
        {"metric": "Выручка", "value": paid_orders["total_amount"].sum()},
        {"metric": "Средний чек", "value": paid_orders["total_amount"].mean()},
        {"metric": "Конверсия сессии в заказ", "value": paid_orders_count / sessions_count},
    ]
    return pd.DataFrame(rows)


def build_monthly_metrics(sessions: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
    monthly_sessions = sessions.copy()
    monthly_sessions["month"] = monthly_sessions["session_started_at"].dt.to_period("M").dt.to_timestamp()
    monthly_sessions = (
        monthly_sessions.groupby("month", as_index=False)
        .agg(
            active_users_count=("user_id", "nunique"),
            sessions_count=("session_id", "nunique"),
        )
        .sort_values("month")
    )

    paid_orders = orders[orders["payment_status"] == "paid"].copy()
    paid_orders["month"] = paid_orders["order_created_at"].dt.to_period("M").dt.to_timestamp()
    monthly_orders = (
        paid_orders.groupby("month", as_index=False)
        .agg(
            paying_users_count=("user_id", "nunique"),
            paid_orders_count=("order_id", "nunique"),
            revenue=("total_amount", "sum"),
            average_order_value=("total_amount", "mean"),
        )
        .sort_values("month")
    )

    monthly_metrics = monthly_sessions.merge(monthly_orders, on="month", how="left").fillna(0)
    monthly_metrics["session_to_order_conversion"] = (
        monthly_metrics["paid_orders_count"] / monthly_metrics["sessions_count"]
    )
    return monthly_metrics


def build_funnel(events: pd.DataFrame) -> pd.DataFrame:
    funnel_order = ["view_item", "add_to_cart", "purchase"]
    funnel = (
        events.groupby("event_type", as_index=False)
        .agg(users_count=("user_id", "nunique"))
        .set_index("event_type")
        .loc[funnel_order]
        .reset_index()
    )
    funnel["step_order"] = range(1, len(funnel) + 1)
    funnel["conversion_from_previous_step"] = funnel["users_count"] / funnel["users_count"].shift(1)
    funnel["conversion_from_first_step"] = funnel["users_count"] / funnel.loc[0, "users_count"]
    return funnel


def build_traffic_source_funnel(events: pd.DataFrame, sessions: pd.DataFrame) -> pd.DataFrame:
    source_events = events.merge(sessions[["session_id", "traffic_source"]], on="session_id", how="left")
    rows = []
    for source, group in source_events.groupby("traffic_source"):
        viewed_users = group.loc[group["event_type"] == "view_item", "user_id"].nunique()
        cart_users = group.loc[group["event_type"] == "add_to_cart", "user_id"].nunique()
        purchase_users = group.loc[group["event_type"] == "purchase", "user_id"].nunique()
        rows.append(
            {
                "traffic_source": source,
                "viewed_users": viewed_users,
                "cart_users": cart_users,
                "purchase_users": purchase_users,
                "view_to_cart_conversion": cart_users / viewed_users if viewed_users else 0,
                "cart_to_purchase_conversion": purchase_users / cart_users if cart_users else 0,
                "view_to_purchase_conversion": purchase_users / viewed_users if viewed_users else 0,
            }
        )
    return pd.DataFrame(rows).sort_values("view_to_purchase_conversion", ascending=False)


def build_acquisition_channel_metrics(users: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
    paid_orders = orders[orders["payment_status"] == "paid"]
    orders_by_channel = users.merge(paid_orders, on="user_id", how="left")
    metrics = (
        orders_by_channel.groupby("acquisition_channel", as_index=False)
        .agg(
            users_count=("user_id", "nunique"),
            paying_users_count=("order_id", lambda x: orders_by_channel.loc[x.index, "user_id"][x.notna()].nunique()),
            paid_orders_count=("order_id", "nunique"),
            revenue=("total_amount", "sum"),
        )
        .fillna(0)
    )
    metrics["revenue_per_paying_user"] = metrics["revenue"] / metrics["paying_users_count"].replace(0, pd.NA)
    metrics["user_to_buyer_conversion"] = metrics["paying_users_count"] / metrics["users_count"]
    return metrics.sort_values("revenue", ascending=False)


def build_device_metrics(sessions: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
    paid_orders = orders[orders["payment_status"] == "paid"].copy()
    paid_orders["order_date"] = paid_orders["order_created_at"].dt.date
    sessions = sessions.copy()
    sessions["session_date"] = sessions["session_started_at"].dt.date

    metrics = (
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
        .fillna(0)
    )
    metrics["session_to_order_conversion"] = metrics["paid_orders_count"] / metrics["sessions_count"]
    return metrics.sort_values("revenue", ascending=False)


def build_category_revenue(products: pd.DataFrame, orders: pd.DataFrame, order_items: pd.DataFrame) -> pd.DataFrame:
    paid_order_ids = orders.loc[orders["payment_status"] == "paid", ["order_id"]]
    metrics = (
        order_items.merge(paid_order_ids, on="order_id", how="inner")
        .merge(products[["product_id", "category"]], on="product_id", how="left")
        .groupby("category", as_index=False)
        .agg(
            paid_orders_count=("order_id", "nunique"),
            items_sold=("quantity", "sum"),
            revenue=("item_amount", "sum"),
        )
    )
    metrics["average_item_price"] = metrics["revenue"] / metrics["items_sold"]
    return metrics.sort_values("revenue", ascending=False)


def build_top_products(products: pd.DataFrame, orders: pd.DataFrame, order_items: pd.DataFrame) -> pd.DataFrame:
    paid_order_ids = orders.loc[orders["payment_status"] == "paid", ["order_id"]]
    return (
        order_items.merge(paid_order_ids, on="order_id", how="inner")
        .merge(products[["product_id", "product_name", "category"]], on="product_id", how="left")
        .groupby(["product_id", "product_name", "category"], as_index=False)
        .agg(
            paid_orders_count=("order_id", "nunique"),
            items_sold=("quantity", "sum"),
            revenue=("item_amount", "sum"),
        )
        .sort_values("revenue", ascending=False)
        .head(10)
    )


def build_retention_cohorts(users: pd.DataFrame, sessions: pd.DataFrame) -> pd.DataFrame:
    cohort_base = users[["user_id", "signup_date"]].copy()
    cohort_base["cohort_month"] = cohort_base["signup_date"].dt.to_period("M").dt.to_timestamp()

    activity = sessions[["user_id", "session_started_at"]].drop_duplicates().copy()
    activity["activity_month"] = activity["session_started_at"].dt.to_period("M").dt.to_timestamp()
    activity = activity[["user_id", "activity_month"]].drop_duplicates()

    cohort_activity = cohort_base.merge(activity, on="user_id", how="inner")
    cohort_activity = cohort_activity[cohort_activity["activity_month"] >= cohort_activity["cohort_month"]].copy()
    cohort_activity["month_number"] = (
        (cohort_activity["activity_month"].dt.year - cohort_activity["cohort_month"].dt.year) * 12
        + (cohort_activity["activity_month"].dt.month - cohort_activity["cohort_month"].dt.month)
    )

    cohort_sizes = cohort_base.groupby("cohort_month", as_index=False).agg(cohort_size=("user_id", "nunique"))
    retention = (
        cohort_activity.groupby(["cohort_month", "month_number"], as_index=False)
        .agg(active_users=("user_id", "nunique"))
        .merge(cohort_sizes, on="cohort_month", how="left")
    )
    retention["retention_rate"] = retention["active_users"] / retention["cohort_size"]
    return retention.sort_values(["cohort_month", "month_number"])


def main() -> None:
    data = load_data()

    datasets = {
        "kpi_overview.csv": build_kpi_overview(data["users"], data["sessions"], data["orders"]),
        "monthly_metrics.csv": build_monthly_metrics(data["sessions"], data["orders"]),
        "funnel.csv": build_funnel(data["events"]),
        "traffic_source_funnel.csv": build_traffic_source_funnel(data["events"], data["sessions"]),
        "acquisition_channel_metrics.csv": build_acquisition_channel_metrics(data["users"], data["orders"]),
        "device_metrics.csv": build_device_metrics(data["sessions"], data["orders"]),
        "category_revenue.csv": build_category_revenue(data["products"], data["orders"], data["order_items"]),
        "top_products.csv": build_top_products(data["products"], data["orders"], data["order_items"]),
        "retention_cohorts.csv": build_retention_cohorts(data["users"], data["sessions"]),
    }

    for filename, df in datasets.items():
        export_csv(df, filename)
        print(f"Экспортирован файл: {OUTPUT_DIR / filename}")


if __name__ == "__main__":
    main()
