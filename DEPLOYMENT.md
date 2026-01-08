# Deployment Configuration Guide

## Backend Deployment (Railway)

### Required Environment Variables

Add these in Railway → Service → Variables:

```bash
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://neondb_owner:npg_sTVtWHiXo15L@ep-damp-wildflower-ada8vtmu-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require

# Environment
ENVIRONMENT=production

# CORS - Allow Vercel frontend and localhost
CORS_ORIGINS=https://web-taskflow.vercel.app,http://localhost:3000

# JWT Authentication
JWT_SECRET_KEY=BeYWoWvyT1eFr0HFiDeVU1rCJ6EpRZcw9IB/dcZ9by8=
JWT_ALGORITHM=HS256

# Better Auth
BETTER_AUTH_SECRET=pgkePkCIxaibL3qlPYRyihR73KUx7kKt
```

### Railway URLs
- **Backend API**: https://tasklow-web-production.up.railway.app
- **Health Check**: https://tasklow-web-production.up.railway.app/health
- **API Docs**: https://tasklow-web-production.up.railway.app/docs

---

## Frontend Deployment (Vercel)

### Required Environment Variables

Add these in Vercel → Project Settings → Environment Variables:

```bash
# Backend API URLs (Railway)
NEXT_PUBLIC_API_URL=https://tasklow-web-production.up.railway.app
NEXT_PUBLIC_AUTH_URL=https://tasklow-web-production.up.railway.app

# Database (Neon PostgreSQL - for Better Auth)
DATABASE_URL=postgresql://neondb_owner:npg_sTVtWHiXo15L@ep-damp-wildflower-ada8vtmu-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# JWT Configuration (must match backend)
JWT_SECRET=BeYWoWvyT1eFr0HFiDeVU1rCJ6EpRZcw9IB/dcZ9by8=
JWT_EXPIRY=7d

# Better Auth Configuration
BETTER_AUTH_SECRET=pgkePkCIxaibL3qlPYRyihR73KUx7kKt
BETTER_AUTH_URL=https://web-taskflow.vercel.app

# Environment
NODE_ENV=production
```

### Vercel URLs
- **Frontend**: https://web-taskflow.vercel.app

---

## Known Issues & Fixes

### Railway Environment Variable Leading Space Bug

Railway may inject environment variables with a **leading space** (e.g., ` DATABASE_URL` instead of `DATABASE_URL`).

**Fix Applied**: `backend/src/config.py` includes a workaround that checks for both formats:
- Normal: `DATABASE_URL`
- With space: ` DATABASE_URL`

If you see this in Railway logs:
```
[CONFIG] ⚠️  WARNING: Found Railway env var with leading space: ' DATABASE_URL'
```

This is expected and the workaround is handling it correctly.

---

## Deployment Checklist

### Initial Setup
- [x] Backend deployed to Railway
- [x] Database (Neon PostgreSQL) configured
- [x] Frontend deployed to Vercel
- [ ] Add CORS_ORIGINS to Railway (includes Vercel URL)
- [ ] Add environment variables to Vercel
- [ ] Redeploy Vercel after adding variables

### Testing
- [ ] Test health check: `curl https://tasklow-web-production.up.railway.app/health`
- [ ] Verify CORS: `curl -i -X OPTIONS https://tasklow-web-production.up.railway.app/api/v1/auth/signup -H "Origin: https://web-taskflow.vercel.app"`
- [ ] Open Vercel app and test sign up/sign in
- [ ] Create a test task
- [ ] Verify data persists in Neon database

### Production Ready
- [ ] Remove debug logging from `config.py` and `database.py`
- [ ] Ensure all secrets are set in environment variables (not hardcoded)
- [ ] Set up monitoring/alerts in Railway
- [ ] Configure custom domain (optional)

---

## Troubleshooting

### "Failed to fetch" Error
1. Check CORS_ORIGINS includes your frontend URL
2. Verify Railway backend is running: check health endpoint
3. Check browser console for specific error messages
4. Verify Vercel environment variables are set correctly

### Database Connection Issues
1. Check Railway logs for database connection messages
2. Verify DATABASE_URL is set correctly (no trailing newlines)
3. Check Neon dashboard to ensure database is not suspended

### CORS Errors
1. Verify CORS_ORIGINS in Railway includes both:
   - Production: `https://web-taskflow.vercel.app`
   - Development: `http://localhost:3000`
2. Check Railway logs for CORS configuration on startup
3. Test with curl to verify headers

---

## Update Process

### Backend Updates
1. Push changes to GitHub branch `004-backend-deployment`
2. Railway auto-deploys on push
3. Check deployment logs for errors
4. Test health endpoint

### Frontend Updates
1. Push changes to GitHub
2. Vercel auto-deploys on push to main branch
3. Check deployment logs
4. Test production URL

---

## Security Notes

⚠️ **IMPORTANT**: This file contains production secrets and should be:
- Added to `.gitignore`
- Stored securely (password manager, team secrets vault)
- Never committed to version control in production

For development, use `.env.local` files (already in `.gitignore`).
