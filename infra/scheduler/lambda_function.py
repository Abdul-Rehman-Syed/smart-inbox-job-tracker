import os
from typing import Any

import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client("ec2")
rds = boto3.client("rds")

EC2_INSTANCE_ID = os.environ["EC2_INSTANCE_ID"]
RDS_INSTANCE_ID = os.environ["RDS_INSTANCE_ID"]


def _client_error_code(error: ClientError) -> str:
    return error.response.get("Error", {}).get("Code", "")


def start_resources() -> list[str]:
    messages = []
    try:
        rds.start_db_instance(DBInstanceIdentifier=RDS_INSTANCE_ID)
        messages.append(f"Requested RDS start: {RDS_INSTANCE_ID}")
    except ClientError as error:
        code = _client_error_code(error)
        if code == "InvalidDBInstanceState":
            messages.append(f"RDS is not in a startable state: {RDS_INSTANCE_ID}")
        else:
            raise

    try:
        ec2.start_instances(InstanceIds=[EC2_INSTANCE_ID])
        messages.append(f"Requested EC2 start: {EC2_INSTANCE_ID}")
    except ClientError as error:
        code = _client_error_code(error)
        if code == "IncorrectInstanceState":
            messages.append(f"EC2 is not in a startable state: {EC2_INSTANCE_ID}")
        else:
            raise

    return messages


def stop_resources() -> list[str]:
    messages = []
    try:
        ec2.stop_instances(InstanceIds=[EC2_INSTANCE_ID])
        messages.append(f"Requested EC2 stop: {EC2_INSTANCE_ID}")
    except ClientError as error:
        code = _client_error_code(error)
        if code == "IncorrectInstanceState":
            messages.append(f"EC2 is not in a stoppable state: {EC2_INSTANCE_ID}")
        else:
            raise

    try:
        rds.stop_db_instance(DBInstanceIdentifier=RDS_INSTANCE_ID)
        messages.append(f"Requested RDS stop: {RDS_INSTANCE_ID}")
    except ClientError as error:
        code = _client_error_code(error)
        if code == "InvalidDBInstanceState":
            messages.append(f"RDS is not in a stoppable state: {RDS_INSTANCE_ID}")
        else:
            raise

    return messages


def lambda_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    action = event.get("action")

    if action == "start":
        messages = start_resources()
    elif action == "stop":
        messages = stop_resources()
    else:
        raise ValueError("Expected event action to be 'start' or 'stop'")

    return {"action": action, "messages": messages}
