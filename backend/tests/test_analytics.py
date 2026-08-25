"""Tests for the analytics engine — pipeline, revenue, operations, cross-board."""
import pytest

from models.deal import Deal
from models.work_order import WorkOrder
from services.analytics.pipeline import PipelineAnalytics
from services.analytics.revenue import RevenueAnalytics
from services.analytics.operations import OperationsAnalytics
from services.analytics.cross_board import CrossBoardAnalytics


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _sample_deals():
    return [
        Deal(name="DEAL-001", owner="OWN-A", client="CLI-A", status="Open",
             deal_value=100000, closure_probability="High", sector="Mining", stage="Proposal"),
        Deal(name="DEAL-002", owner="OWN-B", client="CLI-B", status="Open",
             deal_value=200000, closure_probability="Medium", sector="Energy", stage="Negotiation"),
        Deal(name="DEAL-003", owner="OWN-A", client="CLI-A", status="Won",
             deal_value=50000, sector="Mining", stage="Closed"),
        Deal(name="DEAL-004", owner="OWN-C", client="CLI-C", status="Open",
             deal_value=None, closure_probability=None, sector=None),  # missing data
        Deal(name="DEAL-005", status="Open", deal_value=150000,
             closure_probability="Low", sector="Mining"),
    ]


def _sample_work_orders():
    return [
        WorkOrder(deal_reference="DEAL-001", customer="CLI-A", wo_status="Open",
                  billing_status="Partially Billed", collection_status="Not Collected",
                  amount_excl_gst=80000, billed_value_excl_gst=40000,
                  collected_amount_incl_gst=10000, amount_receivable=30000,
                  sector="Mining", work_type="Survey",
                  quantities_as_per_po=100, quantity_billed_till_date=40),
        WorkOrder(deal_reference="DEAL-002", customer="CLI-B", wo_status="Executed",
                  billing_status="Fully Billed", collection_status="Collected",
                  amount_excl_gst=200000, billed_value_excl_gst=200000,
                  collected_amount_incl_gst=230000, amount_receivable=0,
                  sector="Energy", work_type="Mapping"),
        WorkOrder(deal_reference="DEAL-003", customer="CLI-A", wo_status="Completed",
                  billing_status="Fully Billed", collection_status="Collected",
                  amount_excl_gst=50000, billed_value_excl_gst=50000,
                  collected_amount_incl_gst=57500, amount_receivable=0,
                  sector="Mining"),
        WorkOrder(customer="CLI-D", wo_status="Open",
                  billing_status=None, sector="Infra"),  # no deal ref
    ]


# ---------------------------------------------------------------------------
# Pipeline analytics tests
# ---------------------------------------------------------------------------

class TestPipelineAnalytics:
    def test_total_pipeline_value(self):
        pa = PipelineAnalytics(_sample_deals())
        result = pa.total_pipeline_value()
        # Open deals with value: DEAL-001 (100k), DEAL-002 (200k), DEAL-005 (150k)
        # DEAL-004 is open but has no value
        assert result.value == 450000
        assert result.missing_count == 1  # DEAL-004

    def test_weighted_pipeline(self):
        pa = PipelineAnalytics(_sample_deals())
        result = pa.weighted_pipeline()
        # DEAL-001: 100k * 0.75 = 75k, DEAL-002: 200k * 0.50 = 100k, DEAL-005: 150k * 0.25 = 37.5k
        assert result.value == 212500
        assert result.missing_count == 1  # DEAL-004 excluded

    def test_deals_missing_close_dates(self):
        pa = PipelineAnalytics(_sample_deals())
        result = pa.deals_missing_close_dates()
        assert result.value == 5  # all sample deals have no close_date

    def test_deals_missing_probability(self):
        pa = PipelineAnalytics(_sample_deals())
        result = pa.deals_missing_probability()
        # DEAL-003 and DEAL-004 missing probability
        assert result.value == 2

    def test_pipeline_by_sector(self):
        pa = PipelineAnalytics(_sample_deals())
        breakdown = pa.pipeline_by_sector()
        sector_keys = {item.key for item in breakdown.items}
        assert "Mining" in sector_keys

    def test_deal_status_distribution(self):
        pa = PipelineAnalytics(_sample_deals())
        dist = pa.deal_status_distribution()
        assert dist.total == 5.0

    def test_summary_structure(self):
        pa = PipelineAnalytics(_sample_deals())
        s = pa.summary()
        assert "total_deals" in s
        assert "total_pipeline_value" in s
        assert "weighted_pipeline" in s
        assert s["total_deals"] == 5


