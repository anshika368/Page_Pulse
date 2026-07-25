# Deployment Guide — Page Pulse

This guide walks you through deploying Page Pulse to **Render** (backend) and **Vercel** (frontend) on their free tiers. This combination is reliable and requires no credit card.

> **Important:** The repo has a `backend/` directory for the Python service and a `frontend/` directory for the Next.js app. The deployment configs are set up so each platform only builds the part it needs.

---

## Recommended Platform Pairing

| Service | Platform | Why |
|---------|----------|-----|
| **FastAPI backend** | [Render](https://render.com) | Native Python web services, free tier, stable public URL, health checks built in. |
| **Next.js frontend** | [Vercel](https://vercel.com) | Built for Next.js, automatic GitHub deploys, global CDN, generous free tier. |

> **Note on free-tier limitations:** Render’s free web services spin down after inactivity and take 30–60 seconds to wake up. Vercel’s free tier has generous bandwidth and build minutes for a project of this size. Both are perfectly adequate for a training task, portfolio demo, or small production app.

---

## Part 1: Push Code to GitHub

Make sure your latest code is on the `master` branch of `https://github.com/anshika368/Page_Pulse.git`.

```bash
cd D:\digitalheros
git add .
git commit -m "Add deployment configs for Render and Vercel"
git push origin master
```

---

## Part 2: Deploy the FastAPI Backend on Render

### Step 1: Sign up / log in
Go to [https://render.com](https://render.com) and sign up with your GitHub account.

### Step 2: Create a new Web Service
1. From the Render dashboard, click **New +** → **Web Service**.
2. Select the `anshika368/Page_Pulse` repository.

> **Using the Blueprint (recommended):** If Render asks whether to use `render.yaml`, click **Use Blueprint**. The `rootDir: backend` setting in that file tells Render to run all commands from the `backend/` folder.

3. If you are creating the service manually, configure it as follows:

| Setting | Value |
|---------|-------|
| Name | `page-pulse-api` |
| Runtime | `Python` |
| Root Directory | `backend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Region | `Oregon (US West)` (or closest to you) |
| Plan | `Free` |

4. Set environment variables under **Advanced**:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.12.0` |
| `CORS_ALLOWED_ORIGINS` | `*` (for now; we will restrict this after Vercel deployment) |

5. Click **Create Web Service**.

If you see an error saying `requirements.txt` cannot be found, it means Render is running commands from the repo root instead of `backend/`. Fix it by either:
- Using the `render.yaml` Blueprint (recommended), or
- Setting the **Root Directory** field to `backend` in the service settings.

Render will build and deploy the backend. Once finished, it gives you a public URL like:

```
https://page-pulse-api.onrender.com
```

### Step 3: Verify the backend
Open `https://page-pulse-api.onrender.com/health` in your browser. You should see:

```json
{"status": "ok", "service": "page-pulse-audit"}
```

Test the audit endpoint:

```bash
curl -X POST https://page-pulse-api.onrender.com/api/audit \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

---

## Part 3: Deploy the Next.js Frontend on Vercel

### Step 1: Sign up / log in
Go to [https://vercel.com](https://vercel.com) and sign up with your GitHub account.

### Step 2: Import the project
1. Click **Add New…** → **Project**.
2. Select the `anshika368/Page_Pulse` repository.
3. Vercel will auto-detect Next.js. Leave the default settings.

### Step 3: Set the environment variable
Before deploying, add:

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `https://page-pulse-api.onrender.com` |

> `NEXT_PUBLIC_` variables are embedded at build time, so this must be set before the first deployment.

### Step 4: Deploy
Click **Deploy**. Vercel builds and deploys the frontend, giving you a URL like:

```
https://page-pulse.vercel.app
```

### Step 5: Verify the frontend
1. Open the Vercel URL.
2. Paste `https://example.com` into the input and click **Pulse Check**.
3. You should see the audit dashboard load with the score ring, SEO metrics, and issue list.

---

## Part 4: Lock Down CORS (Recommended)

After both services are live, restrict the backend so only your Vercel frontend can call it.

1. In Render, go to your Web Service → **Environment** → **Add Environment Variable** (or edit existing).
2. Change `CORS_ALLOWED_ORIGINS` from `*` to your Vercel URL:

```
CORS_ALLOWED_ORIGINS=https://page-pulse.vercel.app
```

3. Click **Save Changes**. Render will redeploy automatically.

Now the backend rejects cross-origin requests from unknown domains, which is a small but important security improvement.

---

## Part 5: Custom Domain (Optional)

If you own a domain:

- **Vercel**: Project → **Settings** → **Domains** → follow the DNS instructions.
- **Render**: Web Service → **Settings** → **Custom Domains** → add your domain and update DNS records.

Remember to update `CORS_ALLOWED_ORIGINS` if you add a custom domain.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Frontend shows “Error 503 — Could not reach the host” | Backend is waking up from cold start | Wait 30–60 s and retry; consider a ping service for keep-alive. |
| Frontend audit never returns | `NEXT_PUBLIC_API_URL` is wrong or missing | Check Vercel environment variables and redeploy. |
| CORS errors in browser console | `CORS_ALLOWED_ORIGINS` doesn’t match Vercel URL | Update the Render env var with the exact frontend URL. |
| Build fails on Render | Python version mismatch | Set `PYTHON_VERSION=3.12.0`. |
| Build fails on Vercel | Node version too old | Vercel uses Node 20+ by default; `package.json` already specifies `>=20.0.0`. |

---

## Architecture After Deployment

```
User Browser
     │
     ▼
┌─────────────────────┐
│  Vercel Frontend    │  https://page-pulse.vercel.app
│  Next.js 15 + TS    │
└─────────┬───────────┘
          │ POST /api/audit
          ▼
┌─────────────────────┐
│  Render Backend     │  https://page-pulse-api.onrender.com
│  FastAPI + httpx    │
└─────────┬───────────┘
          │ GET /api/audit upstream URL
          ▼
┌─────────────────────┐
│   Target Website    │
└─────────────────────┘
```

Both platforms deploy automatically on every push to `master`, so your live app stays in sync with your GitHub repo.

---

## Cost Summary

| Platform | Free Tier Includes |
|----------|-------------------|
| Render Web Service | 512 MB RAM, spins down after inactivity, 100 GB egress/month |
| Vercel | 100 GB bandwidth, 6,000 build minutes/month, unlimited seats |

For a training task or portfolio piece, you will remain well within free limits.
