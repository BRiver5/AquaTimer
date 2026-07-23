DEVICE_ID = "33333333-3333-3333-3333-333333333333"
HEADERS = {"X-Device-Id": DEVICE_ID}


def test_create_list_update_delete_reminder(client):
    created = client.post("/reminders", headers=HEADERS, json={"hour": 9, "minute": 0}).json()
    assert created["hour"] == 9
    assert created["enabled"] is True

    listed = client.get("/reminders", headers=HEADERS).json()
    assert len(listed) == 1

    updated = client.put(
        f"/reminders/{created['id']}",
        headers=HEADERS,
        json={"enabled": False, "notification_identifier": "abc-123"},
    ).json()
    assert updated["enabled"] is False
    assert updated["notification_identifier"] == "abc-123"

    delete_response = client.delete(f"/reminders/{created['id']}", headers=HEADERS)
    assert delete_response.status_code == 204

    listed_after = client.get("/reminders", headers=HEADERS).json()
    assert len(listed_after) == 0


def test_update_missing_reminder_404s(client):
    response = client.put("/reminders/9999", headers=HEADERS, json={"enabled": False})
    assert response.status_code == 404
