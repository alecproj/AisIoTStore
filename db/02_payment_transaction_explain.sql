-- EXPLAIN ANALYZE for POST /payments.
-- The transaction is rolled back so the script can be executed repeatedly.

\timing on

BEGIN;

\echo '1. Lock order by primary key'
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, user_id, status, total
FROM orders
WHERE id = '00000000-0000-0000-0000-000000000001'
FOR UPDATE;

\echo '2. Read order items by order_id'
EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id, quantity, unit_price
FROM order_items
WHERE order_id = '00000000-0000-0000-0000-000000000001';

\echo '3. Find available sensor devices'
EXPLAIN (ANALYZE, BUFFERS)
SELECT id
FROM devices
WHERE product_id = 'sensor-001'
  AND status = 'AVAILABLE'
ORDER BY created_at
LIMIT 2
FOR UPDATE SKIP LOCKED;

\echo '4. Mark sensor devices as sold'
EXPLAIN (ANALYZE, BUFFERS)
WITH selected_devices AS (
    SELECT id
    FROM devices
    WHERE product_id = 'sensor-001'
      AND status = 'AVAILABLE'
    ORDER BY created_at
    LIMIT 2
    FOR UPDATE SKIP LOCKED
)
UPDATE devices AS d
SET status = 'SOLD',
    order_id = '00000000-0000-0000-0000-000000000001',
    sold_at = now()
FROM selected_devices
WHERE d.id = selected_devices.id;

\echo '5. Mark hub device as sold'
EXPLAIN (ANALYZE, BUFFERS)
WITH selected_devices AS (
    SELECT id
    FROM devices
    WHERE product_id = 'hub-001'
      AND status = 'AVAILABLE'
    ORDER BY created_at
    LIMIT 1
    FOR UPDATE SKIP LOCKED
)
UPDATE devices AS d
SET status = 'SOLD',
    order_id = '00000000-0000-0000-0000-000000000001',
    sold_at = now()
FROM selected_devices
WHERE d.id = selected_devices.id;

\echo '6. Mark camera device as sold'
EXPLAIN (ANALYZE, BUFFERS)
WITH selected_devices AS (
    SELECT id
    FROM devices
    WHERE product_id = 'camera-001'
      AND status = 'AVAILABLE'
    ORDER BY created_at
    LIMIT 1
    FOR UPDATE SKIP LOCKED
)
UPDATE devices AS d
SET status = 'SOLD',
    order_id = '00000000-0000-0000-0000-000000000001',
    sold_at = now()
FROM selected_devices
WHERE d.id = selected_devices.id;

\echo '7. Insert payment record'
EXPLAIN (ANALYZE, BUFFERS)
INSERT INTO payments (id, order_id, amount, status, provider, external_payment_id, created_at)
VALUES (
    gen_random_uuid(),
    '00000000-0000-0000-0000-000000000001',
    319.96,
    'SUCCESS',
    'mock_gateway',
    'pay-practice-3-sample',
    now()
);

\echo '8. Update order status'
EXPLAIN (ANALYZE, BUFFERS)
UPDATE orders
SET status = 'PAID',
    paid_at = now()
WHERE id = '00000000-0000-0000-0000-000000000001';

ROLLBACK;
