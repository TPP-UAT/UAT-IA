CREATE TABLE IF NOT EXISTS Files (
    file_id VARCHAR(255) PRIMARY KEY,
    abstract TEXT,
    full_text TEXT
);

CREATE TABLE IF NOT EXISTS Keywords (
    keyword_id INT NOT NULL,
    file_id VARCHAR(255),
    "Order" INT,
    FOREIGN KEY (file_id) REFERENCES Files(file_id)
);

CREATE INDEX IF NOT EXISTS idx_keywords_file_id ON Keywords(file_id);
