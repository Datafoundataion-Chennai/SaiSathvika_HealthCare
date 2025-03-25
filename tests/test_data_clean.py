import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

def test_data_clean_import():
    """Test if data_clean.py can be imported without errors"""
    from scripts.data_clean import combine_names
    assert True  # Passes if import succeeds

def test_combine_names_full():
    row = {'FIRST': 'John', 'MIDDLE': 'Q', 'LAST': 'Doe'}
    from scripts.data_clean import combine_names
    assert combine_names(row) == 'John Q Doe'

def test_combine_names_null_middle():
    row = {'FIRST': 'Jane', 'MIDDLE': None, 'LAST': 'Smith'}
    from scripts.data_clean import combine_names
    assert combine_names(row) == 'Jane Smith'

def test_combine_names_empty():
    row = {'FIRST': '', 'MIDDLE': '', 'LAST': ''}
    from scripts.data_clean import combine_names
    assert combine_names(row) == ''

def test_csv_output_exists():
    from pathlib import Path
    output_path = Path(__file__).parent.parent / 'data' / 'processed' / 'patients_data_cleaned.csv'
    assert output_path.exists()

def test_columns_renamed():
    from scripts.data_clean import patients_data
    assert 'patient_id' in patients_data.columns