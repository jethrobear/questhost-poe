from django.contrib import admin
from .models import *


class CheckInTabularInline(admin.TabularInline):
    model = CheckIn


class TicketInventoryTabularInline(admin.TabularInline):
    model = TicketInventory


@admin.register(Ticket)
class TicketModelAdmin(admin.ModelAdmin):
    inlines = [CheckInTabularInline, TicketInventoryTabularInline]
    list_display = ("id", "ticket_type",)


@admin.register(LostAndFoundVoucher)
class LostAndFoundVoucherModelAdmin(admin.ModelAdmin):
    pass


@admin.register(LockerVoucher)
class LockerVoucherModelAdmin(admin.ModelAdmin):
    pass


@admin.register(PrintJob)
class PrintJobModelAdmin(admin.ModelAdmin):
    pass
