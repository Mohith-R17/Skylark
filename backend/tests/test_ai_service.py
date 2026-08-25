import pytest
from unittest.mock import MagicMock
from services.ai_service import AIService
from models.deal import Deal

@pytest.fixture
def mock_data_service():
    ds = MagicMock()
    ds.full_summary.return_value = {
        "pipeline": {
            "total_deals": 100,
            "open_deals": 50,
            "total_pipeline_value": {"value": 1000000, "missing_count": 2},
            "deals_missing_close_dates": {"value": 5},
            "deals_missing_probability": {"value": 3},
        },
        "operations": {
            "total_work_orders": 20,
            "active_work_orders": {"value": 10, "missing_count": 1},
        },
        "cross_board": {
            "match_summary": {"unmatched_work_orders": 0}
        },
        "revenue": {
            "total_wo_value": {"value": 500000}
        }
    }
    return ds


def test_ai_deal_missing_intent_with_deal_details(mock_data_service):
    # Set up mock deals
    d1 = Deal(id="d1", name="Deal 1", close_date=None, closure_probability="High", deal_value=1000, status="Open", client="C1", owner="O1", stage="S1", product="P1", sector="Sec1")
    d2 = Deal(id="d2", name="Deal 2", close_date="2025-01-01", closure_probability=None, deal_value=2000, status="Open", client="C2", owner="O2", stage="S2", product="P2", sector="Sec2")
    
    # Needs valid normalized model args or we just mock it simply
    # Wait, the Deal model might be stricter. Let's just mock the objects entirely.
    mock_d1 = MagicMock()
    mock_d1.name = "Deal 1"
    mock_d1.id = "1"
    mock_d1.close_date = None
    mock_d1.closure_probability = "High"
    mock_d1.deal_value = 1000
    mock_d1.status = "Open"
    
    mock_d2 = MagicMock()
    mock_d2.name = "Deal 2"
    mock_d2.id = "2"
    mock_d2.close_date = "2025-01-01"
    mock_d2.closure_probability = None
    mock_d2.deal_value = 2000
    mock_d2.status = "Open"
    
    mock_data_service.deals = [mock_d1, mock_d2]
    
    ai = AIService(mock_data_service)
    response = ai.ask_skylark("Which deals are missing important information?")
    
    assert "The following deals are missing important information:" in response["answer"]
    assert "- **Deal 1** (ID: 1): Missing close date" in response["answer"]
    assert "- **Deal 2** (ID: 2): Missing probability" in response["answer"]


def test_ai_deal_missing_intent_grouped_by_name(mock_data_service):
    # Simulate environment where IDs are not unique (e.g., Excel fallback where ID == Name)
    mock_d1 = MagicMock()
    mock_d1.name = "Deal X"
    mock_d1.id = "Deal X"
    mock_d1.close_date = None
    mock_d1.closure_probability = None
    mock_d1.deal_value = 1000
    mock_d1.status = "Open"
    
    mock_d2 = MagicMock()
    mock_d2.name = "Deal X"
    mock_d2.id = "Deal X"
    mock_d2.close_date = None
    mock_d2.closure_probability = "High"
    mock_d2.deal_value = 2000
    mock_d2.status = "Open"
    
    mock_data_service.deals = [mock_d1, mock_d2]
    
    ai = AIService(mock_data_service)
    response = ai.ask_skylark("Which deals are missing important information?")
    
    assert "The following deals are missing important information:" in response["answer"]
    assert "- **Deal X**: 2 deals missing close date, 1 deal missing probability" in response["answer"]


def test_ai_deal_missing_intent_without_deal_details(mock_data_service):
    # Simulate environment where individual deals are unavailable
    mock_data_service.deals = []
    
    ai = AIService(mock_data_service)
    response = ai.ask_skylark("Which deals are missing important information?")
    
    assert "The current data supports aggregate data-quality counts" in response["answer"]
    assert "2 open deals missing value" in response["answer"]
    assert "5 deals missing close dates" in response["answer"]
    assert "3 deals missing probability" in response["answer"]
