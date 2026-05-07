-- Test data for Practice 3.
-- Target volume: 50-100K+ rows in the main tables.

\timing on

TRUNCATE payments, devices, order_items, orders, products, users RESTART IDENTITY CASCADE;

INSERT INTO users (email, password_hash, full_name, created_at)
SELECT
    'user' || g || '@test.local',
    repeat('x', 60),
    'Test User ' || g,
    now() - (random() * interval '365 days')
FROM generate_series(1, 100000) AS g;

INSERT INTO products (id, name, price, firmware_version, firmware_download_url, created_at)
VALUES
    ('sensor-001', 'Temperature Sensor', 49.99, '1.2.0', 'https://example.com/fw/sensor-001/1.2.0.bin', now()),
    ('hub-001', 'Smart Hub', 129.99, '2.5.1', 'https://example.com/fw/hub-001/2.5.1.bin', now()),
    ('camera-001', 'Indoor Camera', 89.99, '3.1.4', 'https://example.com/fw/camera-001/3.1.4.bin', now());

INSERT INTO products (id, name, price, firmware_version, firmware_download_url, created_at)
SELECT
    'iot-' || lpad(g::text, 5, '0'),
    'IoT Device ' || g,
    (10 + random() * 990)::numeric(10, 2),
    (1 + floor(random() * 5))::int || '.' || floor(random() * 10)::int || '.' || floor(random() * 10)::int,
    'https://example.com/fw/iot-' || lpad(g::text, 5, '0') || '/latest.bin',
    now() - (random() * interval '180 days')
FROM generate_series(1, 49997) AS g;

-- Deterministic order for EXPLAIN experiments.
INSERT INTO orders (id, user_id, status, total, created_at, paid_at)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    1,
    'CREATED',
    319.96,
    now() - interval '1 hour',
    NULL
);

INSERT INTO orders (id, user_id, status, total, created_at, paid_at)
SELECT
    gen_random_uuid(),
    (1 + floor(random() * 100000))::bigint,
    CASE WHEN g % 5 = 0 THEN 'CREATED' ELSE 'PAID' END,
    (20 + random() * 1500)::numeric(12, 2),
    now() - (random() * interval '180 days'),
    CASE WHEN g % 5 = 0 THEN NULL ELSE now() - (random() * interval '90 days') END
FROM generate_series(1, 99999) AS g;

-- Items for the deterministic order.
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'sensor-001', 2, 49.99),
    ('00000000-0000-0000-0000-000000000001', 'hub-001', 1, 129.99),
    ('00000000-0000-0000-0000-000000000001', 'camera-001', 1, 89.99);

CREATE TEMP TABLE tmp_order_ids AS
SELECT row_number() OVER () AS rn, id
FROM orders;

INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT
    o.id,
    p.id,
    src.quantity,
    p.price
FROM (
    SELECT
        (floor(random() * 100000) + 1)::int AS order_rn,
        CASE
            WHEN random() < 0.00005 THEN 'sensor-001'
            WHEN random() < 0.00010 THEN 'hub-001'
            WHEN random() < 0.00015 THEN 'camera-001'
            ELSE 'iot-' || lpad((floor(random() * 49997) + 1)::int::text, 5, '0')
        END AS product_id,
        (floor(random() * 4) + 1)::int AS quantity
    FROM generate_series(1, 99997)
) AS src
JOIN tmp_order_ids AS o ON o.rn = src.order_rn
JOIN products AS p ON p.id = src.product_id;

-- Available devices for the deterministic payment scenario.
INSERT INTO devices (id, product_id, serial_number, status, order_id, created_at, sold_at)
SELECT gen_random_uuid(), 'sensor-001', 'SN-SENSOR-SAMPLE-' || g, 'AVAILABLE', NULL, now() - interval '10 days', NULL
FROM generate_series(1, 20) AS g;

INSERT INTO devices (id, product_id, serial_number, status, order_id, created_at, sold_at)
SELECT gen_random_uuid(), 'hub-001', 'SN-HUB-SAMPLE-' || g, 'AVAILABLE', NULL, now() - interval '10 days', NULL
FROM generate_series(1, 20) AS g;

INSERT INTO devices (id, product_id, serial_number, status, order_id, created_at, sold_at)
SELECT gen_random_uuid(), 'camera-001', 'SN-CAMERA-SAMPLE-' || g, 'AVAILABLE', NULL, now() - interval '10 days', NULL
FROM generate_series(1, 20) AS g;

INSERT INTO devices (id, product_id, serial_number, status, order_id, created_at, sold_at)
SELECT
    gen_random_uuid(),
    'iot-' || lpad((floor(random() * 49997) + 1)::int::text, 5, '0'),
    'SN-IOT-' || lpad(g::text, 8, '0'),
    CASE
        WHEN random() < 0.75 THEN 'AVAILABLE'
        WHEN random() < 0.90 THEN 'SOLD'
        ELSE 'RESERVED'
    END,
    NULL,
    now() - (random() * interval '365 days'),
    NULL
FROM generate_series(1, 99940) AS g;

INSERT INTO payments (id, order_id, amount, status, provider, external_payment_id, created_at)
SELECT
    gen_random_uuid(),
    id,
    total,
    'SUCCESS',
    'mock_gateway',
    'pay-' || substr(md5(id::text), 1, 32),
    COALESCE(paid_at, created_at + interval '5 minutes')
FROM orders
WHERE status = 'PAID';

DROP TABLE tmp_order_ids;

ANALYZE;
