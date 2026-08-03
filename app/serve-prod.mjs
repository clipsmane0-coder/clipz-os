import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const CLIENT_DIR = path.join(__dirname, "dist/client");
const PORT = process.env.PORT || 3000;

const MIME_TYPES = {
  ".js": "application/javascript",
  ".css": "text/css",
  ".html": "text/html",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
  ".webp": "image/webp",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".json": "application/json",
  ".map": "application/json",
};

async function start() {
  // Load the SSR handler
  const mod = await import(path.join(__dirname, "dist/server/server.js"));
  const ssrHandler = mod.default.fetch;

  const server = http.createServer(async (req, res) => {
    try {
      const url = new URL(req.url, `http://localhost:${PORT}`);

      // 1. Try serving static files from dist/client/
      if (url.pathname !== "/" && !url.pathname.startsWith("/assets")) {
        // Check if it's a known static file
        const staticPath = path.join(CLIENT_DIR, url.pathname);
        const ext = path.extname(url.pathname);
        if (ext && fs.existsSync(staticPath) && fs.statSync(staticPath).isFile()) {
          const content = fs.readFileSync(staticPath);
          res.writeHead(200, { "Content-Type": MIME_TYPES[ext] || "application/octet-stream" });
          res.end(content);
          return;
        }
      }

      // 2. Serve client assets from /assets/ prefix
      if (url.pathname.startsWith("/assets/")) {
        const assetPath = path.join(CLIENT_DIR, url.pathname);
        if (fs.existsSync(assetPath) && fs.statSync(assetPath).isFile()) {
          const ext = path.extname(url.pathname);
          const content = fs.readFileSync(assetPath);
          res.writeHead(200, { "Content-Type": MIME_TYPES[ext] || "application/octet-stream" });
          res.end(content);
          return;
        }
      }

      // 3. Fall back to SSR
      const headers = new Headers();
      for (const [k, v] of Object.entries(req.headers)) {
        if (v) headers.set(k, Array.isArray(v) ? v.join(", ") : v);
      }

      const request = new Request(url, {
        method: req.method,
        headers,
        body: req.method !== "GET" && req.method !== "HEAD" ? await new Promise((r) => { let d = []; req.on("data", (c) => d.push(c)); req.on("end", () => r(Buffer.concat(d))); }) : undefined,
      });

      const response = await ssrHandler(request, {}, {});
      const responseBody = await response.text();

      res.writeHead(response.status, Object.fromEntries(response.headers.entries()));
      res.end(responseBody);
    } catch (err) {
      console.error("Server error:", err);
      // Try serving index.html as fallback for client-side routing
      try {
        const indexPath = path.join(CLIENT_DIR, "index.html");
        if (fs.existsSync(indexPath)) {
          const content = fs.readFileSync(indexPath, "utf8");
          res.writeHead(200, { "Content-Type": "text/html" });
          res.end(content);
          return;
        }
      } catch (_) {}
      res.writeHead(500, { "Content-Type": "text/plain" });
      res.end("Internal Server Error");
    }
  });

  server.listen(PORT, () => {
    console.log(`CLIPZ production server running at http://localhost:${PORT}`);
  });
}

start().catch(console.error);
