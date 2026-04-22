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

CREATE OR REPLACE VIEW vw_marketing_efficiency AS
WITH channel_metrics AS (
    SELECT
        u.acquisition_channel,
        COUNT(DISTINCT u.user_id) AS users_count,
        COUNT(DISTINCT o.user_id) AS paying_users_count,
        COUNT(DISTINCT o.order_id) AS paid_orders_count,
        COALESCE(SUM(o.total_amount), 0) AS revenue
    FROM users u
    LEFT JOIN orders o
        ON o.user_id = u.user_id
        AND o.payment_status = 'paid'
    GROUP BY u.acquisition_channel
)
SELECT
    cm.acquisition_channel,
    cm.users_count,
    cm.paying_users_count,
    cm.paid_orders_count,
    cm.revenue,
    ms.marketing_spend,
    ROUND(ms.marketing_spend / NULLIF(cm.users_count, 0), 2) AS cost_per_user,
    ROUND(ms.marketing_spend / NULLIF(cm.paying_users_count, 0), 2) AS cac,
    ROUND(cm.revenue / NULLIF(cm.users_count, 0), 2) AS revenue_per_user,
    ROUND(cm.revenue - ms.marketing_spend, 2) AS profit_after_marketing,
    ROUND((cm.revenue - ms.marketing_spend) / NULLIF(ms.marketing_spend, 0), 4) AS romi,
    ROUND(cm.revenue / NULLIF(ms.marketing_spend, 0), 4) AS payback_ratio
FROM channel_metrics cm
JOIN marketing_spend ms ON ms.acquisition_channel = cm.acquisition_channel;

CREATE OR REPLACE VIEW vw_ltv_by_channel AS
WITH user_order_metrics AS (
    SELECT
        u.user_id,
        u.acquisition_channel,
        COUNT(DISTINCT o.order_id) AS orders_count,
        COALESCE(SUM(o.total_amount), 0) AS revenue
    FROM users u
    LEFT JOIN orders o
        ON o.user_id = u.user_id
        AND o.payment_status = 'paid'
    GROUP BY u.user_id, u.acquisition_channel
)
SELECT
    uom.acquisition_channel,
    COUNT(DISTINCT uom.user_id) AS users_count,
    COUNT(DISTINCT uom.user_id) FILTER (WHERE uom.orders_count > 0) AS paying_users_count,
    COUNT(DISTINCT uom.user_id) FILTER (WHERE uom.orders_count >= 2) AS repeat_buyers_count,
    ROUND(
        COUNT(DISTINCT uom.user_id) FILTER (WHERE uom.orders_count >= 2)::NUMERIC
        / NULLIF(COUNT(DISTINCT uom.user_id) FILTER (WHERE uom.orders_count > 0), 0),
        4
    ) AS repeat_purchase_rate,
    SUM(uom.revenue) AS total_revenue,
    ROUND(SUM(uom.revenue) / NULLIF(COUNT(DISTINCT uom.user_id), 0), 2) AS avg_ltv_per_user,
    ROUND(
        SUM(uom.revenue)
        / NULLIF(COUNT(DISTINCT uom.user_id) FILTER (WHERE uom.orders_count > 0), 0),
        2
    ) AS avg_ltv_per_paying_user,
    ROUND(AVG(uom.orders_count) FILTER (WHERE uom.orders_count > 0), 2) AS average_orders_per_paying_user,
    ms.marketing_spend,
    ROUND(
        ms.marketing_spend
        / NULLIF(COUNT(DISTINCT uom.user_id) FILTER (WHERE uom.orders_count > 0), 0),
        2
    ) AS cac,
    ROUND(
        (
            SUM(uom.revenue)
            / NULLIF(COUNT(DISTINCT uom.user_id) FILTER (WHERE uom.orders_count > 0), 0)
        )
        / NULLIF(
            ms.marketing_spend
            / NULLIF(COUNT(DISTINCT uom.user_id) FILTER (WHERE uom.orders_count > 0), 0),
            0
        ),
        2
    ) AS ltv_cac_ratio,
    ROUND(SUM(uom.revenue) / NULLIF(ms.marketing_spend, 0), 4) AS payback_ratio
