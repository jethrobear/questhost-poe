from rest_framework import serializers
from .models import *


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            "id",
            "status",
            "ticket_type",
            "start_date",
            "end_date",
        )
