# Backend Production Deployment Quickstart

This guide covers deploying the FastAPI backend to Railway with Neon PostgreSQL.

## Prerequisites

- Railway account (connected to GitHub)
- Neon account with PostgreSQL database created
- Vercel account with frontend deployed (for CORS)

## Step 1: Configure Neon Database

1. Create a new project in [Neon Console](https://console.neon.tech)
2. Create a database (e.g., `todo_app`)
3. Get the connection string from **Connection Details**
4. Use the **Pooled** connection string (includes `-pooler` suffix)

```text
# Pooled connection format
postgresql://user:password@ep-xxx-pooler.us-east-1.aws.neon.tech/dbname?sslmode=require
```

## Step 2: Configure Railway

### Environment Variables

Set these in Railway **Variables** tab:

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | Neon pooled connection string | Required |
| `JWT_SECRET_KEY` | Strong random secret | Required (no default) |
| `BETTER_AUTH_SECRET` | Strong random secret | Required (no default) |
| `ENVIRONMENT` | `production` | Enables production mode |
| `CORS_ORIGINS` | Vercel frontend URLs | Comma-separated |

### Example CORS Origins

```
https://todo-app-web.vercel.app,https://todo-app-git-main.vercel.app
```

### Deploy

1. Connect your GitHub repository to Railway
2. Select the `backend/` directory as the root
3. Railway will auto-detect Python and run `uvicorn`
4. Ensure `Procfile` is in the `backend/` directory

## Step 3: Verify Deployment

### Health Check

```bash
curl https://your-railway-app.up.railway.app/health
```

Expected response (200 OK):
```json
{
  "status": "ok",
  "database": "connected",
  "environment": "production",
  "timestamp": "2025-12-31T12:00:00Z"
}
```

### CORS Verification

```bash
curl -I -H "Origin: https://todo-app-web.vercel.app" \
  https://your-railway-app.up.railway.app/health
```

Expected headers:
- `Access-Control-Allow-Origin: https://todo-app-web.vercel.app`

### Non-whitelisted Origin Rejection

```bash
curl -I -H "Origin: https://evil-site.com" \
  https://your-railway-app.up.railway.app/health
```

Expected: 403 or missing CORS headers

## Step 4: Run Production Verification Suite

```bash
cd backend
python3 verify_production.py --url https://your-railway-app.up.railway.app
```

This script validates:
- Deep health check with database connectivity
- CORS whitelist enforcement
- JWT authentication required for protected endpoints

## Rollback Procedure

If issues occur:

1. **Railway Dashboard**: Go to Deployments → Previous deployment → Redeploy
2. **Database**: Neon retains data; no migration needed for config changes
3. **Environment Variables**: Update in Railway dashboard, triggers restart

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 503 Unhealthy | Check Neon compute is active; increase pool size |
| CORS errors | Verify `CORS_ORIGINS` includes exact frontend URL |
| JWT errors | Ensure `JWT_SECRET_KEY` is set in Railway |
| Port binding error | Railway sets `PORT` automatically; do not hardcode |

## Security Checklist

- [ ] No hardcoded secrets in codebase
- [ ] `ENVIRONMENT=production` set in Railway
- [ ] API docs disabled in production (`docs_url=None`)
- [ ] CORS restricted to Vercel domains only
- [ ] Health check accessible without auth
