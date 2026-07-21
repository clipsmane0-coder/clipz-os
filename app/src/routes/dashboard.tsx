import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "../components/clipz/AppShell";
import { DashboardPage } from "../components/clipz/DashboardPage";

export const Route = createFileRoute("/dashboard")({
  component: function DashboardRoute() {
    return (
      <AppShell title="Dashboard" subtitle="Overview of your clipping operation">
        <DashboardPage />
      </AppShell>
    );
  },
});
