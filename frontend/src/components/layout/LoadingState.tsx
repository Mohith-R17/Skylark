import React from "react";
import { Loader2 } from "lucide-react";

interface LoadingStateProps {
  text?: string;
  size?: "sm" | "md" | "lg";
}

export default function LoadingState({ text = "Loading data...", size = "md" }: LoadingStateProps) {
  const sizeMap = { sm: "w-4 h-4", md: "w-6 h-6", lg: "w-8 h-8" };

  return (
    <div className="flex min-h-[200px] items-center justify-center">
      <div className="flex flex-col items-center gap-3">
        <Loader2 className={`${sizeMap[size]} text-indigo-500 animate-spin`} />
        {text && <p className="text-sm text-slate-400">{text}</p>}
      </div>
    </div>
  );
}