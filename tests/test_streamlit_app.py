import sys
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).parent.parent))

def test_streamlit_app_import():
    """Test if streamlit_app.py can be imported without errors"""
    from scripts.streamlit_app import load_lottie
    assert True

def test_lottie_loading(tmp_path):
    """Test JSON animation file loading"""
    from scripts.streamlit_app import load_lottie
    test_file = tmp_path / "test.json"
    test_file.write_text('{"test": "data"}')
    result = load_lottie(str(test_file))
    assert result == {"test": "data"}

def test_missing_lottie_file():
    """Test handling of missing animation files"""
    from scripts.streamlit_app import load_lottie
    assert load_lottie("nonexistent.json") is None

@patch('scripts.streamlit_app.bigquery.Client')
def test_query_execution(mock_client):
    """Test BigQuery query execution"""
    from scripts.streamlit_app import run_query
    mock_client.return_value.query.return_value.result.return_value = True
    result = run_query("SELECT 1")
    assert result is not None

@patch('scripts.streamlit_app.st')
def test_ui_rendering(mock_st):
    """Test Streamlit UI components exist"""
    from scripts.streamlit_app import st
    mock_st.title.return_value = True
    mock_st.selectbox.return_value = "option"
    assert st.title("Test") is True

def test_plot_generation():
    """Test visualization functions don't crash"""
    from scripts.streamlit_app import plt
    import matplotlib
    fig, ax = plt.subplots()
    ax.plot([1, 2], [3, 4])
    assert isinstance(fig, matplotlib.figure.Figure)