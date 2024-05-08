import csv
from pathlib import Path
import uuid
from django.core.management.base import BaseCommand
import boto3
from boto3.dynamodb.types import TypeSerializer
from terminal.models import *

td = TypeSerializer()


class Command(BaseCommand):
    help = """Update Ticket model with values from DynamoDB.
    Note that a valid AWS Credentials should been loaded in awscli."""

    def add_arguments(self, parser):
        parser.add_argument("evid", type=str)
        parser.add_argument("table_name", type=str)
        parser.add_argument("csv_path", type=str)

    def handle(self, *args, **options):
        evid = uuid.UUID(options["evid"])  # INFO: Just to check
        csv_path = Path(options["csv_path"])
        dynamodb = boto3.client("dynamodb", region_name="ap-southeast-1")
        with csv_path.open(encoding="utf-16") as FILE:
            for x in csv.DictReader(FILE, delimiter="\t"):
                if not x["Ticket number"]:
                    continue

                ddb_obj = dict()
                ddb_obj["evid"] = {
                    "Value": td.serialize(str(evid)),
                    "Action": "PUT",
                }
                ddb_obj["status"] = {
                    "Value": td.serialize(x["Payment status"]),
                    "Action": "PUT",
                }
                ddb_obj["ticket_type"] = {
                    "Value": td.serialize(x["Ticket type"]),
                    "Action": "PUT",
                }
                ddb_obj["subid"] = {
                    "Value": td.serialize(x["Email"]),
                    "Action": "PUT",
                }

                # TODO: Need to be automated
                dates: list[str] = []
                if "(Day 1)" in x["Ticket type"]:
                    dates.append("2024-08-31T00:00:00+08:00")
                if "(Day 2)" in x["Ticket type"]:
                    dates.append("2024-09-01T00:00:00+08:00")
                if "(Day 1 and 2)" in x["Ticket type"]:
                    dates.append("2024-08-31T00:00:00+08:00")
                    dates.append("2024-09-01T00:00:00+08:00")
                ddb_obj["dates"] = {
                    "Value": td.serialize(dates),
                    "Action": "PUT",
                }

                inventories: list[str] = list()
                if "CompactFlash" in x["Ticket type"]:
                    inventories.append("0TIV-PF24-00001")
                    inventories.append("0TIV-PF24-00002")
                if "DVD" in x["Ticket type"] or "CompactFlash" in x["Ticket type"]:
                    inventories.append("0TIV-PF24-00003")
                    inventories.append("0TIV-PF24-00004")
                if (
                    "Floppy disk" in x["Ticket type"]
                    or "DVD" in x["Ticket type"]
                    or "CompactFlash" in x["Ticket type"]
                ):
                    inventories.append("0TIV-PF24-00005")
                    inventories.append("0TIV-PF24-00006")
                    inventories.append("0TIV-PF24-00007")
                    inventories.append("0TIV-PF24-00008")
                ddb_obj["inventories"] = {
                    "Value": td.serialize(inventories),
                    "Action": "PUT",
                }

                result = dynamodb.update_item(
                    TableName=options["table_name"],
                    Key={
                        "objtype": {"S": "TICKET"},
                        "objid": {"S": x["Ticket number"]},
                    },
                    AttributeUpdates=ddb_obj,
                )
                print(result)
