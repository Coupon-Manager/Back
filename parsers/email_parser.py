from __future__ import annotations
import re
from dataclasses import dataclass

SUPPLIER_RE = re.compile(r'קיבלנו את הזמנת השובר שלך מ(.+)')
VALUE_RE = re.compile(r'סכום הזמנה:\s*₪([\d.]+)')
CODE_RE = re.compile(r'\b(\d{15,})\b')


@dataclass
class ParsedCoupon:
    supplier_name: str
    value: int
    code: str | None


def parse_coupon_email(body: str) -> ParsedCoupon | None:
    supplier_match = SUPPLIER_RE.search(body)
    value_match = VALUE_RE.search(body)
    if not supplier_match or not value_match:
        return None

    supplier_name = supplier_match.group(1).strip()
    value = round(float(value_match.group(1)))

    code_match = CODE_RE.search(body)
    code = code_match.group(1) if code_match else None

    return ParsedCoupon(supplier_name=supplier_name, value=value, code=code)
