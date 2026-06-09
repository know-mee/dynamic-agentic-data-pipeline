CREATE TABLE IF NOT EXISTS target_table_placeholder (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    price NUMERIC(10,2) NOT NULL,
    stock_quantity INT NOT NULL,
    supplier VARCHAR(100),
    country VARCHAR(50),
    added_date DATE NOT NULL,
    is_active BOOLEAN NOT NULL,
    source_file VARCHAR(255),
    raw_row_data TEXT -- ADD THIS LINE
);
