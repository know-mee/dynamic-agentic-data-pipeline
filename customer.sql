CREATE TABLE IF NOT EXISTS  target_table_placeholder (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    gender VARCHAR(20),
    ip_address INET,
    country VARCHAR(100),
    registration_date DATE NOT NULL,
    is_active BOOLEAN NOT NULL,
    source_file VARCHAR(255),
    raw_row_data TEXT -- ADD THIS LINE
);
