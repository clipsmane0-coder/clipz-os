"use client";

import { useState, useRef } from "react";
import { Upload, Link, X, FileVideo, CheckCircle2, AlertTriangle, Loader2, RefreshCw } from "lucide-react";
import { uploadSource, registerSourceUrl } from "../../lib/api/client";
import { useProfiles, useSourceList } from "../../lib/api/hooks";

interface UploadDialogProps {
  open: boolean;
  onClose: () => void;
}

export function UploadDialog({ open, onClose }: UploadDialogProps) {
  const [tab, setTab] = useState<"upload" | "url">("upload");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [url, setUrl] = useState("");
  const [title, setTitle] = useState("");
  const [profileId, setProfileId] = useState("");
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const { data: profilesData } = useProfiles({ pageSize: 50 });
  const sourcesQ = useSourceList({ pageSize: 50 });
  const profiles = profilesData?.data || [];

  if (!open) return null;

  const reset = () => {
    setSelectedFile(null);
    setUrl("");
    setTitle("");
    setProfileId("");
    setUploading(false);
    setProgress(0);
    setResult(null);
    setError(null);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) setSelectedFile(file);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!profileId || !selectedFile) return;
    setUploading(true);
    setProgress(10);
    setError(null);
    setResult(null);
    try {
      const resp = await uploadSource(profileId, selectedFile, title || undefined);
      setProgress(100);
      setResult(resp.data || resp);
      sourcesQ.refetch();
    } catch (err: any) {
      setError(err?.error?.message || err?.message || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleRegisterUrl = async () => {
    if (!profileId || !url.trim()) return;
    setUploading(true);
    setError(null);
    setResult(null);
    try {
      const resp = await registerSourceUrl(profileId, url.trim(), title || undefined);
      setResult(resp.data || resp);
      sourcesQ.refetch();
    } catch (err: any) {
      setError(err?.error?.message || err?.message || "Registration failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="w-full max-w-lg rounded-xl border border-clipz-border bg-clipz-panel shadow-2xl overflow-hidden" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between p-4 border-b border-clipz-border-soft">
          <h3 className="text-[15px] font-semibold text-white">Add Source</h3>
          <button onClick={() => { reset(); onClose(); }} className="p-1 text-clipz-text-muted hover:text-white"><X size={16} /></button>
        </div>

        <div className="flex border-b border-clipz-border-soft">
          <button onClick={() => setTab("upload")} className={`flex-1 py-2.5 text-[12px] font-medium text-center transition-colors ${tab === "upload" ? "bg-clipz-accent/10 text-clipz-accent-soft border-b-2 border-clipz-accent" : "text-clipz-text-muted hover:text-white"}`}>
            <Upload size={14} className="inline mr-1.5" /> Upload File
          </button>
          <button onClick={() => setTab("url")} className={`flex-1 py-2.5 text-[12px] font-medium text-center transition-colors ${tab === "url" ? "bg-clipz-accent/10 text-clipz-accent-soft border-b-2 border-clipz-accent" : "text-clipz-text-muted hover:text-white"}`}>
            <Link size={14} className="inline mr-1.5" /> Register URL
          </button>
        </div>

        <div className="p-4 space-y-4">
          {/* Profile selector */}
          <div>
            <label className="block text-[11px] text-clipz-text-muted mb-1">Profile *</label>
            <select
              value={profileId}
              onChange={(e) => setProfileId(e.target.value)}
              className="w-full h-9 rounded-md border border-clipz-border bg-clipz-surface px-3 text-[12px] text-white focus:outline-none focus:border-clipz-accent/50"
            >
              <option value="">Select a profile...</option>
              {profiles.map((p: any) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>

          {tab === "upload" && (
            <>
              <div
                onDrop={handleDrop}
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${dragOver ? "border-clipz-accent bg-clipz-accent/5" : "border-clipz-border hover:border-clipz-accent/40 hover:bg-clipz-surface/30"}`}
                onClick={() => fileRef.current?.click()}
              >
                <input ref={fileRef} type="file" accept=".mp4,.mov,.avi,.mkv,.webm,.flv,.wmv,.m4v,.mpg,.mpeg" onChange={handleFileSelect} className="hidden" />
                {selectedFile ? (
                  <div className="flex items-center gap-3">
                    <FileVideo size={24} className="text-clipz-accent-soft" />
                    <div className="text-left flex-1 min-w-0">
                      <p className="text-[12px] text-white truncate">{selectedFile.name}</p>
                      <p className="text-[10px] text-clipz-text-dim">{(selectedFile.size / (1024 * 1024)).toFixed(1)} MB</p>
                    </div>
                    <button onClick={(e) => { e.stopPropagation(); setSelectedFile(null); }} className="p-1 text-clipz-text-muted hover:text-white"><X size={14} /></button>
                  </div>
                ) : (
                  <div className="text-clipz-text-muted">
                    <Upload size={32} className="mx-auto mb-2 opacity-50" />
                    <p className="text-[12px]">Drop a video file here or click to browse</p>
                    <p className="text-[10px] mt-1">MP4, MOV, AVI, MKV, WebM, FLV, WMV, MPG</p>
                  </div>
                )}
              </div>

              <div>
                <label className="block text-[11px] text-clipz-text-muted mb-1">Title (optional)</label>
                <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="My video" className="w-full h-9 rounded-md border border-clipz-border bg-clipz-surface px-3 text-[12px] text-white placeholder:text-clipz-text-dim focus:outline-none focus:border-clipz-accent/50" />
              </div>
            </>
          )}

          {tab === "url" && (
            <>
              <div>
                <label className="block text-[11px] text-clipz-text-muted mb-1">Video URL *</label>
                <input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://example.com/video.mp4" className="w-full h-9 rounded-md border border-clipz-border bg-clipz-surface px-3 text-[12px] text-white placeholder:text-clipz-text-dim focus:outline-none focus:border-clipz-accent/50" />
              </div>
              <div>
                <label className="block text-[11px] text-clipz-text-muted mb-1">Title (optional)</label>
                <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="My external video" className="w-full h-9 rounded-md border border-clipz-border bg-clipz-surface px-3 text-[12px] text-white placeholder:text-clipz-text-dim focus:outline-none focus:border-clipz-accent/50" />
              </div>
              <p className="text-[10px] text-clipz-text-dim">This source URL is registered for a future import. The video is not downloaded yet.</p>
            </>
          )}

          {/* Upload progress */}
          {uploading && (
            <div className="flex items-center gap-2 text-[12px] text-clipz-accent-soft">
              <Loader2 size={14} className="animate-spin" /> Processing...
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="flex items-start gap-2 rounded-lg border border-rose-500/20 bg-rose-500/10 px-3 py-2 text-[12px] text-rose-400">
              <AlertTriangle size={14} className="mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Result */}
          {result && (
            <div className="rounded-lg border border-emerald-500/20 bg-emerald-500/10 px-3 py-2 space-y-1">
              <div className="flex items-center gap-2 text-[12px] text-emerald-400">
                <CheckCircle2 size={14} /> {tab === "upload" ? "Upload complete" : "URL registered"}
              </div>
              {result.source_id && <p className="text-[10px] text-clipz-text-dim">Source ID: {result.source_id}</p>}
              {result.job_id && <p className="text-[10px] text-clipz-text-dim">Analysis job queued: {result.job_id}</p>}
              {result.job_status && <p className="text-[10px] text-clipz-text-dim">Job status: {result.job_status}</p>}
              {result.inspection_status && <p className="text-[10px] text-clipz-text-dim">Inspection: {result.inspection_status}</p>}
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end gap-2 pt-2">
            <button onClick={() => { reset(); onClose(); }} className="px-4 py-2 rounded-md border border-clipz-border bg-clipz-surface text-[12px] text-clipz-text-muted hover:text-white transition-colors">
              {result ? "Close" : "Cancel"}
            </button>
            {!result && (
              <button
                onClick={tab === "upload" ? handleUpload : handleRegisterUrl}
                disabled={uploading || !profileId || (tab === "upload" && !selectedFile) || (tab === "url" && !url.trim())}
                className="px-4 py-2 rounded-md bg-clipz-accent text-[12px] font-medium text-white hover:bg-clipz-accent/90 disabled:opacity-40 transition-colors"
              >
                {uploading ? "Processing..." : tab === "upload" ? "Upload" : "Register URL"}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}