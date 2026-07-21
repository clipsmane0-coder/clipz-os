import { createFileRoute } from "@tanstack/react-router";
import { AppShell } from "../components/clipz/AppShell";
import { LibraryPage } from "../features/library/LibraryPage";

export const Route = createFileRoute("/library")({
  component: function LibraryRoute() {
    return (
      <AppShell title="Library" subtitle="All generated clips and their performance">
        <LibraryPage />
      </AppShell>
    );
  },
});
