"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Sidebar } from "./Sidebar";
import { ErrorBoundary } from "./ErrorBoundary";
import { Bell, Search, Command, Menu, X, CheckCircle2, AlertTriangle, Info, ArrowRight, LogOut, User } from "lucide-react";
import { useNotifications, useHealth, useProfiles } from "../../lib/api/hooks";
import { Link, useNavigate, useRouter } from "@tanstack/react-router";
import { useAuth } from "../../lib/auth/auth-context";
import type { FNotification } from "../../lib/api/mapper";

interface AppShellProps {
  children: React.ReactNode;
  title: string;
  subtitle?: string;
  rightSlot?: React.ReactNode;
}

const TYPE_ICONS: Record<string, React.ReactNode> = {
  success: <CheckCircle2 size={14} className="text-emerald-400" />,
  warning: <AlertTriangle size={14} className="text-amber-400" />,
  error: <AlertTriangle size={14} className="text-rose-400" />,
  action_required: <Info size={14} className="text-clipz-accent-soft" />,
  informational: <Info size={14} className="text-cyan-400" />,
};

export function AppShell({ children, title, subtitle, rightSlot }: AppShellProps) {
  const { isAuthenticated, isLoading, user, signOut } = useAuth();
  const router = useRouter();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [time, setTime] = useState("");
  const [notifOpen, setNotifOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);

  // Redirect to sign-in if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.navigate({ to: "/signin" });
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-q-background-primary">
        <div className="text-q-text-secondary text-sm">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }
  const [searchQuery, setSearchQuery] = useState("");
  const [profileSelectorOpen, setProfileSelectorOpen] = useState(false);
  const notifRef = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const { data: notifData, isLoading: notifLoading } = useNotifications({ unreadOnly: true });
  const allNotifs = useNotifications({ pageSize: 20 });
  const { data: healthData } = useHealth();
  const { data: profilesData } = useProfiles({ pageSize: 50 });

  const unreadCount = notifData?.total || 0;
  const notifications = notifData?.data || [];
  const allNotifications = allNotifs.data?.data || [];
  const profiles = profilesData?.data || [];

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl + K = open search
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setSearchOpen((prev) => !prev);
        if (!searchOpen) setTimeout(() => searchRef.current?.focus(), 100);
      }
      // Escape = close everything
      if (e.key === "Escape") {
        setSearchOpen(false);
        setNotifOpen(false);
        setProfileSelectorOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [searchOpen]);

  // Click outside handlers
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) {
        setNotifOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTime(now.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false }));
    };
    updateTime();
    const t = setInterval(updateTime, 1000);
    return () => clearInterval(t);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    const q = searchQuery.toLowerCase();
    // Route to the most likely match
    if (profiles.some((p: any) => p.name?.toLowerCase().includes(q))) {
      navigate({ to: "/profiles" });
    } else {
      navigate({ to: "/sources" });
    }
    setSearchOpen(false);
    setSearchQuery("");
  };

  const healthOk = healthData?.api && healthData?.database && healthData?.worker;
  const allHealthy = healthData && Object.values(healthData).filter((v) => typeof v === "boolean").every(Boolean);

  return (
    <div className="flex min-h-dvh bg-clipz-bg text-clipz-text">
      {/* Sidebar - desktop */}
      <div className="hidden lg:block">
        <div className="sticky top-0 h-dvh">
          <Sidebar />
        </div>
      </div>

      {/* Mobile menu drawer */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setMobileMenuOpen(false)} />
          <div className="absolute left-0 top-0 h-full">
            <Sidebar onNavigate={() => setMobileMenuOpen(false)} />
          </div>
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        {/* Top bar */}
        <header className="sticky top-0 z-40 flex h-14 items-center gap-3 border-b border-clipz-border-soft bg-clipz-panel/80 px-4 backdrop-blur-sm lg:px-6">
          {/* Mobile hamburger */}
          <button
            className="lg:hidden -ml-1 p-1.5 text-clipz-text-muted hover:text-white transition-colors"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
            aria-expanded={mobileMenuOpen}
          >
            {mobileMenuOpen ? <X size={18} /> : <Menu size={18} />}
          </button>

          {/* Page title */}
          <div className="min-w-0">
            <h1 className="truncate text-[14px] font-semibold text-white">{title}</h1>
            {subtitle && <p className="hidden text-[11px] text-clipz-text-dim md:block">{subtitle}</p>}
          </div>

          {/* Search trigger */}
          <div className="hidden md:flex items-center ml-6 flex-1 max-w-md">
            <button
              onClick={() => { setSearchOpen(!searchOpen); if (!searchOpen) setTimeout(() => searchRef.current?.focus(), 100); }}
              className="w-full flex items-center h-8 rounded-md border border-clipz-border bg-clipz-surface px-3 text-[12px] text-clipz-text-dim hover:text-clipz-text-muted hover:border-clipz-accent/30 transition-colors text-left"
              aria-label="Open search"
            >
              <Search size={14} className="mr-2 shrink-0" />
              <span className="flex-1">Search clips, sources, profiles...</span>
              <div className="flex items-center gap-0.5 rounded bg-clipz-elevated px-1 py-0.5 text-[10px] text-clipz-text-dim">
                <Command size={10} />K
              </div>
            </button>
          </div>

          <div className="flex-1 md:hidden" />

          {/* Right-side controls */}
          <div className="flex items-center gap-2">
            {/* System health */}
            <div
              className="hidden md:flex items-center gap-1.5 rounded-md border border-clipz-border bg-clipz-surface px-2.5 py-1"
              title={`System: ${allHealthy ? "All systems operational" : "Some services degraded"}`}
            >
              <div className={`h-1.5 w-1.5 rounded-full ${healthOk ? "bg-emerald-400 pulse-dot" : "bg-amber-400"}`} />
              <span className="text-[11px] text-clipz-text-muted">{healthOk ? "Healthy" : "Degraded"}</span>
            </div>

            {/* Time */}
            <div className="hidden sm:flex items-center gap-1.5 text-[11px] text-clipz-text-dim font-mono">{time}</div>

            {/* Profile selector */}
            <div className="relative">
              <button
                onClick={() => setProfileSelectorOpen(!profileSelectorOpen)}
                className="p-1.5 rounded-md hover:bg-clipz-surface text-clipz-text-muted hover:text-white transition-colors"
                aria-label="Select profile"
                aria-expanded={profileSelectorOpen}
              >
                <div className="h-6 w-6 rounded-full bg-gradient-to-br from-violet-500 to-pink-500" />
              </button>
              {profileSelectorOpen && (
                <div className="absolute right-0 top-full mt-2 w-56 rounded-xl border border-clipz-border bg-clipz-panel shadow-xl shadow-black/30 overflow-hidden z-50">
                  <div className="p-3 border-b border-clipz-border-soft">
                    <p className="text-[11px] font-semibold text-white">Active Profiles</p>
                  </div>
                  <div className="max-h-64 overflow-y-auto">
                    {profiles.filter((p: any) => p.status === "active").map((p: any) => (
                      <Link
                        key={p.id}
                        to="/profiles/$profileId"
                        params={{ profileId: p.id }}
                        onClick={() => setProfileSelectorOpen(false)}
                        className="flex items-center gap-2.5 px-3 py-2 hover:bg-clipz-surface transition-colors"
                      >
                        <div className="h-6 w-6 shrink-0 rounded-full bg-clipz-elevated overflow-hidden">
                          <img src={p.avatarPath || ""} alt="" className="h-full w-full object-cover" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-[12px] text-white truncate">{p.name}</p>
                          <p className="text-[9px] text-clipz-text-dim capitalize">{p.profileType}</p>
                        </div>
                      </Link>
                    ))}
                  </div>
                  <Link
                    to="/profiles"
                    onClick={() => setProfileSelectorOpen(false)}
                    className="flex items-center justify-center gap-1 border-t border-clipz-border-soft px-3 py-2 text-[11px] text-clipz-accent-soft hover:bg-clipz-surface transition-colors"
                  >
                    Manage profiles <ArrowRight size={12} />
                  </Link>
                  <div className="border-t border-clipz-border-soft px-3 py-2">
                    <p className="text-[9px] text-clipz-text-dim mb-1">{user?.display_name || user?.email}</p>
                    <button
                      onClick={() => { signOut(); setProfileSelectorOpen(false); }}
                      className="flex items-center gap-1.5 text-[11px] text-clipz-text-dim hover:text-rose-400 transition-colors w-full"
                    >
                      <LogOut size={12} /> Sign out
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Notifications */}
            <div className="relative" ref={notifRef}>
              <button
                onClick={() => setNotifOpen(!notifOpen)}
                className="relative p-1.5 rounded-md hover:bg-clipz-surface text-clipz-text-muted hover:text-white transition-colors"
                aria-label={`Notifications${unreadCount > 0 ? ` (${unreadCount} unread)` : ""}`}
                aria-expanded={notifOpen}
              >
                <Bell size={16} />
                {unreadCount > 0 && (
                  <span className="absolute -top-0.5 -right-0.5 h-4 min-w-[14px] flex items-center justify-center rounded-full bg-clipz-red text-[9px] font-bold text-white px-1">
                    {unreadCount > 9 ? "9+" : unreadCount}
                  </span>
                )}
              </button>

              {notifOpen && (
                <div className="absolute right-0 top-full mt-2 w-80 rounded-xl border border-clipz-border bg-clipz-panel shadow-xl shadow-black/30 overflow-hidden z-50">
                  <div className="flex items-center justify-between p-3 border-b border-clipz-border-soft">
                    <p className="text-[12px] font-semibold text-white">Notifications</p>
                    {unreadCount > 0 && <span className="text-[10px] text-clipz-accent-soft">{unreadCount} new</span>}
                  </div>
                  <div className="max-h-80 overflow-y-auto divide-y divide-clipz-border-soft">
                    {allNotifications.length > 0 ? allNotifications.slice(0, 8).map((n: any) => (
                      <div key={n.id} className={`flex items-start gap-2.5 px-3 py-2.5 hover:bg-clipz-surface/30 transition-colors ${!n.isRead ? "bg-clipz-accent/5" : ""}`}>
                        <div className="mt-0.5 shrink-0">{TYPE_ICONS[n.type] || <Info size={14} className="text-clipz-text-dim" />}</div>
                        <div className="flex-1 min-w-0">
                          <p className="text-[11px] font-medium text-white">{n.title}</p>
                          <p className="text-[10px] text-clipz-text-muted line-clamp-2">{n.message}</p>
                          <p className="text-[9px] text-clipz-text-dim mt-0.5">{new Date(n.createdAt).toLocaleDateString()}</p>
                        </div>
                      </div>
                    )) : (
                      <div className="p-6 text-center">
                        <CheckCircle2 size={24} className="mx-auto mb-2 text-emerald-400/50" />
                        <p className="text-[12px] text-clipz-text-dim">All clear!</p>
                        <p className="text-[10px] text-clipz-text-muted/50">No new notifications</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {rightSlot}
          </div>
        </header>

        {/* Global search overlay */}
        {searchOpen && (
          <div className="fixed inset-0 z-50 flex items-start justify-center pt-[10vh] bg-black/50 backdrop-blur-sm" onClick={() => setSearchOpen(false)}>
            <div className="w-full max-w-xl rounded-xl border border-clipz-border bg-clipz-panel shadow-2xl overflow-hidden" onClick={(e) => e.stopPropagation()}>
              <form onSubmit={handleSearch} className="flex items-center gap-2 border-b border-clipz-border-soft px-4 py-3">
                <Search size={16} className="text-clipz-text-dim shrink-0" />
                <input
                  ref={searchRef}
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search clips, sources, profiles... (press Enter to navigate)"
                  className="flex-1 bg-transparent text-[14px] text-white placeholder:text-clipz-text-dim focus:outline-none"
                  autoFocus
                  aria-label="Global search"
                />
                <div className="flex items-center gap-1 rounded bg-clipz-elevated px-1.5 py-0.5 text-[10px] text-clipz-text-dim">
                  <Command size={10} />K
                </div>
              </form>
              <div className="p-2 max-h-64 overflow-y-auto">
                {searchQuery.trim() && (
                  <div className="space-y-0.5">
                    <p className="px-2 py-1 text-[10px] text-clipz-text-dim uppercase tracking-wider">Quick actions</p>
                    {profiles.filter((p: any) => p.name?.toLowerCase().includes(searchQuery.toLowerCase())).slice(0, 3).map((p: any) => (
                      <Link
                        key={p.id}
                        to="/profiles/$profileId"
                        params={{ profileId: p.id }}
                        onClick={() => { setSearchOpen(false); setSearchQuery(""); }}
                        className="flex items-center gap-2.5 rounded-lg px-2.5 py-2 hover:bg-clipz-surface transition-colors"
                      >
                        <div className="h-6 w-6 rounded-full bg-clipz-elevated overflow-hidden">
                          <img src={p.avatarPath || ""} alt="" className="h-full w-full object-cover" />
                        </div>
                        <span className="text-[12px] text-white">{p.name}</span>
                        <span className="ml-auto text-[10px] text-clipz-text-dim">Profile</span>
                      </Link>
                    ))}
                  </div>
                )}
                {!searchQuery.trim() && (
                  <p className="p-4 text-center text-[12px] text-clipz-text-dim">Type to search profiles, sources, and clips...</p>
                )}
              </div>
            </div>
          </div>
        )}

        <main className="flex-1 overflow-x-hidden">
          <ErrorBoundary>{children}</ErrorBoundary>
        </main>
      </div>
    </div>
  );
}