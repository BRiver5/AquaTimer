DEVICE_ID = "11111111-1111-1111-1111-111111111111"


def test_init_creates_default_profile(client):
    response = client.post("/users/init", headers={"X-Device-Id": DEVICE_ID})
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == DEVICE_ID
    assert body["daily_goal_ml"] == 2000
    assert body["units"] == "ml"
    assert body["container_type"] == "glass"


def test_get_me_without_header_fails(client):
    response = client.get("/users/me")
    assert response.status_code == 400


def test_update_me_persists_changes(client):
    client.post("/users/init", headers={"X-Device-Id": DEVICE_ID})
    response = client.put(
        "/users/me",
        headers={"X-Device-Id": DEVICE_ID},
        json={"daily_goal_ml": 2500, "accent_color": "sky", "weight_kg": 70},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["daily_goal_ml"] == 2500
    assert body["accent_color"] == "sky"
    assert body["weight_kg"] == 70

    refetched = client.get("/users/me", headers={"X-Device-Id": DEVICE_ID}).json()
    assert refetched["daily_goal_ml"] == 2500
