import React from "react";
import { Sunrise, Moon, } from "lucide-react";

interface PageHeaderProps {
  title: string;
  subtitle: string;
  showTime?: boolean;
}

export function PageHeader({ title, subtitle, showTime = true }: PageHeaderProps) {
  const timeOfDay = showTime ? new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" }) : "";

  const period = timeOfDay.split(":")[0] < 12 ? "Good morning" : "Good afternoon";

  return (
    <header className="mb-8 border-b border-border bg-background">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center gap-3">
          <span className="text-2xl font-bold tracking-tight">{period}, Founder</span>
        </div>
        <h1 className="mt-3 text-3xl font-bold tracking-tight">{title}</h1>
        <p className="mt-2 text-muted-foreground subtitle">{subtitle}</p>
      </div>
    </header>
  );
}