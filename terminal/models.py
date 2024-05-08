from uuid import uuid4
from django.db import models
from random import randrange


# Create your models here.
class Ticket(models.Model):
    id = models.CharField(max_length=15, primary_key=True)
    status = models.CharField(max_length=64, default="Unknown")
    ticket_type = models.CharField(max_length=64, default="Unknown")
    is_poi = models.BooleanField(default=False)
    poi_name = models.CharField(max_length=64, null=True, blank=True)
    poi_address = models.CharField(max_length=64, null=True, blank=True)
    poi_contact = models.CharField(max_length=64, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.is_poi = False
        if self.poi_name or self.poi_address or self.poi_contact:
            self.is_poi = True
        return super().save(*args, **kwargs)


class CheckIn(models.Model):
    """Local check-in cache, that will be periodically sent back to DyDB
    once the job had ran
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    date = models.DateTimeField(auto_now=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)


class LostAndFoundVoucher(models.Model):
    slug = models.SlugField(null=True, blank=True)
    date = models.DateTimeField(auto_now=True)
    found = models.BooleanField(default=False)
    found_owner = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        # TODO: Add event in the future

        if not self.slug:
            while True:
                slug = f"0INV-PF24-"
                for _ in range(5):
                    slug += chr(randrange(ord("A"), ord("Z") + 1))
                # TODO: Have a way to get the rands faster
                try:
                    LostAndFoundVoucher.objects.get(slug=slug)
                except:
                    self.slug = slug
                    break

        if self.found_owner:
            self.found = True
        super().save(*args, **kwargs)


class LockerVoucher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    had_uploaded = models.BooleanField(default=False)
