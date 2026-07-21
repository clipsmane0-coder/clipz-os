"use client";

import { useState, useEffect, useCallback } from "react";
import { Settings, Cpu, HardDrive, Video, Volume2, Shield, Palette, Bell, Key, Globe, HelpCircle, FolderOpen, CheckCircle2, AlertTriangle, RefreshCw } from "lucide-react";
import { useSystemSettings } from "../../lib/api/hooks";
import { apiConfig } from "../../lib/api/config";

interface SettingsSection {
  id: string;
  label: string;
  icon: React.ReactNode;
  description: string;
}

const sections: SettingsSection[] = [
  { id: "general", label: "General", icon: <Settings size={16} />, description: "System-wide preferences" },
  { id: "processing", label: "Processing", icon: <Cpu size={16} />, description: "Hardware and quality settings" },
  { id: "storage", label: "Storage", icon: <HardDrive size={16} />, description: "Paths, folders and limits" },
  { id: "video", label: "Video", icon: <Video size={16} />, description: "Default render and export settings" },
  { id: "audio", label: "Audio", icon: <Volume2 size={16} />, description: "Audio processing presets" },
  { id: "safety", label: "Safety", icon: <Shield size={16} />, description: "Content safety and rights" },
  { id: "branding", label: "Branding", icon: <Palette size={16} />, description: "Default brand presets" },
  { id: "platforms", label: "Platforms", icon: <Globe size={16} />, description: "Publishing platforms and APIs" },
  { id: "notifications", label: "Notifications", icon: <Bell size={16} />, description: "Alerts and notifications" },
  { id: "keys", label: "API Keys", icon: <Key size={16} />, description: "External service integrations" },
  { id: "about", label: "About", icon: <HelpCircle size={16} />, description: "Version info and support" },
];

function Toggle({ enabled, onChange, label, description }: { enabled: boolean; onChange: (v: boolean) => void; label: string; description?: string }) {
  return (
    <div className="flex items-center justify-between py-2.5">
      <div>
        <p className="text-[12px] font-medium text-white">{label}</p>
        {description && <p className="text-[11px] text-clipz-text-muted">{description}</p>}
      </div>
      <button
        onClick={() => onChange(!enabled)}
        className={`relative w-10 h-5.5 rounded-full transition-colors ${enabled ? "bg-clipz-accent" : "bg-clipz-border"}`}
        aria-label={label}
      >
        <div className={`absolute top-0.5 w-4.5 h-4.5 rounded-full bg-white shadow-md transition-transform ${enabled ? "translate-x-5" : "translate-x-0.5"}`} />
      </button>
    </div>
  );
}

