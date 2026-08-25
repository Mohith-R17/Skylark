import React from "react";
import { AlertCircle, } from "lucide-react";

interface ErrorStateProps {
  title?: string;
  description?: string;
  error?: unknown;
  retryLabel?: string;
  onRetry?: () => void;
}

export default function ErrorState({
  title = "Something went wrong",
  description = "Please try again later.",
  error,
  retryLabel = "Retry",
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="text-center py-16 text-muted-foreground">
      <AlertCircle className="w-12 h-12 mx-auto text-red-500 mb-4" />
      <h3 className="text-font font-medium mb-2">{title}</h3>
      <p className="">{description}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 px-4 py-2 border rounded-lg border-primary text-primary hover:bg-primary/10 transition-colors text-sm"
        >
          {retryLabel}
        </button>
      )}
    </div>
  );
}