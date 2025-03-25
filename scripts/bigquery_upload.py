import pandas as pd
from google.cloud import bigquery
from google.cloud.bigquery import DatasetReference
from pathlib import Path

base_dir = Path(__file__).parent.parent
patients_path = base_dir / 'data' / 'processed' / 'patients_data_cleaned.csv'
appointments_path = base_dir / 'data' / 'processed' / 'appointments_data_cleaned.csv'
cms_path = base_dir / 'data' / 'processed' / 'cms_data_cleaned.csv'

patients_data = pd.read_csv(patients_path)
appointments_data = pd.read_csv(appointments_path)
cms_data = pd.read_csv(cms_path)

dataset_id = 'healthcare_analytics'
tables = {
    'patients_data': patients_data,
    'appointments_data': appointments_data,
    'cms_data': cms_data,
}

client = bigquery.Client()
dataset_ref = DatasetReference(client.project, dataset_id)
try:
    client.get_dataset(dataset_ref)
    print(f"Dataset {dataset_id} Already Exists.")
except Exception:
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = 'US'
    client.create_dataset(dataset)
    print(f"Dataset {dataset_id} Created.")

for table_name, df in tables.items():
    table_ref = dataset_ref.table(table_name)
    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE  
    )
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()  
    print(f"Table {table_name} Created and Data Uploaded.")