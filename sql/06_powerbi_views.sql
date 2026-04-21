-- Представления для подключения Power BI к PostgreSQL.
-- Их можно использовать вместо CSV-файлов, если хочется строить дашборд напрямую от базы.

CREATE OR REPLACE VIEW vw_kpi_overview AS
WITH user_metrics AS (
    SELECT COUNT(DISTINCT user_id) AS users_count
    FROM users
),
session_metrics AS (
    SELECT COUNT(DISTINCT session_id) AS sessions_count
    FROM sessions
),
order_metrics AS (
    SELECT
        COUNT(DISTINCT order_id) AS paid_orders_count,
        SUM(total_amount) AS revenue,
        AVG(total_amount) AS average_order_value
    FROM orders
    WHERE payment_status = 'paid'
)
SELECT
    um.users_count,
    sm.sessions_count,
    om.paid_orders_count,
    om.revenue,
    ROUND(om.average_order_value, 2) AS average_order_value,
    ROUND(om.paid_orders_count::NUMERIC / NULLIF(sm.sessions_count, 0), 4) AS session_to_order_conversion
FROM user_metrics um
CROSS JOIN session_metrics sm
CROSS JOIN order_metrics om;

CREATE OR REPLACE VIEW vw_monthly_metrics AS
WITH monthly_sessions AS (
    SELECT
        DATE_TRUNC('month', session_started_at)::DATE AS month,
        COUNT(DISTINCT session_id) AS sessions_count,
        COUNT(DISTINCT user_id) AS active_users_count
    FROM sessions
    GROUP BY DATE_TRUNC('month', session_started_at)::DATE
),
monthly_orders AS (
    SELECT
        DATE_TRUNC('month', order_created_at)::DATE AS month,
        COUNT(DISTINCT order_id) AS paid_orders_count,
        COUNT(DISTINCT user_id) AS paying_users_count,
        SUM(total_amount) AS revenue,
        AVG(total_amount) AS average_order_value
    FROM orders
    WHERE payment_status = 'paid'
    GROUP BY DATE_TRUNC('month', order_created_at)::DATE
)
SELECT
    ms.month,
    ms.active_users_count,
    ms.sessions_count,
    COALESCE(mo.paying_users_count, 0) AS paying_users_count,
    COALESCE(mo.paid_orders_count, 0) AS paid_orders_count,
    COALESCE(mo.revenue, 0) AS revenue,
    ROUND(COALESCE(mo.average_order_value, 0), 2) AS average_order_value,
    ROUND(COALESCE(mo.paid_orders_count, 0)::NUMERIC / NULLIF(ms.sessions_count, 0), 4) AS session_to_order_conversion
FROM monthly_sessions ms
LEFT JOIN monthly_orders mo ON mo.month = ms.month;

CREATE OR REPLACE VIEW vw_funnel AS
WITH funnel AS (
    SELECT
        COUNT(DISTINCT CASE WHEN event_type = 'view_item' THEN user_id END) AS viewed_users,
        COUNT(DISTINCT CASE WHEN event_type = 'add_to_cart' THEN user_id END) AS cart_users,
        COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) AS purchase_users
    FROM events
)
SELECT 'view_item' AS event_type, 1 AS step_order, viewed_users AS users_count, 1.0 AS conversion_from_first_step
FROM funnel
UNION ALL
SELECT 'add_to_cart', 2, cart_users, ROUND(cart_users::NUMERIC / NULLIF(viewed_users, 0), 4)
FROM funnel
UNION ALL
SELECT 'purchase', 3, purchase_users, ROUND(purchase_users::NUMERIC / NULLIF(viewed_users, 0), 4)
FROM funnel;

CREATE OR REPLACE VIEW vw_traffic_source_funnel AS
WITH source_funnel AS (
    SELECT
        s.traffic_source,
        COUNT(DISTINCT CASE WHEN e.event_type = 'view_item' THEN e.user_id END) AS viewed_users,
        COUNT(DISTINCT CASE WHEN e.event_type = 'add_to_cart' THEN e.user_id END) AS cart_users,
        COUNT(DISTINCT CASE WHEN e.event_type = 'purchase' THEN e.user_id END) AS purchase_users
    FROM events e
    JOIN sessions s ON s.session_id = e.session_id
    GROUP BY s.traffic_source
)
SELECT
    traffic_source,
    viewed_users,
    cart_users,
    purchase_users,
    ROUND(cart_users::NUMERIC / NULLIF(viewed_users, 0), 4) AS view_to_cart_conversion,
    ROUND(purchase_users::NUMERIC / NULLIF(cart_users, 0), 4) AS cart_to_purchase_conversion,
    ROUND(purchase_users::NUMERIC / NULLIF(viewed_users, 0), 4) AS view_to_purchase_conversion
