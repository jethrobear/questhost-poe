from typing import Any
from django.core.management.base import BaseCommand, CommandError
import boto3
from boto3.dynamodb.types import TypeDeserializer
from terminal.models import *


class Command(BaseCommand):
    help = """Update Ticket model with values from DynamoDB.
    Note that a valid AWS Credentials should been loaded in awscli."""

    def add_arguments(self, parser):
        parser.add_argument("table_name", type=str)

    def handle(self, *args, **options):
        td = TypeDeserializer()
        dynamodb = boto3.client("dynamodb", region="ap-southeast-1")
        result = dynamodb.query(
            TableName=options["table_name"],
            KeyConditionExpression="#hash=:hash ",
            ExpressionAttributeNames={"#hash": "objtype"},
            ExpressionAttributeValues={":hash": {"S": "TICKET"}},
        )
        item: dict[str, dict[str, Any]]
        for item in result["Items"]:
            poi_status = td.deserialize(item.get("poi_contact", {"M": dict()}))
            defaults = {
                "status": td.deserialize(
                    item.get(
                        "status",
                        {"S": "Unknown"},
                    )
                ),
                "ticket_type": td.deserialize(
                    item.get(
                        "ticket_type",
                        {"S": "Unknown"},
                    )
                ),
                "is_poi": td.deserialize(
                    item.get(
                        "is_poi",
                        {"BOOL": False},
                    )
                ),
                "poi_name": poi_status.get("name"),
                "poi_address": poi_status.get("address"),
                "poi_contact": poi_status.get("contact_number"),
            }
            self.stdout.write(str(defaults))
            object, _ = Ticket.objects.get_or_create(
                pk=td.deserialize(item["objid"]),
                defaults=defaults,
            )
            object.save()

            self.stdout.write(self.style.SUCCESS("Successfully closed poll"))
