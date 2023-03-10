CREATE TABLE IF NOT EXISTS USERS(
    user_id     BIGINT PRIMARY KEY,
    username    TEXT,
    first_name  TEXT,
    last_name   TEXT,
    referrer    TEXT,
    join_date   TIMESTAMP DEFAULT current_timestamp
);

CREATE TABLE IF NOT EXISTS SETTINGS(
    user_id         INTEGER PRIMARY KEY REFERENCES USERS(user_id) ON DELETE CASCADE,
    language        TEXT DEFAULT "english",
    restricted_mode INTEGER DEFAULT 1
);
