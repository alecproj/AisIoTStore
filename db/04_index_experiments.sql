-- Task 4: hash index vs B-tree index on devices.product_id.
-- product_id is intentionally not indexed in 00_schema.sql.

\timing on

DROP INDEX IF EXISTS idx_devices_product_id_hash;
DROP INDEX IF EXISTS idx_devices_product_id_btree;
ANALYZE devices;

\echo 'Scenario 1. No index: point query'
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM devices
WHERE product_id = 'sensor-001';

\echo 'Scenario 1. No index: range query'
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM devices
WHERE product_id BETWEEN 'iot-01000' AND 'iot-02000';

\echo 'Scenario 2. Hash index: create index'
CREATE INDEX idx_devices_product_id_hash ON devices USING hash(product_id);
ANALYZE devices;

\echo 'Scenario 2. Hash index: point query'
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM devices
WHERE product_id = 'sensor-001';

\echo 'Scenario 2. Hash index: range query'
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM devices
WHERE product_id BETWEEN 'iot-01000' AND 'iot-02000';

\echo 'Scenario 3. B-tree index: replace hash with B-tree'
DROP INDEX idx_devices_product_id_hash;
CREATE INDEX idx_devices_product_id_btree ON devices USING btree(product_id);
ANALYZE devices;

\echo 'Scenario 3. B-tree index: point query'
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM devices
WHERE product_id = 'sensor-001';

\echo 'Scenario 3. B-tree index: range query'
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM devices
WHERE product_id BETWEEN 'iot-01000' AND 'iot-02000';
