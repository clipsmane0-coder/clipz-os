import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "../components/clipz/AppShell";
import { CalendarPage } from "../components/clipz/CalendarPage";

export const Route = createFileRoute("/calendar")({
  component: function CalendarRoute() {
    return (
      <AppShell title="Calendar" subtitle="Posting schedule and distribution calendar">
        <CalendarPage />
      </AppShell>
    );
  },
});
