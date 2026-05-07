-- EXPLAIN ANALYZE for POST /payments.
-- The transaction is rolled back so the script can be executed repeatedly.

\timing on

BEGIN;

-- 1. Находим заказ по первичному ключу и блокируем его строку.
-- Это нужно, чтобы другой параллельный процесс не смог одновременно изменить этот же заказ,
-- например повторно провести оплату.
\echo '1. Lock order by primary key'
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, user_id, status, total
FROM orders
WHERE id = '00000000-0000-0000-0000-000000000001'
FOR UPDATE;

-- 2. Получаем все позиции выбранного заказа.
-- По этим данным система понимает, какие товары и в каком количестве нужно выдать покупателю.
\echo '2. Read order items by order_id'
EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id, quantity, unit_price
FROM order_items
WHERE order_id = '00000000-0000-0000-0000-000000000001';

-- 3. Ищем доступные физические устройства товара sensor-001.
-- Берутся только устройства со статусом AVAILABLE, самые старые по created_at.
-- FOR UPDATE SKIP LOCKED нужен, чтобы заблокировать выбранные устройства
-- и не ждать строки, которые уже заблокированы другой транзакцией.
\echo '3. Find available sensor devices'
EXPLAIN (ANALYZE, BUFFERS)
SELECT id
FROM devices
WHERE product_id = 'sensor-001'
  AND status = 'AVAILABLE'
ORDER BY created_at
LIMIT 2
FOR UPDATE SKIP LOCKED;

-- 4. Выбираем два доступных устройства sensor-001 и помечаем их как проданные.
-- В selected_devices сначала попадают подходящие устройства,
-- затем UPDATE меняет их status, привязывает к заказу и записывает время продажи.
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

-- 5. Выбираем одно доступное устройство hub-001 и помечаем его как проданное.
-- Логика такая же, как на предыдущем шаге, но требуется только одно устройство.
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

-- 6. Выбираем одно доступное устройство camera-001 и помечаем его как проданное.
-- Устройство получает статус SOLD, привязывается к заказу и получает дату продажи.
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

-- 7. Создаём запись об успешном платеже.
-- В таблицу payments сохраняется сумма, статус платежа, провайдер
-- и внешний идентификатор платежа.
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

-- 8. Обновляем сам заказ после успешного платежа.
-- Заказ получает статус PAID, а в paid_at записывается время оплаты.
\echo '8. Update order status'
EXPLAIN (ANALYZE, BUFFERS)
UPDATE orders
SET status = 'PAID',
    paid_at = now()
WHERE id = '00000000-0000-0000-0000-000000000001';

ROLLBACK;
