# StudyFlow API

A backend for a personal study planner. It stores your subjects, tasks, deadlines and extracurricular goals, builds a daily schedule, and (as the project grows) uses AI to suggest what to do next and sends reminders to your phone and email.

Built with **FastAPI**, **SQLAlchemy** and **MySQL**.

## Status

Early development (v0.1.0).

| Area | State |
|---|---|
| Project setup, config, database connection | Done |
| Database tables (users, subjects, tasks, activities, blocks, suggestions, notifications) | Done |
| Request/response schemas | Done |
| Users endpoints and health check | Done |
| Tasks, subjects, activities and schedule endpoints | Planned |
| AI suggestions (Claude API) | Planned |
| Notifications: Telegram, Gmail | Planned |
| Notifications: Google Calendar | Code written, needs testing |
| Scheduler (morning plan, reminders, evening review) | Planned |

## Features (planned)

- Track subjects, tasks, deadlines and estimated study time
- Daily schedule of study blocks, breaks and activities
- AI coach that suggests the next action and a plan for the day
- Extracurricular goals, such as "gym 3 times a week"
- Reminders through Telegram, Gmail and Google Calendar
- Skip tracking, so the AI sees what you keep avoiding
- Morning plan and evening review

## Tech stack

- Python 3.12
- FastAPI and Uvicorn
- SQLAlchemy 2.0 with MySQL (PyMySQL driver)
- Pydantic and pydantic-settings
- APScheduler (timed jobs)
- Anthropic Claude API (AI suggestions)
- Telegram Bot API, Gmail SMTP, Google Calendar API

## Project structure

```
studyflow-api/
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI app and endpoints
│   ├── config.py             # settings loaded from .env
│   ├── db.py                 # database engine, sessions, init_db()
│   ├── database_models.py    # SQLAlchemy tables
│   ├── schemas.py            # Pydantic request/response shapes
│   └── services/
│       ├── __init__.py
│       └── calendar_sync.py  # Google Calendar events
├── .env                      # secrets (never commit)
├── .gitignore
├── credentials.json          # Google OAuth client (never commit)
├── token.json                # created on first Google login (never commit)
├── requirements.txt
└── README.md
```

Planned additions: `app/routers/` (tasks, schedule, activities, ai), `app/services/ai_coach.py`, `app/services/notifier.py`, `app/jobs/scheduler.py`.

## Getting started (Windows)

### 1. Requirements

- Python 3.12 (3.14 may lack ready-made packages)
- MySQL server running locally
- Git

### 2. Clone and create the environment

```
git clone https://github.com/YOUR_USERNAME/studyflow-api.git
cd studyflow-api
py -3.12 -m venv myenv
myenv\Scripts\activate
```

Use `py`, not `python`, to create the environment. If you have MSYS2 installed, `python` may point to a Linux-style Python that creates a `bin` folder instead of `Scripts`.

### 3. Install packages

```
pip install -r requirements.txt
```

If you are starting without a `requirements.txt`:

```
pip install fastapi "uvicorn[standard]" sqlalchemy pymysql cryptography pydantic-settings apscheduler anthropic requests python-dotenv google-api-python-client google-auth-oauthlib google-auth-httplib2
pip freeze > requirements.txt
```

### 4. Create the database

In MySQL:

```sql
CREATE DATABASE studyflow_api CHARACTER SET utf8mb4;
CREATE USER 'studyflow'@'localhost' IDENTIFIED BY 'a-strong-password';
GRANT ALL PRIVILEGES ON studyflow_api.* TO 'studyflow'@'localhost';
FLUSH PRIVILEGES;
```

The tables are created automatically when the server starts.

### 5. Configure `.env`

Create a file named `.env` in the project root:

```
DATABASE_URL=mysql+pymysql://studyflow:a-strong-password@127.0.0.1:3306/studyflow_api?charset=utf8mb4

ANTHROPIC_API_KEY=
TELEGRAM_TOKEN=
TELEGRAM_CHAT_ID=

GMAIL_ADDRESS=
GMAIL_APP_PASSWORD=
```

