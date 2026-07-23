from datetime import datetime, timedelta, timezone

DEVICE_ID = "22222222-2222-2222-2222-222222222222"
HEADERS = {"X-Device-Id": DEVICE_ID}


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def test_add_and_fetch_today_intake(client):
    now = datetime.now(timezone.utc)
    client.post("/intake", headers=HEADERS, json={"amount_ml": 250, "logged_at": _iso(now)})
    client.post("/intake", headers=HEADERS, json={"amount_ml": 300, "logged_at": _iso(now)})

    start = now - timedelta(hours=1)
    end = now + timedelta(hours=1)
    response = client.get(
        "/intake/today",
        headers=HEADERS,
        params={"range_start": _iso(start), "range_end": _iso(end)},
    )
    assert response.status_code == 200
    entries = response.json()
    assert len(entries) == 2
    assert sum(e["amount_ml"] for e in entries) == 550


def test_delete_intake_entry(client):
    now = datetime.now(timezone.utc)
    created = client.post(
        "/intake", headers=HEADERS, json={"amount_ml": 200, "logged_at": _iso(now)}
    ).json()

    delete_response = client.delete(f"/intake/{created['id']}", headers=HEADERS)
    assert delete_response.status_code == 204

    start = now - timedelta(hours=1)
    end = now + timedelta(hours=1)
    remaining = client.get(
        "/intake/today",
        headers=HEADERS,
        params={"range_start": _iso(start), "range_end": _iso(end)},
    ).json()
    assert all(e["id"] != created["id"] for e in remaining)


def test_weekly_totals_and_stats(client):
    client.put("/users/me", headers=HEADERS, json={"daily_goal_ml": 500})

    today = datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)

    client.post("/intake", headers=HEADERS, json={"amount_ml": 600, "logged_at": _iso(today)})
    client.post("/intake", headers=HEADERS, json={"amount_ml": 600, "logged_at": _iso(yesterday)})

    range_start = today - timedelta(days=6)
    weekly = client.get(
        "/intake/weekly", headers=HEADERS, params={"range_start": _iso(range_start)}
    ).json()
    assert len(weekly) == 7
    assert any(day["goal_met"] for day in weekly)

    stats = client.get("/intake/stats", headers=HEADERS).json()
    assert stats["total_days_tracked"] == 2
    assert stats["best_streak_days"] == 2


def test_clear_all_history(client):
    now = datetime.now(timezone.utc)
    client.post("/intake", headers=HEADERS, json={"amount_ml": 250, "logged_at": _iso(now)})

    clear_response = client.delete("/intake", headers=HEADERS)
    assert clear_response.status_code == 204

    stats = client.get("/intake/stats", headers=HEADERS).json()
    assert stats["total_days_tracked"] == 0
