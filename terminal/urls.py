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
        "lostandfound/create",
        LostAndFoundVoucherCreateView.as_view(),
        name="lostandfound_create",
    ),
    path(
        "lostandfound/<str:slug>/claim",
        LostAndFoundVoucherUpdateView.as_view(),
        name="lostandfound_update_owner",
    ),
]
