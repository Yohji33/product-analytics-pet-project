CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    signup_date DATE NOT NULL,
    first_session_at TIMESTAMP,
    country VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    acquisition_channel VARCHAR(100) NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    birth_year INT,
    gender VARCHAR(20)
);

CREATE TABLE products (
    product_id BIGSERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    brand VARCHAR(100),
    price NUMERIC(10, 2) NOT NULL,
    cost NUMERIC(10, 2),
    created_at TIMESTAMP NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE marketing_spend (
    acquisition_channel VARCHAR(100) PRIMARY KEY,
    marketing_spend NUMERIC(12, 2) NOT NULL CHECK (marketing_spend >= 0)
);

CREATE TABLE sessions (
    session_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id),
    session_started_at TIMESTAMP NOT NULL,
    session_ended_at TIMESTAMP,
    traffic_source VARCHAR(100) NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    country VARCHAR(100),
    city VARCHAR(100)
);

CREATE TABLE orders (
    order_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id),
    order_created_at TIMESTAMP NOT NULL,
    order_status VARCHAR(50) NOT NULL,
    payment_status VARCHAR(50) NOT NULL,
    discount_amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
    shipping_amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
    total_amount NUMERIC(10, 2) NOT NULL
);

CREATE TABLE order_items (
    order_item_id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(order_id),
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL,
    item_amount NUMERIC(10, 2) NOT NULL
);

CREATE TABLE events (
    event_id BIGSERIAL PRIMARY KEY,
    session_id BIGINT NOT NULL REFERENCES sessions(session_id),
    user_id BIGINT NOT NULL REFERENCES users(user_id),
    product_id BIGINT REFERENCES products(product_id),
    order_id BIGINT REFERENCES orders(order_id),
    event_time TIMESTAMP NOT NULL,
    event_type VARCHAR(50) NOT NULL
);

CREATE INDEX idx_users_signup_date ON users(signup_date);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_started_at ON sessions(session_started_at);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_created_at ON orders(order_created_at);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_events_session_id ON events(session_id);
CREATE INDEX idx_events_user_id ON events(user_id);
CREATE INDEX idx_events_time ON events(event_time);
CREATE INDEX idx_events_type ON events(event_type);
