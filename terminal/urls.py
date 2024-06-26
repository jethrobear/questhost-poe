from django.urls import path
from .views import *

urlpatterns = [
    path(
        "",
        TerminalHomeView.as_view(),
        name="terminal_index",
    ),
    path(
        "ticket/",
        TicketDetailView.as_view(),
        name="ticket_detail",
    ),
    path(
        "ticket/<str:pk>/",
        TicketDetailView.as_view(),
        name="ticket_detail_id",
    ),
    path(
        "lostandfound/",
        LostAndFoundRedeemDetailView.as_view(),
        name="lostandfound_detail",
    ),
    path(
        "lostandfound/<str:slug>/",
        LostAndFoundRedeemDetailView.as_view(),
        name="lostandfound_detail_id",
    ),
    path(
        "ticket/<str:pk>/poi_update",
        UpdatePOIStatusView.as_view(),
        name="ticket_update_poi",
    ),
    path(
        "ticket/<str:pk>/status_update",
        UpdateTicketStatusView.as_view(),
        name="ticket_update_status",
    ),
    path(
        "lostandfound/create",
        LostAndFoundVoucherCreateView.as_view(),
        name="lostandfound_create",
    ),
    path(
        "lostandfound/<str:slug>/claim",
        LostAndFoundVoucherUpdateView.as_view(),
        name="lostandfound_update_owner",
    ),
    path(
        "checkin/<str:pk>/",
        CheckInCreateView.as_view(),
        name="checkin_create",
    ),
    path(
        "locker/<str:pk>/create",
        LockerVoucherCreateView.as_view(),
        name="lockervoucher_create",
    ),
    path(
        "locker/<str:pk>/claim",
        LockerVoucherUpdateView.as_view(),
        name="lockervoucher_update_claimed",
    ),
    path(
        "inventory/<str:pk>/claim",
        TicketInventoryUpdateView.as_view(),
        name="ticketinventory_update_claimed",
    ),
    path(
        "print/<int:pk>/",
        PrintDocumentView.as_view(),
        name="print_detail",
    ),
    # TUI
    path(
        "api/ticket/<str:pk>/",
        TicketRetrieveAPIView.as_view(),
        name="ticket_detail_api_id",
    ),
]
