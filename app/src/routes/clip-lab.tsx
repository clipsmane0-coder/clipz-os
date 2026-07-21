import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "../components/clipz/AppShell";
import { ClipLabPage } from "../components/clipz/ClipLabPage";

export const Route = createFileRoute("/clip-lab")({
  component: function ClipLabRoute() {
    return (
      <AppShell title="Clip Lab" subtitle="Review and edit candidate clips">
        <ClipLabPage />
      </AppShell>
    );
  },
});
