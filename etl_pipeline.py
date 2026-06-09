import json
import uuid
import sys
import argparse
from datetime import datetime
from ftp_extractor import FTPDownloaderEngine
from postgres_loader import PostgresLoader

def load_pipeline_config(config_path="pipeline_config.json") -> list:
    with open(config_path, 'r') as file:
        return json.load(file)

def read_external_ddl(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return file.read()

def run_fast_csv_pipeline(requested_pipeline=None):
    print("[CHECKPOINT 3] Entering main pipeline function")
    configs = load_pipeline_config()
    
    # If a specific pipeline was requested, filter the list
    if requested_pipeline:
        configs = [c for c in configs if c['pipeline_name'] == requested_pipeline]
        if not configs:
            print(f"[ERROR] Pipeline '{requested_pipeline}' not found in configuration.")
            return

    for config in configs:
        print(f"\n>>> PROCESSING PIPELINE: {config['pipeline_name']}")
        
        target_table = config['target']['table_name_template'].format(
            date=datetime.now().strftime("%Y%m%d"), 
            run_id=str(uuid.uuid4())[:8]
        )
        
        ftp_engine = FTPDownloaderEngine()
        db_loader = PostgresLoader()
        
        try:
            # --- EXTRACT ---
            ftp_engine.connect()
            csv_records = ftp_engine.fetch_records_by_pattern(
                remote_directory=config['source']['remote_directory'],
                file_pattern=config['source']['file_pattern']
            )
            ftp_engine.disconnect()

            if not csv_records:
                print(f"No records found for {config['pipeline_name']}. Skipping.")
                continue

            # --- TARGET DDL GENERATION ---
            raw_sql = read_external_ddl(config['target']['ddl_file_path'])
            if "target_table_placeholder" not in raw_sql:
                print(f"[ERROR] Placeholder 'target_table_placeholder' not found in {config['target']['ddl_file_path']}")
                continue
                
            compiled_ddl = raw_sql.replace("target_table_placeholder", target_table)
            
            # --- EXECUTE ---
            db_loader.connect()
            db_loader.execute_dynamic_ddl(compiled_ddl)
            
            # --- BULK LOAD ---
            print(f"Initiating bulk load into {target_table}...")
            db_loader.bulk_load_csv_data(
                table_name=target_table, 
                records=csv_records, 
                conflict_key=config.get('conflict_key')
            )
            print(f"Pipeline {config['pipeline_name']} successful.")

        except Exception as e:
            print(f"\n[PIPELINE BROKE] Error in {config['pipeline_name']}: {e}")
        finally:
            db_loader.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ETL Pipelines.")
    parser.add_argument("--pipeline", help="Name of the specific pipeline to run")
    args = parser.parse_args()
    
    run_fast_csv_pipeline(args.pipeline)