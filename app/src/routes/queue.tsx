import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "../components/clipz/AppShell";
import { QueuePage } from "../components/clipz/QueuePage";

export const Route = createFileRoute("/queue")({
  component: function QueueRoute() {
    return (
      <AppShell title="Queue" subtitle="Render queue and job management">
        <QueuePage />
      </AppShell>
    );
  },
});
