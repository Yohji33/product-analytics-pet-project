from __future__ import annotations

import csv
import random
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "data" / "sample"
RANDOM_SEED = 42


def random_datetime(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_users(n_users: int) -> list[dict]:
    countries = ["Russia", "Kazakhstan", "Belarus"]
    cities = ["Saint Petersburg", "Moscow", "Kazan", "Minsk", "Almaty"]
    channels = ["organic", "ads", "social", "referral", "email"]
    devices = ["mobile", "desktop", "tablet"]
    genders = ["male", "female"]

    start = datetime(2025, 1, 1)
    end = datetime(2025, 12, 31, 23, 59, 59)

    users = []
    for user_id in range(1, n_users + 1):
        signup_at = random_datetime(start, end)
        users.append(
            {
                "user_id": user_id,
                "signup_date": signup_at.date().isoformat(),
                "first_session_at": signup_at.isoformat(sep=" "),
                "country": random.choice(countries),
                "city": random.choice(cities),
                "acquisition_channel": random.choice(channels),
                "device_type": random.choice(devices),
                "birth_year": random.randint(1985, 2006),
                "gender": random.choice(genders),
            }
        )
    return users


def generate_products() -> list[dict]:
    categories = {
        "Electronics": ["Phone", "Laptop", "Headphones", "Monitor"],
        "Home": ["Lamp", "Chair", "Table", "Storage Box"],
        "Sports": ["Sneakers", "Backpack", "Yoga Mat", "Bottle"],
        "Beauty": ["Cream", "Shampoo", "Perfume", "Mask"],
    }
    brands = ["Nova", "Atlas", "Orion", "Pulse", "Aero"]
    created_at = datetime(2024, 1, 1, 10, 0, 0)

    products = []
    product_id = 1
    for category, names in categories.items():
        for name in names:
            price = round(random.uniform(10, 500), 2)
            cost = round(price * random.uniform(0.45, 0.75), 2)
            products.append(
                {
                    "product_id": product_id,
                    "product_name": f"{random.choice(brands)} {name}",
                    "category": category,
                    "brand": random.choice(brands),
                    "price": price,
                    "cost": cost,
                    "created_at": created_at.isoformat(sep=" "),
                    "is_active": "true",
                }
            )
            product_id += 1
            created_at += timedelta(days=3)
    return products


def generate_marketing_spend() -> list[dict]:
    return [
        {"acquisition_channel": "organic", "marketing_spend": 4500},
        {"acquisition_channel": "ads", "marketing_spend": 24500},
        {"acquisition_channel": "social", "marketing_spend": 17000},
        {"acquisition_channel": "referral", "marketing_spend": 11000},
        {"acquisition_channel": "email", "marketing_spend": 8500},
    ]


def generate_ab_test_assignments(users: list[dict]) -> list[dict]:
    assignments = []
    experiment_name = "product_card_cta_test"
    assigned_at = datetime(2025, 7, 1, 9, 0, 0)
    converted_limits = {"control": 45, "test": 65}
    variant_counts = {"control": 0, "test": 0}

    for assignment_id, user in enumerate(sorted(users, key=lambda item: item["user_id"]), start=1):
        variant = "control" if assignment_id % 2 else "test"
        variant_counts[variant] += 1
        converted = variant_counts[variant] <= converted_limits[variant]
        base_revenue = 480 if variant == "control" else 520
        conversion_revenue = round(base_revenue + (int(user["user_id"]) % 7) * 17.35, 2) if converted else 0

        assignments.append(
            {
                "assignment_id": assignment_id,
                "user_id": user["user_id"],
                "experiment_name": experiment_name,
                "variant": variant,
                "assigned_at": (assigned_at + timedelta(minutes=assignment_id * 17)).isoformat(sep=" "),
                "converted": "true" if converted else "false",
                "conversion_revenue": conversion_revenue,
            }
        )
    return assignments


def generate_sessions(users: list[dict]) -> list[dict]:
    traffic_sources = ["google", "yandex", "telegram", "vk", "email", "direct"]
    sessions = []
    session_id = 1

    for user in users:
        base_dt = datetime.fromisoformat(user["first_session_at"])
        sessions_per_user = random.randint(1, 8)
        for _ in range(sessions_per_user):
            started_at = base_dt + timedelta(days=random.randint(0, 90), hours=random.randint(0, 23))
            duration_minutes = random.randint(2, 45)
            ended_at = started_at + timedelta(minutes=duration_minutes)
            sessions.append(
                {
                    "session_id": session_id,
                    "user_id": user["user_id"],
                    "session_started_at": started_at.isoformat(sep=" "),
                    "session_ended_at": ended_at.isoformat(sep=" "),
                    "traffic_source": random.choice(traffic_sources),
                    "device_type": user["device_type"],
                    "country": user["country"],
                    "city": user["city"],
                }
            )
            session_id += 1
    return sessions


def generate_orders(users: list[dict], sessions: list[dict], products: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    product_prices = {product["product_id"]: float(product["price"]) for product in products}
    sessions_by_user = defaultdict(list)
    for session in sessions:
        sessions_by_user[session["user_id"]].append(session)

    orders = []
    order_items = []
    events = []
    order_id = 1
    order_item_id = 1
    event_id = 1

    for user in users:
        user_sessions = sessions_by_user[user["user_id"]]
        for session in user_sessions:
            session_started_at = datetime.fromisoformat(session["session_started_at"])

            viewed_product_ids = random.sample([p["product_id"] for p in products], k=random.randint(1, 4))
            for product_id in viewed_product_ids:
                events.append(
                    {
                        "event_id": event_id,
                        "session_id": session["session_id"],
                        "user_id": user["user_id"],
                        "product_id": product_id,
                        "order_id": "",
                        "event_time": (session_started_at + timedelta(minutes=random.randint(1, 5))).isoformat(sep=" "),
                        "event_type": "view_item",
                    }
                )
                event_id += 1

            if random.random() < 0.35:
                cart_product_id = random.choice(viewed_product_ids)
                cart_time = session_started_at + timedelta(minutes=random.randint(6, 12))
                events.append(
                    {
                        "event_id": event_id,
                        "session_id": session["session_id"],
                        "user_id": user["user_id"],
                        "product_id": cart_product_id,
                        "order_id": "",
                        "event_time": cart_time.isoformat(sep=" "),
                        "event_type": "add_to_cart",
                    }
                )
                event_id += 1

                if random.random() < 0.55:
                    checkout_time = cart_time + timedelta(minutes=random.randint(2, 10))
                    quantity = random.randint(1, 3)
                    unit_price = product_prices[cart_product_id]
                    item_amount = round(quantity * unit_price, 2)
                    discount_amount = round(item_amount * random.choice([0, 0, 0.05, 0.1]), 2)
                    shipping_amount = round(random.choice([0, 3.99, 4.99, 6.99]), 2)
                    total_amount = round(item_amount - discount_amount + shipping_amount, 2)

                    orders.append(
                        {
                            "order_id": order_id,
                            "user_id": user["user_id"],
                            "order_created_at": checkout_time.isoformat(sep=" "),
                            "order_status": "completed",
                            "payment_status": "paid",
                            "discount_amount": discount_amount,
                            "shipping_amount": shipping_amount,
                            "total_amount": total_amount,
                        }
                    )

                    order_items.append(
                        {
                            "order_item_id": order_item_id,
                            "order_id": order_id,
                            "product_id": cart_product_id,
                            "quantity": quantity,
                            "unit_price": unit_price,
                            "item_amount": item_amount,
                        }
                    )

                    events.append(
                        {
                            "event_id": event_id,
                            "session_id": session["session_id"],
                            "user_id": user["user_id"],
                            "product_id": cart_product_id,
                            "order_id": order_id,
                            "event_time": checkout_time.isoformat(sep=" "),
                            "event_type": "purchase",
                        }
                    )

                    event_id += 1
                    order_item_id += 1
                    order_id += 1

    return orders, order_items, events


def main() -> None:
    random.seed(RANDOM_SEED)

    users = generate_users(n_users=500)
    products = generate_products()
    marketing_spend = generate_marketing_spend()
    ab_test_assignments = generate_ab_test_assignments(users)
    sessions = generate_sessions(users)
    orders, order_items, events = generate_orders(users, sessions, products)

    write_csv(
        OUTPUT_DIR / "users.csv",
        users,
        [
            "user_id",
            "signup_date",
            "first_session_at",
            "country",
            "city",
            "acquisition_channel",
            "device_type",
            "birth_year",
            "gender",
        ],
    )
    write_csv(
        OUTPUT_DIR / "products.csv",
        products,
        ["product_id", "product_name", "category", "brand", "price", "cost", "created_at", "is_active"],
    )
    write_csv(
        OUTPUT_DIR / "marketing_spend.csv",
        marketing_spend,
        ["acquisition_channel", "marketing_spend"],
    )
    write_csv(
        OUTPUT_DIR / "ab_test_assignments.csv",
        ab_test_assignments,
        [
            "assignment_id",
            "user_id",
            "experiment_name",
            "variant",
            "assigned_at",
            "converted",
            "conversion_revenue",
        ],
    )
    write_csv(
        OUTPUT_DIR / "sessions.csv",
        sessions,
        [
            "session_id",
            "user_id",
            "session_started_at",
            "session_ended_at",
            "traffic_source",
            "device_type",
            "country",
            "city",
        ],
    )
    write_csv(
        OUTPUT_DIR / "orders.csv",
        orders,
        [
            "order_id",
            "user_id",
            "order_created_at",
            "order_status",
            "payment_status",
            "discount_amount",
            "shipping_amount",
            "total_amount",
        ],
    )
    write_csv(
        OUTPUT_DIR / "order_items.csv",
        order_items,
        ["order_item_id", "order_id", "product_id", "quantity", "unit_price", "item_amount"],
    )
    write_csv(
        OUTPUT_DIR / "events.csv",
        events,
        ["event_id", "session_id", "user_id", "product_id", "order_id", "event_time", "event_type"],
    )

    print(f"Sample data generated in: {OUTPUT_DIR}")
    print(f"Users: {len(users)}")
    print(f"Products: {len(products)}")
    print(f"Marketing spend rows: {len(marketing_spend)}")
    print(f"A/B test assignments: {len(ab_test_assignments)}")
    print(f"Sessions: {len(sessions)}")
    print(f"Orders: {len(orders)}")
    print(f"Order items: {len(order_items)}")
    print(f"Events: {len(events)}")


if __name__ == "__main__":
    main()
