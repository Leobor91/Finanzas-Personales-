-- assign_userid_sqlite.sql
-- Assigns NULL user_id values to the first existing user (ORDER BY id LIMIT 1)
-- BACKUP your SQLite DB file before running this script.

WITH first(uid) AS (
  SELECT id FROM users ORDER BY id LIMIT 1
)
UPDATE movements
SET user_id = (SELECT uid FROM first)
WHERE user_id IS NULL
  AND (SELECT uid FROM first) IS NOT NULL;

WITH first(uid) AS (
  SELECT id FROM users ORDER BY id LIMIT 1
)
UPDATE categories
SET user_id = (SELECT uid FROM first)
WHERE user_id IS NULL
  AND (SELECT uid FROM first) IS NOT NULL;

WITH first(uid) AS (
  SELECT id FROM users ORDER BY id LIMIT 1
)
UPDATE accounts
SET user_id = (SELECT uid FROM first)
WHERE user_id IS NULL
  AND (SELECT uid FROM first) IS NOT NULL;

WITH first(uid) AS (
  SELECT id FROM users ORDER BY id LIMIT 1
)
UPDATE transfers
SET user_id = (SELECT uid FROM first)
WHERE user_id IS NULL
  AND (SELECT uid FROM first) IS NOT NULL;

WITH first(uid) AS (
  SELECT id FROM users ORDER BY id LIMIT 1
)
UPDATE denominations
SET user_id = (SELECT uid FROM first)
WHERE user_id IS NULL
  AND (SELECT uid FROM first) IS NOT NULL;
