import pytest

from models.deal import Deal
from models.work_order import WorkOrder
from services.normalization.date_normalizer import normalize_date
from services.normalization.numeric_normalizer import normalize_numeric
from services.normalization.status_normalizer import normalize_status
from services.normalization.text_normalizer import normalize_text


def test_valid_date():
    result = normalize_date("2025-08-25")
    assert result is not None


def test_invalid_date():
    result = normalize_date("not-a-date")
    assert result is None


def test_missing_date():
    result = normalize_date(None)
    assert result is None


def test_numeric_value():
    result = normalize_numeric("1,250.50")
    assert result == 1250.50


def test_missing_numeric():
    result = normalize_numeric(None)
    assert result is None


def test_text_normalization():
    result = normalize_text("  Hello WORLD  ")
    assert result == "Hello WORLD"


def test_missing_text():
    result = normalize_text(None)
    assert result is None


def test_status_normalization():
    result = normalize_status("High")
    assert result is not None


def test_deal_model_import():
    assert Deal is not None


def test_work_order_model_import():
    assert WorkOrder is not None
