# Beta Deployment Guide

Deploying the Self-Observation app for closed beta with 3-5 real users.

## Architecture

- **Frontend**: Vercel (static React build)
- **Backend**: Railway or Render (FastAPI)
- **Bot**: Railway/Render worker (aiogram)
- **Database**: Railway PostgreSQL or Supabase

## Prerequisites

1. Telegram Bot from @BotFather
2. Accounts on Railway/Render and Vercel
3. Domain (optional, can use platform URLs)

## Step 1: Database Setup

### Option A: Railway PostgreSQL (Recommended)

1. In Railway dashboard, click "New" → "Database" → "Add PostgreSQL"
2. Copy the "Postgres Connection URL"
3. Save it for later (DATABASE_URL)

### Option B: Supabase

1. Create project at supabase.com
2. Go to Settings → Database → Connection string
3. Use "Transaction" mode pooler URL

## Step 2: Backend Deployment (Railway)

1. **Create project**: Railway → New → Empty Project

2. **Add PostgreSQL**: If not done in Step 1

3. **Deploy backend**:
   - Click "New" → "GitHub Repo"
   - Select your repository
   - Railway auto-detects Python

4. **Environment variables** (Railway Variables):
   ```
   APP_ENV=production
   DATABASE_URL=${{Postgres.DATABASE_URL}}  # Auto-filled if Railway Postgres
   JWT_SECRET=your-256-bit-secret-here
   BOT_TOKEN=your-bot-token
   MINI_APP_URL=https://your-frontend.vercel.app
   BACKEND_URL=https://your-backend.up.railway.app
   TELEGRAM_AUTH_MOCK=false
   CORS_ORIGINS=https://your-frontend.vercel.app
   ```

5. **Generate JWT_SECRET**:
   ```bash
   openssl rand -base64 32
   ```

6. **Run migrations** (Railway CLI or dashboard):
   ```bash
   railway run -- alembic upgrade head
   ```
   Or create a startup command in Railway: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

7. **Health check**: Visit `https://your-backend.up.railway.app/health`

## Step 3: Frontend Deployment (Vercel)

1. **Push frontend code to GitHub** (if separate repo) or use monorepo

2. **Vercel setup**:
   - Import project from GitHub
   - Framework: `Vite`
   - Build command: `npm run build`
   - Output directory: `dist`
   - Root directory: `frontend` (if monorepo)

3. **Environment variables**:
   ```
   VITE_API_URL=https://your-backend.up.railway.app
   ```

4. **Deploy**: Vercel auto-deploys on push

5. **Copy the deployed URL** for backend CORS and bot Mini App URL

## Step 4: Bot Deployment (Railway Worker)

Option 1: **Same Railway project** (separate service)
1. Add new service to existing project
2. Use same repo, but override start command:
   ```
   python -m bot.bot.main
   ```
