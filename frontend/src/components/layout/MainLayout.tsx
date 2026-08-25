import React, { useState } from "react";
import Sidebar from "./Sidebar";

interface MainLayoutProps {
  children: React.ReactNode;
  showSidebar?: boolean;
  activePage?: string;
  onNavigate?: (page: string) => void;
}

export function MainLayout({ children, showSidebar = true, activePage, onNavigate }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-background text-foreground overflow-x-hidden">
      {showSidebar && (
        <Sidebar activePage={activePage} onNavigate={onNavigate} />
      )}

      <main className="flex-1 p-6 md:ml-64 transition-all">
        <div className="max-w-7xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
}