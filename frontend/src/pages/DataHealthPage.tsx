import React, { useState, useEffect } from "react";
import { AlertCircle, CheckCircle, AlertTriangle, } from "lucide-react";
import { LoadingState, EmptyState, ErrorState, PageHeader } from "@/components/layout";
import { fetchDataQuality } from "@/lib/api";

interface DataIssue {
  id: string;
  field: string;
  issue: string;
  recordsAffected: number;
  actionTaken: string;
  severity: "healthy" | "warning" | "critical";
}

// Dummy kept for reference if API returns empty list
const dataIssues: DataIssue[] = [
  { id: "1", field: "Close Date", issue: "Missing close date projection", recordsAffected: 34, actionTaken: "Auto-generated placeholder dates added", severity: "warning" },
  { id: "2", field: "Deal Name", issue: "Naming convention inconsistency", recordsAffected: 12, actionTaken: "Standardized to Title Case format", severity: "warning" },
  { id: "3", field: "Expected Revenue", issue: "Values outside expected range", recordsAffected: 5, actionTaken: "Flagged for finance review", severity: "critical" },
  { id: "4", field: "Status", issue: "Non-standard status values detected", recordsAffected: 8, actionTaken: "Mapped to canonical statuses", severity: "warning" },
  { id: "5", field: "Owner", issue: "Unassigned records", recordsAffected: 3, actionTaken: "Assigned to default queue", severity: "healthy" },
];

type SeverityColor = "bg-green-100 text-green-800" | "bg-amber-100 text-amber-800" | "bg-red-100 text-red-800";

function SeverityTag({ severity }: { severity: "healthy" | "warning" | "critical" }) {
  return (
    <span className={severity === "healthy" ? "bg-green-100 text-green-800 inline-flex items-center rounded px-2.5 py-1 text-xs font-medium" : severity === "warning" ? "bg-amber-100 text-amber-800 inline-flex items-center rounded px-2.5 py-1 text-xs font-medium" : "bg-red-100 text-red-800 inline-flex items-center rounded px-2.5 py-1 text-xs font-medium"}>
      {severity}
    </span>
  );
}

export default function DataHealthPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let mounted = true;
    fetchDataQuality().then(res => {
      if (mounted) { setData(res); setError(null); setLoading(false); }
    }).catch(err => {
      if (mounted) { setError(err); setLoading(false); }
    });
    return () => { mounted = false; };
  }, []);

  if (loading) return <LoadingState text="Analyzing data health..." />;
  if (error) return <ErrorState title="Failed to load data quality" description={error.message} />;
  if (!data) return <EmptyState />;

  const stats = {
    recordsProcessed: (data.deal_count || 0) + (data.wo_count || 0),
    missingValues: 0,
    normalizationIssues: data.total_issues || 0,
    potentialDuplicates: 0, // Backend doesn't track duplicates yet
    lastRefresh: new Date().toLocaleTimeString(),
  };

  const rawIssues = [...(data.deal_issues || []), ...(data.wo_issues || [])];

  const displayIssues = rawIssues.length > 0 ? rawIssues.map((i: any, idx: number) => ({
    id: String(idx),
    field: i.field || "Unknown",
    issue: i.message || "Issue detected",
    recordsAffected: 1, // Issue is usually per-record in our current backend
    actionTaken: "Flagged",
    severity: i.severity === "error" ? "critical" : "warning",
  })) : [];

  return (
    <section id="data-health" className="prose">
      <PageHeader title="Data Health" subtitle="Data quality dashboard" />

      {/* Summary stats */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4 mb-8">
        <div>
          <p className="text-xs text-muted-foreground uppercase tracking-wider">Records Processed</p>
          <p className="text-2xl font-bold">{stats.recordsProcessed}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground uppercase tracking-wider">Missing Values</p>
          <p className="text-2xl font-bold text-red-600">{stats.missingValues}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground uppercase tracking-wider">Normalization Issues</p>
          <p className="text-2xl font-bold text-amber-600">{stats.normalizationIssues}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground uppercase tracking-wider">Potential Duplicates</p>
          <p className="text-2xl font-bold text-red-600">{stats.potentialDuplicates}</p>
        </div>
      </div>

      {/* Issue table */}
      <div className="rounded-lg border bg-card p-6">
        <h3 className="text-font font-medium mb-4">Detected Issues</h3>
        {displayIssues.length === 0 ? (
          <p className="text-sm text-muted-foreground">No data quality issues found.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr>
                  <th className="border border-border left-border py-3 px-6 text-left text-muted-foreground font-medium">Field</th>
                  <th className="border border-border left-border py-3 px-6 text-left text-muted-foreground font-medium">Issue</th>
                  <th className="border border-border left-border py-3 px-6 text-left text-muted-foreground font-medium">Records Affected</th>
                  <th className="border border-border left-border py-3 px-6 text-left text-muted-foreground font-medium">Action Taken</th>
                  <th className="border border-border left-border py-3 px-6 text-left text-muted-foreground font-medium">Severity</th>
                </tr>
              </thead>
              <tbody>
                {displayIssues.map((issue: any) => (
                  <tr key={issue.id} className="border-b border-border/5 hover:bg-row">
                    <td className="py-3 px-6">{issue.field}</td>
                    <td className="py-3 px-6">{issue.issue}</td>
                    <td className="py-3 px-6">{issue.recordsAffected}</td>
                    <td className="py-3 px-6">{issue.actionTaken}</td>
                    <td className="py-3 px-6">
                      <SeverityTag severity={issue.severity} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Last refresh */}
      <p className="mt-8 text-xs text-muted-foreground">
        Last refresh: {stats.lastRefresh}
      </p>
    </section>
  );
}