3. Use same environment variables as backend
4. Set no health check (bot doesn't expose HTTP)

Option 2: **Separate Railway project**
- Same steps as backend, but start command is bot

Option 3: **Render** (alternative)
1. Create new Web Service
2. Build command: `pip install -r requirements.txt`
3. Start command: `python -m bot.bot.main`
4. Environment variables same as above

## Step 5: Configure Telegram Mini App

1. Go to @BotFather
2. Send `/mybots`
3. Select your bot
4. "Bot Settings" → "Menu Button" → "Configure menu button"
5. Set button text: "📝 Пульс"
6. Set URL: `https://your-frontend.vercel.app`

7. Test: Open bot in Telegram, click menu button

## Step 6: Verify Deployment

Checklist:
- [ ] Backend health endpoint works
- [ ] Frontend loads
- [ ] Mini App opens from Telegram
- [ ] Can create Pulse entry
- [ ] Entry appears in History
- [ ] Telegram auth works (not mock)
- [ ] Weekly reflection works (placeholder)
- [ ] Goals can be created
- [ ] Database persists between deploys

## Database Migrations

### First deploy:
```bash
# Railway CLI
railway login
railway link
railway run -- alembic upgrade head
```

### Subsequent migrations:
1. Commit migration files
2. Deploy backend
3. Run `railway run -- alembic upgrade head`

Or set startup command to auto-run migrations:
```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Environment Variables Reference

| Variable | Local Dev | Production | Description |
|----------|-----------|------------|-------------|
| APP_ENV | `development` | `production` | Environment mode |
| DATABASE_URL | `sqlite:///./app.db` | `postgresql://...` | Database connection |
| JWT_SECRET | `change-me` | Random 32+ chars | JWT signing key |
| BOT_TOKEN | From BotFather | Same | Telegram bot token |
| MINI_APP_URL | `http://localhost:5173` | Vercel URL | Frontend URL |
| BACKEND_URL | `http://localhost:8000` | Railway URL | Backend URL |
| TELEGRAM_AUTH_MOCK | `true` | `false` | Enable real Telegram auth |
| CORS_ORIGINS | Auto | `https://...` | Allowed frontend origins |
| AI_API_KEY | Optional | Optional | OpenAI/Anthropic key |

## Troubleshooting

### CORS errors:
- Check CORS_ORIGINS includes exact Vercel URL (no trailing slash)
- Check MINI_APP_URL matches Vercel URL

### Database connection fails:
- Verify DATABASE_URL format
- Check PostgreSQL is "Available" in Railway
- Ensure SSL is not required (Railway provides SSL automatically)

### Bot doesn't respond:
- Check BOT_TOKEN is correct
- Ensure only one bot instance is running
- Check logs: `railway logs`

### Mini App doesn't load:
- Verify Mini App URL in BotFather matches Vercel URL
- Check HTTPS (required for Mini Apps)
- Check backend health endpoint

## Beta Testing Checklist

Before inviting users:
- [ ] Create at least 5 Pulse entries yourself
- [ ] Create one goal in each horizon
- [ ] Test Weekly Reflection
- [ ] Test Goal Review
- [ ] Verify data persists after redeploy
- [ ] Test user deletion flow

## Admin Commands

### Delete user (emergency):
```bash
railway run -- python -c "
from app.database import SessionLocal
from app.models import User
db = SessionLocal()
user = db.query(User).filter(User.telegram_user_id == 'USER_ID').first()
if user:
    db.delete(user)
    db.commit()
    print('Deleted')
else:
    print('Not found')
"
```

## BotFather Pre-Start Setup

Before inviting beta users, configure the bot profile via @BotFather:

### 1. /setname
```
Пульс — мягкое самонаблюдение
```

### 2. /setabouttext
Short text shown in bot profile:
```
Мягкое самонаблюдение в Telegram: Пульс дня, цели, динамика и недельные отражения.
```

### 3. /setdescription
Full description shown before /start:
```
Приложение для мягкого самонаблюдения.

Каждый день можно за 1 минуту отметить настроение, энергию, тревогу, короткий инсайт и один фокус на завтра.

Также можно задать цели на месяц, год, 3 года, 5 лет и описать "жизнь мечты".

Это ранняя тестовая версия. Приложение не является медицинской или психологической помощью.
```

### 4. /setcommands
```
start - начать и открыть приложение
pulse - записать Пульс дня
goals - открыть цели и ориентиры
history - посмотреть историю записей
feedback - отправить обратную связь
help - как пользоваться
```

### 5. /setmenubutton
- Text: `Открыть приложение`
- URL: `https://frontend-mu-ecru-12.vercel.app` (replace with production URL)

### 6. /setuserpic
Upload a bot avatar image.

---

## Rollback

If critical issue:
1. Railway: "Deployments" → click previous deploy → "Deploy"
2. Vercel: "Deployments" → promote previous deployment
3. Database: Restore from Railway backups (if enabled)

## Cost Estimation (Railway + Vercel)

- Railway Starter: ~$5/month
- Railway PostgreSQL: ~$5/month  
- Vercel Hobby: Free
- **Total: ~$10/month** for beta
