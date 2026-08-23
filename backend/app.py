from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import threading
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request

APP_VERSION = "2026.08.22-checkout-access-v1"
UTC = timezone.utc


def _env(name: str, default: str = "") -> str:
    return str(os.getenv(name, default) or "").strip()


def _env_int(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(_env(name, str(default)))
    except Exception:
        value = default
    return max(minimum, min(maximum, value))


def _env_float(name: str, default: float, minimum: float, maximum: float) -> float:
    try:
        value = float(_env(name, str(default)).replace(",", "."))
    except Exception:
        value = default
    return max(minimum, min(maximum, value))


def _iso(dt: datetime | None = None) -> str:
    return (dt or datetime.now(UTC)).astimezone(UTC).isoformat()


def _parse_dt(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def _db_path() -> Path:
    configured = _env("CHECKOUT_DB_PATH")
    if configured:
        return Path(configured)
    data = Path("/data")
    if data.exists() and data.is_dir():
        return data / "checkout_access.sqlite3"
    return Path(__file__).with_name("checkout_access.sqlite3")


@contextmanager
def db():
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(path), timeout=20)
    con.row_factory = sqlite3.Row
    try:
        con.execute("PRAGMA busy_timeout=10000")
        yield con
        con.commit()
    finally:
        con.close()


def init_db() -> None:
    with db() as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                public_token TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                name TEXT NOT NULL,
                email_norm TEXT NOT NULL,
                phone_norm TEXT NOT NULL,
                cpf_hash TEXT NOT NULL UNIQUE,
                telegram_user_id TEXT UNIQUE,
                telegram_username TEXT,
                trial_used INTEGER NOT NULL DEFAULT 0,
                trial_started_at TEXT,
                trial_expires_at TEXT,
                access_kind TEXT NOT NULL DEFAULT 'none',
                access_status TEXT NOT NULL DEFAULT 'inactive',
                access_started_at TEXT,
                access_expires_at TEXT,
                last_removed_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email_norm);
            CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_norm);
            CREATE INDEX IF NOT EXISTS idx_users_access_expiry ON users(access_status,access_expires_at);

            CREATE TABLE IF NOT EXISTS trial_tokens(
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                consumed_at TEXT,
                telegram_user_id TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS subscriptions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                external_reference TEXT NOT NULL UNIQUE,
                mp_preapproval_id TEXT UNIQUE,
                mp_status TEXT,
                amount REAL NOT NULL,
                coupon_code TEXT,
                checkout_url TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_payment_id TEXT,
                last_payment_status TEXT,
                last_payment_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON subscriptions(user_id);

            CREATE TABLE IF NOT EXISTS webhook_events(
                source TEXT NOT NULL,
                event_key TEXT NOT NULL,
                received_at TEXT NOT NULL,
                event_type TEXT,
                resource_id TEXT,
                payload_json TEXT,
                PRIMARY KEY(source,event_key)
            );
            """
        )


def _digits(value: str) -> str:
    return "".join(ch for ch in str(value or "") if ch.isdigit())


def _valid_cpf(value: str) -> bool:
    cpf = _digits(value)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for pos in (9, 10):
        total = sum(int(cpf[i]) * ((pos + 1) - i) for i in range(pos))
        digit = (total * 10 % 11) % 10
        if digit != int(cpf[pos]):
            return False
    return True


def _pii_secret() -> bytes:
    value = _env("CHECKOUT_PII_SECRET")
    if value:
        return value.encode("utf-8")
    if _env("CHECKOUT_ENV", "development").lower() == "production":
        raise RuntimeError("CHECKOUT_PII_SECRET is required in production")
    return b"development-only-change-me"


def _cpf_hash(cpf: str) -> str:
    return hmac.new(_pii_secret(), _digits(cpf).encode("ascii"), hashlib.sha256).hexdigest()


def _normalize_email(value: str) -> str:
    return str(value or "").strip().lower()


def _normalize_phone(value: str) -> str:
    digits = _digits(value)
    if len(digits) in {10, 11}:
        return "55" + digits
    return digits


def _valid_email(value: str) -> bool:
    text = _normalize_email(value)
    return "@" in text and "." in text.rsplit("@", 1)[-1] and len(text) <= 254


def _money(value: float) -> float:
    return round(float(value) + 1e-9, 2)


def _json_error(message: str, status: int = 400):
    return jsonify({"ok": False, "error": message}), status


def _buyer_from_payload(payload: dict[str, Any]) -> tuple[str, str, str, str]:
    name = str(payload.get("name") or "").strip()
    email = str(payload.get("email") or "").strip()
    phone = str(payload.get("phone") or "").strip()
    cpf = str(payload.get("cpf") or "").strip()
    if len(name) < 2 or len(name) > 120:
        raise ValueError("Nome inválido")
    if not _valid_email(email):
        raise ValueError("E-mail inválido")
    phone_n = _normalize_phone(phone)
    if len(phone_n) < 12 or len(phone_n) > 15:
        raise ValueError("WhatsApp inválido")
    if not _valid_cpf(cpf):
        raise ValueError("CPF inválido")
    return name, email, phone, cpf


def _http_json(
    url: str,
    *,
    method: str = "GET",
    body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 20,
) -> dict[str, Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    final_headers = {"Accept": "application/json"}
    if body is not None:
        final_headers["Content-Type"] = "application/json"
    if headers:
        final_headers.update(headers)
    req = urllib.request.Request(url, data=data, headers=final_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {raw[:600]}") from exc
    except Exception as exc:
        raise RuntimeError(f"HTTP request failed: {type(exc).__name__}: {exc}") from exc


def _telegram_call(method: str, payload: dict[str, Any]) -> dict[str, Any]:
    token = _env("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not configured")
    result = _http_json(
        f"https://api.telegram.org/bot{token}/{method}",
        method="POST",
        body=payload,
    )
    if not bool(result.get("ok")):
        raise RuntimeError(f"Telegram rejected {method}: {result}")
    return dict(result.get("result") or {})


def _send_telegram(user_id: str, text: str, *, invite_url: str = "") -> None:
    payload: dict[str, Any] = {
        "chat_id": str(user_id),
        "text": text,
        "disable_web_page_preview": True,
    }
    if invite_url:
        payload["reply_markup"] = {
            "inline_keyboard": [[{"text": "Entrar no Consenso", "url": invite_url}]]
        }
    _telegram_call("sendMessage", payload)


def _make_invite(user_id: str, label: str) -> str:
    chat_id = _env("TELEGRAM_CONSENSUS_CHAT_ID")
    if not chat_id:
        raise RuntimeError("TELEGRAM_CONSENSUS_CHAT_ID not configured")
    expire = int(time.time()) + _env_int("TELEGRAM_INVITE_TTL_SECONDS", 900, 60, 86400)
    result = _telegram_call(
        "createChatInviteLink",
        {
            "chat_id": chat_id,
            "name": f"{label}-{str(user_id)[-8:]}",
            "expire_date": expire,
            "member_limit": 1,
        },
    )
    invite = str(result.get("invite_link") or "")
    if not invite:
        raise RuntimeError("Telegram did not return invite_link")
    return invite


def _remove_from_group(user_id: str) -> None:
    chat_id = _env("TELEGRAM_CONSENSUS_CHAT_ID")
    if not chat_id:
        raise RuntimeError("TELEGRAM_CONSENSUS_CHAT_ID not configured")
    _telegram_call(
        "banChatMember",
        {"chat_id": chat_id, "user_id": int(user_id), "revoke_messages": False},
    )
    _telegram_call(
        "unbanChatMember",
        {"chat_id": chat_id, "user_id": int(user_id), "only_if_banned": True},
    )


def _mp_headers() -> dict[str, str]:
    token = _env("MERCADOPAGO_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("MERCADOPAGO_ACCESS_TOKEN not configured")
    return {"Authorization": f"Bearer {token}"}


def _mp_get(path: str) -> dict[str, Any]:
    return _http_json(f"https://api.mercadopago.com{path}", headers=_mp_headers())


def _mp_post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    return _http_json(
        f"https://api.mercadopago.com{path}",
        method="POST",
        body=payload,
        headers=_mp_headers(),
    )


def _coupon_discount(code: str) -> tuple[float, str]:
    code = str(code or "").strip().upper()
    if not code:
        return 0.0, ""
    configured = _env("COUPON_CODE").upper()
    if not configured or not hmac.compare_digest(code, configured):
        raise ValueError("Cupom inválido ou indisponível")
    pct = _env_float("COUPON_PERCENT", 5.0, 0.0, 100.0)
    return pct, code


def _find_user_by_identity(
    con: sqlite3.Connection,
    cpf_hash: str,
    email: str,
    phone: str,
) -> sqlite3.Row | None:
    return con.execute(
        "SELECT * FROM users WHERE cpf_hash=? OR email_norm=? OR phone_norm=? ORDER BY id LIMIT 1",
        (cpf_hash, email, phone),
    ).fetchone()


def _upsert_user(name: str, email: str, phone: str, cpf: str) -> sqlite3.Row:
    email_n = _normalize_email(email)
    phone_n = _normalize_phone(phone)
    cpf_h = _cpf_hash(cpf)
    now = _iso()
    with db() as con:
        row = _find_user_by_identity(con, cpf_h, email_n, phone_n)
        if row is None:
            public_token = secrets.token_urlsafe(24)
            cur = con.execute(
                "INSERT INTO users(public_token,created_at,updated_at,name,email_norm,phone_norm,cpf_hash) VALUES(?,?,?,?,?,?,?)",
                (public_token, now, now, name.strip(), email_n, phone_n, cpf_h),
            )
            row = con.execute("SELECT * FROM users WHERE id=?", (cur.lastrowid,)).fetchone()
        else:
            con.execute(
                "UPDATE users SET updated_at=?,name=?,email_norm=?,phone_norm=? WHERE id=?",
                (now, name.strip(), email_n, phone_n, row["id"]),
            )
            row = con.execute("SELECT * FROM users WHERE id=?", (row["id"],)).fetchone()
        assert row is not None
        return row


def _grant_paid_access(user_id: int, payment_id: str) -> None:
    now = datetime.now(UTC)
    expires = now + timedelta(days=30)
    invite_user: tuple[str, str] | None = None
    with db() as con:
        user = con.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        if user is None:
            return
        current_expiry = _parse_dt(user["access_expires_at"])
        was_active = str(user["access_status"] or "") == "active" and bool(current_expiry and current_expiry > now)
        con.execute(
            "UPDATE users SET access_kind='paid',access_status='active',access_started_at=?,access_expires_at=?,updated_at=? WHERE id=?",
            (_iso(now), _iso(expires), _iso(now), user_id),
        )
        if user["telegram_user_id"] and not was_active:
            invite_user = (str(user["telegram_user_id"]), str(user["name"] or "Assinante"))
        con.execute(
            "UPDATE subscriptions SET last_payment_id=?,last_payment_status='approved',last_payment_at=?,updated_at=? WHERE id=(SELECT id FROM subscriptions WHERE user_id=? ORDER BY id DESC LIMIT 1)",
            (str(payment_id), _iso(now), _iso(now), user_id),
        )
    if invite_user:
        try:
            invite = _make_invite(invite_user[0], "paid")
            _send_telegram(
                invite_user[0],
                "✅ Pagamento confirmado. Seu acesso ao Consenso está ativo por 30 dias.",
                invite_url=invite,
            )
        except Exception:
            pass


def _expire_due_accesses() -> int:
    now = datetime.now(UTC)
    with db() as con:
        due = con.execute(
            "SELECT * FROM users WHERE access_status='active' AND access_expires_at IS NOT NULL AND access_expires_at<=?",
            (_iso(now),),
        ).fetchall()
    expired = 0
    for user in due:
        tg = str(user["telegram_user_id"] or "")
        if tg:
            try:
                _remove_from_group(tg)
                try:
                    _send_telegram(
                        tg,
                        "Seu período de acesso ao Consenso terminou. Para voltar, renove sua assinatura no site.",
                    )
                except Exception:
                    pass
            except Exception:
                continue
        with db() as con:
            con.execute(
                "UPDATE users SET access_status='expired',access_kind='none',last_removed_at=?,updated_at=? WHERE id=? AND access_status='active'",
                (_iso(now), _iso(now), user["id"]),
            )
        expired += 1
    return expired


def _expiry_loop() -> None:
    interval = _env_int("EXPIRY_SCAN_SECONDS", 60, 30, 3600)
    while True:
        try:
            _expire_due_accesses()
        except Exception:
            pass
        time.sleep(interval)


def _validate_mp_signature(x_signature: str, x_request_id: str, data_id: str) -> bool:
    secret = _env("MERCADOPAGO_WEBHOOK_SECRET")
    if not secret:
        return _env("CHECKOUT_ENV", "development").lower() != "production"
    parts: dict[str, str] = {}
    for chunk in str(x_signature or "").split(","):
        if "=" in chunk:
            key, value = chunk.split("=", 1)
            parts[key.strip()] = value.strip()
    ts = parts.get("ts", "")
    received = parts.get("v1", "")
    if not ts or not received:
        return False
    manifest = ""
    if data_id:
        manifest += f"id:{data_id};"
    if x_request_id:
        manifest += f"request-id:{x_request_id};"
    manifest += f"ts:{ts};"
    expected = hmac.new(
        secret.encode("utf-8"),
        manifest.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, received)


def _record_webhook(
    source: str,
    event_key: str,
    event_type: str,
    resource_id: str,
    payload: dict[str, Any],
) -> bool:
    with db() as con:
        cur = con.execute(
            "INSERT OR IGNORE INTO webhook_events(source,event_key,received_at,event_type,resource_id,payload_json) VALUES(?,?,?,?,?,?)",
            (
                source,
                event_key,
                _iso(),
                event_type,
                resource_id,
                json.dumps(payload, ensure_ascii=False)[:20000],
            ),
        )
        return cur.rowcount == 1


app = Flask(__name__)


@app.after_request
def _cors(response):
    origin = request.headers.get("Origin", "")
    allowed = _env("FRONTEND_URL", "https://fonsecatools.com.br")
    if origin == allowed:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Telegram-Bot-Api-Secret-Token, X-Signature, X-Request-Id, X-Internal-Key"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response


@app.route("/health", methods=["GET"])
def health():
    with db() as con:
        users = int(con.execute("SELECT COUNT(*) FROM users").fetchone()[0])
    return jsonify(
        {
            "status": "ok",
            "version": APP_VERSION,
            "users": users,
            "telegram_ready": bool(
                _env("TELEGRAM_BOT_TOKEN")
                and _env("TELEGRAM_CONSENSUS_CHAT_ID")
                and _env("TELEGRAM_BOT_USERNAME")
            ),
            "mercadopago_ready": bool(_env("MERCADOPAGO_ACCESS_TOKEN")),
        }
    )


@app.route("/checkout/trial/request", methods=["POST", "OPTIONS"])
def request_trial():
    if request.method == "OPTIONS":
        return ("", 204)
    payload = request.get_json(silent=True) or {}
    try:
        name, email, phone, cpf = _buyer_from_payload(payload)
    except ValueError as exc:
        return _json_error(str(exc), 400)
    user = _upsert_user(name, email, phone, cpf)
    if int(user["trial_used"] or 0) == 1:
        return jsonify(
            {
                "eligible": False,
                "reason": "TRIAL_ALREADY_USED",
                "message": "Este cadastro já utilizou os 3 dias grátis. Para voltar ao Consenso, faça a assinatura.",
                "public_token": user["public_token"],
            }
        )
    token = secrets.token_urlsafe(24)
    now = datetime.now(UTC)
    expires = now + timedelta(minutes=30)
    with db() as con:
        con.execute(
            "INSERT INTO trial_tokens(token,user_id,created_at,expires_at) VALUES(?,?,?,?)",
            (token, user["id"], _iso(now), _iso(expires)),
        )
    username = _env("TELEGRAM_BOT_USERNAME").lstrip("@")
    if not username:
        return jsonify(
            {
                "eligible": True,
                "integration_pending": True,
                "message": "Telegram ainda não está conectado ao backend.",
                "public_token": user["public_token"],
            }
        )
    return jsonify(
        {
            "eligible": True,
            "telegram_url": f"https://t.me/{username}?start=trial_{token}",
            "expires_in_minutes": 30,
            "public_token": user["public_token"],
        }
    )


@app.route("/telegram/webhook", methods=["POST"])
def telegram_webhook():
    expected = _env("TELEGRAM_WEBHOOK_SECRET")
    received = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if expected and not hmac.compare_digest(expected, received):
        return _json_error("Invalid Telegram webhook secret", 401)
    payload = request.get_json(silent=True) or {}
    message = payload.get("message") or {}
    text = str(message.get("text") or "").strip()
    sender = message.get("from") or {}
    tg_id = str(sender.get("id") or "")
    if not tg_id or not text.startswith("/start"):
        return jsonify({"ok": True})
    parts = text.split(maxsplit=1)
    start_arg = parts[1].strip() if len(parts) > 1 else ""
    if not start_arg.startswith("trial_"):
        try:
            _send_telegram(tg_id, "Acesse fonsecatools.com.br para iniciar seu acesso ao Consenso.")
        except Exception:
            pass
        return jsonify({"ok": True})
    token = start_arg[len("trial_") :]
    now = datetime.now(UTC)
    with db() as con:
        trial = con.execute("SELECT * FROM trial_tokens WHERE token=?", (token,)).fetchone()
        if trial is None or trial["consumed_at"] or (_parse_dt(trial["expires_at"]) or now) <= now:
            try:
                _send_telegram(
                    tg_id,
                    "Esse link de ativação expirou ou já foi usado. Volte ao site e gere um novo.",
                )
            except Exception:
                pass
            return jsonify({"ok": True})
        user = con.execute("SELECT * FROM users WHERE id=?", (trial["user_id"],)).fetchone()
        other = con.execute(
            "SELECT id,trial_used FROM users WHERE telegram_user_id=? AND id<>?",
            (tg_id, trial["user_id"]),
        ).fetchone()
        if user is None or int(user["trial_used"] or 0) == 1 or (
            other is not None and int(other["trial_used"] or 0) == 1
        ):
            con.execute(
                "UPDATE trial_tokens SET consumed_at=?,telegram_user_id=? WHERE token=?",
                (_iso(now), tg_id, token),
            )
            try:
                _send_telegram(
                    tg_id,
                    "Seu teste grátis já foi utilizado. Para voltar ao Consenso, faça a assinatura no site.",
                )
            except Exception:
                pass
            return jsonify({"ok": True})
        trial_end = now + timedelta(hours=_env_int("TRIAL_HOURS", 72, 1, 720))
        con.execute(
            "UPDATE users SET telegram_user_id=?,telegram_username=?,trial_used=1,trial_started_at=?,trial_expires_at=?,access_kind='trial',access_status='active',access_started_at=?,access_expires_at=?,updated_at=? WHERE id=?",
            (
                tg_id,
                str(sender.get("username") or ""),
                _iso(now),
                _iso(trial_end),
                _iso(now),
                _iso(trial_end),
                _iso(now),
                user["id"],
            ),
        )
        con.execute(
            "UPDATE trial_tokens SET consumed_at=?,telegram_user_id=? WHERE token=?",
            (_iso(now), tg_id, token),
        )
    try:
        invite = _make_invite(tg_id, "trial")
        _send_telegram(
            tg_id,
            "🎁 Seus 3 dias grátis começaram agora. Use o botão abaixo para entrar no grupo Consenso.",
            invite_url=invite,
        )
    except Exception as exc:
        return _json_error(f"Falha ao liberar Telegram: {exc}", 502)
    return jsonify({"ok": True})


@app.route("/checkout/purchase", methods=["POST", "OPTIONS"])
def create_purchase():
    if request.method == "OPTIONS":
        return ("", 204)
    payload = request.get_json(silent=True) or {}
    try:
        name, email, phone, cpf = _buyer_from_payload(payload)
        discount_pct, coupon_code = _coupon_discount(str(payload.get("coupon") or ""))
    except ValueError as exc:
        return _json_error(str(exc), 400)
    user = _upsert_user(name, email, phone, cpf)
    base = _env_float("MONTHLY_PRICE", 150.0, 1.0, 100000.0)
    amount = _money(base * (1.0 - discount_pct / 100.0))
    external_reference = f"fonsequinha:{user['id']}:{secrets.token_hex(8)}"
    frontend = _env("FRONTEND_URL", "https://fonsecatools.com.br")
    mp_payload = {
        "reason": "Consenso Premium - assinatura mensal",
        "external_reference": external_reference,
        "payer_email": user["email_norm"],
        "auto_recurring": {
            "frequency": 1,
            "frequency_type": "months",
            "transaction_amount": amount,
            "currency_id": "BRL",
        },
        "back_url": f"{frontend}/?payment=return",
        "status": "pending",
    }
    try:
        mp = _mp_post("/preapproval", mp_payload)
    except RuntimeError as exc:
        return _json_error(f"Mercado Pago indisponível: {exc}", 503)
    mp_id = str(mp.get("id") or "")
    checkout_url = str(mp.get("init_point") or "")
    if not mp_id or not checkout_url:
        return _json_error("Mercado Pago não retornou o link da assinatura", 502)
    now = _iso()
    with db() as con:
        con.execute(
            "INSERT INTO subscriptions(user_id,external_reference,mp_preapproval_id,mp_status,amount,coupon_code,checkout_url,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)",
            (
                user["id"],
                external_reference,
                mp_id,
                str(mp.get("status") or "pending"),
                amount,
                coupon_code,
                checkout_url,
                now,
                now,
            ),
        )
    return jsonify(
        {
            "checkout_url": checkout_url,
            "subscription_id": mp_id,
            "amount": amount,
            "discount_percent": discount_pct,
            "public_token": user["public_token"],
        }
    )


@app.route("/checkout/status/<public_token>", methods=["GET"])
def checkout_status(public_token: str):
    with db() as con:
        user = con.execute("SELECT * FROM users WHERE public_token=?", (public_token,)).fetchone()
        if user is None:
            return _json_error("Cadastro não encontrado", 404)
        sub = con.execute(
            "SELECT * FROM subscriptions WHERE user_id=? ORDER BY id DESC LIMIT 1",
            (user["id"],),
        ).fetchone()
    return jsonify(
        {
            "trial_used": bool(user["trial_used"]),
            "trial_expires_at": user["trial_expires_at"],
            "access_kind": user["access_kind"],
            "access_status": user["access_status"],
            "access_expires_at": user["access_expires_at"],
            "subscription_status": sub["mp_status"] if sub else None,
            "last_payment_status": sub["last_payment_status"] if sub else None,
        }
    )


@app.route("/mercadopago/webhook", methods=["POST"])
def mercadopago_webhook():
    payload = request.get_json(silent=True) or {}
    resource_id = str(
        request.args.get("data.id", "") or (payload.get("data") or {}).get("id") or ""
    )
    if not _validate_mp_signature(
        request.headers.get("X-Signature", ""),
        request.headers.get("X-Request-Id", ""),
        resource_id,
    ):
        return _json_error("Invalid Mercado Pago signature", 401)
    event_type = str(payload.get("type") or payload.get("topic") or "")
    event_key = str(
        payload.get("id")
        or f"{event_type}:{resource_id}:{request.headers.get('X-Request-Id', '')}"
    )
    if not _record_webhook("mercadopago", event_key, event_type, resource_id, payload):
        return jsonify({"ok": True, "duplicate": True})

    if event_type == "subscription_preapproval" and resource_id:
        try:
            pre = _mp_get(f"/preapproval/{resource_id}")
        except RuntimeError:
            return jsonify({"ok": True, "deferred": True})
        status = str(pre.get("status") or "")
        ext = str(pre.get("external_reference") or "")
        with db() as con:
            con.execute(
                "UPDATE subscriptions SET mp_status=?,updated_at=? WHERE mp_preapproval_id=? OR external_reference=?",
                (status, _iso(), resource_id, ext),
            )
        return jsonify({"ok": True, "subscription_status": status})

    if event_type == "subscription_authorized_payment" and resource_id:
        try:
            invoice = _mp_get(f"/authorized_payments/{resource_id}")
        except RuntimeError:
            return jsonify({"ok": True, "deferred": True})
        preapproval_id = str(invoice.get("preapproval_id") or "")
        payment = invoice.get("payment") or {}
        payment_status = str(payment.get("status") or "")
        payment_id = str(payment.get("id") or resource_id)
        with db() as con:
            sub = con.execute(
                "SELECT * FROM subscriptions WHERE mp_preapproval_id=? ORDER BY id DESC LIMIT 1",
                (preapproval_id,),
            ).fetchone()
            if sub:
                con.execute(
                    "UPDATE subscriptions SET last_payment_id=?,last_payment_status=?,last_payment_at=?,updated_at=? WHERE id=?",
                    (payment_id, payment_status, _iso(), _iso(), sub["id"]),
                )
        if sub and payment_status == "approved":
            _grant_paid_access(int(sub["user_id"]), payment_id)
        return jsonify({"ok": True, "payment_status": payment_status})

    if event_type == "payment" and resource_id:
        try:
            payment = _mp_get(f"/v1/payments/{resource_id}")
        except RuntimeError:
            return jsonify({"ok": True, "deferred": True})
        status = str(payment.get("status") or "")
        ext = str(payment.get("external_reference") or "")
        with db() as con:
            sub = con.execute(
                "SELECT * FROM subscriptions WHERE external_reference=? ORDER BY id DESC LIMIT 1",
                (ext,),
            ).fetchone()
        if sub and status == "approved":
            _grant_paid_access(int(sub["user_id"]), resource_id)
        return jsonify({"ok": True, "payment_status": status})

    return jsonify({"ok": True, "ignored": True, "type": event_type})


@app.route("/internal/expire", methods=["POST"])
def force_expire():
    expected = _env("INTERNAL_API_KEY")
    received = request.headers.get("X-Internal-Key", "")
    if not expected or not hmac.compare_digest(expected, received):
        return _json_error("Unauthorized", 401)
    return jsonify({"expired": _expire_due_accesses()})


init_db()
_worker_started = False
_worker_lock = threading.Lock()


def _start_worker_once() -> None:
    global _worker_started
    if _env("ENABLE_EXPIRY_WORKER", "1").lower() in {"0", "false", "no"}:
        return
    with _worker_lock:
        if _worker_started:
            return
        thread = threading.Thread(target=_expiry_loop, name="checkout-expiry-worker", daemon=True)
        thread.start()
        _worker_started = True


_start_worker_once()


if __name__ == "__main__":
    port = _env_int("PORT", 8092, 1, 65535)
    app.run(host="0.0.0.0", port=port, debug=False)
