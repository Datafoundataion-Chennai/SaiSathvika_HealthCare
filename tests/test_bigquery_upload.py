import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

def test_bigquery_upload_import():
    """Test if bigquery_upload.py can be imported without errors"""
    from scripts.bigquery_upload import dataset_id
    assert True

def test_dataset_config():
    from scripts.bigquery_upload import dataset_id
    assert dataset_id == 'healthcare_analytics'

def test_data_loading():
    from scripts.bigquery_upload import patients_data
    assert not patients_data.empty
    assert 'patient_id' in patients_data.columns

from unittest.mock import patch

@patch('scripts.bigquery_upload.bigquery.Client')
def test_table_upload(mock_client):
    from scripts.bigquery_upload import tables
    assert 'patients_data' in tables

def test_data_paths():
    from scripts.bigquery_upload import base_dir
    expected_path = base_dir / 'data' / 'processed' / 'patients_data_cleaned.csv'
    assert expected_path.exists()

def test_schema_autodetection():
    from scripts.bigquery_upload import cms_data
    assert 'Facility Name' in cms_data.columns
    assert 'Number of Readmissions' in cms_data.columns
