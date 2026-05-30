from __future__ import annotations
import email
import imaplib
import os
from datetime import datetime, timezone
from email.header import decode_header

from sqlmodel import Session, select

from models import Coupon, Supplier, User
from parsers.email_parser import ParsedCoupon, parse_coupon_email

GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
IMAP_HOST = "imap.gmail.com"


def _decode_str(value: str | bytes, charset: str | None) -> str:
    if isinstance(value, bytes):
        return value.decode(charset or "utf-8", errors="replace")
    return value


def _get_body(msg: email.message.Message) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset()
                return _decode_str(payload, charset)
    else:
        payload = msg.get_payload(decode=True)
        charset = msg.get_content_charset()
        return _decode_str(payload, charset)
    return ""


def _get_or_create_supplier(session: Session, name: str) -> Supplier:
    supplier = session.exec(
        select(Supplier).where(Supplier.name == name)
    ).first()
    if not supplier:
        supplier = Supplier(name=name)
        session.add(supplier)
        session.flush()
    return supplier


def import_emails(session: Session, added_by_id: int) -> dict:
    user = session.get(User, added_by_id)
    if not user:
        return {"imported": 0, "skipped": 0, "coupons": []}

    mail = imaplib.IMAP4_SSL(IMAP_HOST)
    mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
    mail.select("inbox")

    if user.last_email_sync:
        since = user.last_email_sync.strftime("%d-%b-%Y")
        _, message_ids = mail.search(None, f"SINCE {since}")
    else:
        _, message_ids = mail.search(None, "ALL")

    ids = message_ids[0].split()

    imported: list[Coupon] = []
    skipped = 0

    for uid in ids:
        _, msg_data = mail.fetch(uid, "(RFC822)")
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)
        body = _get_body(msg)

        parsed: ParsedCoupon | None = parse_coupon_email(body)
        if not parsed:
            skipped += 1
            continue

        if parsed.code:
            existing = session.exec(select(Coupon).where(Coupon.code == parsed.code)).first()
            if existing:
                skipped += 1
                continue

        supplier = _get_or_create_supplier(session, parsed.supplier_name)
        coupon = Coupon(
            supplier_id=supplier.id,
            value=parsed.value,
            code=parsed.code,
            added_by_id=added_by_id,
        )
        session.add(coupon)
        imported.append(coupon)

    user.last_email_sync = datetime.now(timezone.utc)
    session.add(user)
    session.commit()
    for c in imported:
        session.refresh(c)

    mail.logout()
    return {"imported": len(imported), "skipped": skipped, "coupons": imported}
