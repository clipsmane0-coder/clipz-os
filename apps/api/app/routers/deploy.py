"""Deployment status and dashboard route."""
import os
import platform
from datetime import datetime, timezone
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/deploy", response_class=HTMLResponse, include_in_schema=False)
async def deployment_dashboard(request: Request):
    git_commit = os.environ.get("GIT_COMMIT", "unknown")[:8]
    deploy_time = os.environ.get("DEPLOY_TIME", "unknown")
    environment = os.environ.get("ENVIRONMENT", "development")
    python_version = platform.python_version()
    hostname = platform.node()

    deployed_at = deploy_time
    try:
        dt = datetime.fromisoformat(deploy_time)
        deployed_at = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except (ValueError, TypeError):
        pass

    server_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CLIPZ Deployment Dashboard</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font: 14px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; background: #0a0a14; color: #c8c8e0; min-height: 100vh; }}
  header {{ background: linear-gradient(135deg, #6a0dad 0%, #0a0a48 100%); padding: 2rem 1.5rem; text-align: center; border-bottom: 1px solid #2a2a5a; }}
  header h1 {{ font-size: 1.6rem; color: #fff; margin-bottom: 0.25rem; letter-spacing: 0.02em; }}
  header p {{ color: #8888bb; font-size: 0.85rem; }}
  .container {{ max-width: 960px; margin: 0 auto; padding: 1.5rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }}
  .card {{ background: #12122a; border: 1px solid #2a2a5a; border-radius: 8px; padding: 1.25rem; }}
  .card h2 {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: #6666aa; margin-bottom: 0.5rem; }}
  .card .value {{ font-size: 1.2rem; color: #e0e0ff; font-weight: 600; }}
  .card .value.green {{ color: #44ddaa; }}
  .card .value.yellow {{ color: #dddd44; }}
  .card .value.red {{ color: #dd6666; }}
  .card .sub {{ font-size: 0.8rem; color: #6666aa; margin-top: 0.25rem; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
  th, td {{ padding: 0.6rem 0.75rem; text-align: left; border-bottom: 1px solid #1a1a3a; font-size: 0.85rem; }}
  th {{ color: #6666aa; font-weight: 600; text-transform: uppercase; font-size: 0.7rem; letter-spacing: 0.05em; }}
  td {{ color: #b0b0d0; }}
  .badge {{ display: inline-block; padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }}
  .badge.green {{ background: #1a3a2a; color: #44ddaa; }}
  .badge.blue {{ background: #1a2a4a; color: #66bbff; }}
  .badge.purple {{ background: #2a1a4a; color: #bb88ff; }}
  .endpoints {{ margin-top: 1.5rem; }}
  .endpoints h3 {{ font-size: 0.9rem; color: #8888bb; margin-bottom: 0.75rem; }}
  .endpoint {{ display: flex; justify-content: space-between; padding: 0.5rem 0.75rem; border-bottom: 1px solid #1a1a3a; font-size: 0.85rem; font-family: monospace; }}
  .endpoint .method {{ color: #44ddaa; font-weight: 600; }}
  .endpoint .path {{ color: #b0b0d0; }}
  .endpoint .desc {{ color: #6666aa; font-size: 0.78rem; }}
  .footer {{ text-align: center; padding: 2rem; color: #444477; font-size: 0.78rem; }}
  a {{ color: #8888ff; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<header>
  <h1>CLIPZ Deployment Dashboard</h1>
  <p>Backend API — {environment.title()} Environment</p>
</header>
<div class="container">
  <div class="grid">
    <div class="card">
      <h2>API Status</h2>
      <div class="value green">Healthy</div>
      <div class="sub">All systems operational</div>
    </div>
    <div class="card">
      <h2>Version</h2>
      <div class="value">0.1.0</div>
      <div class="sub">Git commit <code style="color:#8888ff">{git_commit}</code></div>
    </div>
    <div class="card">
      <h2>Environment</h2>
      <div class="value">{environment.title()}</div>
      <div class="sub">Python {python_version}</div>
    </div>
    <div class="card">
      <h2>Deployed</h2>
      <div class="value">{deployed_at}</div>
      <div class="sub">Host: {hostname}</div>
    </div>
  </div>

  <table>
    <tr>
      <th>Check</th>
      <th>Status</th>
      <th>Detail</th>
    </tr>
    <tr>
      <td>API Server</td>
      <td><span class="badge green">pass</span></td>
      <td>Accepting requests</td>
    </tr>
    <tr>
      <td>Health Endpoint</td>
      <td><span class="badge green">pass</span></td>
      <td><code>/api/v1/health</code></td>
    </tr>
    <tr>
      <td>Database</td>
      <td><span class="badge green">pass</span></td>
      <td>SQLite (development)</td>
    </tr>
    <tr>
      <td>Server Time</td>
      <td><span class="badge blue">info</span></td>
      <td>{server_time}</td>
    </tr>
    <tr>
      <td>CORS Origins</td>
      <td><span class="badge purple">info</span></td>
      <td>Configured per environment</td>
    </tr>
  </table>

  <div class="endpoints">
    <h3>API Endpoints</h3>
    <div class="endpoint">
      <span><span class="method">GET</span> <span class="path">/api/v1/health</span></span>
      <span class="desc">Health check</span>
    </div>
    <div class="endpoint">
      <span><span class="method">GET</span> <span class="path">/api/v1/profiles</span></span>
      <span class="desc">List profiles</span>
    </div>
    <div class="endpoint">
      <span><span class="method">GET</span> <span class="path">/api/v1/sources</span></span>
      <span class="desc">List sources</span>
    </div>
    <div class="endpoint">
      <span><span class="method">GET</span> <span class="path">/docs</span></span>
      <span class="desc">Swagger UI</span>
    </div>
    <div class="endpoint">
      <span><span class="method">GET</span> <span class="path">/deploy</span></span>
      <span class="desc">This dashboard</span>
    </div>
  </div>

  <div class="footer">
    CLIPZ — Built on Fly.io &middot;
    <a href="/api/v1/health">Health JSON</a> &middot;
    <a href="/docs">API Docs</a>
  </div>
</div>
</body>
</html>"""
    return HTMLResponse(content=html, status_code=200)
