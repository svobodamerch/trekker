# Beta Deploy Checklist

## Pre-Deploy (Local)
- [ ] All core tests pass: `pytest tests/test_return_state.py tests/test_weekly_reflection.py`
- [ ] Frontend builds: `npm run build`
- [ ] Environment files ready

## Step 1: Railway Backend + PostgreSQL

### 1.1 Create Railway Project
1. Railway dashboard → New Project → Empty Project
2. Name: `trekker-beta`

### 1.2 Add PostgreSQL
1. New → Database → Add PostgreSQL
2. Wait for "Available" status
3. Copy "Postgres Connection URL"

### 1.3 Deploy Backend
1. New → GitHub Repo → Select your repo
2. Railway auto-detects Python
3. Settings:
   - Build command: (default)
   - Start command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 1.4 Environment Variables
```
APP_ENV=production
DATABASE_URL=${{Postgres.DATABASE_URL}}  # Auto-filled
JWT_SECRET=<generate-256-bit-secret>
BOT_TOKEN=<from-botfather>
MINI_APP_URL=<vercel-url-after-step-2>
BACKEND_URL=<railway-backend-url>
TELEGRAM_AUTH_MOCK=false
CORS_ORIGINS=<vercel-url>
```

Generate JWT_SECRET:
```bash
openssl rand -base64 32
```

### 1.5 Run Migrations
Railway dashboard → your service → "Deploy" → Will run migrations on startup via start command.

Or manually:
```bash
railway login
railway link
railway run -- alembic upgrade head
```

### 1.6 Verify Backend
```bash
curl https://your-backend.up.railway.app/health
```
Should return: `{"status":"ok"}`

## Step 2: Vercel Frontend

### 2.1 Deploy
1. vercel.com → Add New Project
2. Import GitHub repo
3. Framework: Vite
4. Root directory: `frontend` (if monorepo) or `./`
5. Build command: `npm run build`
6. Output directory: `dist`

### 2.2 Environment Variables
```
VITE_API_URL=https://your-backend.up.railway.app
```

### 2.3 Deploy
Click "Deploy"

### 2.4 Copy URL
Copy the deployed URL (e.g., `https://trekker-beta.vercel.app`)

## Step 3: Update Railway Env

Go back to Railway dashboard, update:
```
MINI_APP_URL=https://trekker-beta.vercel.app
CORS_ORIGINS=https://trekker-beta.vercel.app
```

Redeploy backend.

## Step 4: Bot Worker

### 4.1 Create Bot Service
Railway project → New → GitHub Repo (same repo)

### 4.2 Settings
- Start command: `python -m bot.bot.main`
- No healthcheck needed

### 4.3 Environment Variables
Same as backend, plus ensure:
```
BOT_TOKEN=<your-token>
MINI_APP_URL=https://trekker-beta.vercel.app
BACKEND_URL=https://your-backend.up.railway.app
```

### 4.4 Deploy
Deploy the bot service.

## Step 5: BotFather Configuration

1. Open @BotFather
2. `/mybots` → Select your bot
3. "Bot Settings" → "Menu Button" → "Configure menu button"
4. Button text: `📝 Пульс`
5. URL: `https://trekker-beta.vercel.app`

## Step 6: One-User Smoke Test

### Test 1: Bot Entry
1. Open bot in Telegram
2. Press `/start`
3. Click "📝 Записать Пульс"
4. Verify Mini App opens

### Test 2: Telegram Auth
1. Mini App should load without auth errors
2. Check debug panel (DEV only) or console

### Test 3: Create Pulse
1. Go to /pulse
2. Fill: mood=7, energy=8, anxiety=3
3. Add insight: "Test entry"
4. Save
5. Verify success

### Test 4: Verify Database
```sql
-- Connect to Railway PostgreSQL
SELECT telegram_user_id, created_at FROM users;
SELECT user_id, mood, insight, created_at FROM entries ORDER BY created_at DESC;
```

### Test 5: History
1. Go to /history
2. Verify entry appears

### Test 6: Analytics
1. Go to /analytics
2. Verify weekly chart shows data point

### Test 7: Goals
1. Go to /goals
2. Create goal: horizon=month, title="Test Goal"
3. Verify saved

### Test 8: Dream Life
1. Create Dream Life goal with custom timeframe
2. Verify saved

### Test 9: Weekly Reflection
1. Create 3+ entries (may need 3 separate days)
2. Go to /analytics
3. Click "Сделать недельное отражение"
4. Verify placeholder response appears

### Test 10: Beta Analytics
Run SQL queries from `BETA_ANALYTICS.md`:
```sql
SELECT 
  (SELECT COUNT(*) FROM users) as total_users,
  (SELECT COUNT(*) FROM entries) as total_entries,
  (SELECT COUNT(*) FROM goals) as total_goals;
```

## Step 7: Ready for 3-5 Testers

Once smoke test passes:

1. Create invitation message (from beta_russian_copy.md)
2. Send to 3-5 trusted users
3. Include:
   - Bot link
   - Simple instructions
   - Request for feedback after 7 days

## Emergency Contacts & Procedures

### Rollback Backend
Railway dashboard → Deployments → Previous deployment → "Redeploy"

### Check Logs
```bash
railway logs
```

### Delete Test User
```bash
railway run -- python scripts/delete_user.py <telegram_user_id>
```

### Database Backup
Railway dashboard → PostgreSQL → Backups (if enabled)

## URLs After Deploy

| Service | URL |
|---------|-----|
| Frontend | `https://trekker-beta.vercel.app` |
| Backend | `https://trekker-beta-api.up.railway.app` |
| Bot | (worker, no URL) |
| Database | (internal Railway) |

## Post-Deploy Monitoring

Daily checks:
1. Railway dashboard metrics
2. Run beta analytics SQL
3. Check error logs
4. Monitor user engagement

Weekly:
1. Review user feedback
2. Export metrics
3. Plan fixes/improvements

## Success Criteria for Beta

- [ ] 3-5 users invited
- [ ] 60%+ create first Pulse within 24h
- [ ] 40%+ create at least 3 entries
- [ ] 20%+ create at least 1 goal
- [ ] Zero data loss incidents
- [ ] All users can delete data on request

## Known Limitations (Acceptable for Beta)

- AI Reflection in placeholder mode (no AI key)
- No email notifications
- No automated backups (manual Railway backups)
- Goal Review Ritual basic (no polish)
- No voice input yet
