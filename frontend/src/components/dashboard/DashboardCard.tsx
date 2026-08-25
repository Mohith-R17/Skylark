import React from "react";

function DashboardCard() {
  return (
    <div className="rounded-lg border bg-card p-6 shadow-sm">
      <h2 className="text-xl font-medium mb-4">Summary</h2>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-muted-foreground small">Total Items</p>
          <p className="text-2xl font-semibold">—</p>
        </div>
        <div>
          <p className="text-muted-foreground small">Active Items</p>
          <p className="text-2xl font-semibold">—</p>
        </div>
        <div>
          <p className="text-muted-foreground small">Monthly Growth</p>
          <p className="text-2xl font-semibold">—</p>
        </div>
        <div>
          <p className="text-muted-foreground small">Revenue</p>
          <p className="text-2xl font-semibold">—</p>
        </div>
      </div>
    </div>
  );
}

export default DashboardCard;