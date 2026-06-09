CREATE TABLE IF NOT EXISTS target_table_placeholder (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    customer_id INT NOT NULL,
    sale_date DATE NOT NULL,
    quantity INT NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL,
    country VARCHAR(50),
    sales_channel VARCHAR(50),
    is_successful BOOLEAN NOT NULL,
    source_file VARCHAR(255),
    raw_row_data TEXT -- ADD THIS LINE
);
