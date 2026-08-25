import React from "react";

function ChartsOverview() {
  return (
    <div className="rounded-lg border bg-card p-6 shadow-sm">
      <h2 className="text-xl font-medium mb-4">Key Metrics</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <ChartCard title="MRR" />
        <ChartCard title="ARR" />
        <ChartCard title="CAC" />
        <ChartCard title="LTV" />
      </div>
    </div>
  );
}

interface ChartCardProps {
  title: string;
}

function ChartCard({ title }: ChartCardProps) {
  return (
    <div className="p-4 borderrounded-lg bg-secondary/10 text-secondary">
      <p className="text-lg font-medium">{title}</p>
      <p className="text-3xl font-bold">—</p>
    </div>
  );
}

export default ChartsOverview;