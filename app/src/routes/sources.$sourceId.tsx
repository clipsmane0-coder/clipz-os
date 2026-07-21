import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "../components/clipz/AppShell";
import { SourceDetail } from "../components/clipz/SourceDetail";

export const Route = createFileRoute("/sources/$sourceId")({
  component: function SourceDetailRoute() {
    const { sourceId } = Route.useParams();
    return (
      <AppShell title="Source" subtitle="Source video details">
        <SourceDetail sourceId={sourceId} />
      </AppShell>
    );
  },
});