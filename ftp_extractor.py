import os
import io
import csv
import fnmatch
from ftplib import FTP
from dotenv import load_dotenv

load_dotenv()

class FTPDownloaderEngine:
    def __init__(self):
        self.host = os.getenv("FTP_HOST")
        self.user = os.getenv("FTP_USER")
        self.password = os.getenv("FTP_PASSWORD")
        self.ftp = None

    def connect(self):
        self.ftp = FTP(self.host)
        self.ftp.login(user=self.user, passwd=self.password)

    def fetch_records_by_pattern(self, remote_directory: str, file_pattern: str) -> list:
        """Finds files matching a wildcard pattern (e.g., customers_*.csv) and reads their rows."""
        try:
            self.ftp.cwd(remote_directory)
        except Exception as e:
            print(f"Error navigating to {remote_directory}: {e}")
            return []

        filenames = self.ftp.nlst()
        all_records = []
        
        # Filter files based on the pattern
        matched_files = fnmatch.filter(filenames, file_pattern)
        print(f"Found files matching '{file_pattern}': {matched_files}")
        
        for filename in matched_files:
            print(f"Streaming and parsing: {filename}")
            csv_bytes = io.BytesIO()
            self.ftp.retrbinary(f"RETR {filename}", csv_bytes.write)
            csv_bytes.seek(0)
            
            csv_text = io.TextIOWrapper(csv_bytes, encoding='utf-8')
            csv_reader = csv.DictReader(csv_text)
            
            for row in csv_reader:
                # 1. Create the text string representation for auditing
                row_string = ", ".join([f"{key}: {value}" for key, value in row.items()])
                
                # 2. Preserve the actual parsed CSV columns (id, first_name, email, etc.)
                record_dict = dict(row)
                
                # 3. Inject the meta-columns expected by your SQL DDL
                record_dict["source_file"] = filename
                record_dict["raw_row_data"] = row_string
                
                all_records.append(record_dict)
                
        return all_records

    def disconnect(self):
        if self.ftp:
            self.ftp.quit()