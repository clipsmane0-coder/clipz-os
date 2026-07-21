import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "../components/clipz/AppShell";
import { SourcesPage } from "../components/clipz/SourcesPage";

export const Route = createFileRoute("/sources")({
  component: function SourcesRoute() {
    return (
      <AppShell title="Sources" subtitle="Source video library and processing status">
        <SourcesPage />
      </AppShell>
    );
  },
});
