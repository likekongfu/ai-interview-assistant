-- 20260709_add_wechat_quiz_user_fields.sql
-- Purpose: make existing users table compatible with quiz mini-program WeChat login.
-- Safe policy:
--   - Do not drop users table.
--   - Do not clear or rewrite existing user data.
--   - Do not drop existing accuracy column if it already exists.
--   - Add missing columns only when absent.
--   - Make username/password nullable for WeChat-only users.

-- =========================
-- Preflight checks
-- =========================
SHOW CREATE TABLE users;
SHOW INDEX FROM users;

SELECT
  COLUMN_NAME,
  COLUMN_TYPE,
  IS_NULLABLE,
  COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'users'
ORDER BY ORDINAL_POSITION;

SELECT
  wechat_appid,
  wechat_openid,
  COUNT(*) AS duplicate_count
FROM users
WHERE wechat_appid IS NOT NULL
  AND wechat_openid IS NOT NULL
GROUP BY wechat_appid, wechat_openid
HAVING COUNT(*) > 1;

-- If the duplicate query returns rows, resolve duplicates before adding the unique index.

-- =========================
-- Forward migration
-- =========================
ALTER TABLE users
  MODIFY COLUMN username VARCHAR(255) NULL,
  MODIFY COLUMN password VARCHAR(255) NULL;

SET @schema_name = DATABASE();

SET @sql = (
  SELECT IF(COUNT(*) = 0,
    'ALTER TABLE users ADD COLUMN wechat_appid VARCHAR(64) NULL',
    'SELECT ''wechat_appid exists'' AS info')
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = @schema_name AND TABLE_NAME = 'users' AND COLUMN_NAME = 'wechat_appid'
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql = (
  SELECT IF(COUNT(*) = 0,
    'ALTER TABLE users ADD COLUMN wechat_openid VARCHAR(128) NULL',
    'SELECT ''wechat_openid exists'' AS info')
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = @schema_name AND TABLE_NAME = 'users' AND COLUMN_NAME = 'wechat_openid'
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql = (
  SELECT IF(COUNT(*) = 0,
    'ALTER TABLE users ADD COLUMN nickname VARCHAR(255) NULL',
    'SELECT ''nickname exists'' AS info')
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = @schema_name AND TABLE_NAME = 'users' AND COLUMN_NAME = 'nickname'
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql = (
  SELECT IF(COUNT(*) = 0,
    'ALTER TABLE users ADD COLUMN avatar_url VARCHAR(1024) NULL',
    'SELECT ''avatar_url exists'' AS info')
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = @schema_name AND TABLE_NAME = 'users' AND COLUMN_NAME = 'avatar_url'
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql = (
  SELECT IF(COUNT(*) = 0,
    'ALTER TABLE users ADD COLUMN level INT NOT NULL DEFAULT 1',
    'SELECT ''level exists'' AS info')
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = @schema_name AND TABLE_NAME = 'users' AND COLUMN_NAME = 'level'
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql = (
  SELECT IF(COUNT(*) = 0,
    'ALTER TABLE users ADD COLUMN answered_count INT NOT NULL DEFAULT 0',
    'SELECT ''answered_count exists'' AS info')
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = @schema_name AND TABLE_NAME = 'users' AND COLUMN_NAME = 'answered_count'
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql = (
  SELECT IF(COUNT(*) = 0,
    'ALTER TABLE users ADD COLUMN correct_count INT NOT NULL DEFAULT 0',
    'SELECT ''correct_count exists'' AS info')
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = @schema_name AND TABLE_NAME = 'users' AND COLUMN_NAME = 'correct_count'
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql = (
  SELECT IF(COUNT(*) = 0,
    'ALTER TABLE users ADD COLUMN streak_days INT NOT NULL DEFAULT 0',
    'SELECT ''streak_days exists'' AS info')
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = @schema_name AND TABLE_NAME = 'users' AND COLUMN_NAME = 'streak_days'
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql = (
  SELECT IF(COUNT(*) = 0,
    'ALTER TABLE users ADD COLUMN total_score INT NOT NULL DEFAULT 0',
    'SELECT ''total_score exists'' AS info')
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = @schema_name AND TABLE_NAME = 'users' AND COLUMN_NAME = 'total_score'
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql = (
  SELECT IF(COUNT(*) = 0,
    'ALTER TABLE users ADD COLUMN last_practice_date DATE NULL',
    'SELECT ''last_practice_date exists'' AS info')
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = @schema_name AND TABLE_NAME = 'users' AND COLUMN_NAME = 'last_practice_date'
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql = (
  SELECT IF(COUNT(*) = 0,
    'ALTER TABLE users ADD COLUMN last_login_at DATETIME NULL',
    'SELECT ''last_login_at exists'' AS info')
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = @schema_name AND TABLE_NAME = 'users' AND COLUMN_NAME = 'last_login_at'
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql = (
  SELECT IF(COUNT(*) = 0,
    'ALTER TABLE users ADD CONSTRAINT uq_users_wechat_identity UNIQUE (wechat_appid, wechat_openid)',
    'SELECT ''uq_users_wechat_identity exists'' AS info')
  FROM INFORMATION_SCHEMA.STATISTICS
  WHERE TABLE_SCHEMA = @schema_name AND TABLE_NAME = 'users' AND INDEX_NAME = 'uq_users_wechat_identity'
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- =========================
-- Post-migration checks
-- =========================
SHOW CREATE TABLE users;
SHOW INDEX FROM users;

-- =========================
-- Rollback SQL
-- =========================
-- Review before executing. This rollback removes only columns introduced by this migration.
--
-- ALTER TABLE users DROP INDEX uq_users_wechat_identity;
-- ALTER TABLE users DROP COLUMN last_login_at;
-- ALTER TABLE users DROP COLUMN last_practice_date;
-- ALTER TABLE users DROP COLUMN total_score;
-- ALTER TABLE users DROP COLUMN streak_days;
-- ALTER TABLE users DROP COLUMN correct_count;
-- ALTER TABLE users DROP COLUMN answered_count;
-- ALTER TABLE users DROP COLUMN level;
-- ALTER TABLE users DROP COLUMN avatar_url;
-- ALTER TABLE users DROP COLUMN nickname;
-- ALTER TABLE users DROP COLUMN wechat_openid;
-- ALTER TABLE users DROP COLUMN wechat_appid;
--
-- Only restore NOT NULL if there are no WeChat-only rows with NULL username/password:
-- SELECT COUNT(*) AS null_login_fields FROM users WHERE username IS NULL OR password IS NULL;
-- ALTER TABLE users
--   MODIFY COLUMN username VARCHAR(255) NOT NULL,
--   MODIFY COLUMN password VARCHAR(255) NOT NULL;
