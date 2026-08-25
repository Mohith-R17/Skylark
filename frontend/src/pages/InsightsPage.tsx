import React, { useMemo } from "react";
import { AlertCircle, AlertTriangle, CheckCircle, TrendingUp, } from "lucide-react";
import { LoadingState, EmptyState, ErrorState } from "@/components/layout";
import { PageHeader } from "@/components/layout/PageHeader";
import { useDashboardData } from "@/hooks/useDashboardData";

interface Insight {
  id: string;
  title: string;
  category: "Opportunity" | "Risk" | "Trend" | "Operations" | "Data Quality";
  severity: "healthy" | "warning" | "critical";
  metric: string;
  explanation: string;
  action: string;
}

// Default insights are kept as placeholders if we don't have enough backend insights yet.
// In the future this should come entirely from a /api/insights endpoint that generates text.

type SeverityClass = "bg-green-100 text-green-800" | "bg-amber-100 text-amber-800" | "bg-red-100 text-red-800";

function SeverityBadge({ severity }: { severity: "healthy" | "warning" | "critical" }) {
  return (
    <span className={`${severity === "healthy" ? "bg-green-100 text-green-800" : severity === "warning" ? "bg-amber-100 text-amber-800" : "bg-red-100 text-red-800"} inline-flex items-center rounded px-2.5 py-1 text-xs font-medium`}>
      {severity}
    </span>
  );
}

export default function InsightsPage() {
  const { data, loading, error } = useDashboardData();

  const generatedInsights = useMemo(() => {
    if (!data) return [];
    
    const insights: Insight[] = [];
    
    // Add data quality insights
    if (data.pipeline?.deals_missing_close_dates?.value > 0) {
      insights.push({
        id: "dq-close-date",
        title: "Missing close dates",
        category: "Data Quality",
        severity: "warning",
        metric: `${data.pipeline.deals_missing_close_dates.value} deals missing close dates`,
        explanation: `Deals lack close date projections, impacting forecast accuracy. ${data.pipeline.deals_missing_close_dates.caveat}`,
        action: "Update close date projections for open opportunities.",
      });
    }

    if (data.pipeline?.deals_missing_probability?.value > 0) {
      insights.push({
        id: "dq-prob",
        title: "Missing probability",
        category: "Data Quality",
        severity: "warning",
        metric: `${data.pipeline.deals_missing_probability.value} deals missing probability`,
        explanation: `Without probability, weighted pipeline calculations are skewed. ${data.pipeline.deals_missing_probability.caveat}`,
        action: "Ensure all active deals have a win probability percentage.",
      });
    }

    // Add cross-board insights
    if (data.cross_board?.unmatched_deals?.value > 0) {
      insights.push({
        id: "cb-unmatched-deals",
        title: "Disconnected Deals",
        category: "Operations",
        severity: "warning",
        metric: `${data.cross_board.unmatched_deals.value} deals with no active work order`,
        explanation: "Some closed deals do not have a matching work order in the Operations board, which may indicate delays in handoff.",
        action: "Review closed-won deals and ensure operations are mobilized.",
      });
    }

    if (data.cross_board?.unmatched_work_orders?.value > 0) {
      insights.push({
        id: "cb-unmatched-wo",
        title: "Orphaned Work Orders",
        category: "Operations",
        severity: "warning",
        metric: `${data.cross_board.unmatched_work_orders.value} work orders without a deal`,
        explanation: "Work is being executed without a clear linkage to the pipeline, potentially causing unbilled work.",
        action: "Ensure all work orders are linked to a CRM deal.",
      });
    }

    return insights;
  }, [data]);

  if (loading) return <LoadingState text="Loading insights..." />;
  if (error) return <ErrorState title="Failed to load insights" description={error.message} />;
  if (!data) return <EmptyState />;

  return (
    <section id="insights" className="prose max-w-none">
      <PageHeader title="Insights" subtitle="Curated findings from your business data" />

      {generatedInsights.length === 0 ? (
        <EmptyState title="No critical insights" description="Your business data looks healthy right now." />
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {generatedInsights.map((insight) => (
            <div
              key={insight.id}
              className={`rounded-lg border p-5 transition-colors hover:border-${insight.severity === "critical" ? "red-300" : insight.severity === "warning" ? "amber-300" : "green-300"} ${insight.severity === "critical" ? "bg-red-50" : insight.severity === "warning" ? "bg-amber-50" : "bg-green-50"}`}
            >
              <div className="flex items-start gap-3">
                <SeverityBadge severity={insight.severity} />
                <div className="flex-1">
                  <h3 className="font-medium mb-1">{insight.title}</h3>
                  <p className="text-sm text-muted-foreground mb-2">{insight.metric}</p>
                  <p className="text-sm line-clamp-3">{insight.explanation}</p>
                </div>
              </div>
              <p className="text-xs text-muted-foreground mt-3 pt-3 border-t border-black/5 font-medium">{insight.action}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}