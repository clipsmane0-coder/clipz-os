import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "../components/clipz/AppShell";
import { ProfilesPage } from "../components/clipz/ProfilesPage";

export const Route = createFileRoute("/profiles")({
  component: function ProfilesRoute() {
    return (
      <AppShell title="Profiles" subtitle="Manage creator profiles and clip preferences">
        <ProfilesPage />
      </AppShell>
    );
  },
});
