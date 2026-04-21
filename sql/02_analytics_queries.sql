-- 1. Daily revenue and number of paid orders
SELECT
    DATE(order_created_at) AS order_date,
    COUNT(*) AS orders_count,
    SUM(total_amount) AS revenue,
    AVG(total_amount) AS average_order_value
FROM orders
WHERE payment_status = 'paid'
GROUP BY DATE(order_created_at)
ORDER BY order_date;

-- 2. Revenue by product category
SELECT
    p.category,
    SUM(oi.item_amount) AS category_revenue,
    SUM(oi.quantity) AS items_sold
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o ON o.order_id = oi.order_id
WHERE o.payment_status = 'paid'
GROUP BY p.category
ORDER BY category_revenue DESC;

-- 3. Session to order conversion by day
WITH daily_sessions AS (
    SELECT
        DATE(session_started_at) AS event_date,
        COUNT(DISTINCT session_id) AS sessions_count
    FROM sessions
    GROUP BY DATE(session_started_at)
),
daily_orders AS (
    SELECT
        DATE(order_created_at) AS event_date,
        COUNT(DISTINCT order_id) AS orders_count
    FROM orders
    WHERE payment_status = 'paid'
    GROUP BY DATE(order_created_at)
)
SELECT
    s.event_date,
    s.sessions_count,
    COALESCE(o.orders_count, 0) AS orders_count,
    ROUND(COALESCE(o.orders_count, 0)::NUMERIC / NULLIF(s.sessions_count, 0), 4) AS session_to_order_conversion
FROM daily_sessions s
LEFT JOIN daily_orders o ON o.event_date = s.event_date
ORDER BY s.event_date;

-- 4. Funnel by event type
SELECT
    event_type,
    COUNT(*) AS events_count,
    COUNT(DISTINCT user_id) AS users_count,
    COUNT(DISTINCT session_id) AS sessions_count
FROM events
GROUP BY event_type
ORDER BY events_count DESC;

-- 5. Monthly signup cohorts and month-1 retention
WITH cohort_base AS (
    SELECT
        user_id,
        DATE_TRUNC('month', signup_date)::DATE AS cohort_month
    FROM users
),
activity_months AS (
    SELECT DISTINCT
        s.user_id,
        DATE_TRUNC('month', s.session_started_at)::DATE AS activity_month
    FROM sessions s
),
cohort_activity AS (
    SELECT
        cb.cohort_month,
        am.activity_month,
        COUNT(DISTINCT cb.user_id) AS active_users
    FROM cohort_base cb
    JOIN activity_months am ON am.user_id = cb.user_id
    GROUP BY cb.cohort_month, am.activity_month
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
    ca.activity_month,
    cs.cohort_size,
    ca.active_users,
    ROUND(ca.active_users::NUMERIC / NULLIF(cs.cohort_size, 0), 4) AS retention_rate
FROM cohort_activity ca
JOIN cohort_sizes cs ON cs.cohort_month = ca.cohort_month
ORDER BY ca.cohort_month, ca.activity_month;