export function SettingsPage() {
  const [activeSection, setActiveSection] = useState("general");
  const [dirty, setDirty] = useState(false);
  const [saveStatus, setSaveStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saveRequestId, setSaveRequestId] = useState<string | null>(null);

  // Load settings from API
  const { data: apiSettings, isLoading, error, refetch } = useSystemSettings();

  // Local form state
  const [settings, setSettings] = useState({
    autoStart: true,
    minimizeToTray: false,
    checkUpdates: true,
    hardwareAcceleration: true,
    gpuRendering: true,
    cpuThreads: 8,
    renderQuality: "balanced",
    audioNormalization: true,
    noiseReduction: false,
    safetyReview: true,
    notifications: true,
    soundEffects: true,
    theme: "dark",
    maxParallelJobs: 4,
    gpuEnabled: true,
    safetyThreshold: 0.5,
    duplicateThreshold: 0.7,
  });

  const [originalSettings, setOriginalSettings] = useState(settings);

  // Sync API settings to local state on load
  useEffect(() => {
    if (apiSettings) {
      const parsed: Record<string, any> = {};
      (apiSettings as any[]).forEach((s: any) => {
        let val: any = s.value;
        if (s.valueType === "boolean") val = s.value === "true";
        else if (s.valueType === "number") val = parseFloat(s.value);
        parsed[s.key] = val;
      });
      setSettings((prev) => ({ ...prev, ...parsed }));
      setOriginalSettings((prev) => ({ ...prev, ...parsed }));
      setDirty(false);
    }
  }, [apiSettings]);

  const updateSetting = useCallback((key: string, value: any) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
    setDirty(true);
    setSaveStatus("idle");
    setSaveError(null);
  }, []);

  const handleSave = async () => {
    setSaveStatus("saving");
    setSaveError(null);
    setSaveRequestId(null);

    try {
      const changedKeys = Object.keys(settings).filter((key) => {
        const orig = (originalSettings as any)[key];
        const curr = (settings as any)[key];
        return String(orig) !== String(curr);
      });

      for (const key of changedKeys) {
        const value = String((settings as any)[key]);
        if (apiConfig.isMock) {
          // Mock mode: simulate save by waiting
          await new Promise((r) => setTimeout(r, 300));
        } else {
          const resp = await fetch(`${apiConfig.baseUrl}/settings`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ key, value }),
          });
          const json = await resp.json();
          if (!resp.ok) throw json;
          if (json?.meta?.request_id) setSaveRequestId(json.meta.request_id);
        }
      }

      setOriginalSettings({ ...settings });
      setDirty(false);
      setSaveStatus("saved");
      refetch(); // Reload from API
      setTimeout(() => setSaveStatus("idle"), 3000);
    } catch (err: any) {
      setSaveStatus("error");
      setSaveError(err?.error?.message || err?.message || "Failed to save settings");
      setSaveRequestId(err?.meta?.request_id || null);
    }
  };

  const handleCancel = () => {
    setSettings({ ...originalSettings });
    setDirty(false);
    setSaveStatus("idle");
    setSaveError(null);
  };

  if (isLoading) {
    return (
      <div className="flex min-h-[calc(100dvh-3.5rem)]">
        <div className="hidden md:block w-[240px] shrink-0 border-r border-clipz-border bg-clipz-panel py-4 animate-pulse" />
        <div className="flex-1 p-4 lg:p-6">
          <div className="animate-pulse space-y-6">
            <div className="h-8 w-64 bg-clipz-surface rounded" />
            <div className="h-48 bg-clipz-panel rounded-xl border border-clipz-border" />
            <div className="h-48 bg-clipz-panel rounded-xl border border-clipz-border" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-[calc(100dvh-3.5rem)]">
        <div className="hidden md:block w-[240px] shrink-0 border-r border-clipz-border bg-clipz-panel py-4" />
        <div className="flex-1 p-4 lg:p-6">
          <div className="rounded-xl border border-rose-500/20 bg-rose-500/5 p-8 text-center max-w-lg mx-auto">
            <AlertTriangle size={40} className="mx-auto mb-3 text-rose-400" />
            <h3 className="text-[15px] font-semibold text-white mb-1">Failed to load settings</h3>
            <p className="text-[12px] text-clipz-text-muted mb-2">{(error as any)?.message || "Could not connect to settings API"}</p>
            <button onClick={() => refetch()} className="inline-flex items-center gap-2 rounded-lg bg-clipz-accent px-3.5 py-2 text-[12px] font-medium text-white hover:bg-clipz-accent/90 transition-colors">
              <RefreshCw size={14} /> Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-[calc(100dvh-3.5rem)]">
      <div className="hidden md:block w-[240px] shrink-0 border-r border-clipz-border bg-clipz-panel py-4">
        <div className="px-3 pb-3">
          <h3 className="text-[13px] font-semibold text-white mb-1">Settings</h3>
          <p className="text-[11px] text-clipz-text-muted mb-4">Configure your CLIPZ installation</p>
        </div>
        <nav className="px-2 space-y-0.5" aria-label="Settings sections">
          {sections.map((section) => (
            <button
              key={section.id}
              onClick={() => setActiveSection(section.id)}
              className={`w-full flex items-center gap-3 rounded-lg px-2.5 py-2 text-left transition-colors ${
                activeSection === section.id
                  ? "bg-clipz-accent/10 text-white font-medium"
                  : "text-clipz-text-muted hover:bg-clipz-surface hover:text-white"
              }`}
              aria-current={activeSection === section.id ? "true" : undefined}
            >
              <span className={activeSection === section.id ? "text-clipz-accent-soft" : ""}>{section.icon}</span>
              <span className="text-[12px]">{section.label}</span>
            </button>
          ))}
        </nav>
      </div>

      <div className="flex-1 p-4 lg:p-6 overflow-y-auto">
        <div className="max-w-2xl">
          {/* Save status bar */}
          {saveStatus === "saved" && (
            <div className="flex items-center gap-2 rounded-lg border border-emerald-500/20 bg-emerald-500/10 px-3 py-2 text-[12px] text-emerald-400 mb-4">
              <CheckCircle2 size={14} /> Settings saved successfully
            </div>
          )}
          {saveStatus === "error" && saveError && (
            <div className="rounded-lg border border-rose-500/20 bg-rose-500/10 px-3 py-2 text-[12px] text-rose-400 mb-4">
              <div className="flex items-center gap-2 mb-1"><AlertTriangle size={14} /> {saveError}</div>
              {saveRequestId && <div className="text-[11px] text-rose-400/70">Request ID: {saveRequestId}</div>}
            </div>
          )}
          {saveStatus === "saving" && (
            <div className="flex items-center gap-2 rounded-lg border border-clipz-accent/20 bg-clipz-accent/10 px-3 py-2 text-[12px] text-clipz-accent-soft mb-4">
              <RefreshCw size={14} className="animate-spin" /> Saving settings...
            </div>
          )}

          {activeSection === "general" && (
            <div className="space-y-6">
              <div>
                <h2 className="text-[16px] font-semibold text-white mb-1">General Settings</h2>
                <p className="text-[12px] text-clipz-text-muted">System-wide preferences and behavior</p>
              </div>

              <div className="rounded-xl border border-clipz-border bg-clipz-panel p-4 space-y-1">
                <Toggle enabled={settings.autoStart} onChange={(v) => updateSetting("autoStart", v)} label="Start on system boot" description="Launch CLIPZ automatically when your system starts" />
                <div className="border-t border-clipz-border-soft my-1" />
                <Toggle enabled={settings.minimizeToTray} onChange={(v) => updateSetting("minimizeToTray", v)} label="Minimize to system tray" description="Keep CLIPZ running in the background" />
                <div className="border-t border-clipz-border-soft my-1" />
                <Toggle enabled={settings.checkUpdates} onChange={(v) => updateSetting("checkUpdates", v)} label="Automatically check for updates" description="Get notified when new versions are available" />
              </div>

              <div className="rounded-xl border border-clipz-border bg-clipz-panel p-4">
                <h4 className="text-[13px] font-medium text-white mb-3">Appearance</h4>
                <div>
                  <label className="block text-[11px] text-clipz-text-muted mb-1.5">Theme</label>
                  <div className="flex gap-2">
                    {["dark", "light", "system"].map((theme) => (
                      <button
                        key={theme}
                        onClick={() => updateSetting("theme", theme)}
                        className={`px-3 py-1.5 rounded-md border text-[11px] font-medium capitalize ${
                          settings.theme === theme
                            ? "bg-clipz-accent/15 text-clipz-accent-soft border-clipz-accent/30"
                            : "bg-clipz-surface text-clipz-text-muted border-clipz-border hover:text-white"
                        }`}
                      >
                        {theme}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <div className="rounded-xl border border-clipz-border bg-clipz-panel p-4">
                <h4 className="text-[13px] font-medium text-white mb-3">Language</h4>
                <select
                  defaultValue="en"
                  className="w-full h-9 rounded-md border border-clipz-border bg-clipz-surface px-3 text-[12px] text-white focus:outline-none focus:border-clipz-accent/50"
                  aria-label="Language"
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                  <option value="ja">Japanese</option>
                </select>
              </div>
            </div>
          )}

          {activeSection === "processing" && (
            <div className="space-y-6">
              <div>
                <h2 className="text-[16px] font-semibold text-white mb-1">Processing</h2>
                <p className="text-[12px] text-clipz-text-muted">Hardware acceleration and quality settings</p>
              </div>

              <div className="rounded-xl border border-clipz-border bg-clipz-panel p-4 space-y-1">
                <Toggle enabled={settings.hardwareAcceleration} onChange={(v) => updateSetting("hardwareAcceleration", v)} label="Hardware acceleration" description="Use GPU for video processing when available" />
                <div className="border-t border-clipz-border-soft my-1" />
                <Toggle enabled={settings.gpuRendering} onChange={(v) => updateSetting("gpuRendering", v)} label="GPU rendering" description="Offload final rendering to GPU for faster exports" />
                <div className="border-t border-clipz-border-soft my-1" />
                <div className="py-2.5">
                  <div className="flex justify-between mb-1">
                    <p className="text-[12px] font-medium text-white">CPU Threads</p>
                    <p className="text-[12px] text-clipz-accent-soft font-mono">{settings.cpuThreads}</p>
                  </div>
                  <input
                    type="range"
                    min={4}
                    max={16}
                    value={settings.cpuThreads}
                    onChange={(e) => updateSetting("cpuThreads", parseInt(e.target.value))}
                    className="w-full clipz-range"
                    aria-label="CPU threads"
                  />
                  <p className="text-[10px] text-clipz-text-dim mt-1">CPU threads to use for processing tasks</p>
                </div>
              </div>

              <div className="rounded-xl border border-clipz-border bg-clipz-panel p-4">
                <h4 className="text-[13px] font-medium text-white mb-3">Default Quality</h4>
                <div className="flex gap-2">
                  {[{ id: "fast", label: "Fast" }, { id: "balanced", label: "Balanced" }, { id: "maximum", label: "Maximum" }].map((q) => (
                    <button
                      key={q.id}
                      onClick={() => updateSetting("renderQuality", q.id)}
                      className={`flex-1 py-2 rounded-md border text-[11px] font-medium ${
                        settings.renderQuality === q.id
                          ? "bg-clipz-accent/15 text-clipz-accent-soft border-clipz-accent/30"
                          : "bg-clipz-surface text-clipz-text-muted border-clipz-border hover:text-white"
                      }`}
                    >
                      {q.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeSection === "storage" && (
            <div className="space-y-6">
              <div>
                <h2 className="text-[16px] font-semibold text-white mb-1">Storage</h2>
                <p className="text-[12px] text-clipz-text-muted">Storage paths, limits and cleanup</p>
              </div>
              <div className="rounded-xl border border-clipz-border bg-clipz-panel p-4 space-y-3">
                {[{ label: "Inbox folder", path: "~/CLIPZ/INBOX" }, { label: "Output folder", path: "~/CLIPZ/OUTPUT" }, { label: "Temporary files", path: "~/CLIPZ/TEMP" }].map((f) => (
                  <div key={f.label}>
                    <label className="block text-[11px] text-clipz-text-muted mb-1">{f.label}</label>
                    <div className="flex gap-2">
                      <div className="flex-1 h-9 rounded-md border border-clipz-border bg-clipz-surface px-3 text-[12px] text-white flex items-center">
                        <FolderOpen size={14} className="text-clipz-text-dim mr-2" />
                        <span className="font-mono text-clipz-text-muted">{f.path}</span>
                      </div>
                      <button className="px-3 py-1.5 rounded-md border border-clipz-border bg-clipz-surface text-[11px] text-white hover:bg-clipz-elevated">Browse</button>
                    </div>
                  </div>
                ))}
              </div>
              <div className="rounded-xl border border-clipz-border bg-clipz-panel p-4 space-y-2">
                <h4 className="text-[13px] font-medium text-white">Storage Usage</h4>
                <div className="flex justify-between text-[11px]"><span className="text-clipz-text-muted">Total used</span><span className="text-white">342 GB / 1 TB</span></div>
                <div className="h-2 rounded-full progress-track"><div className="h-full rounded-full bg-clipz-accent" style={{ width: "34%" }} /></div>
              </div>
            </div>
          )}

          {!["general", "processing", "storage"].includes(activeSection) && (
            <div className="space-y-6">
              <div>
                <h2 className="text-[16px] font-semibold text-white capitalize mb-1">{activeSection}</h2>
                <p className="text-[12px] text-clipz-text-muted">{sections.find((s) => s.id === activeSection)?.description}</p>
              </div>
              <div className="rounded-xl border border-clipz-border bg-clipz-panel p-8 text-center">
                <Settings size={32} className="mx-auto mb-3 text-clipz-text-dim" />
                <p className="text-[13px] text-clipz-text-muted">{sections.find((s) => s.id === activeSection)?.label} settings will be available in an upcoming build.</p>
                <p className="text-[11px] text-clipz-text-dim mt-1">Full configuration options coming soon.</p>
              </div>
            </div>
          )}

          <div className="mt-8 flex justify-end gap-2">
            <button
              onClick={handleCancel}
              disabled={!dirty || saveStatus === "saving"}
              className="px-4 py-2 rounded-md border border-clipz-border bg-clipz-surface text-[12px] text-clipz-text-muted hover:text-white disabled:opacity-40 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={!dirty || saveStatus === "saving"}
              className="px-4 py-2 rounded-md bg-clipz-accent text-[12px] font-medium text-white hover:bg-clipz-accent/90 disabled:opacity-40 transition-colors"
            >
              {saveStatus === "saving" ? "Saving..." : "Save Changes"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}