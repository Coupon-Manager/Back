#!/usr/bin/env python3
"""
Restore the latest backup from R2.
Run inside the api container:
    docker compose exec api python scripts/restore.py
"""
import gzip
import os
import subprocess
import sys

import boto3
from botocore.config import Config

DATABASE_URL = os.getenv("DATABASE_URL", "")
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID", "")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID", "")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY", "")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "coupon-assets")


def get_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


def restore() -> None:
    client = get_r2_client()

    response = client.list_objects_v2(Bucket=R2_BUCKET_NAME, Prefix="backups/")
    objects = response.get("Contents", [])
    if not objects:
        print("No backups found in R2.", file=sys.stderr)
        sys.exit(1)

    latest = max(objects, key=lambda o: o["LastModified"])
    key = latest["Key"]
    print(f"Downloading {key}...")

    obj = client.get_object(Bucket=R2_BUCKET_NAME, Key=key)
    compressed = obj["Body"].read()

    print("Decompressing...")
    sql = gzip.decompress(compressed)

    print("Restoring...")
    result = subprocess.run(["psql", DATABASE_URL], input=sql, capture_output=True)
    if result.returncode != 0:
        print(f"psql failed:\n{result.stderr.decode()}", file=sys.stderr)
        sys.exit(1)

    print(f"Done — restored from {key}")


if __name__ == "__main__":
    restore()
