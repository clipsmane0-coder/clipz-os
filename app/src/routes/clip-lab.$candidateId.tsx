import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "../components/clipz/AppShell";
import { ClipLabPage } from "../components/clipz/ClipLabPage";

export const Route = createFileRoute("/clip-lab/$candidateId")({
  component: function ClipLabCandidateRoute() {
    const { candidateId } = Route.useParams();
    return (
      <AppShell title="Clip Lab" subtitle="Review candidate clip">
        <ClipLabPage preselectedId={candidateId} />
      </AppShell>
    );
  },
});