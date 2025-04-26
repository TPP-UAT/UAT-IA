CREATE TABLE IF NOT EXISTS files (
    file_id VARCHAR(255) PRIMARY KEY,
    abstract TEXT,
    full_text TEXT,
    summarized_text TEXT,
    title TEXT,
    link TEXT,
);

CREATE TABLE IF NOT EXISTS keywords (
    keyword_id INT NOT NULL,
    file_id VARCHAR(255),
    "order" INT,
    FOREIGN KEY (file_id) REFERENCES files(file_id)
);

CREATE INDEX IF NOT EXISTS idx_keywords_file_id ON keywords(file_id);
