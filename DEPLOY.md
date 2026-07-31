# Deploy guide

- **Frontend** → [Vercel](https://vercel.com) (GitHub, root `frontend/`)
- **Backend** → [GCP Cloud Run](https://cloud.google.com/run) (`backend/Dockerfile`)
- **Model** → `gemini/gemini-3-flash-preview` via LiteLLM (free tier on [Google AI Studio](https://aistudio.google.com))

Deploy **Vercel first** so you have the URL for `CORS_ORIGINS` before the backend goes live.

## Setup

```bash
cp deploy.env.example deploy.env   # edit PROJECT_ID, REGION, SERVICE
source deploy.env
gcloud config set project "$PROJECT_ID"
```

`deploy.env` is gitignored — shell-only, not read by the app. Put `GEMINI_API_KEY` in `backend/.env` for local dev (same key as production, or a separate AI Studio key).

Enable GCP APIs (once):

```bash
gcloud services enable run.googleapis.com secretmanager.googleapis.com cloudbuild.googleapis.com
```

---

## 1. Deploy frontend on Vercel

1. [vercel.com/new](https://vercel.com/new) → **Import** this GitHub repo.
2. **Root Directory** → `frontend`
3. Deploy (no env vars needed yet).

Copy the production URL into `deploy.env`:

```bash
VERCEL_URL=https://your-app.vercel.app   # no trailing slash
```

Re-`source deploy.env` after editing.

---

## 2. Store `GEMINI_API_KEY` in Secret Manager

Get a key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

```bash
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create GEMINI_API_KEY \
  --data-file=- \
  --replication-policy=automatic
```

Grant Cloud Run access:

```bash
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')

gcloud secrets add-iam-policy-binding GEMINI_API_KEY \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

To rotate: `echo -n "NEW_KEY" | gcloud secrets versions add GEMINI_API_KEY --data-file=-`

---

## 3. Deploy backend to Cloud Run

From repo root. No `--reload`; listens on Cloud Run `$PORT`. CORS allows Vercel + local dev.

```bash
gcloud run deploy "$SERVICE" \
  --source ./backend \
  --region "$REGION" \
  --allow-unauthenticated \
  --set-secrets GEMINI_API_KEY=GEMINI_API_KEY:latest \
  --set-env-vars "^@^CORS_ORIGINS=${VERCEL_URL},http://localhost:3000" \
  --timeout 3600 \
  --min-instances 0 \
  --max-instances 3
```

`^@^` tells gcloud to use `@` as the delimiter (not comma/colon), so the comma inside `CORS_ORIGINS` is kept as part of the value.

`--timeout 3600` — up to 1 hour for NDJSON streaming on `POST /runs/stream`.

Save the API URL to `deploy.env`:

```bash
API_URL=$(gcloud run services describe "$SERVICE" \
  --region "$REGION" \
  --format='value(status.url)')
echo "$API_URL"
```

Quick checks:

```bash
curl -i "$API_URL/health"    # HTTP 204
curl -s "$API_URL/" | head
```

---

## 4. Point Vercel at the backend

In Vercel → Project → **Settings → Environment Variables** (Production):

| Name                  | Value           |
| --------------------- | --------------- |
| `NEXT_PUBLIC_API_URL` | your `$API_URL` |

**Redeploy** (env vars are baked in at build time).

---

## 5. Verify

**Backend stream:**

```bash
curl -N -X POST "$API_URL/runs/stream" \
  -F "goal=Say hello in one sentence." \
  -F "max_iterations=1"
```

**Frontend:** open `$VERCEL_URL`, run a short goal, confirm steps stream and a final result appears.

If requests fail from the UI: check browser Network tab for CORS errors, and that `NEXT_PUBLIC_API_URL` matches `$API_URL`.
