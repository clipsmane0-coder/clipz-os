"use client";

import { Component, type ReactNode } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  requestId?: string;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;

      return (
        <div className="flex items-center justify-center p-8 min-h-[300px]">
          <div className="max-w-md rounded-xl border border-rose-500/20 bg-rose-500/5 p-6 text-center">
            <AlertTriangle size={40} className="mx-auto mb-3 text-rose-400" />
            <h3 className="text-[15px] font-semibold text-white mb-1">Something went wrong</h3>
            <p className="text-[12px] text-clipz-text-muted mb-4">
              {this.state.error?.message || "An unexpected error occurred."}
            </p>
            <button
              onClick={() => window.location.reload()}
              className="inline-flex items-center gap-2 rounded-lg bg-clipz-accent px-3.5 py-2 text-[12px] font-medium text-white hover:bg-clipz-accent/90 transition-colors"
            >
              <RefreshCw size={14} /> Retry
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}