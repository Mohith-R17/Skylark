from typing import Any, Dict, List, Optional
from services.data_service import DataService

class AIService:
    """
    Provider-agnostic AI Layer. 
    Currently uses a structured rule-based fallback but designed to be replaced 
    with a LangChain/OpenAI/Anthropic provider that accepts context and generates text.
    """
    
    def __init__(self, data_service: DataService):
        self.data_service = data_service
        
    def _format_currency(self, value: float) -> str:
        if value >= 1_000_000:
            return f"${value/1_000_000:.1f}M"
        if value >= 1_000:
            return f"${value/1_000:.1f}K"
        return f"${value:.0f}"

    def ask_skylark(self, query: str) -> Dict[str, Any]:
        """
        Answering founder-level business questions using actual computed metrics,
        distinguishing insights from data-quality warnings.
        """
        lower_query = query.lower().strip()
        summary = self.data_service.full_summary()
        pipeline = summary.get("pipeline", {})
        revenue = summary.get("revenue", {})
        ops = summary.get("operations", {})
        cb = summary.get("cross_board", {})
        
        insight_text = ""
        warnings = []
        
        # Simple routing based on keywords
        has_pipeline = "pipeline" in lower_query or "deal" in lower_query
        has_wo = "operation" in lower_query or "work order" in lower_query
        has_sector = "sector" in lower_query
        has_revenue = "revenue" in lower_query or "bill" in lower_query
        has_dq = any(k in lower_query for k in ["data quality", "data issues", "leadership", "missing", "quality issues", "risks"])
        has_deal_missing = any(k in lower_query for k in ["deal", "opportunity"]) and any(k in lower_query for k in ["missing", "attention", "information", "data"])

        if has_deal_missing:
            deals = getattr(self.data_service, "deals", [])
            if deals:
                unique_ids = set()
                total_deals = 0
                for d in deals:
                    if getattr(d, 'id', None):
                        unique_ids.add(d.id)
                        total_deals += 1

                has_stable_ids = (len(unique_ids) == total_deals) and total_deals > 0
                
                missing_deals = []
                if has_stable_ids:
                    for d in deals:
                        missing_fields = []
                        if d.close_date is None:
                            missing_fields.append("close date")
                        if d.closure_probability is None:
                            missing_fields.append("probability")
                        if d.deal_value is None and (d.status or "").lower() in ("open", "pending", "proposal", "negotiation"):
                            missing_fields.append("deal value")
                        
                        if missing_fields:
                            deal_name = getattr(d, "name", None) or getattr(d, "id", "Unknown Deal")
                            missing_deals.append(f"- **{deal_name}** (ID: {d.id}): Missing {', '.join(missing_fields)}")
                else:
                    from collections import defaultdict
                    grouped = defaultdict(lambda: defaultdict(int))
                    for d in deals:
                        missing = []
                        if d.close_date is None:
                            missing.append("close date")
                        if d.closure_probability is None:
                            missing.append("probability")
                        if d.deal_value is None and (d.status or "").lower() in ("open", "pending", "proposal", "negotiation"):
                            missing.append("deal value")
                            
                        if missing:
                            deal_name = getattr(d, "name", None) or "Unknown Deal"
                            for m in missing:
                                grouped[deal_name][m] += 1
                                
                    for name, issues in grouped.items():
                        parts = []
                        for issue, count in issues.items():
                            if count > 1:
                                parts.append(f"{count} deals missing {issue}")
                            else:
                                parts.append(f"1 deal missing {issue}")
                        missing_deals.append(f"- **{name}**: {', '.join(parts)}")
                
                if missing_deals:
                    displayed = missing_deals[:20]
                    insight_text = "The following deals are missing important information:\n\n" + "\n".join(displayed)
                    if len(missing_deals) > 20:
                        insight_text += f"\n\n...and {len(missing_deals) - 20} more deals with missing fields."
                else:
                    insight_text = "All deals currently have their required fields populated."
            else:
                insight_text = "The current data supports aggregate data-quality counts, but individual deal-level details are not available through the current data service."
                
                missing_val = pipeline.get("total_pipeline_value", {}).get("missing_count", 0)
                missing_close = pipeline.get("deals_missing_close_dates", {}).get("value", 0)
                missing_prob = pipeline.get("deals_missing_probability", {}).get("value", 0)
                
                insight_text += f"\n\n- {missing_val} open deals missing value"
                insight_text += f"\n- {missing_close} deals missing close dates"
                insight_text += f"\n- {missing_prob} deals missing probability"

        elif has_pipeline and has_wo and "compare" in lower_query:
            total_val = pipeline.get("total_pipeline_value", {}).get("value", 0)
            open_deals = pipeline.get("open_deals", 0)
            active = ops.get("active_work_orders", {}).get("value", 0)
            
            insight_text = (
                f"We currently have {self._format_currency(total_val)} in pipeline across {open_deals} open opportunities, "
                f"compared to {active} active work orders. "
                "Pipeline represents prospective business, while active work orders represent our current operations."
            )
            
            dq_pipe = pipeline.get("total_pipeline_value", {}).get("caveat", "")
            if dq_pipe:
                warnings.append(f"Pipeline Data Note: {dq_pipe}")
                
            dq_ops = ops.get("active_work_orders", {}).get("caveat", "")
            if dq_ops:
                warnings.append(f"Operations Data Note: {dq_ops}")

        elif has_pipeline and not has_sector and not has_deal_missing:
            total_val = pipeline.get("total_pipeline_value", {}).get("value", 0)
            open_deals = pipeline.get("open_deals", 0)
            insight_text = f"Our current pipeline is {self._format_currency(total_val)} across {open_deals} open opportunities."
            
            dq = pipeline.get("total_pipeline_value", {}).get("caveat", "")
            if dq:
                warnings.append(f"Pipeline Total Data Note: {dq}")
                
            missing_close = pipeline.get("deals_missing_close_dates", {}).get("value", 0)
            if missing_close > 0:
                warnings.append(f"{missing_close} deals are missing close dates, which impacts forecast accuracy.")
                
        elif has_sector:
            sectors = pipeline.get("pipeline_by_sector", {}).get("items", [])
            if sectors:
                top_sector = max(sectors, key=lambda x: x["value"])
                top_key = "Unclassified" if top_sector["key"] == "__missing__" else top_sector["key"]
                insight_text = f"Our top sector is {top_key} with {self._format_currency(top_sector['value'])} in pipeline ({top_sector['pct']}% of total)."
                insight_text += "\n\nBreakdown:\n"
                for s in sectors:
                    s_key = "Unclassified" if s["key"] == "__missing__" else s["key"]
                    insight_text += f"- {s_key}: {self._format_currency(s['value'])}\n"
            else:
                insight_text = "I don't have enough data to break down pipeline by sector."
                
        elif has_revenue:
            total_rev = revenue.get("total_wo_value", {}).get("value", 0)
            collected = revenue.get("total_collected", {}).get("value", 0)
            insight_text = f"Total work order value is {self._format_currency(total_rev)}. We have collected {self._format_currency(collected)}."
            
            dq_rev = revenue.get("total_wo_value", {}).get("caveat", "")
            if dq_rev:
                warnings.append(f"Revenue Data Note: {dq_rev}")
                
        elif has_wo:
            active = ops.get("active_work_orders", {}).get("value", 0)
            insight_text = f"We currently have {active} active work orders."
            
            dq_ops = ops.get("active_work_orders", {}).get("caveat", "")
            if dq_ops:
                warnings.append(f"Operations Data Note: {dq_ops}")
                
            unmatched_wo = cb.get("match_summary", {}).get("unmatched_work_orders", 0)
            if unmatched_wo > 0:
                warnings.append(f"Cross-board Risk: {unmatched_wo} work orders do not link back to a CRM deal.")
                
        elif has_dq and not has_deal_missing:
            missing_close = pipeline.get("deals_missing_close_dates", {}).get("value", 0)
            missing_prob = pipeline.get("deals_missing_probability", {}).get("value", 0)
            missing_val = pipeline.get("total_pipeline_value", {}).get("missing_count", 0)
            missing_wo_status = ops.get("active_work_orders", {}).get("missing_count", 0)
            unmatched_wo = cb.get("match_summary", {}).get("unmatched_work_orders", 0)
            
            insight_text = "Here is a summary of the data quality issues that need leadership attention:\n\n"
            if missing_close > 0:
                insight_text += f"- **Missing Close Dates**: {missing_close} deals lack a close date, impacting forecast visibility.\n"
            if missing_prob > 0:
                insight_text += f"- **Missing Probability**: {missing_prob} deals lack closure probability, skewing weighted pipeline.\n"
            if missing_val > 0:
                insight_text += f"- **Missing Values**: {missing_val} open deals are missing a deal value.\n"
            if missing_wo_status > 0:
                insight_text += f"- **Missing WO Status**: {missing_wo_status} work orders are missing a status, reducing operational visibility.\n"
            if unmatched_wo > 0:
                insight_text += f"- **Unlinked Work Orders**: {unmatched_wo} work orders do not link back to a CRM deal.\n"
                
            if insight_text == "Here is a summary of the data quality issues that need leadership attention:\n\n":
                insight_text = "There are currently no significant data quality issues detected across pipeline and operations."
            
        else:
            insight_text = "I can analyze pipeline, revenue, sectors, operations, or cross-board metrics based on current Skylark data. What would you like to know?"

        # If data is completely missing (empty datasets)
        if summary.get("pipeline", {}).get("total_deals", 0) == 0 and summary.get("operations", {}).get("total_work_orders", 0) == 0:
            insight_text = "I currently don't have any data loaded to answer your question. Please check the data source configuration."
            warnings = ["No dataset loaded."]

        return {
            "answer": insight_text,
            "caveats": warnings,
            "assumptions": ["Metrics are computed directly from the normalized datasets without speculative AI forecasting."]
        }
        
    def generate_leadership_update(self) -> List[Dict[str, str]]:
        """
        Generates a structured leadership update based on all data domains.
        """
        summary = self.data_service.full_summary()
        pipeline = summary.get("pipeline", {})
        revenue = summary.get("revenue", {})
        ops = summary.get("operations", {})
        cb = summary.get("cross_board", {})
        
        # Check if we have data
        if pipeline.get("total_deals", 0) == 0 and ops.get("total_work_orders", 0) == 0:
            return [{
                "title": "Insufficient Data",
                "content": "No data is currently loaded to generate a leadership update. Please provide valid datasets."
            }]
            
        sections = []
        
        # Executive Summary
        total_val = pipeline.get("total_pipeline_value", {}).get("value", 0)
        open_deals = pipeline.get("open_deals", 0)
        total_rev = revenue.get("total_wo_value", {}).get("value", 0)
        
        exec_content = (
            f"The business currently has {self._format_currency(total_val)} in open pipeline across {open_deals} opportunities, "
            f"and {self._format_currency(total_rev)} in active work order value."
        )
        sections.append({"title": "Executive Summary", "content": exec_content})
        
        # Pipeline
        sectors = pipeline.get("pipeline_by_sector", {}).get("items", [])
        if sectors:
            top_sector = max(sectors, key=lambda x: x["value"])
            top_key = "Unclassified" if top_sector["key"] == "__missing__" else top_sector["key"]
            pipe_content = (
                f"Pipeline is led by the {top_key} sector, contributing {top_sector['pct']}% "
                f"of total value ({self._format_currency(top_sector['value'])})."
            )
        else:
            pipe_content = f"Total pipeline is {self._format_currency(total_val)}."
            
        missing_close = pipeline.get("deals_missing_close_dates", {}).get("value", 0)
        if missing_close > 0:
            pipe_content += f" Note: {missing_close} deals are missing close dates, affecting forecast visibility."
        sections.append({"title": "Pipeline", "content": pipe_content})
        
        # Revenue
        collected = revenue.get("total_collected", {}).get("value", 0)
        to_bill = revenue.get("total_to_be_billed", {}).get("value", 0)
        rev_content = (
            f"Of the {self._format_currency(total_rev)} total work order value, {self._format_currency(collected)} "
            f"has been collected. We have {self._format_currency(to_bill)} remaining to be billed."
        )
        sections.append({"title": "Revenue", "content": rev_content})
        
        # Operations
        active_wo = ops.get("active_work_orders", {}).get("value", 0)
        ops_content = f"The operations team is managing {active_wo} active work orders."
        sections.append({"title": "Operations", "content": ops_content})
        
        # Risks & Data Quality
        risks = []
        unmatched_deals = cb.get("match_summary", {}).get("unmatched_deals", 0)
        if unmatched_deals > 0:
            risks.append(f"{unmatched_deals} closed deals do not have matching work orders.")
            
        unmatched_wos = cb.get("match_summary", {}).get("unmatched_work_orders", 0)
        if unmatched_wos > 0:
            risks.append(f"{unmatched_wos} work orders cannot be linked to a CRM deal.")
            
        if missing_close > 0:
            risks.append(f"{missing_close} deals missing close dates.")
            
        if risks:
            risks_content = " Identified risks include:\n" + "\n".join(f"- {r}" for r in risks)
        else:
            risks_content = "No major data risks identified."
            
        sections.append({"title": "Risks & Data Quality", "content": risks_content})
        
        return sections
