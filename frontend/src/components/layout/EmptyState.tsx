import React from "react";
import { Search } from "lucide-react";

interface EmptyStateProps {
  icon?: React.ElementType;
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}

export default function EmptyState({
  icon: Icon = Search,
  title = "No data yet",
  description = "There's nothing here right now.",
  actionLabel = "Add Item",
  onAction,
}: EmptyStateProps) {
  return (
    <div className="text-center py-16 text-slate-400">
      <Icon className="w-12 h-12 mx-auto text-slate-500/50 mb-4" />
      <h3 className="text-base font-medium mb-2 text-slate-300">{title}</h3>
      <p className="text-sm">{description}</p>
      {onAction && (
        <button
          onClick={onAction}
          className="mt-4 px-4 py-2 border rounded-lg border-indigo-500 text-indigo-400 hover:bg-indigo-500/10 transition-colors text-sm"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}