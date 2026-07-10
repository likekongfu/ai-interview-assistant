-- 20260710_add_quiz_practice_tables.sql
-- Purpose: add persistent quiz question bank and practice session tables.
-- Safe behavior: create tables if missing; do not drop existing data.

-- Preflight checks
SHOW TABLES LIKE 'quiz_questions';
SHOW TABLES LIKE 'practice_sessions';
SHOW TABLES LIKE 'practice_session_questions';
SHOW TABLES LIKE 'practice_answers';

CREATE TABLE IF NOT EXISTS quiz_questions (
  id INT NOT NULL AUTO_INCREMENT,
  source_id VARCHAR(64) NULL,
  category VARCHAR(64) NOT NULL,
  stem TEXT NOT NULL,
  options_json TEXT NOT NULL,
  correct_answer VARCHAR(8) NOT NULL,
  explanation TEXT NOT NULL,
  knowledge_point VARCHAR(255) NULL,
  difficulty VARCHAR(20) NOT NULL DEFAULT 'medium',
  status VARCHAR(20) NOT NULL DEFAULT 'active',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_quiz_questions_source_id (source_id),
  KEY ix_quiz_questions_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS practice_sessions (
  id INT NOT NULL AUTO_INCREMENT,
  user_id INT NOT NULL,
  category VARCHAR(64) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'in_progress',
  total_questions INT NOT NULL DEFAULT 0,
  score INT NOT NULL DEFAULT 0,
  current_index INT NOT NULL DEFAULT 0,
  started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  completed_at DATETIME NULL,
  PRIMARY KEY (id),
  KEY ix_practice_sessions_user_id (user_id),
  CONSTRAINT fk_practice_sessions_user_id FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS practice_session_questions (
  id INT NOT NULL AUTO_INCREMENT,
  session_id INT NOT NULL,
  question_id INT NOT NULL,
  question_order INT NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_practice_session_question (session_id, question_id),
  UNIQUE KEY uq_practice_session_order (session_id, question_order),
  KEY ix_practice_session_questions_session_id (session_id),
  CONSTRAINT fk_practice_session_questions_session_id FOREIGN KEY (session_id) REFERENCES practice_sessions(id),
  CONSTRAINT fk_practice_session_questions_question_id FOREIGN KEY (question_id) REFERENCES quiz_questions(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS practice_answers (
  id INT NOT NULL AUTO_INCREMENT,
  session_id INT NOT NULL,
  question_id INT NOT NULL,
  user_answer VARCHAR(8) NOT NULL,
  is_correct BOOLEAN NOT NULL DEFAULT FALSE,
  score INT NOT NULL DEFAULT 0,
  answered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_practice_answer_question (session_id, question_id),
  KEY ix_practice_answers_session_id (session_id),
  CONSTRAINT fk_practice_answers_session_id FOREIGN KEY (session_id) REFERENCES practice_sessions(id),
  CONSTRAINT fk_practice_answers_question_id FOREIGN KEY (question_id) REFERENCES quiz_questions(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Post checks
SHOW CREATE TABLE quiz_questions;
SHOW CREATE TABLE practice_sessions;
SHOW CREATE TABLE practice_session_questions;
SHOW CREATE TABLE practice_answers;

-- Rollback, review carefully before running:
-- DROP TABLE IF EXISTS practice_answers;
-- DROP TABLE IF EXISTS practice_session_questions;
-- DROP TABLE IF EXISTS practice_sessions;
-- DROP TABLE IF EXISTS quiz_questions;
