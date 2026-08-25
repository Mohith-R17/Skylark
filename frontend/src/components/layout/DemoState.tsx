import React from "react";
import { Loader2, AlertCircle, CheckCircle, } from "lucide-react";

interface DemoStateProps {
  hasData?: boolean;
  loading?: boolean;
  title?: string;
  description?: string;
}

export function DemoState({ hasData = true, loading = false, title, description }: DemoStateProps) {
  if (loading) {
    return (
      <div className="py-8 text-center">
        <Loader2 className="w-6 h-6 mx-auto text-muted-foreground/50 mb-3" />
        <p className="text-sm text-muted-foreground">{title || "Loading data..."}</p>
      </div>
    );
  }

  if (!hasData) {
    return (
      <div className="py-8 text-center text-muted-foreground">
        <CheckCircle className="w-12 h-12 mx-auto mb-4 text-muted-foreground/30" />
        <p>{title || "No demo data available"}</p>
        <p className="mt-2">{description || ""}</p>
      </div>
    );
  }

  return (
    <div className="py-8 border-t border-border/10 pt-8">
      <div className="max-w-2xl mx-auto text-center">
        <h3 className="text-font font-medium mb-2">{title || "Demo Mode"}</h3>
        <p className="">{description || "Using demo/mock data for development"}</p>
      </div>
    </div>
  );
}