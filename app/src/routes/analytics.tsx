import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "../components/clipz/AppShell";
import { AnalyticsPage } from "../features/analytics/AnalyticsPage";

export const Route = createFileRoute("/analytics")({
  component: function AnalyticsRoute() {
    return (
      <AppShell title="Analytics" subtitle="Performance metrics and insights">
        <AnalyticsPage />
      </AppShell>
    );
  },
});
