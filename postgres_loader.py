import os
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor, execute_values
from dotenv import load_dotenv

load_dotenv()

class PostgresLoader:
    def __init__(self):
        self.connection = None
        self.host = os.getenv("DB_HOST")
        self.port = os.getenv("DB_PORT")
        self.dbname = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")

    def connect(self):
        self.connection = psycopg2.connect(
            host=self.host, port=self.port, dbname=self.dbname,
            user=self.user, password=self.password, cursor_factory=RealDictCursor
        )

    def execute_dynamic_ddl(self, ddl_string: str):
        with self.connection.cursor() as cursor:
            cursor.execute(ddl_string)
            self.connection.commit()
    
    def bulk_load_csv_data(self, table_name: str, records: list, conflict_key: str = None):
        """High-speed bulk insert. Uses conflict_key if provided."""
        if not records:
            return

        columns = list(records[0].keys())
        if 'id' in columns:
            columns.remove('id')
        
        # Base query
        query_str = "INSERT INTO {} ({}) VALUES %s"
        
        # Append conflict resolution if key is provided
        if conflict_key:
            query_str += f" ON CONFLICT ({conflict_key}) DO NOTHING"
            
        query = sql.SQL(query_str).format(
            sql.Identifier(table_name),
            sql.SQL(', ').join(map(sql.Identifier, columns))
        )

        values = [[row.get(col) for col in columns] for row in records]

        with self.connection.cursor() as cursor:
            execute_values(cursor, query, values)
            self.connection.commit()
            print(f"Successfully bulk loaded batch into {table_name}.")
    
    def close(self):
        """Closes the database connection if it exists."""
        if self.connection:
            self.connection.close()
            print("Database connection closed successfully.")

"""
    def bulk_load_csv_data(self, table_name: str, records: list):
        #High-speed bulk insert bypassing the LLM for clean structured data.
        if not records:
            return

        # Extract column headers from the first dictionary
        # We ignore 'id' if your CSV has it, to let PostgreSQL SERIAL handle it natively, 
        # but since your CSV has 'id', we will map exactly what is in the CSV.
        columns = list(records[0].keys())
        
        # Prepare the execution query
        query = sql.SQL("INSERT INTO {} ({}) VALUES %s").format(
            sql.Identifier(table_name),
            sql.SQL(', ').join(map(sql.Identifier, columns))
        )

        # Extract values as a list of tuples
        values = [[row[col] for col in columns] for row in records]

        with self.connection.cursor() as cursor:
            # execute_values is incredibly fast for large batch inserts
            execute_values(cursor, query, values)
            self.connection.commit()
            print(f"Successfully bulk loaded {len(records)} rows into {table_name}.")"""

