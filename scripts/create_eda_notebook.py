from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent


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
                # EDA для e-commerce проекта

                Этот notebook анализирует синтетические данные интернет-магазина, созданные для pet-проекта по продуктовой аналитике.

                Основные цели:

                - изучить структуру данных
                - посчитать ключевые бизнес-метрики
                - проанализировать динамику выручки
                - разобрать продуктовую воронку
                - сравнить категории товаров и типы устройств
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
                ## 1. Загрузка данных

                В проекте используется шесть основных таблиц:

                - `users`
                - `products`
                - `sessions`
                - `orders`
                - `order_items`
                - `events`
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
                ## 2. Общие метрики

                Считаем базовые KPI проекта:

                - количество пользователей
                - количество сессий
                - количество оплаченных заказов
                - выручка
                - средний чек
                - конверсия из сессии в заказ
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
                **Интерпретация**

                Эта таблица дает верхнеуровневый срез продукта.
                Такие KPI обычно выносят в карточки на BI-дашборде.
                """
            ),
            markdown_cell(
                """
                ## 3. Динамика выручки по месяцам
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
                plt.title("Выручка по месяцам")
                plt.xlabel("Месяц")
                plt.ylabel("Выручка")
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig(FIGURES_DIR / "monthly_revenue.png", dpi=160)
                plt.show()
                """
            ),
            markdown_cell(
                """
                **Интерпретация**

                Помесячная выручка помогает находить сезонность, периоды роста и возможные просадки.
                В текущем сгенерированном датасете декабрь 2025 - самый сильный месяц по выручке и количеству заказов.
                """
            ),
            markdown_cell(
                """
                ## 4. Анализ воронки

                Шаги воронки:

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
                plt.title("Пользовательская воронка")
                plt.xlabel("Тип события")
                plt.ylabel("Уникальные пользователи")
                plt.tight_layout()
                plt.savefig(FIGURES_DIR / "user_funnel.png", dpi=160)
                plt.show()
                """
            ),
            markdown_cell(
                """
                **Интерпретация**

                Воронка показывает, на каких шагах пользователи отваливаются до покупки.
                Это один из базовых инструментов продуктового аналитика.
                """
            ),
            markdown_cell(
                """
                ## 5. Выручка по категориям товаров
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
                plt.title("Выручка по категориям")
                plt.xlabel("Категория")
                plt.ylabel("Выручка")
                plt.tight_layout()
                plt.savefig(FIGURES_DIR / "category_revenue.png", dpi=160)
                plt.show()
                """
            ),
            markdown_cell(
                """
                **Интерпретация**

                Анализ категорий помогает найти основные драйверы выручки.
                В текущем датасете категории Electronics и Home дают наибольшую выручку.
                """
            ),
            markdown_cell(
                """
                ## 6. Конверсия по типам устройств
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
                plt.title("Конверсия из сессии в заказ по устройствам")
                plt.xlabel("Тип устройства")
                plt.ylabel("Конверсия")
                plt.tight_layout()
                plt.savefig(FIGURES_DIR / "device_conversion.png", dpi=160)
                plt.show()
                """
            ),
            markdown_cell(
                """
                **Интерпретация**

                Анализ устройств помогает находить UX-проблемы или проблемы в checkout.
                В этом датасете desktop-пользователи конвертируются лучше, чем mobile-пользователи.
                """
            ),
            markdown_cell(
                """
                ## 7. Финальные заметки

                Этот notebook покрывает первый этап EDA.
                Финальные выводы по LTV, маркетинговой эффективности и A/B-тесту описаны в `docs/final_report.md`.

                Что уже добавлено в проект после базового EDA:

                - маркетинговые расходы и ROMI
                - повторные покупки и LTV
                - LTV/CAC по каналам
                - синтетический A/B-тест
                - финальный dashboard
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
    print(f"Notebook создан: {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()
