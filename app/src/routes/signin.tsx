import { createFileRoute, useRouter } from "@tanstack/react-router";
import { useState, useEffect, useRef } from "react";
import { useAuth } from "../lib/auth/auth-context";

export const Route = createFileRoute("/signin")({
  component: SignInPage,
});

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: {
            client_id: string;
            callback: (response: { credential: string }) => void;
            cancel_on_tap_outside?: boolean;
          }) => void;
          renderButton: (
            element: HTMLElement,
            options: {
              theme?: "outline" | "filled_blue" | "filled_black";
              size?: "large" | "medium" | "small";
              text?: "signin_with" | "signup_with" | "continue_with";
              shape?: "rectangular" | "pill" | "square" | "circle";
              logo_alignment?: "left" | "center";
              width?: string;
            }
          ) => void;
          prompt: (momentListener?: (moment: { type: string }) => void) => void;
        };
      };
    };
  }
}

function SignInPage() {
  const auth = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const googleBtnRef = useRef<HTMLDivElement>(null);
  const [googleClientId] = useState(() => {
    // Expose the Google Client ID as a build-time env var
    return (import.meta as any).env?.VITE_GOOGLE_CLIENT_ID || "";
  });

  if (auth.isAuthenticated) {
    router.navigate({ to: "/" });
    return null;
  }

  // Load Google Identity Services and render the button
  useEffect(() => {
    if (!googleClientId || !googleBtnRef.current) return;

    // Check if already loaded
    if (window.google?.accounts?.id) {
      window.google.accounts.id.initialize({
        client_id: googleClientId,
        callback: async (response) => {
          try {
            setLoading(true);
            await auth.signInWithGoogle(response.credential);
            await router.navigate({ to: "/" });
          } catch (err: any) {
            setError(err?.error?.message || "Google sign-in failed.");
          } finally {
            setLoading(false);
          }
        },
        cancel_on_tap_outside: false,
      });
      window.google.accounts.id.renderButton(googleBtnRef.current, {
        theme: "outline",
        size: "large",
        text: "signin_with",
        shape: "rectangular",
        width: "320",
      });
      return;
    }

    // Load the GIS script
    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;
    script.onload = () => {
      if (window.google?.accounts?.id && googleBtnRef.current) {
        window.google.accounts.id.initialize({
          client_id: googleClientId,
          callback: async (response) => {
            try {
              setLoading(true);
              await auth.signInWithGoogle(response.credential);
              await router.navigate({ to: "/" });
            } catch (err: any) {
              setError(err?.error?.message || "Google sign-in failed.");
            } finally {
              setLoading(false);
            }
          },
          cancel_on_tap_outside: false,
        });
        window.google.accounts.id.renderButton(googleBtnRef.current, {
          theme: "outline",
          size: "large",
          text: "signin_with",
          shape: "rectangular",
          width: "320",
        });
      }
    };
    document.head.appendChild(script);

    return () => {
      // Cleanup script on unmount (optional, but prevents duplicates)
      if (script.parentNode) {
        script.parentNode.removeChild(script);
      }
    };
  }, [googleClientId, auth, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await auth.signIn(email, password);
      await router.navigate({ to: "/" });
    } catch (err: any) {
      setError(err?.error?.message || err?.detail?.error?.message || err?.message || JSON.stringify(err) || "Sign in failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-q-background-primary px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <h1 className="text-q-heading-md text-q-text-primary">CLIPZ</h1>
          <p className="mt-2 text-q-body-sm-regular text-q-text-secondary">Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
              {error}
            </div>
          )}

          <div>
            <label className="mb-1 block text-sm font-medium text-q-text-secondary">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full rounded-lg border border-q-border-primary bg-q-background-primary px-4 py-2.5 text-sm text-q-text-primary placeholder:text-q-text-tertiary focus:border-cyan-500 focus:outline-none"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-q-text-secondary">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full rounded-lg border border-q-border-primary bg-q-background-primary px-4 py-2.5 text-sm text-q-text-primary placeholder:text-q-text-tertiary focus:border-cyan-500 focus:outline-none"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-cyan-500 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-cyan-600 disabled:opacity-50"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>

          {googleClientId && (
            <>
              <div className="relative my-4">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-q-border-primary" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-q-background-primary px-2 text-q-text-tertiary">or continue with</span>
                </div>
              </div>

              <div className="flex justify-center" ref={googleBtnRef} />
            </>
          )}

          <p className="text-center text-sm text-q-text-secondary">
            Don't have an account?{" "}
            <a
              href="/signup"
              onClick={(e) => {
                e.preventDefault();
                router.navigate({ to: "/signup" });
              }}
              className="text-cyan-400 hover:underline"
            >
              Sign up
            </a>
          </p>
        </form>
      </div>
    </div>
  );
}