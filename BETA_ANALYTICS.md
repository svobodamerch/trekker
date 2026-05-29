# Beta Analytics Queries

Run these SQL queries to track beta metrics.

## Connection

```bash
# Railway PostgreSQL
railway connect postgres

# Or use connection string
psql $DATABASE_URL
```

## Core Metrics

### Total users
```sql
SELECT COUNT(*) as total_users FROM users;
```

### Activated users (created at least 1 Pulse entry)
```sql
SELECT COUNT(DISTINCT user_id) as activated_users 
FROM entries 
WHERE entry_type = 'pulse';
```

### Entries per user (distribution)
```sql
SELECT 
    user_id,
    telegram_user_id,
    COUNT(*) as entry_count
FROM entries 
JOIN users ON entries.user_id = users.id
WHERE entry_type = 'pulse'
GROUP BY user_id, telegram_user_id
ORDER BY entry_count DESC;
```

### Users with 3+ entries (engaged users)
```sql
SELECT 
    user_id,
    telegram_user_id,
    COUNT(*) as entry_count
FROM entries 
JOIN users ON entries.user_id = users.id
WHERE entry_type = 'pulse'
GROUP BY user_id, telegram_user_id
HAVING COUNT(*) >= 3
ORDER BY entry_count DESC;
```

### Users with goals
```sql
SELECT 
    users.telegram_user_id,
    COUNT(goals.id) as goal_count,
    STRING_AGG(goals.horizon, ', ') as horizons
FROM users
JOIN goals ON users.id = goals.user_id
WHERE goals.status = 'active'
GROUP BY users.telegram_user_id;
```

### Users who requested Weekly Reflection
```sql
SELECT 
    users.telegram_user_id,
    COUNT(ai_analyses.id) as reflection_count,
    MAX(ai_analyses.created_at) as last_reflection_at
FROM users
JOIN ai_analyses ON users.id = ai_analyses.user_id
WHERE ai_analyses.analysis_type = 'weekly_reflection'
GROUP BY users.telegram_user_id;
```

### Last activity per user
```sql
SELECT 
    users.telegram_user_id,
    MAX(entries.created_at) as last_entry_at,
    MAX(ai_analyses.created_at) as last_analysis_at,
    MAX(goals.last_reviewed_at) as last_goal_review_at
FROM users
LEFT JOIN entries ON users.id = entries.user_id
LEFT JOIN ai_analyses ON users.id = ai_analyses.user_id
LEFT JOIN goals ON users.id = goals.user_id
GROUP BY users.telegram_user_id
ORDER BY last_entry_at DESC NULLS LAST;
```

### Churned users (no entry in 7+ days)
```sql
SELECT 
    users.telegram_user_id,
    MAX(entries.created_at) as last_entry_at,
    EXTRACT(DAY FROM NOW() - MAX(entries.created_at)) as days_since_last_entry
FROM users
JOIN entries ON users.id = entries.user_id
GROUP BY users.telegram_user_id
HAVING MAX(entries.created_at) < NOW() - INTERVAL '7 days'
ORDER BY last_entry_at DESC;
```

### Daily active users (by entry creation)
```sql
SELECT 
    DATE(entries.created_at) as date,
    COUNT(DISTINCT entries.user_id) as dau
FROM entries
WHERE entries.created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE(entries.created_at)
ORDER BY date DESC;
```

### Goal creation by horizon
```sql
SELECT 
    horizon,
    COUNT(*) as count,
    COUNT(DISTINCT user_id) as unique_users
FROM goals
WHERE status = 'active'
GROUP BY horizon
ORDER BY count DESC;
```

### Average entries per day (engagement)
```sql
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_entries,
    COUNT(DISTINCT user_id) as unique_users,
    ROUND(COUNT(*)::float / NULLIF(COUNT(DISTINCT user_id), 0), 2) as avg_entries_per_user
FROM entries
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

### AI Reflection usage (placeholder vs real)
```sql
SELECT 
    analysis_type,
    COUNT(*) as total,
    SUM(CASE WHEN raw_output->>'is_placeholder' = 'true' THEN 1 ELSE 0 END) as placeholder_count,
    SUM(CASE WHEN raw_output->>'is_placeholder' = 'false' THEN 1 ELSE 0 END) as real_count
FROM ai_analyses
GROUP BY analysis_type;
```

### Goal review frequency
```sql
SELECT 
    users.telegram_user_id,
    COUNT(goal_versions.id) as version_count,
    MAX(goals.last_reviewed_at) as last_review_at
FROM users
LEFT JOIN goals ON users.id = goals.user_id
LEFT JOIN goal_versions ON goals.id = goal_versions.goal_id
GROUP BY users.telegram_user_id
HAVING COUNT(goal_versions.id) > 0
ORDER BY version_count DESC;
```

## Quick Health Check Script

```sql
-- Run this daily during beta
SELECT 
    (SELECT COUNT(*) FROM users) as total_users,
    (SELECT COUNT(DISTINCT user_id) FROM entries WHERE entry_type = 'pulse') as activated,
    (SELECT COUNT(*) FROM entries WHERE created_at > NOW() - INTERVAL '24 hours') as entries_today,
    (SELECT COUNT(*) FROM goals WHERE status = 'active') as active_goals,
    (SELECT COUNT(*) FROM ai_analyses WHERE created_at > NOW() - INTERVAL '24 hours') as analyses_today;
```

## Export User List for Outreach

```sql
-- CSV export for manual outreach to inactive users
COPY (
    SELECT 
        users.telegram_user_id,
        users.first_name,
        MAX(entries.created_at) as last_active,
        COUNT(entries.id) as total_entries
    FROM users
    LEFT JOIN entries ON users.id = entries.user_id
    GROUP BY users.telegram_user_id, users.first_name
    ORDER BY last_active DESC NULLS LAST
) TO STDOUT WITH CSV HEADER;
```

## Notes

- Run queries in Railway dashboard or via `railway connect postgres`
- For privacy, only aggregate data should leave production
- Never export raw entry text or personal insights
- Focus on engagement metrics: DAU, entries/user, goal creation
