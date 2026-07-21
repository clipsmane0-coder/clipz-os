"use client";

import { useState, useEffect } from "react";
import { Sidebar } from "./Sidebar";
import {
  Bell,
  Search,
  Command,
  Menu,
  X,
} from "lucide-react";

interface AppShellProps {
  children: React.ReactNode;
  title: string;
  subtitle?: string;
  rightSlot?: React.ReactNode;
}

export function AppShell({ children, title, subtitle, rightSlot }: AppShellProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [time, setTime] = useState("");

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTime(
        now.toLocaleTimeString("en-US", {
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        })
      );
    };
    updateTime();
    const t = setInterval(updateTime, 1000);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="flex min-h-dvh bg-clipz-bg text-clipz-text">
      <div className="hidden lg:block">
        <div className="sticky top-0 h-dvh">
          <Sidebar />
        </div>
      </div>

      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={() => setMobileMenuOpen(false)}
          />
          <div className="absolute left-0 top-0 h-full">
            <Sidebar onNavigate={() => setMobileMenuOpen(false)} />
          </div>
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-40 flex h-14 items-center gap-3 border-b border-clipz-border-soft bg-clipz-panel/80 px-4 backdrop-blur-sm lg:px-6">
          <button
            className="lg:hidden -ml-1 p-1.5 text-clipz-text-muted hover:text-white"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X size={18} /> : <Menu size={18} />}
          </button>

          <div className="min-w-0">
            <h1 className="truncate text-[14px] font-semibold text-white">
              {title}
            </h1>
            {subtitle && (
              <p className="hidden text-[11px] text-clipz-text-dim md:block">
                {subtitle}
              </p>
            )}
          </div>

          <div className="hidden md:flex items-center ml-6 flex-1 max-w-md">
            <div className="relative w-full">
              <Search
                size={14}
                className="absolute left-2.5 top-1/2 -translate-y-1/2 text-clipz-text-dim"
              />
              <input
                type="text"
                placeholder="Search clips, sources, profiles..."
                className="w-full h-8 rounded-md border border-clipz-border bg-clipz-surface pl-8 pr-16 text-[12px] text-clipz-text placeholder:text-clipz-text-dim focus:outline-none focus:border-clipz-accent/50 focus:ring-1 focus:ring-clipz-accent/30 transition-colors"
              />
              <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-0.5 rounded bg-clipz-elevated px-1 py-0.5 text-[10px] text-clipz-text-dim">
                <Command size={10} />
                <span>K</span>
              </div>
            </div>
          </div>

          <div className="flex-1 md:hidden" />

          <div className="flex items-center gap-2">
            <div className="hidden md:flex items-center gap-1.5 rounded-md border border-clipz-border bg-clipz-surface px-2.5 py-1">
              <div className="h-1.5 w-1.5 rounded-full bg-clipz-green pulse-dot" />
              <span className="text-[11px] text-clipz-text-muted">GPU 67%</span>
            </div>

            <div className="hidden sm:flex items-center gap-1.5 text-[11px] text-clipz-text-dim font-mono">
              {time}
            </div>

            <button className="relative p-1.5 rounded-md hover:bg-clipz-surface text-clipz-text-muted hover:text-white transition-colors">
              <Bell size={16} />
              <span className="absolute top-1 right-1 h-1.5 w-1.5 rounded-full bg-clipz-red" />
            </button>

            {rightSlot}
          </div>
        </header>

        <main className="flex-1 overflow-x-hidden">
          {children}
        </main>
      </div>
    </div>
  );
}
