# AquaTimer: Drink Water Alarm

**Hydration on your schedule.**

A minimal, local-first water-intake tracker with scheduled reminders, built for
a first Google Play submission.

## Structure

```
AquaTimer/
├── mobile/    Expo (React Native + TypeScript) app — the shipped artifact
└── backend/   FastAPI + SQLAlchemy + SQLite reference service
```

### `mobile/` — the app users install

Fully self-contained: all data (profile, intake log, reminders) is stored
on-device via `expo-sqlite`. It makes **zero network calls** and needs no
backend running to work, review, or ship. See `mobile/src/data/repository.ts`
for the storage contract and `mobile/src/data/local/` for the SQLite-backed
implementation actually in use.

```bash
cd mobile
npm install
npx expo start
```

### `backend/` — parity reference, not required at runtime

A complete FastAPI implementation of the same data model (`User`,
`IntakeEntry`, `Reminder`), matched 1:1 against `mobile/src/data/remote/RestRepository.ts`.
It exists so a future server-synced release can switch the mobile app's data
source with a single env var (`EXPO_PUBLIC_DATA_SOURCE=rest`, see
`mobile/src/data/config.ts`) instead of a rewrite. See `backend/README.md` to
run it standalone.

## Notes for Google Play submission

- No privacy policy is included in this repo by design — Play Console still
  requires a hosted privacy policy URL in the store listing once you declare
  the anonymous device identifier, even though the app itself makes no
  network calls. That's a store-listing task, not app code.
- The shipped app's honest Data Safety answer is "no data collected/shared"
  as long as it stays on `DATA_SOURCE=local` (the default).
