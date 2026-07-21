"use client";

import { Link } from "@tanstack/react-router";
import {
  Gauge,
  Users,
  Video,
  Scissors,
  ListChecks,
  Library,
  Calendar,
  BarChart3,
  Settings,
  UploadCloud,
  Zap,
  ChevronRight,
} from "lucide-react";
import { profiles } from "../../lib/mock-data";

interface NavItem {
  to: string;
  label: string;
  icon: React.ReactNode;
  badge?: string | number;
}

const navSections: { title: string; items: NavItem[] }[] = [
  {
    title: "Workspace",
    items: [
      { to: "/dashboard", label: "Dashboard", icon: <Gauge size={18} /> },
      { to: "/profiles", label: "Profiles", icon: <Users size={18} />, badge: 6 },
      { to: "/sources", label: "Sources", icon: <Video size={18} />, badge: 10 },
      { to: "/clip-lab", label: "Clip Lab", icon: <Scissors size={18} />, badge: 32 },
      { to: "/queue", label: "Queue", icon: <ListChecks size={18} />, badge: 7 },
      { to: "/library", label: "Library", icon: <Library size={18} /> },
    ],
  },
  {
    title: "Distribution",
    items: [
      { to: "/calendar", label: "Calendar", icon: <Calendar size={18} />, badge: 28 },
      { to: "/analytics", label: "Analytics", icon: <BarChart3 size={18} /> },
    ],
  },
  {
    title: "System",
    items: [
      { to: "/settings", label: "Settings", icon: <Settings size={18} /> },
    ],
  },
];

export function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  const activeProfiles = profiles.filter((p) => p.status === "active");

  return (
    <aside className="flex h-full w-[240px] shrink-0 flex-col border-r border-clipz-border bg-clipz-panel">
      {/* Logo */}
      <div className="flex h-16 items-center gap-2.5 px-5 border-b border-clipz-border-soft">
        <div className="relative flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500 to-cyan-400 shadow-lg shadow-violet-500/20">
          <Zap size={16} className="text-white" />
        </div>
        <div>
          <div className="text-[15px] font-bold tracking-tight text-white">CLIPZ</div>
          <div className="text-[10px] text-clipz-text-dim tracking-wider uppercase">
            Clipping OS v1.0
          </div>
        </div>
      </div>

      {/* Scrollable nav */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        {navSections.map((section) => (
          <div key={section.title}>
            <div className="mb-2 px-2 text-[10px] font-semibold uppercase tracking-[0.14em] text-clipz-text-dim">
              {section.title}
            </div>
            <nav className="space-y-0.5">
              {section.items.map((item) => (
                <Link
                  key={item.to}
                  to={item.to}
                  onClick={onNavigate}
                  className="group flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-[13px] text-clipz-text-muted transition-all hover:bg-clipz-surface hover:text-white [&.active]:bg-clipz-accent/10 [&.active]:text-white [&.active]:font-medium [&.active]:shadow-[inset_0_0_0_1px_rgba(124,92,255,0.2)]"
                >
                  <span className="text-clipz-text-muted group-hover:text-white [.active_&]:text-clipz-accent-soft">
                    {item.icon}
                  </span>
                  <span className="flex-1 truncate">{item.label}</span>
                  {item.badge !== undefined && (
                    <span className="rounded-full bg-clipz-surface px-1.5 py-0.5 text-[10px] font-medium text-clipz-text-muted [.active_&]:bg-clipz-accent/20 [.active_&]:text-clipz-accent-soft">
                      {item.badge}
                    </span>
                  )}
                </Link>
              ))}
            </nav>
          </div>
        ))}

        {/* Active profiles quick list */}
        <div>
          <div className="mb-2 px-2 text-[10px] font-semibold uppercase tracking-[0.14em] text-clipz-text-dim">
            Active Profiles
          </div>
          <div className="space-y-0.5">
            {activeProfiles.slice(0, 4).map((p) => (
              <div
                key={p.id}
                className="flex items-center gap-2 rounded-lg px-2 py-1.5 hover:bg-clipz-surface cursor-pointer group"
              >
                <div className="relative h-5 w-5 shrink-0 rounded-full bg-clipz-elevated overflow-hidden">
                  <img
                    src={p.image}
                    alt=""
                    className="h-full w-full object-cover"
                  />
                  <div className="absolute -bottom-0.5 -right-0.5 h-2 w-2 rounded-full bg-clipz-green ring-2 ring-clipz-panel" />
                </div>
                <span className="flex-1 truncate text-[12px] text-clipz-text-muted group-hover:text-white">
                  {p.name}
                </span>
                <ChevronRight size={12} className="text-clipz-text-dim opacity-0 group-hover:opacity-100" />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom: upload + user */}
      <div className="border-t border-clipz-border-soft p-3 space-y-2">
        <button className="flex w-full items-center justify-center gap-2 rounded-lg bg-clipz-accent px-3 py-2 text-[12px] font-medium text-white transition-all hover:bg-clipz-accent/90 glow-accent">
          <UploadCloud size={14} />
          New Source
        </button>
        <div className="flex items-center gap-2.5 rounded-lg px-2 py-1.5 hover:bg-clipz-surface cursor-pointer">
          <div className="h-7 w-7 rounded-full bg-gradient-to-br from-violet-500 to-pink-500 shrink-0" />
          <div className="flex-1 min-w-0">
            <div className="text-[12px] font-medium text-white truncate">Operator</div>
            <div className="text-[10px] text-clipz-text-dim truncate">admin@clipz.io</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
