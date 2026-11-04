"""
FasalWatch — AWS DynamoDB Farmer Profile Tool
Manages farmer profiles in real AWS DynamoDB table: 'FasalWatch_Farmers'.
Falls back to local JSON if AWS DynamoDB is unavailable.
"""

import os
import json
import boto3
from botocore.exceptions import ClientError
from strands import tool

TABLE_NAME = "FasalWatch_Farmers"
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
LOCAL_PROFILES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "farmer_profiles.json")


def get_dynamo_resource():
    return boto3.resource("dynamodb", region_name=REGION)


def init_dynamodb_table():
    """Create and seed DynamoDB table if it doesn't exist."""
    dynamo = get_dynamo_resource()
    client = boto3.client("dynamodb", region_name=REGION)

    existing_tables = client.list_tables()["TableNames"]
    if TABLE_NAME not in existing_tables:
        print(f"📦 Creating AWS DynamoDB table '{TABLE_NAME}'...")
        table = dynamo.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{"AttributeName": "farmer_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "farmer_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        table.meta.client.get_waiter("table_exists").wait(TableName=TABLE_NAME)
        print("✅ DynamoDB table created.")

        # Seed with initial data
        with open(LOCAL_PROFILES_PATH, "r", encoding="utf-8") as f:
            profiles = json.load(f)

        for fid, data in profiles.items():
            item = dict(data)
            item["farmer_id"] = fid
            # DynamoDB requires floats to be Decimal or strings
            item["latitude"] = str(item["latitude"])
            item["longitude"] = str(item["longitude"])
            table.put_item(Item=item)
        print(f"✅ Seeded {len(profiles)} farmer profiles into AWS DynamoDB.")
    return dynamo.Table(TABLE_NAME)


@tool
def get_farmer_profile_db(farmer_id: str) -> dict:
    """
    Retrieve a farmer profile from AWS DynamoDB.

    Args:
        farmer_id: Farmer unique ID (e.g., 'farmer_001')
    """
    try:
        table = get_dynamo_resource().Table(TABLE_NAME)
        resp = table.get_item(Key={"farmer_id": farmer_id})
        if "Item" in resp:
            item = resp["Item"]
            item["latitude"] = float(item["latitude"])
            item["longitude"] = float(item["longitude"])
            return {"status": "found", "source": "aws_dynamodb", "farmer": item}
    except Exception as e:
        print(f"⚠️ DynamoDB lookup notice: {e}. Checking local cache...")

    # Fallback to local
    with open(LOCAL_PROFILES_PATH, "r", encoding="utf-8") as f:
        profiles = json.load(f)
    if farmer_id in profiles:
        return {"status": "found", "source": "local_fallback", "farmer": profiles[farmer_id]}

    return {"status": "not_found", "error": f"No profile found for {farmer_id}"}


if __name__ == "__main__":
    table = init_dynamodb_table()
    res = get_farmer_profile_db("farmer_001")
    print("DynamoDB Profile result:", res)

