# https://www.ietf.org/rfc/rfc5545.txt

from datetime import datetime, timezone

DATE_FORMAT = '%Y%m%dT%H%M%SZ'

class Event:
    def __init__(
        self, 
        uid: str, 
        name: str, 
        start_date: datetime, 
        end_date: datetime
    ):
        self.uid = uid
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.create_date = datetime.utcnow()

    def generate_ical(self):
        lines = [
            "BEGIN:VEVENT",
            "UID:" + self.uid,
            "SUMMARY:" + self.name,
            "DTSTAMP:" + self.create_date.strftime(DATE_FORMAT),
            "DTSTART:" + self.start_date.strftime(DATE_FORMAT),
            "DTEND:" + self.end_date.strftime(DATE_FORMAT),
            "END:VEVENT",
        ]
        return '\n'.join(lines)


class Calendar:
    def __init__(self):
        self.events = {}

    def add_event(self, event: Event):
        if event.uid not in self.events:
            self.events[event.uid] = event

    def generate_ical(self):
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:spadiff",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
        ]
        for event in self.events.values():
            lines.append(event.generate_ical())
        lines.append("END:VCALENDAR")
        return '\n'.join(lines)
