#!/usr/bin/env python3
"""
Run inside the api container:
    docker compose exec api python scripts/backup.py
"""
import gzip
import os
import subprocess
import sys
from datetime import datetime, timezone

import boto3
from botocore.config import Config

DATABASE_URL = os.getenv("DATABASE_URL", "")
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID", "")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID", "")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY", "")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "coupon-assets")


def backup() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    key = f"backups/backup_{timestamp}.sql.gz"

    print("Running pg_dump...")
    result = subprocess.run(["pg_dump", "--clean", "--if-exists", DATABASE_URL], capture_output=True)
    if result.returncode != 0:
        print(f"pg_dump failed:\n{result.stderr.decode()}", file=sys.stderr)
        sys.exit(1)

    print("Compressing...")
    compressed = gzip.compress(result.stdout)

    print(f"Uploading to R2 as {key}...")
    client = boto3.client(
        "s3",
        endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )
    client.put_object(
        Bucket=R2_BUCKET_NAME,
        Key=key,
        Body=compressed,
        ContentType="application/gzip",
    )
    print(f"Done: {key}")
    return key


if __name__ == "__main__":
    backup()
