import os
import pytest
from pathlib import Path
from services.data_service import DataService, _auto_select_adapter
from services.adapters.excel_adapter import ExcelAdapter
from services.adapters.monday_adapter import MondayAdapter

@pytest.fixture
def mock_env(monkeypatch):
    """Clear env vars to ensure a clean state."""
    monkeypatch.delenv("MONDAY_API_TOKEN", raising=False)
    monkeypatch.delenv("SKYLARK_DEALS_PATH", raising=False)
    monkeypatch.delenv("SKYLARK_WO_PATH", raising=False)

def test_auto_select_adapter_monday(mock_env, monkeypatch):
    monkeypatch.setenv("MONDAY_API_TOKEN", "test_token")
    adapter = _auto_select_adapter()
    assert isinstance(adapter, MondayAdapter)
    assert adapter.source_name() == "monday.com (production)"

def test_auto_select_adapter_excel(mock_env, monkeypatch):
    monkeypatch.setenv("SKYLARK_DEALS_PATH", "fake_deals.xlsx")
    adapter = _auto_select_adapter()
    assert isinstance(adapter, ExcelAdapter)
    assert adapter.source_name() == "Excel (development)"

@pytest.mark.anyio
async def test_data_service_excel_load(mock_env, monkeypatch):
    # Point to the actual real files for the test
    deals_path = "C:\\Users\\R Mohith\\Downloads\\Deal funnel Data.xlsx"
    wo_path = "C:\\Users\\R Mohith\\Downloads\\Work_Order_Tracker Data.xlsx"
    
    if Path(deals_path).exists() and Path(wo_path).exists():
        monkeypatch.setenv("SKYLARK_DEALS_PATH", deals_path)
        monkeypatch.setenv("SKYLARK_WO_PATH", wo_path)
        
        ds = DataService()
        await ds.load()
        
        # Verify that we loaded non-zero data from the excel files
        assert len(ds.deals) > 0
        assert len(ds.work_orders) > 0
        
        # Verify analytics can run on this dataset
        pipe = ds.pipeline_analytics().summary()
        assert pipe["total_deals"] > 0
        assert pipe["total_pipeline_value"]["value"] > 0
        
        # Validate data quality summary doesn't crash
        dq = ds.data_quality_summary()
        assert "total_issues" in dq
