import hashlib
import hmac
import importlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PACKAGES = ROOT / ".packages"
sys.path.insert(0, str(PACKAGES))
sys.path.insert(0, str(ROOT))

TEST_DB = ROOT / "test_checkout_access.sqlite3"
try:
    TEST_DB.unlink()
except FileNotFoundError:
    pass

os.environ.update(
    {
        "CHECKOUT_DB_PATH": str(TEST_DB),
        "CHECKOUT_PII_SECRET": "test-pii-secret",
        "CHECKOUT_ENV": "development",
        "ENABLE_EXPIRY_WORKER": "0",
        "TELEGRAM_BOT_USERNAME": "fonsequinha_test_bot",
        "TELEGRAM_WEBHOOK_SECRET": "telegram-secret",
        "TELEGRAM_CONSENSUS_CHAT_ID": "-1001234567890",
        "MERCADOPAGO_ACCESS_TOKEN": "dummy-token",
        "MERCADOPAGO_WEBHOOK_SECRET": "mp-secret",
        "MONTHLY_PRICE": "150",
        "COUPON_CODE": "FONSECA5",
        "COUPON_PERCENT": "5",
        "FRONTEND_URL": "https://fonsecatools.com.br",
    }
)

backend = importlib.import_module("app")
backend.app.config.update(TESTING=True)

BUYER = {
    "name": "Cliente Teste",
    "email": "cliente@example.com",
    "phone": "11999998888",
    "cpf": "52998224725",
}


def reset_db():
    backend.init_db()
    with backend.db() as con:
        con.execute("DELETE FROM webhook_events")
        con.execute("DELETE FROM subscriptions")
        con.execute("DELETE FROM trial_tokens")
        con.execute("DELETE FROM users")


def test_cpf_validation():
    assert backend._valid_cpf("529.982.247-25") is True
    assert backend._valid_cpf("111.111.111-11") is False
    assert backend._valid_cpf("529.982.247-24") is False


def test_trial_first_use_and_second_use_blocked(monkeypatch):
    reset_db()
    sent = []
    monkeypatch.setattr(backend, "_make_invite", lambda uid, label: "https://t.me/+TEST")
    monkeypatch.setattr(backend, "_send_telegram", lambda uid, text, invite_url="": sent.append((uid, text, invite_url)))

    client = backend.app.test_client()
    first = client.post("/checkout/trial/request", json=BUYER)
    assert first.status_code == 200
    data = first.get_json()
    assert data["eligible"] is True
    assert "trial_" in data["telegram_url"]
    token = data["telegram_url"].split("trial_", 1)[1]

    telegram = client.post(
        "/telegram/webhook",
        headers={"X-Telegram-Bot-Api-Secret-Token": "telegram-secret"},
        json={
            "message": {
                "text": f"/start trial_{token}",
                "from": {"id": 987654321, "username": "cliente_teste"},
            }
        },
    )
    assert telegram.status_code == 200
    assert sent and sent[-1][2] == "https://t.me/+TEST"

    second = client.post("/checkout/trial/request", json=BUYER)
    assert second.status_code == 200
    second_data = second.get_json()
    assert second_data["eligible"] is False
    assert second_data["reason"] == "TRIAL_ALREADY_USED"

    with sqlite3.connect(TEST_DB) as con:
        row = con.execute("SELECT trial_used,access_kind,access_status,telegram_user_id FROM users").fetchone()
    assert row == (1, "trial", "active", "987654321")


def test_purchase_price_and_coupon(monkeypatch):
    reset_db()
    calls = []

    def fake_mp_post(path, payload):
        calls.append((path, payload))
        n = len(calls)
        return {"id": f"sub-{n}", "status": "pending", "init_point": f"https://mp.test/sub-{n}"}

    monkeypatch.setattr(backend, "_mp_post", fake_mp_post)
    client = backend.app.test_client()

    normal = client.post("/checkout/purchase", json={**BUYER, "coupon": ""})
    assert normal.status_code == 200
    assert normal.get_json()["amount"] == 150.0
    assert calls[-1][1]["auto_recurring"]["transaction_amount"] == 150.0

    discounted = client.post("/checkout/purchase", json={**BUYER, "coupon": "FONSECA5"})
    assert discounted.status_code == 200
    assert discounted.get_json()["amount"] == 142.5
    assert discounted.get_json()["discount_percent"] == 5.0
    assert calls[-1][1]["auto_recurring"]["transaction_amount"] == 142.5

    invalid = client.post("/checkout/purchase", json={**BUYER, "coupon": "INVALIDO"})
    assert invalid.status_code == 400


