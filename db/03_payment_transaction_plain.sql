-- Plain SQL transaction for POST /payments without EXPLAIN.
-- This is the business transaction that the application would execute later.

BEGIN;

SELECT id, user_id, status, total
FROM orders
WHERE id = '00000000-0000-0000-0000-000000000001'
FOR UPDATE;

SELECT product_id, quantity, unit_price
FROM order_items
WHERE order_id = '00000000-0000-0000-0000-000000000001';

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

UPDATE orders
SET status = 'PAID',
    paid_at = now()
WHERE id = '00000000-0000-0000-0000-000000000001';

COMMIT;
