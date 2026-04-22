-- Row counts by table
SELECT 'users' AS table_name, COUNT(*) AS row_count FROM users
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'marketing_spend', COUNT(*) FROM marketing_spend
UNION ALL
SELECT 'sessions', COUNT(*) FROM sessions
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL
SELECT 'events', COUNT(*) FROM events;

-- Payment status breakdown
SELECT
    payment_status,
    COUNT(*) AS orders_count,
    SUM(total_amount) AS total_revenue
FROM orders
GROUP BY payment_status
ORDER BY orders_count DESC;

-- Event type breakdown
SELECT
    event_type,
    COUNT(*) AS events_count,
    COUNT(DISTINCT user_id) AS users_count
FROM events
GROUP BY event_type
ORDER BY events_count DESC;

-- Check for orphaned rows
SELECT COUNT(*) AS orphan_sessions
FROM sessions s
LEFT JOIN users u ON u.user_id = s.user_id
WHERE u.user_id IS NULL;

SELECT COUNT(*) AS orphan_orders
FROM orders o
LEFT JOIN users u ON u.user_id = o.user_id
WHERE u.user_id IS NULL;

SELECT COUNT(*) AS orphan_order_items
FROM order_items oi
LEFT JOIN orders o ON o.order_id = oi.order_id
WHERE o.order_id IS NULL;

SELECT COUNT(*) AS orphan_events_sessions
FROM events e
LEFT JOIN sessions s ON s.session_id = e.session_id
WHERE s.session_id IS NULL;
