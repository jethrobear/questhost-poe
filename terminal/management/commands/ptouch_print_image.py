from subprocess import Popen, PIPE
import time
from typing import Any
from django.core.management.base import BaseCommand, CommandError
from ..commands import PTouchAccessError, PTouchNotFoundError
from terminal.models import *


class Command(BaseCommand):
    help = "Print provided image path using ptouch-print"

    def add_arguments(self, parser):
        parser.add_argument("image_path", type=str)

    def handle(self, *args, **options):
        errlist = list()
        for retryidx in range(10):
            stdout, stderr = Popen(
                f"ptouch-print --image {options['image_path']}",
                shell=True,
                stdout=PIPE,
                stderr=PIPE,
            ).communicate()
            if "No P-Touch printer found on USB" in stderr.decode():
                # Don't retry printing if the printer is not found
                raise PTouchNotFoundError()
            if "libusb_open error :LIBUSB_ERROR_ACCESS" in stderr.decode():
                # Udev rule was not properly installed
                raise PTouchAccessError()
            if "busy" in stderr.decode().lower() or "busy" in stdout.decode().lower():
                # If the printer is busy, then wait
                time.sleep(0.5)
                errlist.append(f"[{retryidx}/10] {stdout} {stderr}")
                continue
            else:
                return stdout.decode()
        raise CommandError("Retries exhausted. Errors where:\n" + "\n".join(errlist))
