def incident_payload(equipment_id, **overrides):
    return {
        "equipment_id": equipment_id,
        "title": "Probe channel reads zero",
        "detail": "Channel B stayed flat during the afternoon practical.",
        "severity": "high",
        "reported_by": "Lab coordinator",
        **overrides,
    }


def test_health_and_readiness(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").json() == {"status": "ready"}


def test_equipment_create_and_list(client, equipment):
    assert equipment["status"] == "operational"
    assert client.get("/api/equipment").json() == [equipment]
    assert client.get(f"/api/equipment/{equipment['id']}").json() == equipment


def test_duplicate_equipment_code_is_rejected(client, equipment):
    response = client.post(
        "/api/equipment",
        json={
            "code": "ece-osc-04",
            "name": "Duplicate",
            "room": "Lab 2",
            "category": "Test",
        },
    )
    assert response.status_code == 409


def test_incident_marks_equipment_offline(client, equipment):
    response = client.post("/api/incidents", json=incident_payload(equipment["id"]))
    assert response.status_code == 201
    assert response.json()["status"] == "open"
    assert client.get(f"/api/equipment/{equipment['id']}").json()["status"] == "offline"
    assert client.get("/api/summary").json()["open_incidents"] == 1


def test_resolving_last_incident_restores_equipment(client, equipment):
    incident = client.post(
        "/api/incidents", json=incident_payload(equipment["id"])
    ).json()
    response = client.put(
        f"/api/incidents/{incident['id']}", json={"status": "resolved"}
    )
    assert response.status_code == 200
    assert response.json()["resolved_at"] is not None
    assert (
        client.get(f"/api/equipment/{equipment['id']}").json()["status"]
        == "operational"
    )
    assert client.get("/api/summary").json()["resolved_incidents"] == 1


def test_low_priority_incident_needs_attention(client, equipment):
    client.post(
        "/api/incidents", json=incident_payload(equipment["id"], severity="low")
    )
    assert (
        client.get(f"/api/equipment/{equipment['id']}").json()["status"] == "attention"
    )


def test_filters_and_delete(client, equipment):
    low = client.post(
        "/api/incidents", json=incident_payload(equipment["id"], severity="low")
    ).json()
    high = client.post("/api/incidents", json=incident_payload(equipment["id"])).json()
    assert len(client.get("/api/incidents?severity=high").json()) == 1
    assert len(client.get(f"/api/incidents?equipment_id={equipment['id']}").json()) == 2
    assert client.delete(f"/api/incidents/{high['id']}").status_code == 204
    assert (
        client.get(f"/api/equipment/{equipment['id']}").json()["status"] == "attention"
    )
    assert client.delete(f"/api/incidents/{low['id']}").status_code == 204
    assert (
        client.get(f"/api/equipment/{equipment['id']}").json()["status"]
        == "operational"
    )


def test_missing_equipment_and_incident(client):
    assert client.get("/api/equipment/999").status_code == 404
    assert client.get("/api/incidents/999").status_code == 404
    assert client.post("/api/incidents", json=incident_payload(999)).status_code == 404


def test_invalid_payload_is_rejected(client):
    response = client.post(
        "/api/equipment",
        json={"code": "bad code", "name": "x", "room": "x", "category": "x"},
    )
    assert response.status_code == 422


def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
