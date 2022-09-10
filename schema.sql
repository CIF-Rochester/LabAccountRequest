DROP TABLE IF EXISTS active_requests;

CREATE TABLE active_requests (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  net_id TEXT NOT NULL,
  student_id TEXT NOT NULL,
  id_card_lcc TEXT NOT NULL
);

DROP TABLE IF EXISTS review_sessions;

CREATE TABLE review_sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP NOT NULL
);

DROP TABLE IF EXISTS review_session_requests;

CREATE TABLE review_session_requests (
  review_session INTEGER NOT NULL,
  active_request INTEGER NOT NULL,

  FOREIGN KEY (review_session) REFERENCES review_sessions(id),
  FOREIGN KEY (active_request) REFERENCES active_requests(id),
  PRIMARY KEY (review_session, active_request)
);

DROP TABLE IF EXISTS reviewed_requests;

CREATE TABLE reviewed_requests (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TIMESTAMP NOT NULL,
  reviewed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  reviewed_by TEXT NOT NULL, -- net_id of trusted lab account
  approved BOOLEAN NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  net_id TEXT NOT NULL,
  student_id TEXT NOT NULL,
  id_card_lcc TEXT NOT NULL
);

DROP TABLE IF EXISTS audit_log;

CREATE TABLE audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actor TEXT NOT NULL, -- "anonymous" or net_id of logged in user
  actor_ip TEXT NOT NULL,
  event_type INTEGER NOT NULL,
  event_data JSON NOT NULL,

  FOREIGN KEY (event_type) REFERENCES event_types(id)
);

DROP TABLE IF EXISTS event_types;

CREATE TABLE event_types (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_name TEXT NOT NULL
);

INSERT INTO event_types (event_name) VALUES
  ("notification_sent"),
  ("reminder_sent"),
  ("spam_notification_sent"),
  ("review_session_link_opened"),
  ("review_session_expired"),
  ("review_approve"),
  ("review_deny")
;