def test_mp_signature_validation():
    data_id = "999999999"
    request_id = "abc-123"
    ts = "1704908010"
    manifest = f"id:{data_id};request-id:{request_id};ts:{ts};"
    digest = hmac.new(b"mp-secret", manifest.encode(), hashlib.sha256).hexdigest()
    signature = f"ts={ts},v1={digest}"
    assert backend._validate_mp_signature(signature, request_id, data_id) is True
    assert backend._validate_mp_signature(signature + "x", request_id, data_id) is False


def test_expiry_removes_access(monkeypatch):
    reset_db()
    user = backend._upsert_user(BUYER["name"], BUYER["email"], BUYER["phone"], BUYER["cpf"])
    past = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    with backend.db() as con:
        con.execute(
            "UPDATE users SET telegram_user_id='987654321',trial_used=1,access_kind='trial',access_status='active',access_expires_at=? WHERE id=?",
            (past, user["id"]),
        )
    removed = []
    monkeypatch.setattr(backend, "_remove_from_group", lambda uid: removed.append(uid))
    monkeypatch.setattr(backend, "_send_telegram", lambda *args, **kwargs: None)
    count = backend._expire_due_accesses()
    assert count == 1
    assert removed == ["987654321"]
    with backend.db() as con:
        state = con.execute("SELECT access_status,access_kind FROM users WHERE id=?", (user["id"],)).fetchone()
    assert tuple(state) == ("expired", "none")


def test_authorized_payment_webhook_grants_30_days(monkeypatch):
    reset_db()
    user = backend._upsert_user(BUYER["name"], BUYER["email"], BUYER["phone"], BUYER["cpf"])
    now = backend._iso()
    with backend.db() as con:
        con.execute(
            "INSERT INTO subscriptions(user_id,external_reference,mp_preapproval_id,mp_status,amount,created_at,updated_at) VALUES(?,?,?,?,?,?,?)",
            (user["id"], "fonsequinha:test", "pre-1", "authorized", 150.0, now, now),
        )

    monkeypatch.setattr(
        backend,
        "_mp_get",
        lambda path: {
            "preapproval_id": "pre-1",
            "payment": {"id": 555, "status": "approved", "status_detail": "accredited"},
        },
    )
    monkeypatch.setattr(backend, "_make_invite", lambda uid, label: "https://t.me/+PAID")
    monkeypatch.setattr(backend, "_send_telegram", lambda *args, **kwargs: None)

    data_id = "111"
    request_id = "req-1"
    ts = "1704908010"
    manifest = f"id:{data_id};request-id:{request_id};ts:{ts};"
    digest = hmac.new(b"mp-secret", manifest.encode(), hashlib.sha256).hexdigest()

    client = backend.app.test_client()
    response = client.post(
        f"/mercadopago/webhook?data.id={data_id}",
        headers={"X-Signature": f"ts={ts},v1={digest}", "X-Request-Id": request_id},
        json={"id": 9991, "type": "subscription_authorized_payment", "data": {"id": data_id}},
    )
    assert response.status_code == 200
    assert response.get_json()["payment_status"] == "approved"
    with backend.db() as con:
        row = con.execute("SELECT access_kind,access_status,access_expires_at FROM users WHERE id=?", (user["id"],)).fetchone()
    assert row[0] == "paid"
    assert row[1] == "active"
    expiry = backend._parse_dt(row[2])
    assert expiry is not None
    remaining = expiry - datetime.now(timezone.utc)
    assert timedelta(days=29, hours=23) < remaining <= timedelta(days=30, minutes=1)


def test_make_invite_unbans_before_creating_link(monkeypatch):
    calls = []

    def fake_telegram_call(method, payload):
        calls.append((method, dict(payload)))
        if method == "createChatInviteLink":
            return {"invite_link": "https://t.me/+SAFE"}
        return True

    monkeypatch.setattr(backend, "_telegram_call", fake_telegram_call)
    invite = backend._make_invite("987654321", "trial")

    assert invite == "https://t.me/+SAFE"
    assert [method for method, _ in calls] == ["unbanChatMember", "createChatInviteLink"]
    assert calls[0][1]["only_if_banned"] is True
    assert calls[0][1]["user_id"] == 987654321