FROM source_funnel;

CREATE OR REPLACE VIEW vw_acquisition_channel_metrics AS
SELECT
    u.acquisition_channel,
    COUNT(DISTINCT u.user_id) AS users_count,
    COUNT(DISTINCT o.user_id) AS paying_users_count,
    COUNT(DISTINCT o.order_id) AS paid_orders_count,
    SUM(o.total_amount) AS revenue,
    ROUND(SUM(o.total_amount) / NULLIF(COUNT(DISTINCT o.user_id), 0), 2) AS revenue_per_paying_user,
    ROUND(COUNT(DISTINCT o.user_id)::NUMERIC / NULLIF(COUNT(DISTINCT u.user_id), 0), 4) AS user_to_buyer_conversion
FROM users u
LEFT JOIN orders o
    ON o.user_id = u.user_id
    AND o.payment_status = 'paid'
GROUP BY u.acquisition_channel;

CREATE OR REPLACE VIEW vw_device_metrics AS
SELECT
    s.device_type,
    COUNT(DISTINCT s.session_id) AS sessions_count,
    COUNT(DISTINCT o.order_id) AS paid_orders_count,
    SUM(o.total_amount) AS revenue,
    ROUND(COUNT(DISTINCT o.order_id)::NUMERIC / NULLIF(COUNT(DISTINCT s.session_id), 0), 4) AS session_to_order_conversion
FROM sessions s
LEFT JOIN orders o
    ON o.user_id = s.user_id
    AND o.payment_status = 'paid'
    AND DATE(o.order_created_at) = DATE(s.session_started_at)
GROUP BY s.device_type;

CREATE OR REPLACE VIEW vw_category_revenue AS
SELECT
    p.category,
    COUNT(DISTINCT o.order_id) AS paid_orders_count,
    SUM(oi.quantity) AS items_sold,
    SUM(oi.item_amount) AS revenue,
    ROUND(SUM(oi.item_amount) / NULLIF(SUM(oi.quantity), 0), 2) AS average_item_price
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
JOIN products p ON p.product_id = oi.product_id
WHERE o.payment_status = 'paid'
GROUP BY p.category;

CREATE OR REPLACE VIEW vw_top_products AS
SELECT
    p.product_id,
    p.product_name,
    p.category,
    COUNT(DISTINCT o.order_id) AS paid_orders_count,
    SUM(oi.quantity) AS items_sold,
    SUM(oi.item_amount) AS revenue
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
JOIN products p ON p.product_id = oi.product_id
WHERE o.payment_status = 'paid'
GROUP BY p.product_id, p.product_name, p.category;

CREATE OR REPLACE VIEW vw_retention_cohorts AS
WITH cohort_base AS (
    SELECT
        user_id,
        DATE_TRUNC('month', signup_date)::DATE AS cohort_month
    FROM users
),
user_activity AS (
    SELECT DISTINCT
        user_id,
        DATE_TRUNC('month', session_started_at)::DATE AS activity_month
    FROM sessions
),
cohort_activity AS (
    SELECT
        cb.cohort_month,
        (
            EXTRACT(YEAR FROM age(ua.activity_month, cb.cohort_month)) * 12
            + EXTRACT(MONTH FROM age(ua.activity_month, cb.cohort_month))
        )::INT AS month_number,
        COUNT(DISTINCT cb.user_id) AS active_users
    FROM cohort_base cb
    JOIN user_activity ua ON ua.user_id = cb.user_id
    WHERE ua.activity_month >= cb.cohort_month
    GROUP BY cb.cohort_month, ua.activity_month
),
cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT user_id) AS cohort_size
    FROM cohort_base
    GROUP BY cohort_month
)
SELECT
    ca.cohort_month,
    ca.month_number,
    cs.cohort_size,
    ca.active_users,
    ROUND(ca.active_users::NUMERIC / NULLIF(cs.cohort_size, 0), 4) AS retention_rate
FROM cohort_activity ca
JOIN cohort_sizes cs ON cs.cohort_month = ca.cohort_month;