FROM user_order_metrics uom
JOIN marketing_spend ms ON ms.acquisition_channel = uom.acquisition_channel
GROUP BY uom.acquisition_channel, ms.marketing_spend;

CREATE OR REPLACE VIEW vw_repeat_purchase_summary AS
WITH user_order_metrics AS (
    SELECT
        u.user_id,
        COUNT(DISTINCT o.order_id) AS orders_count,
        COALESCE(SUM(o.total_amount), 0) AS revenue
    FROM users u
    LEFT JOIN orders o
        ON o.user_id = u.user_id
        AND o.payment_status = 'paid'
    GROUP BY u.user_id
),
summary AS (
    SELECT
        COUNT(*) AS users_count,
        COUNT(*) FILTER (WHERE orders_count > 0) AS paying_users_count,
        COUNT(*) FILTER (WHERE orders_count >= 2) AS repeat_buyers_count,
        SUM(revenue) AS revenue,
        SUM(revenue) FILTER (WHERE orders_count >= 2) AS repeat_revenue,
        SUM(orders_count) AS paid_orders_count
    FROM user_order_metrics
)
SELECT 'Покупатели' AS metric, paying_users_count::NUMERIC AS value
FROM summary
UNION ALL
SELECT 'Повторные покупатели', repeat_buyers_count::NUMERIC
FROM summary
UNION ALL
SELECT 'Доля повторных покупателей', repeat_buyers_count::NUMERIC / NULLIF(paying_users_count, 0)
FROM summary
UNION ALL
SELECT 'Среднее заказов на покупателя', paid_orders_count::NUMERIC / NULLIF(paying_users_count, 0)
FROM summary
UNION ALL
SELECT 'Выручка повторных покупателей', repeat_revenue
FROM summary
UNION ALL
SELECT 'Доля выручки повторных покупателей', repeat_revenue / NULLIF(revenue, 0)
FROM summary
UNION ALL
SELECT 'LTV на пользователя', revenue / NULLIF(users_count, 0)
FROM summary
UNION ALL
SELECT 'LTV на покупателя', revenue / NULLIF(paying_users_count, 0)
FROM summary;

CREATE OR REPLACE VIEW vw_ab_test_results AS
WITH experiment_results AS (
    SELECT
        variant,
        COUNT(DISTINCT user_id) AS users_count,
        COUNT(DISTINCT user_id) FILTER (WHERE converted) AS conversions_count,
        ROUND(
            COUNT(DISTINCT user_id) FILTER (WHERE converted)::NUMERIC / NULLIF(COUNT(DISTINCT user_id), 0),
            4
        ) AS conversion_rate,
        SUM(conversion_revenue) AS revenue,
        ROUND(SUM(conversion_revenue) / NULLIF(COUNT(DISTINCT user_id), 0), 2) AS avg_revenue_per_user
    FROM ab_test_assignments
    GROUP BY variant
),
control AS (
    SELECT
        users_count AS control_users_count,
        conversions_count AS control_conversions_count,
        conversion_rate AS control_conversion_rate
    FROM experiment_results
    WHERE variant = 'control'
)
SELECT
    er.variant,
    er.users_count,
    er.conversions_count,
    er.conversion_rate,
    er.revenue,
    er.avg_revenue_per_user,
    ROUND(er.conversion_rate - c.control_conversion_rate, 4) AS absolute_uplift,
    ROUND((er.conversion_rate - c.control_conversion_rate) / NULLIF(c.control_conversion_rate, 0), 4) AS relative_uplift,
    ROUND(
        (er.conversion_rate - c.control_conversion_rate)
        / NULLIF(
            SQRT(
                (
                    (er.conversions_count + c.control_conversions_count)::NUMERIC
                    / NULLIF(er.users_count + c.control_users_count, 0)
                )
                * (
                    1
                    - (
                        (er.conversions_count + c.control_conversions_count)::NUMERIC
                        / NULLIF(er.users_count + c.control_users_count, 0)
                    )
                )
                * (1::NUMERIC / er.users_count + 1::NUMERIC / c.control_users_count)
            ),
            0
        ),
        4
    ) AS z_score
FROM experiment_results er
CROSS JOIN control c;

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
