import React from "react";

interface TableColumn {
  accessorKey: string;
  header: string;
}

interface RowData {
  [key: string]: string | number | Date | null | undefined;
}

function DataTable() {
  return (
    <div className="rounded-lg border bg-card p-6 shadow-sm">
      <h2 className="text-xl font-medium mb-4">Monday.com Items</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr>
              <th className="border border-border left-border py-3 px-6 text-left text-muted-foreground font-medium">Item</th>
              <th className="border border-border left-border py-3 px-6 text-left text-muted-foreground font-medium">Status</th>
              <th className="border border-border left-border py-3 px-6 text-left text-muted-foreground font-medium">Value</th>
              <th className="border border-border left-border py-3 px-6 text-left text-muted-foreground font-medium">Last Updated</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b border-border/5 hover:bg-row">
              <td className="py-3 px-6">Item 1</td>
              <td className="py-3 px-6"><span className="px-2 py-1 text-xs font-medium rounded bg-secondary/10 text-secondary">Active</span></td>
              <td className="py-3 px-6">$12,500</td>
              <td className="py-3 px-6">Mar 15, 2024</td>
            </tr>
            <tr className="border-b border-border/5">
              <td className="py-3 px-6">Item 2</td>
              <td className="py-3 px-6"><span className="px-2 py-1 text-xs font-medium rounded bg-secondary/10 text-secondary">Pending</span></td>
              <td className="py-3 px-6">$8,200</td>
              <td className="py-3 px-6">Mar 10, 2024</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default DataTable;