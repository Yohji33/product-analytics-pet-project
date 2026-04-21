\echo Loading sample CSV data into PostgreSQL...

TRUNCATE TABLE events, order_items, orders, sessions, products, users RESTART IDENTITY CASCADE;

\copy users(user_id, signup_date, first_session_at, country, city, acquisition_channel, device_type, birth_year, gender) FROM 'C:/Users/iliya/Desktop/product-analytics-pet-project/data/sample/users.csv' WITH (FORMAT csv, HEADER true, NULL '');

\copy products(product_id, product_name, category, brand, price, cost, created_at, is_active) FROM 'C:/Users/iliya/Desktop/product-analytics-pet-project/data/sample/products.csv' WITH (FORMAT csv, HEADER true, NULL '');

\copy sessions(session_id, user_id, session_started_at, session_ended_at, traffic_source, device_type, country, city) FROM 'C:/Users/iliya/Desktop/product-analytics-pet-project/data/sample/sessions.csv' WITH (FORMAT csv, HEADER true, NULL '');

\copy orders(order_id, user_id, order_created_at, order_status, payment_status, discount_amount, shipping_amount, total_amount) FROM 'C:/Users/iliya/Desktop/product-analytics-pet-project/data/sample/orders.csv' WITH (FORMAT csv, HEADER true, NULL '');

\copy order_items(order_item_id, order_id, product_id, quantity, unit_price, item_amount) FROM 'C:/Users/iliya/Desktop/product-analytics-pet-project/data/sample/order_items.csv' WITH (FORMAT csv, HEADER true, NULL '');

\copy events(event_id, session_id, user_id, product_id, order_id, event_time, event_type) FROM 'C:/Users/iliya/Desktop/product-analytics-pet-project/data/sample/events.csv' WITH (FORMAT csv, HEADER true, NULL '');

\echo Data loading completed.
