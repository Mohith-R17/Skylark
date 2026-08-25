import React, { useState } from "react";
import { MainLayout } from "@/components/layout";
import OverviewPage from "@/pages/OverviewPage";
import AskSkylarkPage from "@/pages/AskSkylarkPage";
import InsightsPage from "@/pages/InsightsPage";
import DataHealthPage from "@/pages/DataHealthPage";
import LeadershipUpdatePage from "@/pages/LeadershipUpdatePage";

function App() {
  const [activePage, setActivePage] = useState("overview");

  const renderPage = () => {
    switch (activePage) {
      case "overview":
        return <OverviewPage />;
      case "ask-skylark":
        return <AskSkylarkPage />;
      case "insights":
        return <InsightsPage />;
      case "data-health":
        return <DataHealthPage />;
      case "leadership-update":
        return <LeadershipUpdatePage />;
      default:
        return <OverviewPage />;
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <MainLayout showSidebar activePage={activePage} onNavigate={setActivePage}>
        {renderPage()}
      </MainLayout>
    </div>
  );
}

export default App;