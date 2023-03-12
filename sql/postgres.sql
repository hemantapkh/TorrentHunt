CREATE TABLE IF NOT EXISTS USERS(
    user_id     BIGINT PRIMARY KEY,
    user_type   TEXT NOT NULL,
    username    TEXT,
    first_name  TEXT,
    last_name   TEXT,
    referrer    TEXT,
    join_date   TIMESTAMP DEFAULT current_timestamp
);

CREATE TABLE IF NOT EXISTS SETTINGS(
    user_id         BIGINT PRIMARY KEY REFERENCES USERS(user_id) ON DELETE CASCADE,
    language        TEXT DEFAULT 'english',
    restricted_mode BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS ADMINS(
    user_id     BIGINT PRIMARY KEY REFERENCES USERS(user_id) ON DELETE CASCADE,
    date        TIMESTAMP DEFAULT current_timestamp
);
