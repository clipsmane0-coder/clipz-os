import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "../components/clipz/AppShell";
import { ProfileDetail } from "../components/clipz/ProfileDetail";

export const Route = createFileRoute("/profiles/$profileId")({
  component: function ProfileDetailRoute() {
    const { profileId } = Route.useParams();
    return (
      <AppShell title="Profile" subtitle="Profile details and configuration">
        <ProfileDetail profileId={profileId} />
      </AppShell>
    );
  },
});