-- add_userid_to_all_tables_postgres.sql
-- Adds `user_id` INTEGER column to application tables (except `users`) and creates indexes.
-- BACKUP your DB before running (see examples below).

BEGIN;

-- Add column if not exists
ALTER TABLE IF EXISTS movements ADD COLUMN IF NOT EXISTS user_id INTEGER;
ALTER TABLE IF EXISTS categories ADD COLUMN IF NOT EXISTS user_id INTEGER;
ALTER TABLE IF EXISTS accounts ADD COLUMN IF NOT EXISTS user_id INTEGER;
ALTER TABLE IF EXISTS transfers ADD COLUMN IF NOT EXISTS user_id INTEGER;
ALTER TABLE IF EXISTS denominations ADD COLUMN IF NOT EXISTS user_id INTEGER;

-- Optionally add foreign key constraint (commented out). Enable only if you want referential integrity.
-- Note: adding FK may fail if there are user_id values not matching users.id. Uncomment and run after verifying.
-- ALTER TABLE movements ADD CONSTRAINT movements_user_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;
-- ALTER TABLE categories ADD CONSTRAINT categories_user_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;
-- ALTER TABLE accounts ADD CONSTRAINT accounts_user_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;
-- ALTER TABLE transfers ADD CONSTRAINT transfers_user_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;
-- ALTER TABLE denominations ADD CONSTRAINT denominations_user_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;

-- Create indexes to speed up per-user queries
CREATE INDEX IF NOT EXISTS idx_movements_user_id ON movements(user_id);
CREATE INDEX IF NOT EXISTS idx_categories_user_id ON categories(user_id);
CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_transfers_user_id ON transfers(user_id);
CREATE INDEX IF NOT EXISTS idx_denominations_user_id ON denominations(user_id);

COMMIT;

-- After running this script, run `scripts/assign_userid_postgres.sql` if you want to assign NULL rows
-- to an existing user (e.g. the first user).
