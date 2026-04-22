from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "sample"
FIGURES_DIR = BASE_DIR / "dashboards" / "figures"


def load_data() -> dict[str, pd.DataFrame]:
    return {
        "users": pd.read_csv(DATA_DIR / "users.csv", parse_dates=["signup_date", "first_session_at"]),
        "products": pd.read_csv(DATA_DIR / "products.csv", parse_dates=["created_at"]),
        "marketing_spend": pd.read_csv(DATA_DIR / "marketing_spend.csv"),
        "ab_test_assignments": pd.read_csv(DATA_DIR / "ab_test_assignments.csv", parse_dates=["assigned_at"]),
        "sessions": pd.read_csv(
            DATA_DIR / "sessions.csv",
            parse_dates=["session_started_at", "session_ended_at"],
        ),
        "orders": pd.read_csv(DATA_DIR / "orders.csv", parse_dates=["order_created_at"]),
        "order_items": pd.read_csv(DATA_DIR / "order_items.csv"),
        "events": pd.read_csv(DATA_DIR / "events.csv", parse_dates=["event_time"]),
    }


def save_monthly_revenue_chart(orders: pd.DataFrame) -> pd.DataFrame:
    paid_orders = orders[orders["payment_status"] == "paid"].copy()
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

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=monthly_metrics, x="month", y="revenue", marker="o", linewidth=2.5)
    plt.title("Выручка по месяцам")
    plt.xlabel("Месяц")
    plt.ylabel("Выручка")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "monthly_revenue.png", dpi=160)
    plt.close()

    return monthly_metrics


def save_category_revenue_chart(products: pd.DataFrame, orders: pd.DataFrame, order_items: pd.DataFrame) -> pd.DataFrame:
    paid_orders = orders.loc[orders["payment_status"] == "paid", ["order_id"]]
    category_revenue = (
        order_items.merge(paid_orders, on="order_id", how="inner")
        .merge(products[["product_id", "category"]], on="product_id", how="left")
        .groupby("category", as_index=False)
        .agg(revenue=("item_amount", "sum"), items_sold=("quantity", "sum"))
        .sort_values("revenue", ascending=False)
    )

    plt.figure(figsize=(10, 6))
    sns.barplot(data=category_revenue, x="category", y="revenue", hue="category", legend=False)
    plt.title("Выручка по категориям")
    plt.xlabel("Категория")
    plt.ylabel("Выручка")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "category_revenue.png", dpi=160)
    plt.close()

    return category_revenue


def save_funnel_chart(events: pd.DataFrame) -> pd.DataFrame:
    funnel_order = ["view_item", "add_to_cart", "purchase"]
    funnel = (
        events.groupby("event_type", as_index=False)
        .agg(users_count=("user_id", "nunique"))
        .set_index("event_type")
        .loc[funnel_order]
        .reset_index()
    )

    plt.figure(figsize=(9, 6))
    sns.barplot(data=funnel, x="event_type", y="users_count", hue="event_type", legend=False)
    plt.title("Пользовательская воронка")
    plt.xlabel("Тип события")
    plt.ylabel("Уникальные пользователи")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "user_funnel.png", dpi=160)
    plt.close()

    return funnel


def save_device_conversion_chart(sessions: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
    paid_orders = orders[orders["payment_status"] == "paid"].copy()
    paid_orders["order_date"] = paid_orders["order_created_at"].dt.date
    sessions = sessions.copy()
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

    plt.figure(figsize=(9, 6))
    sns.barplot(
        data=device_metrics.sort_values("session_to_order_conversion", ascending=False),
        x="device_type",
        y="session_to_order_conversion",
        hue="device_type",
        legend=False,
    )
    plt.title("Конверсия из сессии в заказ по устройствам")
    plt.xlabel("Тип устройства")
    plt.ylabel("Конверсия")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "device_conversion.png", dpi=160)
    plt.close()

    return device_metrics


def save_ltv_cac_chart(users: pd.DataFrame, orders: pd.DataFrame, marketing_spend: pd.DataFrame) -> pd.DataFrame:
    paid_orders = orders[orders["payment_status"] == "paid"]
    user_orders = paid_orders.groupby("user_id", as_index=False).agg(
        orders_count=("order_id", "nunique"),
        revenue=("total_amount", "sum"),
    )
    user_ltv = (
        users[["user_id", "acquisition_channel"]]
        .merge(user_orders, on="user_id", how="left")
        .fillna({"orders_count": 0, "revenue": 0})
    )

    rows = []
    for channel, group in user_ltv.groupby("acquisition_channel"):
        paying_users_count = (group["orders_count"] > 0).sum()
        total_revenue = group["revenue"].sum()
        rows.append(
            {
                "acquisition_channel": channel,
                "avg_ltv_per_paying_user": total_revenue / paying_users_count,
                "paying_users_count": paying_users_count,
            }
        )

    metrics = pd.DataFrame(rows).merge(marketing_spend, on="acquisition_channel", how="left")
    metrics["cac"] = metrics["marketing_spend"] / metrics["paying_users_count"]
    metrics["ltv_cac_ratio"] = metrics["avg_ltv_per_paying_user"] / metrics["cac"]

    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=metrics.sort_values("ltv_cac_ratio", ascending=False),
        x="acquisition_channel",
        y="ltv_cac_ratio",
        hue="acquisition_channel",
        legend=False,
    )
    plt.title("LTV/CAC по каналам привлечения")
    plt.xlabel("Канал привлечения")
    plt.ylabel("LTV/CAC")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "ltv_cac_by_channel.png", dpi=160)
    plt.close()

    return metrics.sort_values("ltv_cac_ratio", ascending=False)


def save_ab_test_conversion_chart(ab_test_assignments: pd.DataFrame) -> pd.DataFrame:
    ab_results = (
        ab_test_assignments.groupby("variant", as_index=False)
        .agg(users_count=("user_id", "nunique"), conversions_count=("converted", "sum"))
        .sort_values("variant")
    )
    ab_results["conversion_rate"] = ab_results["conversions_count"] / ab_results["users_count"]

    plt.figure(figsize=(8, 6))
    sns.barplot(data=ab_results, x="variant", y="conversion_rate", hue="variant", legend=False)
    plt.title("A/B-тест CTA: конверсия по вариантам")
    plt.xlabel("Вариант")
    plt.ylabel("Конверсия")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "ab_test_conversion.png", dpi=160)
    plt.close()

    return ab_results


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    data = load_data()

    monthly_metrics = save_monthly_revenue_chart(data["orders"])
    category_revenue = save_category_revenue_chart(data["products"], data["orders"], data["order_items"])
    funnel = save_funnel_chart(data["events"])
    device_metrics = save_device_conversion_chart(data["sessions"], data["orders"])
    ltv_cac = save_ltv_cac_chart(data["users"], data["orders"], data["marketing_spend"])
    ab_test_results = save_ab_test_conversion_chart(data["ab_test_assignments"])

    print("EDA завершен.")
    print("\nМетрики по месяцам:")
    print(monthly_metrics.tail())
    print("\nВыручка по категориям:")
    print(category_revenue)
    print("\nВоронка:")
    print(funnel)
    print("\nМетрики по устройствам:")
    print(device_metrics)
    print("\nLTV/CAC по каналам:")
    print(ltv_cac)
    print("\nA/B-тест:")
    print(ab_test_results)
    print(f"\nГрафики сохранены в: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