# ---------------------------------------------------------------------------
# Revenue analytics tests
# ---------------------------------------------------------------------------

class TestRevenueAnalytics:
    def test_total_wo_value(self):
        ra = RevenueAnalytics(_sample_work_orders())
        result = ra.total_wo_value()
        # 80k + 200k + 50k = 330k (4th WO has no amount)
        assert result.value == 330000
        assert result.missing_count == 1

    def test_total_billed(self):
        ra = RevenueAnalytics(_sample_work_orders())
        result = ra.total_billed_value()
        assert result.value == 290000  # 40k + 200k + 50k

    def test_billing_status_distribution(self):
        ra = RevenueAnalytics(_sample_work_orders())
        dist = ra.billing_status_distribution()
        assert dist.total == 4.0

    def test_summary_structure(self):
        ra = RevenueAnalytics(_sample_work_orders())
        s = ra.summary()
        assert "total_work_orders" in s
        assert s["total_work_orders"] == 4


# ---------------------------------------------------------------------------
# Operations analytics tests
# ---------------------------------------------------------------------------

class TestOperationsAnalytics:
    def test_active_work_orders(self):
        oa = OperationsAnalytics(_sample_work_orders())
        result = oa.active_work_orders()
        # Open(2) + Executed(1) = 3 active (Completed excluded)
        assert result.value == 3

    def test_by_sector(self):
        oa = OperationsAnalytics(_sample_work_orders())
        breakdown = oa.by_sector()
        assert breakdown.total == 4.0

    def test_quantity_planned_vs_billed(self):
        oa = OperationsAnalytics(_sample_work_orders())
        result = oa.quantity_planned_vs_billed()
        # Only WO-1 has both: planned=100, billed=40
        assert result["planned"] == 100
        assert result["billed"] == 40
        assert result["gap"] == 60

    def test_summary_structure(self):
        oa = OperationsAnalytics(_sample_work_orders())
        s = oa.summary()
        assert "active_work_orders" in s
        assert "by_sector" in s


# ---------------------------------------------------------------------------
# Cross-board analytics tests
# ---------------------------------------------------------------------------

class TestCrossBoardAnalytics:
    def test_match_summary(self):
        cba = CrossBoardAnalytics(_sample_deals(), _sample_work_orders())
        ms = cba.match_summary()
        assert ms["total_deals"] == 5
        assert ms["total_work_orders"] == 4
        # DEAL-001, DEAL-002, DEAL-003 should match by deal ref
        assert ms["exact_deal_ref_matches"] >= 3

    def test_customers_with_both(self):
        cba = CrossBoardAnalytics(_sample_deals(), _sample_work_orders())
        result = cba.customers_with_both()
        # CLI-A and CLI-B appear in both
        assert result["count"] >= 2

    def test_pipeline_vs_active_wos(self):
        cba = CrossBoardAnalytics(_sample_deals(), _sample_work_orders())
        result = cba.pipeline_vs_active_wos()
        assert result["open_deals"] == 4  # DEAL-001..005 minus Won

    def test_summary_structure(self):
        cba = CrossBoardAnalytics(_sample_deals(), _sample_work_orders())
        s = cba.summary()
        assert "match_summary" in s
        assert "sector_overlap" in s
