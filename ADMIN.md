# Admin Guide

Managing the closed beta deployment.

## Delete User Data

When a user requests data deletion:

### Option 1: Using Railway CLI
```bash
# Set up Railway CLI first
railway login
railway link

# Run deletion script
railway run -- python scripts/delete_user.py <telegram_user_id>
```

### Option 2: Direct database access
```bash
railway connect postgres

# Then run SQL
BEGIN;
-- Find user ID
SELECT id FROM users WHERE telegram_user_id = 'USER_ID';

-- Delete related records (cascade manually)
DELETE FROM ai_analyses WHERE user_id = USER_ID;
DELETE FROM entries WHERE user_id = USER_ID;
DELETE FROM goals WHERE user_id = USER_ID;
DELETE FROM users WHERE id = USER_ID;
COMMIT;
```

## View User Summary

```bash
railway run -- python -c "
from app.database import SessionLocal
from app.models import User, Entry, Goal

db = SessionLocal()
user = db.query(User).filter(User.telegram_user_id == 'USER_ID').first()
if user:
    entries = db.query(Entry).filter(Entry.user_id == user.id).count()
    goals = db.query(Goal).filter(Goal.user_id == user.id).count()
    print(f'User: {user.telegram_user_id}')
    print(f'Entries: {entries}')
    print(f'Goals: {goals}')
    print(f'Created: {user.created_at}')
else:
    print('User not found')
"
```

## Check Database Health

```bash
railway run -- python -c "
from app.database import SessionLocal
from app.models import User, Entry, Goal

db = SessionLocal()
print('Database connection: OK')
print(f'Users: {db.query(User).count()}')
print(f'Entries: {db.query(Entry).count()}')
print(f'Goals: {db.query(Goal).count()}')
"
```

## Beta Monitoring Dashboard

Run daily during beta:

```bash
railway run -- python -c "
from app.database import SessionLocal
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models import User, Entry, Goal, AIAnalysis

db = SessionLocal()

print('=== BETA DAILY REPORT ===')
print(f'Date: {datetime.utcnow().strftime(\"%Y-%m-%d\")}')
print()

# New users today
new_users = db.query(User).filter(
    User.created_at >= datetime.utcnow() - timedelta(days=1)
).count()
print(f'New users today: {new_users}')

# Total active users
total_users = db.query(User).count()
activated = db.query(Entry.user_id).distinct().count()
print(f'Total users: {total_users}')
print(f'Activated (1+ entry): {activated}')
print(f'Activation rate: {activated/total_users*100:.1f}%')

# Today's activity
entries_today = db.query(Entry).filter(
    Entry.created_at >= datetime.utcnow() - timedelta(days=1)
).count()
print(f'Entries created today: {entries_today}')

# Weekly reflections
reflections_today = db.query(AIAnalysis).filter(
    AIAnalysis.created_at >= datetime.utcnow() - timedelta(days=1),
    AIAnalysis.analysis_type == 'weekly_reflection'
).count()
print(f'Weekly reflections today: {reflections_today}')

print()
print('=== TOP ACTIVE USERS ===')
active_users = db.query(
    User.telegram_user_id,
    func.count(Entry.id).label('entry_count')
).join(Entry).group_by(User.id).order_by(func.count(Entry.id).desc()).limit(5).all()

for telegram_id, count in active_users:
    print(f'  {telegram_id}: {count} entries')
"
```

## Emergency Procedures

### Database is full
1. Railway dashboard → PostgreSQL → "Metrics"
2. Check storage usage
3. If approaching limit, upgrade plan or prune old data

### Bot is not responding
1. Check Railway logs: `railway logs`
2. Verify BOT_TOKEN is correct
3. Ensure only one bot instance running
4. Restart service: Railway dashboard → "Deployments" → "Redeploy"

### Frontend 404 errors
1. Check Vercel deployment status
2. Verify build command: `npm run build`
3. Check output directory: `dist`
4. Redeploy from Vercel dashboard

### CORS errors
1. Check backend CORS_ORIGINS env var includes exact Vercel URL
2. No trailing slashes in URLs
3. HTTPS required in production

## Privacy & Data Handling

### What to do when user asks for data export:
1. Use SQL queries from BETA_ANALYTICS.md
2. Export only their records
3. Send as JSON or CSV
4. Do not include other users' data

### What to do when user reports PII leak:
1. Immediately delete the problematic record
2. Check logs for exposure
3. Notify user of remediation
4. Review data handling practices

## Communication Templates

### Data deletion confirmation
```
Ваши данные были удалены из приложения.

Удалено:
- Профиль пользователя
- Все записи Пульс
- Цели и история версий
- AI-анализы
- Настройки

Данные нельзя восстановить.
Спасибо за участие в тестировании.
```

### Data export format
```json
{
  "user_id": "...",
  "exported_at": "...",
  "entries": [...],
  "goals": [...],
  "analyses": [...]
}
```
