-- Table for users
CREATE TABLE IF NOT EXISTS USERS(
    user_id         BIGINT PRIMARY KEY,
    user_type       TEXT NOT NULL,
    username        TEXT,
    first_name      TEXT,
    last_name       TEXT,
    referrer        TEXT,
    join_date       TIMESTAMP DEFAULT current_timestamp,
    last_active     TIMESTAMP DEFAULT current_timestamp
);

-- Table for storing user settings
CREATE TABLE IF NOT EXISTS SETTINGS(
    user_id         BIGINT PRIMARY KEY,
    language        TEXT DEFAULT 'english',
    restricted_mode BOOLEAN DEFAULT TRUE,
    FOREIGN KEY     (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE
);

-- Trigger function to insert a new row into SETTINGS when a new row is inserted into USERS
CREATE FUNCTION insert_default_settings() RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO SETTINGS (user_id) VALUES (NEW.user_id);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to call the function above
CREATE TRIGGER user_insert_trigger AFTER INSERT ON USERS
FOR EACH ROW EXECUTE FUNCTION insert_default_settings();

-- Table for storing bookmarks
CREATE TABLE IF NOT EXISTS BOOKMARKS(
    user_id         BIGINT NOT NULL,
    hash            TEXT NOT NULL,
    title           TEXT NOT NULL,
    magnet          TEXT NOT NULL,
    seeders         TEXT,
    leechers        TEXT,
    size            TEXT,
    uploaded_on     TEXT,
    date            TIMESTAMP DEFAULT current_timestamp,
    PRIMARY KEY     (user_id, hash),
    FOREIGN KEY     (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE
);

-- Table for admins
CREATE TABLE IF NOT EXISTS ADMINS(
    user_id         BIGINT PRIMARY KEY,
    date            TIMESTAMP DEFAULT current_timestamp,
    FOREIGN KEY     (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE
);

-- Table for creating tracking links
CREATE TABLE IF NOT EXISTS REFERRERS(
    referrer_id     TEXT PRIMARY KEY,
    title           TEXT NOT NULL,
    description     TEXT,
    clicks          INTEGER NOT NULL DEFAULT 0,
    date            TIMESTAMP DEFAULT current_timestamp
);
