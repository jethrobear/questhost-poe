import re
from subprocess import Popen, PIPE
import time
from typing import Any
from django.core.management.base import BaseCommand, CommandError
from ..commands import PTouchAccessError, PTouchNotFoundError
from terminal.models import *


class Command(BaseCommand):
    help = """Call `ptouch-print --info` to get the current printer's info
    as well as the printer's max width"""

    def handle(self, *args, **options):
        errlist = list()
        for retryidx in range(10):
            stdout, stderr = Popen(
                "ptouch-print --info", shell=True, stdout=PIPE, stderr=PIPE
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

            regex_result = re.search(
                r"(?P<WIDTH>\d+)px", stdout.decode().replace("\n", "")
            )
            if not regex_result:
                raise CommandError("Cannot find max width from output")
            return regex_result.group("WIDTH")
        raise CommandError("Retries exhausted. Errors where:\n" + "\n".join(errlist))
