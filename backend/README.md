# AquaTimer backend (reference implementation)

FastAPI + SQLAlchemy + SQLite service implementing the same `User` / `IntakeEntry` /
`Reminder` data model the mobile app keeps on-device by default. **The shipped
mobile app does not require this service to be running** — it's a fully working,
independently runnable parity implementation for a future server-synced release
(see `mobile/src/data/remote/RestRepository.ts` and `mobile/src/data/config.ts`).

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is served at `http://127.0.0.1:8000`, with interactive docs at `/docs`.
Data persists to `./aquatimer.db` (override with the `AQUATIMER_DATABASE_URL`
env var — see `.env.example`).

## Test

```bash
pytest
```

## Docker

```bash
docker build -t aquatimer-backend .
docker run -p 8000:8000 -v aquatimer-data:/data aquatimer-backend
```

## Auth model

No login/registration. Every request must include an `X-Device-Id` header —
the same anonymous UUID the mobile app generates and stores locally. There is
no verification that a given UUID "belongs" to a given caller; this mirrors
the mobile app's own no-account design and is only appropriate because no
sensitive data is stored per profile.

## Endpoints

| Method & path | Purpose |
|---|---|
| `POST /users/init` | Create (or fetch, idempotently) the profile for this device ID |
| `GET /users/me` | Fetch the profile (auto-creates if missing) |
| `PUT /users/me` | Partial-update goal / weight / units / accent / container / flags |
| `POST /intake` | Log a water entry |
| `GET /intake/today?range_start=&range_end=` | Entries within an explicit ISO instant range |
| `DELETE /intake/{id}` | Remove one entry |
| `DELETE /intake` | Bulk-delete all entries for this device (added beyond the original spec list so "Clear all history" has an exact REST equivalent to the local repository's `clearAllHistory()`) |
| `GET /intake/weekly?range_start=` | Per-day totals for the 7 days starting at `range_start` |
| `GET /intake/stats` | All-time average/streak/day-count |
| `GET /reminders`, `POST /reminders`, `PUT /reminders/{id}`, `DELETE /reminders/{id}` | Reminder CRUD |

### Known simplifications

- **Timezone handling**: `range_start`/`range_end` are explicit ISO instants
  computed client-side (the client already knows the user's local midnight in
  UTC terms), so `/intake/today` is exact. `/intake/weekly` and `/intake/stats`
  group by the **UTC calendar date** of `logged_at` rather than the caller's
  local calendar date — correct for UTC users, off by up to a few hours near
  midnight for others. Fine for a not-yet-shipped parity/sync path; revisit
  with a client-supplied UTC offset if this backend is ever wired in for real.
- **No Alembic**: schema is created via `Base.metadata.create_all()` on
  startup. Fine for this MVP's single fixed schema; add real migrations
  before evolving the schema after any data exists in production.