Only `DATABASE_URL` is required to start the server. If the password contains special characters such as `@` or `#`, URL-encode them (`@` becomes `%40`).

| Variable | What it is |
|---|---|
| `DATABASE_URL` | MySQL connection string |
| `ANTHROPIC_API_KEY` | Key from https://console.anthropic.com |
| `TELEGRAM_TOKEN` | Bot token from @BotFather on Telegram |
| `TELEGRAM_CHAT_ID` | Your numeric chat ID (send your bot a message, then open `https://api.telegram.org/botYOUR_TOKEN/getUpdates`) |
| `GMAIL_ADDRESS` | The Gmail account that sends email |
| `GMAIL_APP_PASSWORD` | A Google app password (needs 2-Step Verification) |

Optional settings with defaults: `ANTHROPIC_MODEL`, `TIMEZONE` (Africa/Nairobi), `MORNING_PLAN_TIME` (07:00), `EVENING_REVIEW_TIME` (21:30), `REMINDER_MINUTES_BEFORE` (15).

### 6. Run the server

From the project root, with `(myenv)` active:

```
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for the interactive API page.

## API endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | Welcome message |
| GET | `/health` | Checks that the API and database are working |
| GET | `/users` | List users |
| POST | `/users` | Create a user |

Create your first user with `POST /users` on the `/docs` page, because every other table points to a user.

## Google Calendar setup (optional)

1. In https://console.cloud.google.com, create a project and enable the **Google Calendar API**.
2. Configure the OAuth consent screen as **External** and keep it in **Testing** mode.
3. Add your own Gmail address under **Test users**. Without this, login fails with `Error 403: access_denied`.
4. Create an **OAuth client ID** of type **Desktop app**, download the JSON and save it as `credentials.json` in the project root.
5. Run once, and approve access in the browser:

```
python -c "from app.services.calendar_sync import _service; _service()"
```

`token.json` is created automatically. In Testing mode the login expires after about 7 days. Delete `token.json` and repeat step 5 when that happens.

## Data notes

- Store all times in **UTC** and convert to the user's timezone only for display and for AI prompts.
- `Task.status`: `todo`, `done`, `skipped`, `postponed`
- `Block.type`: `study`, `break`, `activity`, `sleep`
- `create_all()` only creates missing tables. It does not change existing ones. While testing, drop and recreate the tables after changing a model. For real data, use Alembic migrations.

## Security

- Never commit `.env`, `credentials.json`, `token.json`, `myenv/` or `*.db`. They are listed in `.gitignore`.
- Use a dedicated MySQL user, not `root`.
- `GET /users` returns every user's email. Remove it or protect it with login before deploying or adding other users.
- If a key or token is ever pushed to GitHub, revoke it and create a new one. Deleting the file later does not remove it from the history.

## Roadmap

1. Tasks, subjects and activities endpoints
2. Schedule generation
3. AI suggestion endpoint (`/ai/suggest`)
4. Telegram and Gmail notifications
5. Scheduler jobs: morning plan, block reminders, evening review
6. Login and multiple users
7. Simple web or mobile-friendly frontend

## Troubleshooting

| Problem | Fix |
|---|---|
| `myenv` has no `Scripts` or `activate.bat` | Recreate it with `py -m venv myenv` |
| `Could not import module "main"` | Run `uvicorn app.main:app --reload` from the project root |
| `ModuleNotFoundError: app.services...` | Check that `app/services/__init__.py` exists |
| `Unknown database` | The name in `DATABASE_URL` must match the database you created |
| Google `Error 403: access_denied` | Add your Gmail as a test user on the OAuth consent screen |
| `field required` for `DATABASE_URL` | `.env` is missing, misspelled, or you are running from the wrong folder |

## License

Add a license of your choice before sharing the project publicly.