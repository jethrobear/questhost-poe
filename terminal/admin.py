from django.contrib import admin
from .models import *


class CheckInTabularInline(admin.TabularInline):
    model = CheckIn


@admin.register(Ticket)
class TicketModelAdmin(admin.ModelAdmin):
    inlines = [CheckInTabularInline]


@admin.register(LostAndFoundVoucher)
class LostAndFoundVoucherModelAdmin(admin.ModelAdmin):
    pass


@admin.register(LockerVoucher)
class LockerVoucherModelAdmin(admin.ModelAdmin):
    pass
