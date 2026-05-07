-- Practice 3: OLTP schema for AIS IoT Store
-- PostgreSQL DDL. The application code is not connected to DB in this task.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS devices CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash CHAR(60) NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE products (
    id VARCHAR(40) PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    firmware_version VARCHAR(32) NOT NULL,
    firmware_download_url TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL REFERENCES users(id),
    status VARCHAR(16) NOT NULL CHECK (status IN ('CREATED', 'PAID', 'CANCELLED')),
    total NUMERIC(12, 2) NOT NULL CHECK (total >= 0),
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    paid_at TIMESTAMP NULL
);

CREATE TABLE order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id VARCHAR(40) NOT NULL REFERENCES products(id),
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0)
);

CREATE TABLE devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id VARCHAR(40) NOT NULL REFERENCES products(id),
    serial_number VARCHAR(80) NOT NULL UNIQUE,
    status VARCHAR(16) NOT NULL CHECK (status IN ('AVAILABLE', 'RESERVED', 'SOLD')),
    order_id UUID NULL REFERENCES orders(id),
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    sold_at TIMESTAMP NULL
);

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL UNIQUE REFERENCES orders(id),
    amount NUMERIC(12, 2) NOT NULL CHECK (amount >= 0),
    status VARCHAR(16) NOT NULL CHECK (status IN ('PENDING', 'SUCCESS', 'FAILED')),
    provider VARCHAR(40) NOT NULL,
    external_payment_id VARCHAR(80) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

-- Indexes that are part of the base OLTP model.
-- devices.product_id is intentionally left without an index for Task 4.
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_devices_order_id ON devices(order_id);
CREATE INDEX idx_payments_status_created_at ON payments(status, created_at);
