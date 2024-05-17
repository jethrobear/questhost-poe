import configparser
import re
from tkinter import (
    BOTH,
    Button,
    END,
    Entry,
    Frame,
    Label,
    LabelFrame,
    LEFT,
    Tk,
    TOP,
    Toplevel,
)
import requests

config = configparser.ConfigParser()
config.read_file(open("tui.ini", "r"))
HOST = config.get("SERVER", "HOST")
API = config.get("SERVER", "API")
config.set("SERVER", "TICKET_URL", f"{HOST}{API}ticket/")
session = requests.Session()


class BarcodeEntry(Entry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind("<Return>", lambda e: self.event_generate("<<Finish>>"))

    def get_tid(self) -> str | None:
        result = re.search(
            r"(?P<TID>[A-Za-z0-9]{3,4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{5})",
            self.get(),
        )
        self.delete(0, END)
        if result:
            return result.group("TID").upper()


class TicketInformationLabelFrame(LabelFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ID = Frame(self)
        self.ID.pack(side=TOP, fill=BOTH)
        self.lblID = Label(self.ID, text="Ticket ID")
        self.lblID.pack(side=LEFT)
        self.txtID = Label(self.ID, borderwidth=1, relief="sunken")
        self.txtID.pack(side=LEFT, expand=True, fill=BOTH)
        self.status = Frame(self)
        self.status.pack(side=TOP, fill=BOTH)
        self.lblStatus = Label(self.status, text="Status")
        self.lblStatus.pack(side=LEFT)
        self.txtStatus = Label(self.status, borderwidth=1, relief="sunken")
        self.txtStatus.pack(side=LEFT, expand=True, fill=BOTH)
        self.ticketType = Frame(self)
        self.ticketType.pack(side=TOP, fill=BOTH)
        self.lblTicketType = Label(self.ticketType, text="Ticket Type")
        self.lblTicketType.pack(side=LEFT)
        self.txtTicketType = Label(self.ticketType, borderwidth=1, relief="sunken")
        self.txtTicketType.pack(side=LEFT, expand=True, fill=BOTH)
        self.buttonGroup = Frame(self)
        self.buttonGroup.pack(fill=BOTH)
        self.buttonCheckIn = Button(
            self.buttonGroup,
            text="Check-in",
            command=lambda: self.event_generate("<<CheckIn>>"),
        )
        self.buttonCheckIn.pack()

    def clear(self):
        self.txtID.configure(text="")
        self.txtStatus.configure(text="")
        self.txtTicketType.configure(text="")

    def set(self, id, status, ticketType):
        self.txtID.configure(text=id)
        self.txtStatus.configure(text=status)
        self.txtTicketType.configure(text=ticketType)

    def get_tid(self):
        return self.txtID.cget("text")


class Root(Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.txtBarcode = BarcodeEntry(self)
        self.txtBarcode.pack(fill=BOTH)
        self.txtBarcode.bind("<<Finish>>", self.on_finish)
        self.ticketDetail = TicketInformationLabelFrame(self, text="Ticket Detail")
        self.ticketDetail.pack(fill="both")
        self.ticketDetail.bind("<<CheckIn>>", self.on_checkin)
        self.txtBarcode.focus_set()

    def on_finish(self, event):
        self.ticketDetail.clear()
        tid = str(event.widget.get_tid() or "")
        if tid:
            try:
                result = session.get(f"{HOST}{API}ticket/{tid}/")
                result.raise_for_status()
                data = result.json()
                self.ticketDetail.set(data["id"], data["status"], data["ticket_type"])
            except requests.exceptions.HTTPError:
                pass

    def on_checkin(self, event):
        tid = self.ticketDetail.get_tid()
        if tid:
            try:
                session.get(f"{HOST}/ticket/{tid}/")
                checkin_result = session.post(
                    f"{HOST}/checkin/{tid}/",
                    headers={
                        "X-CSRFToken": session.cookies["csrftoken"],
                    },
                )
                checkin_result.raise_for_status()
            except requests.exceptions.HTTPError as e:
                top = Toplevel(self)
                lblError = Label(top, text=str(e))
                lblError.pack()


if __name__ == "__main__":
    root = Root()
    root.geometry("800x600")
    root.mainloop()
