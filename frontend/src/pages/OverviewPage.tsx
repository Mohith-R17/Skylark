import React from "react";
import { LineChart, Line, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";
import { TrendingUp, Eye, } from "lucide-react";
import { KPI, LoadingState, EmptyState, ErrorState } from "@/components/layout";
import { PageHeader } from "@/components/layout/PageHeader";
import { useDashboardData } from "@/hooks/useDashboardData";
import { formatCurrency, formatNumber } from "@/lib/utils";

interface KPIProps {
  label: string;
  value: string | number;
  change?: number;
  direction?: "up" | "down" | "neutral";
  description: string;
  icon?: React.ElementType;
}

function KPIItem({ label, value, change, direction, description, icon = Eye }: KPIProps) {
  const changeClass = direction === "up" ? "text-green-600" : direction === "down" ? "text-red-600" : "text-muted-foreground";
  const arrow = direction === "up" ? "▲" : direction === "down" ? "▼" : "";

  return (
    <div className="rounded-lg border bg-card p-6 hover:transition-shadow hover:shadow-sm duration-200">
      <p className="text-xs text-muted-foreground uppercase tracking-wider">{label}</p>
      <div className="flex items-baseline gap-2">
        <p className="text-2xl font-bold">{typeof value === "number" ? `$${value}` : value}</p>
        <p className="text-sm font-medium {changeClass}">
          {arrow} {typeof change === "number" ? `${change > 0 ? "+" : ""}${change}%` : change}
        </p>
      </div>
      <p className="mt-2 text-sm text-muted-foreground">{description}</p>
    </div>
  );
}

// Real data mapped below

export default function OverviewPage() {
  const { data, loading, error } = useDashboardData();

  if (loading) return <LoadingState text="Loading overview metrics..." />;
  if (error) return <ErrorState title="Failed to load data" description={error.message} />;
  if (!data) return <EmptyState />;

  const pipelineValue = data.pipeline?.total_pipeline_value?.value || 0;
  const revenueValue = data.revenue?.total_wo_value?.value || 0;
  const activeWOs = data.operations?.active_work_orders?.value || 0;
  
  // Try to find an overall win rate or just show placeholder if backend doesn't provide yet
  const winRate = data.pipeline?.win_rate?.value || 0;

  const sectors = data.pipeline?.pipeline_by_sector?.items || [];
  const pipelineTrend = data.pipeline?.pipeline_trend?.items || [];
  
  const formattedTrend = pipelineTrend.map((item: any) => ({
    name: item.key === "__missing__" ? "Unknown" : item.key,
    pipeline: item.value
  }));

  return (
    <section id="overview" className="prose">
      <PageHeader
        title="SKYLARK"
        subtitle="Founder Intelligence"
      />

      {/* Executive Snapshot */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
        <KPIItem
          label="Pipeline"
          value={formatCurrency(pipelineValue)}
          description={data.pipeline?.total_pipeline_value?.caveat || "Total value"}
        />
        <KPIItem
          label="Revenue"
          value={formatCurrency(revenueValue)}
          description={data.revenue?.total_work_order_value?.caveat || "Total WO value"}
        />
        <KPIItem
          label="Active Work Orders"
          value={formatNumber(activeWOs)}
          description={data.operations?.active_work_orders?.caveat || "Currently active"}
        />
        <KPIItem
          label="Missing Close Dates"
          value={formatNumber(data.pipeline?.deals_missing_close_dates?.value || 0)}
          description="Deals requiring attention"
          direction="down"
        />
      </div>

      {/* Pipeline Trend */}
      <div className="rounded-lg border bg-card p-6 mb-8">
        <h2 className="text-font font-medium mb-4">Pipeline Trend</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={formattedTrend}>
            <XAxis dataKey="name" stroke="#8884d8" label={{ value: "Month", fontSize: 12, position: "insideBottomRight", offset: -5 }} />
            <YAxis stroke="#8884d8" label={{ value: "$", fontSize: 12, position: "insideLeft", offset: 15 }} tickFormatter={(value) => value >= 1000000 ? `$${(value/1000000).toFixed(0)}M` : `$${(value/1000).toFixed(0)}k`} />
            <Tooltip formatter={(value: number) => formatCurrency(value)} />
            <CartesianGrid strokeDasharray="3 3" />
            <Area type="monotone" dataKey="pipeline" name="Pipeline Generated" stroke="#00d4aa" fill="#00d4aa20" />
            <Legend verticalAlign="bottom" height={36} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Sector Performance */}
      <div className="rounded-lg border bg-card p-6 mb-8">
        <h2 className="text-font font-medium mb-4">Sector Performance</h2>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {sectors.map((sector: any) => (
            <div key={sector.key} className="p-4 rounded-lg bg-secondary/10 text-secondary">
              <p className="text-xs text-muted-foreground uppercase tracking-wider">{sector.key === "__missing__" ? "Unclassified" : sector.key}</p>
              <p className="text-xl font-medium">{formatCurrency(sector.value)} pipeline</p>
              <p className="text-sm text-muted-foreground">{sector.percentage || sector.pct}% of total</p>
            </div>
          ))}
          {sectors.length === 0 && (
            <p className="text-muted-foreground text-sm col-span-full">No sector data available.</p>
          )}
        </div>
      </div>

      {/* Pipeline Health */}
      {/* Pipeline Health */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        <div className="rounded-lg border bg-card p-6">
          <p className="text-xs text-muted-foreground uppercase tracking-wider">Open Opportunities</p>
          <p className="text-2xl font-semibold">{data.pipeline?.open_deals || 0}</p>
          <p className="text-sm text-muted-foreground">Total open deals</p>
        </div>
        <div className="rounded-lg border bg-card p-6">
          <p className="text-xs text-muted-foreground uppercase tracking-wider">Total Deals</p>
          <p className="text-2xl font-semibold">{data.pipeline?.total_deals || 0}</p>
          <p className="text-sm text-muted-foreground">Historical + Open</p>
        </div>
        <div className="rounded-lg border bg-card p-6">
          <p className="text-xs text-muted-foreground uppercase tracking-wider">Missing Close Dates</p>
          <p className="text-2xl font-semibold">{data.pipeline?.deals_missing_close_dates?.value || 0}</p>
          <p className="text-sm text-amber-600">⚠️ {data.pipeline?.deals_missing_close_dates?.caveat || "Review"}</p>
        </div>
        <div className="rounded-lg border bg-card p-6">
          <p className="text-xs text-muted-foreground uppercase tracking-wider">Missing Probability</p>
          <p className="text-2xl font-semibold">{data.pipeline?.deals_missing_probability?.value || 0}</p>
          <p className="text-sm text-amber-600">⚠️ {data.pipeline?.deals_missing_probability?.caveat || "Review"}</p>
        </div>
      </div>

    </section>
  );
}