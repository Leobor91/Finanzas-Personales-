-- assign_userid_postgres.sql
-- Assigns NULL user_id values to the first existing user (ORDER BY id LIMIT 1)
-- BACKUP your database before running this script.

DO $$
DECLARE
    uid integer;
BEGIN
    SELECT id INTO uid FROM users ORDER BY id LIMIT 1;

    IF uid IS NULL THEN
        RAISE NOTICE 'No users found. No changes made.';
    ELSE
        UPDATE movements SET user_id = uid WHERE user_id IS NULL;
        UPDATE categories SET user_id = uid WHERE user_id IS NULL;
        UPDATE accounts SET user_id = uid WHERE user_id IS NULL;
        UPDATE transfers SET user_id = uid WHERE user_id IS NULL;
        UPDATE denominations SET user_id = uid WHERE user_id IS NULL;
        RAISE NOTICE 'Assigned user_id % to movements,categories,accounts,transfers,denominations', uid;
    END IF;
END$$;
