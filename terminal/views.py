from typing import Any
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic
from .forms import *
from .models import *


class TerminalHomeView(generic.TemplateView):
    template_name = "terminal/index.html"


class DetailOrNoneView(generic.DetailView):
    redirect_view: str = None
    redirect_empty_view: str = None
    redirect_kwarg_name: str = None

    def get_object(self, *args, **kwargs):
        if self.kwargs.get(
            self.pk_url_kwarg,
        ) or self.kwargs.get(
            self.slug_url_kwarg,
        ):
            return super().get_object()
        return None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["barcode_form"] = BarcodeSearchForm()
        return context

    def post(self, request, *args, **kwargs):
        form = BarcodeSearchForm(request.POST)
        if form.is_valid():
            kwargs = {self.redirect_kwarg_name: form.cleaned_data["barcode"]}
            return redirect(self.redirect_view, **kwargs)
        return redirect(self.redirect_empty_view)

    def get(self, *args, **kwargs):
        try:
            return super().get(*args, **kwargs)
        except:
            return redirect(self.redirect_empty_view)


class TicketDetailView(DetailOrNoneView):
    model = Ticket
    redirect_view = "ticket_detail_id"
    redirect_empty_view = "ticket_detail"
    redirect_kwarg_name = "pk"


class LostAndFoundRedeemDetailView(DetailOrNoneView):
    model = LostAndFoundVoucher
    redirect_view = "lostandfound_detail_id"
    redirect_empty_view = "lostandfound_detail"
    redirect_kwarg_name = "slug"


class UpdatePOIStatusView(generic.UpdateView):
    model = Ticket
    fields = ["poi_name", "poi_address", "poi_contact"]

    def get_success_url(self) -> str:
        # TODO: Also try to upload to DyDB?
        return reverse("ticket_detail_id", kwargs={"pk": self.get_object().id})


class LostAndFoundVoucherCreateView(generic.CreateView):
    model = LostAndFoundVoucher
    fields = []

    def get_success_url(self) -> str:
        # TODO: Print here
        return reverse("lostandfound_detail")


class LostAndFoundVoucherUpdateView(generic.FormView):
    template_name = "terminal/lostandfoundvoucher_form.html"
    form_class = BarcodeSearchForm

    def form_invalid(self, form: Any) -> HttpResponse:
        # TODO: Add message
        return redirect("lostandfound_update_owner", **self.kwargs)

    def form_valid(self, form: Any) -> HttpResponse:
        try:
            slug = self.kwargs["slug"]
            ticket_object = Ticket.objects.get(
                id=form.cleaned_data["barcode"],
            )
            voucher_object = LostAndFoundVoucher.objects.get(
                slug=slug,
            )
            voucher_object.found_owner = ticket_object
            voucher_object.save()
            return redirect("lostandfound_detail_id", slug=slug)
        except:
            # TODO: Add message
            return redirect("lostandfound_update_owner", **self.kwargs)
