import pickle
from typing import Any
from django.core.management import call_command
from django.db.models import Model as DbModel
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.urls import reverse
from django.views import generic
from rest_framework.generics import RetrieveAPIView
from .forms import *
from .models import *
from .management.commands import PTouchAccessError, PTouchNotFoundError
from .serializers import TicketSerializer


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

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["locker_list"] = LockerVoucher.objects.filter(ticket=context["object"])
        context["inventory_list"] = TicketInventory.objects.filter(
            ticket=context["object"]
        )
        return context


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


class UpdateTicketStatusView(generic.UpdateView):
    model = Ticket
    fields = ["status"]

    def get_success_url(self) -> str:
        # TODO: Also try to upload to DyDB?
        return reverse("ticket_detail_id", kwargs={"pk": self.get_object().id})


class CreateAndPrintView(generic.View):
    redirect_view: str = None
    print_id_field: str = None
    redirect_id_field: str = None

    def get_print_and_redirect_obj(self) -> tuple[DbModel, DbModel]:
        raise NotImplementedError()

    def post(self, request, **kwargs):
        redirect_obj, print_obj = self.get_print_and_redirect_obj()
        print_job = PrintJob.objects.create(
            redirect_blob=pickle.dumps(redirect_obj),
            redirect_id=self.redirect_id_field,
            print_blob=pickle.dumps(print_obj),
            print_id=self.print_id_field,
            redirect_view=self.redirect_view,
        )
        return redirect("print_detail", pk=print_job.id)


class LostAndFoundVoucherCreateView(CreateAndPrintView):
    redirect_view = "lostandfound_detail_id"
    print_id_field = "slug"
    redirect_id_field = "slug"

    def get_print_and_redirect_obj(self) -> DbModel:
        object = LostAndFoundVoucher.objects.create()
        return object, object


class CheckInCreateView(CreateAndPrintView):
    redirect_view = "ticket_detail_id"
    print_id_field = "id"
    redirect_id_field = "pk"

    def get_print_and_redirect_obj(self) -> DbModel:
        object = CheckIn.objects.create(ticket_id=self.kwargs["pk"])
        return object.ticket, object.ticket


class LockerVoucherCreateView(CreateAndPrintView):
    redirect_view = "ticket_detail_id"
    print_id_field = "slug"
    redirect_id_field = "pk"

    def get_print_and_redirect_obj(self) -> DbModel:
        object = LockerVoucher.objects.create(ticket_id=self.kwargs["pk"])
        return object.ticket, object


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


class ClaimableFormView(generic.FormView):
    form_class = BarcodeSearchForm
    claim_model: Claimable = None
    claim_field_name: str = None
    failed_redirect: str = None

    def form_invalid(self, form: Any) -> HttpResponse:
        # TODO: Add message
        return redirect(self.failed_redirect, **self.kwargs)

    def form_valid(self, form: Any) -> HttpResponse:
        try:
            ticket_object = Ticket.objects.get(id=self.kwargs["pk"])
            kwargs = {self.claim_field_name: form.cleaned_data["barcode"]}
            claim_object = self.claim_model.objects.get(**kwargs)
            if claim_object.ticket != ticket_object:
                raise AssertionError()
            claim_object.claimed_date = timezone.now()
            claim_object.save()
            return redirect("ticket_detail_id", pk=claim_object.ticket.id)
        except:
            return redirect(self.failed_redirect, **self.kwargs)


class LockerVoucherUpdateView(ClaimableFormView):
    template_name = "terminal/lostandfoundvoucher_form.html"
    claim_model = LockerVoucher
    claim_field_name = "slug"
    failed_redirect = "lockervoucher_update_claimed"


class TicketInventoryUpdateView(ClaimableFormView):
    template_name = "terminal/ticketinventory_form.html"
    claim_model = TicketInventory
    claim_field_name = "inventory_id"
    failed_redirect = "ticketinventory_update_claimed"


class PrintDocumentView(generic.DetailView):
    model = PrintJob

    def get(self, request, pk=None):
        try:
            # Prepare tape dimensions
            max_width = int(call_command("ptouch_print_get_width"))

            # Unpack print object
            filepath = call_command(
                "generate_template",
                pk,
                max_width,
            )

            # Print image
            object: PrintJob = self.get_object()
            call_command("ptouch_print_image", filepath)
            object.is_printed = True
            object.save()

            # Find redirect
            redirect_obj = pickle.loads(object.redirect_blob)
            redirect_id = getattr(redirect_obj, object.redirect_id)
            return redirect(
                object.redirect_view,
                **{
                    object.redirect_id: redirect_id,
                }
            )

            # TODO: Delete Checkin or LostAndFoundVoucher if print was unsuccessful
        except PTouchNotFoundError:
            return HttpResponse("PTOUCH PRINTER NOT FOUND")
        except PTouchAccessError:
            return HttpResponse("PTOUCH UDEV NOT INSTALLED")


# For TUI
class TicketRetrieveAPIView(RetrieveAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
