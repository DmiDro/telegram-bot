CREATE TABLE IF NOT EXISTS users_results (
    id               SERIAL PRIMARY KEY,
    user_id          BIGINT       NOT NULL UNIQUE,
    full_name        TEXT,
    subscribe        BOOLEAN      DEFAULT TRUE,
    first_test_date  DATE,
    first_test_time  TIME,
    forecast_time    TIME         DEFAULT '09:01:00',
    unsubscribe_date DATE,

    archetype_key    TEXT,
    maturity_key     TEXT,
    socionics_key    TEXT,
    character_key    TEXT
);
