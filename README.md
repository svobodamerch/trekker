# Self-Observation App

Telegram Mini App + Bot для мягкого самонаблюдения, ежедневного Pulse и целеполагания на горизонты от месяца до "жизни мечты".

## Продуктовая концепция

Продукт соединяет три слоя:
1. **Ежедневный Pulse** — настроение, энергия, тревога, инсайт, благодарность, одно обязательство
2. **Мягкая рефлексия** — история, динамика, недельные AI-инсайты, отсутствие осуждения за пропуски
3. **Жизненная траектория** — цели на месяц, год, 3 года, 5 лет и Dream Life

Формула: Telegram собирает короткий Пульс, Mini App показывает динамику и цели, AI помогает увидеть связь между состоянием и направлением.

## Project Structure

```
self-observation-app/
  backend/      FastAPI + SQLite
  frontend/     React + Vite + Tailwind CSS
  bot/          aiogram 3 Telegram bot
```

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

Health check: `curl http://localhost:8000/health`

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### 3. Bot (локально без Telegram)

```bash
cd bot
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m bot.main
```

## Telegram Mini App Setup

### Шаг 1: Создайте бота в BotFather

1. Напишите @BotFather в Telegram
2. Отправьте `/newbot`
3. Укажите название бота (например, "Мой Пульс")
4. Укажите username (например, `mypulse_bot`)
5. Получите **BOT_TOKEN** — сохраните его в `.env`

### Шаг 2: Настройте Mini App

В BotFather:

1. Отправьте `/mybots`
2. Выберите вашего бота
3. Нажмите **Bot Settings**
4. Нажмите **Menu Button**
5. Нажмите **Configure menu button**
6. Выберите **Web App**
7. Укажите:
   - **Button text**: "Открыть"
   - **URL**: ваш URL (см. ниже про туннель)

### Шаг 3: Настройте туннель для локальной разработки

Telegram Mini App требует HTTPS URL. Используйте ngrok или Cloudflare Tunnel:

**Вариант A: Cloudflare Tunnel (рекомендуется)**

```bash
# Установите cloudflared
brew install cloudflared

# Создайте туннель
cloudflared tunnel --url http://localhost:5174

# Получите URL вида https://xxxx.trycloudflare.com
```

**Вариант B: ngrok**

```bash
# Установите ngrok
brew install ngrok

# Запустите туннель
ngrok http 5174

# Получите URL вида https://xxxx.ngrok-free.app
```

### Шаг 4: Настройте окружение

Создайте `.env` в корне проекта:

```bash
# Общие
APP_ENV=development

# Backend
DATABASE_URL=sqlite:///./app.db
JWT_SECRET=your-secret-key-change-in-production

# Telegram
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
MINI_APP_URL=https://your-tunnel-url.trycloudflare.com
TELEGRAM_AUTH_MOCK=false  # true для локальной разработки без Telegram

# AI (опционально)
AI_API_KEY=your-openai-key
AI_MODEL=gpt-4
```

### Шаг 5: Запустите с туннелем

```bash
# 1. Запустите backend
 cd backend && source .venv/bin/activate && uvicorn app.main:app --reload

# 2. В другом терминале — запустите frontend
 cd frontend && npm run dev

# 3. В третьем терминале — запустите туннель
 cloudflared tunnel --url http://localhost:5174

# 4. Обновите MINI_APP_URL в .env на URL из туннеля

# 5. Запустите бота
 cd bot && source .venv/bin/activate && python -m bot.main
```

### Шаг 6: Тестирование в Telegram

1. Откройте бота в Telegram
2. Нажмите "Start" или отправьте `/start`
3. Нажмите кнопку "Открыть" или "Записать Пульс"
4. Mini App должен открыться с авторизацией
5. Проверьте в консоли браузера (в Telegram WebView) логи `[Telegram]` и `[Auth]`

## Environment Variables

| Переменная | Описание | Обязательная |
|-----------|----------|-------------|
| `BOT_TOKEN` | Токен от @BotFather | Да |
| `MINI_APP_URL` | HTTPS URL Mini App | Да |
| `DATABASE_URL` | Путь к SQLite | Нет (default: `sqlite:///./app.db`) |
| `JWT_SECRET` | Секрет для токенов | Нет (default: `change-me`) |
| `TELEGRAM_AUTH_MOCK` | Mock auth для dev | Нет (default: `true`) |
| `AI_API_KEY` | OpenAI ключ | Нет |

## Tech Stack

- **Frontend**: React 18, Vite, Tailwind CSS, Telegram WebApp SDK
- **Backend**: Python 3.11+, FastAPI, SQLModel/SQLAlchemy 2, Alembic, SQLite (MVP)
- **Bot**: aiogram 3
- **Auth**: Telegram initData validation + JWT

## Debug режим

В режиме разработки (DEV) на Home page показывается debug-панель с информацией:
- Режим авторизации (telegram / mock / none)
- Наличие initData
- Наличие JWT токена
- Первые 30 символов initData

## Команды бота

- `/start` — Главное меню с навигацией
- `/pulse` — Открыть запись Пульса
- `/goals` — Открыть цели
- `/history` — История и динамика
