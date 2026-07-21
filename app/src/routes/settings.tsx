import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "../components/clipz/AppShell";
import { SettingsPage } from "../components/clipz/SettingsPage";

export const Route = createFileRoute("/settings")({
  component: function SettingsRoute() {
    return (
      <AppShell title="Settings" subtitle="Configure your CLIPZ installation">
        <SettingsPage />
      </AppShell>
    );
  },
});
