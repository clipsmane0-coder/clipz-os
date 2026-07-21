import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "../components/clipz/AppShell";
import { SourcesPage } from "../features/sources/SourcesPage";

export const Route = createFileRoute("/sources")({
  component: function SourcesRoute() {
    return (
      <AppShell title="Sources" subtitle="Source video library and processing status">
        <SourcesPage />
      </AppShell>
    );
  },
});
