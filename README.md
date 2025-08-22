Website Audit Tool

Audit any public website for Security, SEO, Performance, and Accessibility.
Built for HackYugma 2k25.

Live Frontend:https://suraja-ui.github.io/27_Scube/

 

The frontend is a static site (HTML/CSS/JS) hosted on GitHub Pages.
The backend is a FastAPI service hosted on Render.

 Features

One-click audit from the browser

Scores for Security / SEO / Performance / Accessibility

Top recommendations + passes + issues

Download JSON report

Modern, colorful UI with spinner and animated gauges

Resilient frontend with auto-retry for Render’s free cold start

 

 Quick Start (Local)

You can run only backend locally and use the hosted frontend — or run both locally.

Prerequisites

Python 3.10+ (3.11/3.12/3.13 are fine)

Git

(Optional) A simple HTTP server to serve the frontend locally

1) Clone the repo
git clone  https://suraja-ui.github.io/27_Scube/
cd website-audit-tool

2) Backend — create venv & install

 
 Backend — run
uvicorn app.main:app --reload --port 8000


Open API docs: http://127.0.0.1:8000/docs

 Frontend — use the hosted UI (easiest)

Open:  https://suraja-ui.github.io/27_Scube/

 

 
🧩 API

POST /audit
Request body:

{ "url": "https://example.com" }


Response (example shape):

{
  "scores": {
    "security": 65,
    "seo": 35,
    "performance": 60,
    "accessibility": 0
  },
  "summary": {
    "recommendations": [
      "Missing headers: x-content-type-options, referrer-policy",
      "Mixed content: http:// resources found",
      "Add a meta description (50–160 chars)"
    ],
    "passes": [
      "Uses HTTPS",
      "HSTS enabled",
      "Security headers present"
    ],
    "issues": [
      "Mixed content: http:// resources found",
      "Missing meta description"
    ]
  },
  "page": {
    "title": "Example Domain",
    "description_len": 0,
    "size_bytes": 1256,
    "resource_count": 0
  }
}

Frontend on GitHub Pages

The project already deploys from main branch / docs folder`.

To update:

Edit docs/index.html and/or docs/script.js.

Make sure the API base in docs/script.js is correct:

const API = "https://website-audit-backend-8b6k.onrender.com";


Commit & push:

git add docs
git commit -m "update frontend"
git push


Settings → Pages

Source: Deploy from a branch

Branch: main

Folder: /docs

Wait ~1 minute. Your site is at:

https://suraja-ui.github.io/website-audit-tool/


Cache busting (if the browser shows old JS):

In docs/index.html bump the version:

<script src="./script.js?v=10"></script>


Hard refresh (Ctrl+F5) or open in incognito.

🛠 Tech Stack

Backend: Python, FastAPI, Uvicorn, httpx, (plus small helpers)

Frontend: HTML, CSS, Vanilla JavaScript (no build step)

Hosting: Render (API) + GitHub Pages (static UI)

Troubleshooting

“Failed to reach backend …”

The Render service may be waking up (free plan). Wait 20–60 seconds.

Open the API docs to warm it: https://website-audit-backend-8b6k.onrender.com/docs

Check DevTools → Network → the audit request status.

CORS errors

The backend enables CORS for *. If you lock it down, include your GitHub Pages origin:
https://suraja-ui.github.io

GitHub Pages shows old code

Add ?v=<new number> to <script src> and hard refresh.

Windows: venv activation policy

If Activate.ps1 is blocked:

Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

Smoke Test (local)
# backend
cd backend
.venv\Scripts\Activate.ps1  # or source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# in a second terminal, call API
curl -X POST http://127.0.0.1:8000/audit -H "Content-Type: application/json" -d "{\"url\":\"https://example.com\"}"

 Contributing

Issues and PRs welcome!

Fork the repo

Create a feature branch

Commit with clear messages

Open a PR with before/after screenshots if UI related

📄 License

MIT © 2025 Suraja & Team

Project Links

Frontend (Pages): https://suraja-ui.github.io/27_Scube/

Backend (Render): https://27_Scube-backend-8b6k.onrender.com

 
