CREATE TABLE
  transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    shares INTEGER NOT NULL,
    price NUMERIC NOT NULL,
    transacted_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
  );